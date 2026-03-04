# Training — Evaluación facial con MLflow

Directorio con scripts para **evaluar** el modelo de reconocimiento facial del proyecto
SCA-EMPX y registrar métricas en MLflow. El modelo ya viene pre-entrenado desde HuggingFace;
aquí no se entrena, solo se evalúa.

---

## Script principal: `evaluate_with_mlflow.py`

Evalúa el modelo **`biometric-ai-lab/Face_Recognition`** (Wide ResNet-101-2 + ArcFace, 512-d)
sobre imágenes de caras y registra todo en MLflow.

### Qué registra en MLflow

Para cada paso del barrido de umbral (0.0 → 1.0):

| Métrica | Descripción |
|---------|-------------|
| `loss_train` / `loss_test` | Función de costo (1 − accuracy). Dos trazas por gráfica. |
| `accuracy_train` / `accuracy_test` | Exactitud de identificación. Dos trazas. |
| `f1_train` / `f1_test` | F1-Score macro. Dos trazas. |
| `precision_train` / `precision_test` | Precisión macro. |
| `recall_train` / `recall_test` | Recall macro. |

Artefactos guardados:
- `plots/cost_function.png` — curva de loss train vs test
- `plots/accuracy.png` — curva de accuracy train vs test
- `plots/f1_score.png` — curva de F1 train vs test
- `plots/confusion_matrix.png` — al umbral óptimo
- `evaluation_report.txt` — resumen con los mejores valores

---

### Paso 1 — Preparar el dataset

Crea carpetas con fotos de caras en `training/eval_dataset/`:

```
training/eval_dataset/
  persona_1/   001.jpg  002.jpg  003.jpg  004.jpg  005.jpg
  persona_2/   001.jpg  002.jpg  003.jpg  004.jpg  005.jpg
  persona_3/   001.jpg  002.jpg  003.jpg  004.jpg  005.jpg
```

- **Mínimo:** 2 personas × 2 fotos.
- **Recomendado:** 4–5 personas × 4–5 fotos de cara frontal y bien iluminada.
- Formatos aceptados: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`.
- La **primera foto** de cada carpeta va al gallery (referencia). Las demás se dividen 60% train / 40% test.

---

### Paso 2 — Ejecutar la evaluación

Desde la **raíz del proyecto**:

```powershell
uv run python training/evaluate_with_mlflow.py
```

Listo. Al terminar verás algo así en consola:

```
[TRAIN - Queries 60%]  Accuracy: 0.5833  |  F1: 0.3976  |  Loss: 0.4167
[TEST  - Queries 40%]  Accuracy: 0.7500  |  F1: 0.3333  |  Loss: 0.2500

Evaluacion registrada en MLflow.
  mlflow ui  ->  http://127.0.0.1:5000
  Run ID     :  2b33840e...
```

---

### Paso 3 — Ver los resultados en MLflow

```powershell
uv run mlflow ui
```

Abre **http://127.0.0.1:5000** en el navegador y navega así:

1. Barra izquierda → **Experiments**
2. Clic en **`face_recognition_eval`**
3. Clic en **Go to the Runs**
4. Clic en el nombre del run (ej. `hf_biometric_eval`)
5. Clic en **Evaluation Run**
6. Pestaña **Model Metrics** → selecciona las métricas para ver las gráficas con las dos trazas (train / test)

---

### Opciones avanzadas

```powershell
# Usar 2 fotos por persona en el gallery (más referencia)
uv run python training/evaluate_with_mlflow.py --n-gallery 2

# Más pasos en el barrido de umbral (curvas más suaves)
uv run python training/evaluate_with_mlflow.py --n-steps 100

# Dataset en otra carpeta
uv run python training/evaluate_with_mlflow.py --data-dir mi_carpeta/fotos

# Nombre de experimento y run personalizados
uv run python training/evaluate_with_mlflow.py --experiment mi_exp --run-name run_v2
```

---

### Cómo funciona internamente

La evaluación usa un **barrido de umbral de similitud coseno** (0.0 → 1.0, N pasos):

- En cada paso se compara cada query contra el gallery usando distancia coseno entre embeddings (512-d).
- Si la similitud es ≥ umbral → identifica a la persona más parecida del gallery.
- Si la similitud es < umbral → rechaza (no reconoce).
- Las métricas se calculan por separado para:
  - **Train**: primer 60% de las queries por identidad.
  - **Test**: último 40% de las queries por identidad.
- El **umbral óptimo** se elige donde el accuracy en test es máximo.

Esto produce **dos trazas por métrica** (train y test) a lo largo del barrido, tal como exige la Guía de Monitoreo ML-IA.

---

## Estructura del directorio

```
training/
  evaluate_with_mlflow.py   ← script principal (Guía ML-IA)
  eval_dataset/             ← tus imágenes de caras (una carpeta por persona)
    persona_1/
    persona_2/
    ...
  README.md                 ← este archivo
```

Los resultados de MLflow se guardan en `./mlruns/` (raíz del proyecto).
