"""
Motor de reconocimiento facial — SCA-EMPX.

Implementa un pipeline de dos etapas:

1. **Detección**: localiza el rostro en la imagen usando un detector YOLOv8
   exportado a ONNX (``yolov8s-face-lindevs.onnx``).
2. **Embeddings**: extrae un vector de 512 dimensiones con un backbone
   Wide ResNet-101-2 entrenado con ArcFace
   (``biometric-ai-lab/Face_Recognition``, HuggingFace).

La identificación se resuelve comparando embeddings por **similitud coseno**.
Si el modelo principal no puede cargarse, se activa automáticamente un
fallback basado en DeepFace Facenet512 + MTCNN.

Optimizaciones:
    - Inferencia íntegramente en CPU (``onnxruntime`` + ``torch.device('cpu')``).
    - Modelo singleton cargado una sola vez al arrancar (``lru_cache``).
    - Similitud coseno con ``numpy`` (sin overhead de torch en producción).
    - Caché local en ``<raiz>/.cache/face_recognition/`` para evitar
      re-descargas del repositorio HuggingFace.

API pública::

    emb  = get_embedding_from_bytes(jpeg_bytes)   # bytes → ndarray | None
    sim  = cosine_similarity(emb_a, emb_b)         # float 0–1
    best = find_best_match(query, candidates, thr)  # (id, sim) | None
    raw  = embedding_to_bytes(emb)                  # ndarray → bytes (BD)
    emb  = bytes_to_embedding(raw)                  # bytes   → ndarray
"""
from __future__ import annotations

import io
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as tv_models
from torchvision import transforms
import onnxruntime as ort
from deepface import DeepFace
from huggingface_hub import snapshot_download

log = logging.getLogger("sca.ml")

EMBEDDING_DIM   = 512
EMBEDDING_DTYPE = np.float32
CACHE_DIR       = Path(__file__).resolve().parents[3] / ".cache"

# ── Singleton del modelo ──────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_model():
    """Retorna la instancia singleton del modelo de reconocimiento facial.

    La primera llamada ejecuta la carga completa (descarga + inicialización).
    Las llamadas posteriores retornan el objeto ya en memoria sin coste
    adicional gracias a ``lru_cache``.

    Returns:
        _HFModel | _FallbackModel: Instancia lista para llamar a
        ``get_embedding``.
    """
    return _load_model()


def _load_model():
    """Descarga (si es necesario) e inicializa el modelo HuggingFace en CPU.

    Flujo:
        1. Comprueba si ``pytorch_model.bin`` y ``yolov8s-face-lindevs.onnx``
           ya existen en ``CACHE_DIR/face_recognition/``.
        2. Si faltan, los descarga desde ``biometric-ai-lab/Face_Recognition``
           vía ``snapshot_download``.
        3. Reconstruye la arquitectura ``FaceRecognitionModel`` y carga los
           pesos resolviendo la clave del checkpoint
           (``model_state_dict`` → ``model`` → bare).
        4. Crea una sesión ONNX para el detector YOLO.
        5. Si cualquier paso falla, retorna ``_FallbackModel``.

    Returns:
        _HFModel: Modelo principal listo para inferencia.
        _FallbackModel: Fallback DeepFace si ocurre cualquier excepción.
    """
    try:
        log.info("Cargando modelo biometric-ai-lab/Face_Recognition...")
        model_dir = CACHE_DIR / "face_recognition"
        model_dir.mkdir(parents=True, exist_ok=True)

        _ckpt_needed  = model_dir / "pytorch_model.bin"
        _yolo_needed  = model_dir / "yolov8s-face-lindevs.onnx"
        if _ckpt_needed.exists() and _yolo_needed.exists():
            local_dir = str(model_dir)
            log.info("Modelo ya en cach\u00e9: %s \u2014 omitiendo descarga", local_dir)
        else:
            local_dir = snapshot_download(
                repo_id="biometric-ai-lab/Face_Recognition",
                local_dir=str(model_dir),
            )
            log.info("Modelo descargado en: %s", local_dir)

        # ── Arquitectura (igual que inference.py del repo) ────────────────
        class FaceRecognitionModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.backbone = tv_models.wide_resnet101_2(weights=None)
                self.backbone.fc = nn.Identity()  # type: ignore
                self.embed = nn.Sequential(
                    nn.Linear(2048, 512),
                    nn.BatchNorm1d(512),
                    nn.ReLU(inplace=True),
                )

            def forward(self, x):
                return F.normalize(self.embed(self.backbone(x)), p=2, dim=1)

        device = torch.device("cpu")
        recog_model = FaceRecognitionModel().to(device)
        recog_model.eval()

        # ── Carga del checkpoint ──────────────────────────────────────────
        # El checkpoint fue guardado como training-checkpoint completo;
        # los pesos del modelo viven bajo la clave 'model_state_dict'.
        ckpt_path = Path(local_dir) / "pytorch_model.bin"
        checkpoint = torch.load(str(ckpt_path), map_location=device)
        if isinstance(checkpoint, dict):
            if "model_state_dict" in checkpoint:
                state = checkpoint["model_state_dict"]
            elif "model" in checkpoint:
                state = checkpoint["model"]
            else:
                state = checkpoint
        else:
            state = checkpoint
        recog_model.load_state_dict(state)
        log.info("Pesos del modelo HF cargados OK")

        # ── Detector YOLO ONNX ────────────────────────────────────────────
        yolo_path = Path(local_dir) / "yolov8s-face-lindevs.onnx"
        yolo_session = ort.InferenceSession(
            str(yolo_path),
            providers=["CPUExecutionProvider"],
        )

        hf_model = _HFModel(recog_model, yolo_session, device)
        log.warning("★ Modelo activo: biometric-ai-lab/Face_Recognition (HuggingFace, Wide-ResNet-101-2 + ArcFace)")
        return hf_model

    except Exception as e:
        log.error("Error cargando modelo HF: %s", e)
        log.warning("Fallback: usando DeepFace Facenet512")
        fb = _FallbackModel()
        log.warning("★ Modelo activo: DeepFace Facenet512 (fallback)")
        return fb


class _HFModel:
    """Pipeline de reconocimiento facial con el modelo biometric-ai-lab/Face_Recognition.

    Combina un detector YOLO (ONNX) para localizar el rostro y un backbone
    Wide ResNet-101-2 + ArcFace para extraer el embedding.

    Args:
        model:        Instancia de ``FaceRecognitionModel`` con pesos cargados.
        yolo_session: Sesión ``onnxruntime.InferenceSession`` del detector YOLO.
        device:       Dispositivo PyTorch (siempre ``cpu`` en este proyecto).
    """

    def __init__(self, model, yolo_session, device):
        self._model   = model
        self._yolo    = yolo_session
        self._device  = device
        self._in_name = yolo_session.get_inputs()[0].name
        self._transform = transforms.Compose([
            transforms.Resize((112, 112)),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
        ])

    def get_embedding(self, img_array: np.ndarray) -> Optional[np.ndarray]:
        """Detecta el rostro en la imagen y extrae su embedding.

        Args:
            img_array: Array RGB de forma ``(H, W, 3)`` en ``uint8``.

        Returns:
            Array ``float32`` de 512 dimensiones normalizado a norma unitaria,
            o ``None`` si no se detectó ningún rostro o ocurrió un error.
        """
        try:
            face = self._detect_face(img_array)
            if face is None:
                return None
            tensor: torch.Tensor = self._transform(Image.fromarray(face))  # type: ignore[assignment]
            tensor = tensor.unsqueeze(0).to(self._device)
            with torch.no_grad():
                emb = self._model(tensor).squeeze(0).cpu().numpy()
            return _normalize(emb.astype(EMBEDDING_DTYPE))
        except Exception as ex:
            log.debug("_HFModel.get_embedding: %s", ex)
            return None

    def _detect_face(self, rgb: np.ndarray) -> Optional[np.ndarray]:
        """Localiza el rostro más grande en la imagen con el detector YOLO.

        Redimensiona la imagen a 640×640 (entrada estándar de YOLOv8),
        ejecuta la inferencia ONNX y devuelve el recorte del bounding box
        con mayor área y confianza ≥ 0.5.

        Args:
            rgb: Array RGB de forma ``(H, W, 3)`` en ``uint8``.

        Returns:
            Recorte ``uint8`` del rostro detectado, o ``None`` si no hay
            ningún rostro con confianza suficiente.
        """
        h, w = rgb.shape[:2]
        # Redimensionar a 640x640 con PIL (sin cv2)
        resized = np.array(Image.fromarray(rgb).resize((640, 640))).astype(np.float32) / 255.0
        inp = np.transpose(resized, (2, 0, 1))[None]
        preds = self._yolo.run(None, {self._in_name: inp})[0]
        if preds.ndim == 3:
            preds = preds[0].T
        best, max_area = None, 0
        for pred in preds:
            if float(pred[4]) < 0.5:
                continue
            cx, cy, bw, bh = pred[:4]
            cx *= w / 640
            cy *= h / 640
            bw *= w / 640
            bh *= h / 640
            x1, y1 = max(0, int(cx - bw / 2)), max(0, int(cy - bh / 2))
            x2, y2 = min(w, int(cx + bw / 2)), min(h, int(cy + bh / 2))
            area = (x2 - x1) * (y2 - y1)
            if area > max_area:
                max_area, best = area, (x1, y1, x2, y2)
        if best is None:
            return None
        x1, y1, x2, y2 = best
        return rgb[y1:y2, x1:x2]


class _FallbackModel:
    """Modelo de respaldo basado en DeepFace Facenet512 + MTCNN.

    Se activa automáticamente cuando ``_load_model`` no puede inicializar
    el modelo HuggingFace (p. ej. sin conexión, dependencias faltantes o
    checkpoint corrupto). Produce embeddings de 512 dimensiones compatibles
    con los del modelo principal.
    """

    def __init__(self):
        log.info("Iniciando modelo fallback (DeepFace Facenet512)...")
        self._df = DeepFace
        log.info("Fallback listo")

    def get_embedding(self, img_array: np.ndarray) -> Optional[np.ndarray]:
        """Detecta el rostro con MTCNN y extrae el embedding con Facenet512.

        Args:
            img_array: Array RGB de forma ``(H, W, 3)`` en ``uint8``.

        Returns:
            Array ``float32`` de 512 dimensiones normalizado a norma unitaria,
            o ``None`` si DeepFace no detectó rostro o lanzó una excepción.
        """
        try:
            result: Any = self._df.represent(
                img_array,
                model_name="Facenet512",
                detector_backend="mtcnn",
                enforce_detection=True,
                align=True,
                normalization="Facenet",
            )
            if not result:
                return None
            emb = np.array(result[0]["embedding"], dtype=EMBEDDING_DTYPE)
            return _normalize(emb)
        except Exception:
            return None


# ── API pública ───────────────────────────────────────────────────────────────

def get_embedding_from_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
    """Punto de entrada principal para extraer embeddings desde bytes de imagen.

    Decodifica la imagen, obtiene el modelo activo (HF o fallback) y delega
    la detección + extracción al pipeline correspondiente.

    Args:
        image_bytes: Contenido binario de una imagen JPEG o PNG.

    Returns:
        Array ``float32`` de 512 dimensiones normalizado a norma unitaria,
        o ``None`` si la imagen es inválida o no se detectó rostro.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img)
    except Exception:
        return None

    model = get_model()
    return model.get_embedding(arr)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calcula la similitud coseno entre dos embeddings normalizados.

    Dado que los vectores ya están normalizados a norma unitaria, la similitud
    equivale al producto punto. El resultado se recorta al rango ``[0, 1]``
    para evitar valores negativos por errores de punto flotante.

    Args:
        a: Embedding normalizado de 512 dimensiones.
        b: Embedding normalizado de 512 dimensiones.

    Returns:
        Valor ``float`` en ``[0.0, 1.0]``. Valores cercanos a ``1.0`` indican
        alta similitud (misma persona).
    """
    return float(np.clip(np.dot(a, b), 0.0, 1.0))


def embedding_to_bytes(emb: np.ndarray) -> bytes:
    """Serializa un embedding a bytes para persistir en la base de datos.

    El vector se almacena como una secuencia contigua de valores ``float32``
    en orden nativo little-endian (512 × 4 bytes = 2048 bytes totales).

    Args:
        emb: Array ``float32`` de 512 dimensiones.

    Returns:
        Objeto ``bytes`` de 2048 bytes listo para guardar en una columna
        ``LargeBinary`` de SQLAlchemy.
    """
    return emb.astype(EMBEDDING_DTYPE).tobytes()


def bytes_to_embedding(data: bytes) -> np.ndarray:
    """Deserializa bytes de la base de datos a un array de embedding.

    Args:
        data: Bytes obtenidos de una columna ``LargeBinary`` (2048 bytes).

    Returns:
        Array ``float32`` de 512 dimensiones con copia propia en memoria
        (no comparte buffer con ``data``).
    """
    return np.frombuffer(data, dtype=EMBEDDING_DTYPE).copy()


def find_best_match(
    query: np.ndarray,
    candidates: list[tuple[int, np.ndarray]],
    threshold: float,
) -> Optional[tuple[int, float]]:
    """Busca la persona con mayor similitud coseno respecto a un embedding.

    Itera sobre todos los candidatos, calcula la similitud coseno con cada
    uno y retorna la mejor coincidencia solo si supera el umbral mínimo.

    Args:
        query:      Embedding de consulta normalizado (512-d).
        candidates: Lista de tuplas ``(id_persona, embedding)`` que forman
                    la galería de referencia.
        threshold:  Umbral mínimo de similitud coseno para aceptar el match
                    (valor típico: 0.6–0.8).

    Returns:
        Tupla ``(id_persona, similitud)`` con la mejor coincidencia redondeada
        a 4 decimales, o ``None`` si la lista está vacía o ningún candidato
        supera el umbral.
    """
    if not candidates:
        return None

    best_id  = None
    best_sim = -1.0

    for person_id, emb in candidates:
        sim = cosine_similarity(query, emb)
        if sim > best_sim:
            best_sim = sim
            best_id  = person_id

    if best_id is None or best_sim < threshold:
        return None

    return (best_id, round(best_sim, 4))


def _normalize(v: np.ndarray) -> np.ndarray:
    """Normaliza un vector a norma unitaria (L2).

    Args:
        v: Array numpy de cualquier dimensión.

    Returns:
        Vector escalado a norma 1. Si la norma es 0 retorna el vector
        original sin modificar para evitar división por cero.
    """
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v
