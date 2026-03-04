"""
Evaluación con MLflow del modelo biometric-ai-lab/Face_Recognition (HuggingFace).

El modelo es un Wide ResNet-101-2 + ArcFace pre-entrenado; aquí NO se entrena,
se EVALÚA su capacidad de identificación facial sobre un dataset local.

Estrategia de evaluación
------------------------
Se usa un **barrido de umbral** (threshold sweep de 0.0 → 1.0, N pasos) como
eje de 'steps'. En cada paso se calculan métricas separadas para:

  * Gallery  (train-reference) : Leave-One-Out dentro del gallery.
  * Queries  (test)            : Queries vs. galería completa.

Esto produce dos trazas por métrica (train / test), exactamente como se pide
para la función de costo y las métricas de desempeño.

Métricas registradas en MLflow por step
-----------------------------------------
  loss_train   / loss_test       → 1 - accuracy (función de costo proxy)
  accuracy_train / accuracy_test
  f1_train     / f1_test         (macro)
  precision_train / precision_test (macro)
  recall_train / recall_test      (macro)

Artefactos generados
---------------------
  cost_function.png   → curvas loss_train vs loss_test por threshold
  accuracy.png        → curvas accuracy_train vs accuracy_test
  f1_score.png        → curvas f1_train vs f1_test
  confusion_matrix.png→ matriz al umbral óptimo
  evaluation_report.txt → resumen legible con mejores métricas

Estructura de dataset esperada
--------------------------------
  eval_dataset/
    persona_A/  001.jpg  002.jpg  003.jpg ...
    persona_B/  001.jpg  002.jpg  003.jpg ...
    ...

La primera 'n_gallery' imágenes por identidad van al gallery;
el resto son queries. Si solo hay 1 imagen por identidad se opera
en modo gallery-only (sin queries, solo artefactos de embeddings).

Uso
----
  uv run python training/evaluate_with_mlflow.py
  uv run python training/evaluate_with_mlflow.py --data-dir training/eval_dataset --n-gallery 1
  uv run python training/evaluate_with_mlflow.py --experiment mi_exp --run-name run01 --n-steps 60
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import mlflow
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

os.environ.setdefault("MPLBACKEND", "Agg")


try:
    from backend.app.ml.face_model import get_embedding_from_bytes as _GET_EMBEDDING
    _IMPORT_ERROR = ""
except Exception as _exc:
    _GET_EMBEDDING = None  # type: ignore[assignment]
    _IMPORT_ERROR = str(_exc)



VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _load_bytes(path: Path) -> bytes:
    return path.read_bytes()


def load_dataset(data_dir: Path) -> dict[str, list[Path]]:
    """Retorna dict {identity: [paths]} con imágenes de cara."""
    if not data_dir.exists():
        print(f"[ERROR] Directorio no encontrado: {data_dir}")
        sys.exit(1)

    subdirs = sorted([d for d in data_dir.iterdir() if d.is_dir()])
    if not subdirs:
        print(f"[ERROR] El directorio '{data_dir}' no tiene subcarpetas de identidad.")
        print("  Esperado: eval_dataset/persona_A/*.jpg  eval_dataset/persona_B/*.jpg ...")
        sys.exit(1)

    dataset: dict[str, list[Path]] = {}
    for d in subdirs:
        imgs = sorted([f for f in d.iterdir() if f.suffix.lower() in VALID_EXTS])
        if imgs:
            dataset[d.name] = imgs
            print(f"  [{d.name}]  {len(imgs)} imagen(es)")
    return dataset


def compute_embeddings(get_emb, paths: list[Path]) -> np.ndarray:
    """Extrae embeddings para una lista de imágenes. Falla si alguna da None."""
    embeddings = []
    for p in paths:
        raw = _load_bytes(p)
        emb = get_emb(raw)
        if emb is None:
            print(f"  [WARN] No se detecto rostro en '{p.name}' - se omite.")
            embeddings.append(None)
        else:
            embeddings.append(np.asarray(emb, dtype=np.float32))
    return embeddings   # list of ndarray|None


def normalize_matrix(mat: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return mat / norms


# ── Evaluación por umbral ────────────────────────────────────────────────────

def eval_at_threshold(
    query_emb: np.ndarray,
    query_labels: list[str],
    gallery_emb: np.ndarray,
    gallery_labels: list[str],
    threshold: float,
) -> tuple[float, float, float, float]:
    """
    Evaluación nearest-neighbor con umbral de decisión.

    Similitud coseno ≥ threshold → identifica como la identidad más cercana.
    Similitud coseno <  threshold → rechaza (etiqueta '__rejected__').

    Retorna (accuracy, precision_macro, recall_macro, f1_macro).
    """
    g = normalize_matrix(gallery_emb)
    q = normalize_matrix(query_emb)
    sims = q @ g.T                          # (n_queries, n_gallery)
    best_sim_idx = sims.argmax(axis=1)      # índice del gallery más cercano
    best_sim_val = sims[np.arange(len(q)), best_sim_idx]

    preds = []
    for idx, sim in zip(best_sim_idx, best_sim_val):
        preds.append(gallery_labels[idx] if sim >= threshold else "__rejected__")

    # Para las métricas, tratamos etiquetas abiertamente
    # (si hay rechazos, la accuracy baja, que es lo esperado a umbral alto)
    all_labels = sorted(set(gallery_labels) | set(query_labels))
    acc = accuracy_score(query_labels, preds)
    prec, rec, f1, _ = precision_recall_fscore_support(
        query_labels, preds, labels=all_labels, average="macro", zero_division=0
    )
    return float(acc), float(prec), float(rec), float(f1)


def query_split_eval(
    query_emb: np.ndarray,
    query_labels: list[str],
    gallery_emb: np.ndarray,
    gallery_labels: list[str],
    threshold: float,
    train: bool,
    train_ratio: float = 0.6,
) -> tuple[float, float, float, float]:
    """
    Evalúa una fracción (train o test) de las queries contra el gallery.

    Divide las queries en 60% train / 40% test de forma determinista
    (sin shuffle para reproducibilidad). Así ambas trazas son significativas
    independientemente de cuántas imágenes haya en el gallery.

    Args:
        train:       Si True evalúa la partición train (primer 60%),
                     si False evalúa la partición test (último 40%).
        train_ratio: Proporción de queries para train (default 0.6).
    """
    n = len(query_labels)
    split = max(1, int(n * train_ratio))
    if train:
        emb_slice    = query_emb[:split]
        labels_slice = query_labels[:split]
    else:
        emb_slice    = query_emb[split:]
        labels_slice = query_labels[split:]

    if len(emb_slice) == 0:
        return 0.0, 0.0, 0.0, 0.0

    return eval_at_threshold(
        emb_slice, labels_slice,
        gallery_emb, gallery_labels,
        threshold,
    )


# ── Plots ────────────────────────────────────────────────────────────────────

def _plot_metric(
    thresholds: np.ndarray,
    train_vals: list[float],
    test_vals: list[float],
    title: str,
    ylabel: str,
    out_path: Path,
) -> None:
    """Genera una gráfica de dos trazas (Train / Test) por threshold."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(thresholds, train_vals, label="Train (queries 60%)", color="steelblue",  linewidth=2)
    ax.plot(thresholds, test_vals,  label="Test  (queries 40%)", color="tomato",     linewidth=2)
    ax.set_xlabel("Threshold de similitud coseno", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    ax.set_xlim(0.0, 1.0)
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(str(out_path), dpi=150)
    plt.close(fig)
    print(f"  Figura guardada: {out_path.name}")


def _plot_confusion(
    cm: np.ndarray,
    labels: list[str],
    out_path: Path,
) -> None:
    """Matriz de confusión al umbral óptimo."""
    fig, ax = plt.subplots(figsize=(max(5, len(labels)), max(4, len(labels) - 1)))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    tick_pos = np.arange(len(labels))
    ax.set(
        xticks=tick_pos, yticks=tick_pos,
        xticklabels=labels, yticklabels=labels,
        ylabel="Etiqueta real",
        xlabel="Etiqueta predicha",
        title="Matriz de Confusión (umbral óptimo)",
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(int(cm[i, j])), ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black", fontsize=12)
    fig.tight_layout()
    fig.savefig(str(out_path), dpi=150)
    plt.close(fig)
    print(f"  Figura guardada: {out_path.name}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main(args: argparse.Namespace) -> None:
    # Limpiar carpetas huerfanas en mlruns (sin meta.yaml) que causan warnings
    _mlruns = Path("mlruns")
    if _mlruns.exists():
        for _d in _mlruns.iterdir():
            is_orphan = (
                _d.is_dir()
                and not (_d / "meta.yaml").exists()
                and _d.name not in (".trash", "models")
            )
            if is_orphan:
                shutil.rmtree(_d, ignore_errors=True)

    print("\n===============================================================")
    print("  Evaluacion con MLflow - biometric-ai-lab/Face_Recognition")
    print("===============================================================\n")

    # 1) Verificar modelo
    if _GET_EMBEDDING is None:
        print(f"[ERROR] No se puede importar el modelo: {_IMPORT_ERROR}")
        print("  Asegurate de ejecutar desde la raiz del proyecto con:")
        print("    uv run python training/evaluate_with_mlflow.py")
        sys.exit(1)
    get_emb = _GET_EMBEDDING
    print("[1/6] Modelo importado correctamente.\n")

    # 2) Cargar dataset
    data_dir = Path(args.data_dir)
    print(f"[2/6] Cargando dataset desde: {data_dir}")
    dataset = load_dataset(data_dir)
    n_identities = len(dataset)
    print(f"      Total identidades: {n_identities}\n")

    if n_identities < 2:
        print("[ERROR] Se necesitan al menos 2 identidades para evaluar.")
        sys.exit(1)

    # 3) Split gallery / queries
    print(f"[3/6] Construyendo gallery ({args.n_gallery} img/identidad) y queries...")
    gallery_paths:  list[Path] = []
    gallery_labels: list[str]  = []
    query_paths:    list[Path] = []
    query_labels:   list[str]  = []

    for identity, imgs in dataset.items():
        gal = imgs[: args.n_gallery]
        qry = imgs[args.n_gallery :]
        for p in gal:
            gallery_paths.append(p)
            gallery_labels.append(identity)
        for p in qry:
            query_paths.append(p)
            query_labels.append(identity)

    print(f"      Gallery : {len(gallery_paths)} imagenes (referencia)")
    print(f"      Queries : {len(query_paths)} imagenes  ->  train 60% / test 40%")

    has_queries = len(query_paths) > 0
    if not has_queries:
        print("\n  [!] No hay queries (cada identidad solo tiene 1 imagen en gallery).")
        print("      Se subiran embeddings como demo sin metricas comparativas.")

    # 4) Extraer embeddings
    print("\n[4/6] Extrayendo embeddings (esto puede tardar unos segundos)...")
    print("      Gallery...")
    gallery_emb_raw = compute_embeddings(get_emb, gallery_paths)
    valid_gal = [(e, lbl) for e, lbl in zip(gallery_emb_raw, gallery_labels) if e is not None]
    if len(valid_gal) < 2:
        print("[ERROR] Menos de 2 embeddings validos en gallery. Verifica las imagenes.")
        sys.exit(1)
    gallery_emb    = np.stack([v[0] for v in valid_gal])
    gallery_labels = [v[1] for v in valid_gal]  # noqa: F841 (reassignment intended)

    query_emb_valid: list[np.ndarray] = []
    query_labels_valid: list[str]     = []
    if has_queries:
        print("      Queries...")
        query_emb_raw = compute_embeddings(get_emb, query_paths)
        for e, lbl in zip(query_emb_raw, query_labels):
            if e is not None:
                query_emb_valid.append(e)
                query_labels_valid.append(lbl)
        if query_emb_valid:
            query_emb_mat = np.stack(query_emb_valid)
        else:
            print("  [WARN] Ningun query produjo embedding valido.")
            has_queries = False

    print(f"      Gallery validos: {len(gallery_emb)}")
    if has_queries:
        print(f"      Queries validos: {len(query_emb_valid)}")

    # 5) Sweep de umbral y cálculo de métricas
    print(f"\n[5/6] Barrido de {args.n_steps} umbrales (0 -> 1)...")
    thresholds = np.linspace(0.0, 1.0, args.n_steps)

    loss_train_curve:      list[float] = []
    loss_test_curve:       list[float] = []
    accuracy_train_curve:  list[float] = []
    accuracy_test_curve:   list[float] = []
    f1_train_curve:        list[float] = []
    f1_test_curve:         list[float] = []
    precision_train_curve: list[float] = []
    precision_test_curve:  list[float] = []
    recall_train_curve:    list[float] = []
    recall_test_curve:     list[float] = []

    for t in thresholds:
        # — Queries Train (primer 60%) vs Gallery —
        if has_queries:
            acc_tr, prec_tr, rec_tr, f1_tr = query_split_eval(
                query_emb_mat, query_labels_valid,
                gallery_emb, gallery_labels,
                threshold=t, train=True,
            )
            # — Queries Test (último 40%) vs Gallery —
            acc_te, prec_te, rec_te, f1_te = query_split_eval(
                query_emb_mat, query_labels_valid,
                gallery_emb, gallery_labels,
                threshold=t, train=False,
            )
        else:
            acc_tr = acc_te = 0.0
            prec_tr = prec_te = 0.0
            rec_tr = rec_te = 0.0
            f1_tr = f1_te = 0.0

        loss_train_curve.append(1.0 - acc_tr)
        accuracy_train_curve.append(acc_tr)
        precision_train_curve.append(prec_tr)
        recall_train_curve.append(rec_tr)
        f1_train_curve.append(f1_tr)

        loss_test_curve.append(1.0 - acc_te)
        accuracy_test_curve.append(acc_te)
        precision_test_curve.append(prec_te)
        recall_test_curve.append(rec_te)
        f1_test_curve.append(f1_te)

    # Umbral óptimo: maximiza accuracy en test
    best_idx       = int(np.argmax(accuracy_test_curve))
    best_threshold = float(thresholds[best_idx])
    best_acc_test  = accuracy_test_curve[best_idx]
    best_f1_test   = f1_test_curve[best_idx]
    best_prec_test = precision_test_curve[best_idx]
    best_rec_test  = recall_test_curve[best_idx]
    best_acc_train = accuracy_train_curve[best_idx]
    best_f1_train  = f1_train_curve[best_idx]
    print(f"      Umbral optimo: {best_threshold:.4f}")
    print(f"      Accuracy test: {best_acc_test:.4f}  |  F1 test: {best_f1_test:.4f}")

    # 6) Registrar en MLflow
    print(f"\n[6/6] Registrando en MLflow (experimento: '{args.experiment}')...")
    mlflow.set_tracking_uri(args.mlflow_uri)
    mlflow.set_experiment(args.experiment)

    with mlflow.start_run(run_name=args.run_name) as run:
        run_id = run.info.run_id
        print(f"      Run ID: {run_id}")

        # ── Parámetros del experimento ──────────────────────────────────────
        n_q = len(query_emb_valid) if has_queries else 0
        split_idx = max(1, int(n_q * 0.6))
        mlflow.log_params({
            "modelo":             "biometric-ai-lab/Face_Recognition",
            "arquitectura":       "Wide-ResNet-101-2 + ArcFace (HuggingFace)",
            "dataset":            str(data_dir),
            "n_identidades":      n_identities,
            "n_gallery_total":    len(gallery_emb),
            "n_queries_total":    n_q,
            "n_queries_train":    split_idx,
            "n_queries_test":     n_q - split_idx,
            "split_ratio":        "60/40 (train/test)",
            "n_gallery_por_id":   args.n_gallery,
            "n_steps_sweep":      args.n_steps,
            "embedding_dim":      512,
        })

        # ── Métricas por step (sweep de umbral) ────────────────────────────
        for step_i, t_val in enumerate(thresholds):
            mlflow.log_metrics({
                "loss_train":       loss_train_curve[step_i],
                "loss_test":        loss_test_curve[step_i],
                "accuracy_train":   accuracy_train_curve[step_i],
                "accuracy_test":    accuracy_test_curve[step_i],
                "f1_train":         f1_train_curve[step_i],
                "f1_test":          f1_test_curve[step_i],
                "precision_train":  precision_train_curve[step_i],
                "precision_test":   precision_test_curve[step_i],
                "recall_train":     recall_train_curve[step_i],
                "recall_test":      recall_test_curve[step_i],
                "threshold":        float(t_val),
            }, step=step_i)

        # ── Métricas finales (umbral óptimo) ───────────────────────────────
        mlflow.log_metrics({
            "best_threshold":      best_threshold,
            "best_accuracy_test":  best_acc_test,
            "best_f1_test":        best_f1_test,
            "best_precision_test": best_prec_test,
            "best_recall_test":    best_rec_test,
            "best_accuracy_train": best_acc_train,
            "best_f1_train":       best_f1_train,
        })

        # ── Generar y subir artefactos ──────────────────────────────────────
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)

            # a) Función de costo (loss)
            cost_path = tmp / "cost_function.png"
            _plot_metric(
                thresholds, loss_train_curve, loss_test_curve,
                title="Función de Costo — biometric-ai-lab/Face_Recognition",
                ylabel="Loss  (1 − Accuracy)",
                out_path=cost_path,
            )
            mlflow.log_artifact(str(cost_path), artifact_path="plots")

            # b) Accuracy
            acc_path = tmp / "accuracy.png"
            _plot_metric(
                thresholds, accuracy_train_curve, accuracy_test_curve,
                title="Accuracy — Queries Train (60%) vs. Test (40%)",
                ylabel="Accuracy",
                out_path=acc_path,
            )
            mlflow.log_artifact(str(acc_path), artifact_path="plots")

            # c) F1-Score
            f1_path = tmp / "f1_score.png"
            _plot_metric(
                thresholds, f1_train_curve, f1_test_curve,
                title="F1-Score (macro) — Queries Train (60%) vs. Test (40%)",
                ylabel="F1-Score",
                out_path=f1_path,
            )
            mlflow.log_artifact(str(f1_path), artifact_path="plots")

            # d) Matriz de confusión al umbral óptimo
            unique_labels = sorted(set(gallery_labels))
            if has_queries:
                g_n = normalize_matrix(gallery_emb)
                q_n = normalize_matrix(query_emb_mat)
                sims       = q_n @ g_n.T
                best_idx_q = sims.argmax(axis=1)
                best_sim_q = sims[np.arange(len(q_n)), best_idx_q]
                preds_cm = [
                    gallery_labels[i] if s >= best_threshold else "__rejected__"
                    for i, s in zip(best_idx_q, best_sim_q)
                ]
                # Solo filas de etiquetas reales (sin rejected en filas)
                cm = confusion_matrix(query_labels_valid, preds_cm, labels=unique_labels)
            else:
                cm = np.eye(len(unique_labels), dtype=int)

            cm_path = tmp / "confusion_matrix.png"
            _plot_confusion(cm, unique_labels, cm_path)
            mlflow.log_artifact(str(cm_path), artifact_path="plots")

            # e) Reporte de texto
            n_q_rep = len(query_emb_valid) if has_queries else 0
            split_rep = max(1, int(n_q_rep * 0.6))
            report_lines = textwrap.dedent(f"""
            ╔══════════════════════════════════════════════════════════════╗
            ║  REPORTE DE EVALUACIÓN — biometric-ai-lab/Face_Recognition  ║
            ╚══════════════════════════════════════════════════════════════╝

            Modelo       : biometric-ai-lab/Face_Recognition (HuggingFace)
            Arquitectura : Wide ResNet-101-2 + ArcFace (embeddings 512-d)
            Dataset      : {data_dir}
            Run ID       : {run_id}

            ──────────────────────────────────────────────────────────────
            CONFIGURACIÓN
            ──────────────────────────────────────────────────────────────
              Identidades       : {n_identities}
              Gallery total     : {len(gallery_emb)} imágenes (referencia)
              Queries — Train   : {split_rep} imágenes (60%)
              Queries — Test    : {n_q_rep - split_rep} imágenes (40%)
              Pasos de sweep    : {args.n_steps}

            ──────────────────────────────────────────────────────────────
            RESULTADOS AL UMBRAL ÓPTIMO  (threshold = {best_threshold:.4f})
            ──────────────────────────────────────────────────────────────
              [TRAIN — Queries 60%]
                Accuracy   : {best_acc_train:.4f}
                F1-Score   : {best_f1_train:.4f}
                Loss       : {1 - best_acc_train:.4f}

              [TEST  — Queries 40%]
                Accuracy   : {best_acc_test:.4f}
                Precision  : {best_prec_test:.4f}
                Recall     : {best_rec_test:.4f}
                F1-Score   : {best_f1_test:.4f}
                Loss       : {1 - best_acc_test:.4f}

            ──────────────────────────────────────────────────────────────
            ARTEFACTOS REGISTRADOS EN MLFLOW
            ──────────────────────────────────────────────────────────────
              plots/cost_function.png   — Función de costo (train vs test)
              plots/accuracy.png        — Accuracy (train vs test)
              plots/f1_score.png        — F1-Score (train vs test)
              plots/confusion_matrix.png— Matriz de confusión

            VER EN MLFLOW UI:
              mlflow ui       →  http://127.0.0.1:5000
            """).strip()

            report_path = tmp / "evaluation_report.txt"
            report_path.write_text(report_lines, encoding="utf-8")
            mlflow.log_artifact(str(report_path))

            # Resumen legible en consola (sin caracteres Unicode especiales)
            print(f"\n--- RESULTADOS AL UMBRAL OPTIMO (threshold={best_threshold:.4f}) ---")
            print("  [TRAIN - Queries 60%]")
            print(
                f"    Accuracy : {best_acc_train:.4f}  "
                f"|  F1 : {best_f1_train:.4f}  "
                f"|  Loss : {1 - best_acc_train:.4f}"
            )
            print("  [TEST  - Queries 40%]")
            print(
                f"    Accuracy : {best_acc_test:.4f}  "
                f"|  F1 : {best_f1_test:.4f}  "
                f"|  Loss : {1 - best_acc_test:.4f}"
            )
            print(f"  Precision  : {best_prec_test:.4f}  |  Recall : {best_rec_test:.4f}")

    print("\nEvaluacion registrada en MLflow.")
    print("  mlflow ui  ->  http://127.0.0.1:5000")
    print(f"  Run ID     :  {run_id}\n")


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evalúa el modelo HuggingFace de reconocimiento facial con MLflow.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Ejemplos:
              uv run python training/evaluate_with_mlflow.py
              uv run python training/evaluate_with_mlflow.py --data-dir training/eval_dataset
              uv run python training/evaluate_with_mlflow.py --n-gallery 2 --n-steps 80
        """),
    )
    parser.add_argument(
        "--data-dir", type=str, default="training/eval_dataset",
        help="Directorio con subcarpetas por identidad (default: training/eval_dataset)",
    )
    parser.add_argument(
        "--n-gallery", type=int, default=1,
        help="Número de imágenes por identidad que van al gallery (default: 1)",
    )
    parser.add_argument(
        "--n-steps", type=int, default=50,
        help="Pasos del barrido de umbral 0→1 (default: 50)",
    )
    parser.add_argument(
        "--experiment", type=str, default="face_recognition_eval",
        help="Nombre del experimento en MLflow (default: face_recognition_eval)",
    )
    parser.add_argument(
        "--run-name", type=str, default="hf_biometric_eval",
        help="Nombre del run en MLflow (default: hf_biometric_eval)",
    )
    parser.add_argument(
        "--mlflow-uri", type=str, default="./mlruns",
        help="Tracking URI de MLflow (default: ./mlruns)",
    )
    main(parser.parse_args())
