# Training — Fase 0 + Fase 1 (MLFlow) + Fase 2 (Comet ML)

Script de entrenamiento de un **modelo de clasificación** para cumplir la Guía de Monitoreo ML-IA y el roadmap (Fases 0 → 5).

## Modelo y dataset

- **Dataset:** MNIST (dígitos 0-9, 60k train + 10k test).
- **Modelo:** red convolucional pequeña (`SmallCNN`).
- **Métricas por época:** función de costo (loss), Accuracy y F1-score macro, en **train** y en **validación** (dos trazas por métrica para la Guía).

## Cómo ejecutar

Desde la **raíz del proyecto**:

```bash
uv run python training/train_classifier.py
```

Con opciones (MLFlow y Comet activados por defecto si hay `COMET_API_KEY`):

```bash
uv run python training/train_classifier.py --epochs 5 --batch-size 256 --out training/checkpoints
```

Para **no** registrar en MLFlow o en Comet:

```bash
uv run python training/train_classifier.py --no-mlflow
uv run python training/train_classifier.py --no-comet
uv run python training/train_classifier.py --no-mlflow --no-comet
```

La primera vez se descargará MNIST en `./data`. Los runs de MLFlow se guardan en `./mlruns` (por defecto).

---

## Fase 1 — MLFlow: gráficas para la Guía

El script registra en MLFlow:

- **Parámetros:** `epochs`, `batch_size`, `lr`, `val_ratio`, `seed`.
- **Métricas por época** (step = número de época):
  - `loss_train`, `loss_val` → gráfica de **función de costo** (train y validación).
  - `accuracy_train`, `accuracy_val` → gráfica de **Accuracy** (train y validación).
  - `f1_train`, `f1_val` → gráfica de **F1-score** (train y validación).
- **Modelo:** artefacto PyTorch registrado como `mnist-classifier`.

### Ver las gráficas (MLFlow UI)

1. Desde la **raíz del proyecto**: `mlflow ui`
2. Abrir **http://127.0.0.1:5000**
3. Seleccionar el experimento **mnist-classifier** y un run. En **Métricas** aparecen las tres gráficas (loss, accuracy, f1) con train y val.
4. Capturar o exportar para la entrega de la Guía.

### Tracking URI

Por defecto: `./mlruns`. Para remoto: `--mlflow-uri http://localhost:5000` o variable `MLFLOW_TRACKING_URI`.

---

## Fase 2 — Comet ML: gráficas para la Guía

El script registra en **Comet ML** las **mismas métricas** que en MLFlow (loss, accuracy, f1 en train y validación por época), siempre que esté definida la variable de entorno **`COMET_API_KEY`**.

### Configurar Comet ML

1. Crear cuenta en [comet.com](https://www.comet.com) y obtener tu API key.
2. Definir la variable de entorno (en la sesión o en `.env`):

   ```bash
   set COMET_API_KEY=tu_api_key
   ```

   (En PowerShell; en bash: `export COMET_API_KEY=tu_api_key`.)

3. Ejecutar el entrenamiento como siempre; el script detectará la key y enviará el experimento a Comet.

### Ver las gráficas (Comet)

1. Entrar en **https://www.comet.com** e iniciar sesión.
2. Abrir el proyecto **sca-empx-mnist** (o el nombre indicado con `--comet-project`).
3. Seleccionar el experimento del último run. En la pestaña **Charts** (o **Metrics**) aparecen las gráficas de `loss_train`, `loss_val`, `accuracy_train`, `accuracy_val`, `f1_train`, `f1_val` por paso (época).
4. Capturar o exportar para la entrega de la Guía (alternativa o complemento a MLFlow).

### Opciones Comet

| Opción | Descripción |
|-------|-------------|
| `--no-comet` | No registrar en Comet (aunque exista `COMET_API_KEY`). |
| `--comet-project NOMBRE` | Nombre del proyecto en Comet (por defecto: `sca-empx-mnist`). |

Si **no** defines `COMET_API_KEY`, el script imprime un aviso y continúa sin Comet; MLFlow sigue activo si no usas `--no-mlflow`.

---

## Salida esperada (consola)

Por cada época: una línea con `loss_train`, `loss_val`, `acc_train`, `acc_val`, `f1_train`, `f1_val`.

Al final: mensaje de MLFlow (`mlflow ui`) y, si Comet se usó, mensaje con el enlace a comet.com.

## Fases siguientes

- **Fases 3-5:** MLOps, Docker, pipeline de monitoreo.
