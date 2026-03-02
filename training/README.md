# Training — Fase 0 + Fase 1 (MLFlow)

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

Con opciones (MLFlow activado por defecto):

```bash
uv run python training/train_classifier.py --epochs 5 --batch-size 256 --out training/checkpoints
```

Para **no** registrar en MLFlow (solo imprimir métricas):

```bash
uv run python training/train_classifier.py --no-mlflow
```

La primera vez se descargará MNIST en `./data`. Los runs de MLFlow se guardan en `./mlruns` (por defecto).

## Fase 1 — MLFlow: gráficas para la Guía

El script registra en MLFlow:

- **Parámetros:** `epochs`, `batch_size`, `lr`, `val_ratio`, `seed`.
- **Métricas por época** (step = número de época):
  - `loss_train`, `loss_val` → gráfica de **función de costo** (train y validación).
  - `accuracy_train`, `accuracy_val` → gráfica de **Accuracy** (train y validación).
  - `f1_train`, `f1_val` → gráfica de **F1-score** (train y validación).
- **Modelo:** artefacto PyTorch registrado como `mnist-classifier`.

### Ver las gráficas (MLFlow UI)

1. Desde la **raíz del proyecto**, arrancar la interfaz de MLFlow:

   ```bash
   mlflow ui
   ```

2. Abrir en el navegador: **http://127.0.0.1:5000** (o el puerto que indique MLFlow).

3. Seleccionar el experimento **mnist-classifier** y un run. En la pestaña **Métricas** aparecen las gráficas con dos trazas (train y val) para:
   - **loss** (función de costo),
   - **accuracy**,
   - **f1**.

4. Capturar o exportar esas tres gráficas para la entrega de la Guía de Monitoreo ML-IA.

### Tracking URI

Por defecto se usa el directorio local `./mlruns`. Para usar un servidor remoto:

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
uv run python training/train_classifier.py
```

O con el argumento:

```bash
uv run python training/train_classifier.py --mlflow-uri http://localhost:5000
```

## Salida esperada (consola)

Por cada época se imprime una línea con:

- `loss_train`, `loss_val`
- `acc_train`, `acc_val`
- `f1_train`, `f1_val`

Al final, si MLFlow está activo: mensaje indicando que el run se guardó y el comando `mlflow ui`.

## Fases siguientes

- **Fase 2:** Añadir registro en Comet ML en el mismo script (mismas métricas).
- **Fases 3-5:** MLOps, Docker, pipeline de monitoreo.
