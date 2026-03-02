# Training — Fase 0 (Modelos e implementaciones)

Script de entrenamiento de un **modelo de clasificación** para cumplir la Guía de Monitoreo ML-IA y el roadmap (Fases 0 → 5).

## Modelo y dataset

- **Dataset:** MNIST (dígitos 0-9, 60k train + 10k test).
- **Modelo:** red convolucional pequeña (`SmallCNN`).
- **Métricas por época:** función de costo (loss), Accuracy y F1-score macro, en **train** y en **validación** (dos trazas por métrica para la Guía).

## Cómo ejecutar (Fase 0)

Desde la **raíz del proyecto**:

```bash
uv run python training/train_classifier.py
```

O con opciones:

```bash
uv run python training/train_classifier.py --epochs 5 --batch-size 256 --out training/checkpoints
```

La primera vez se descargará MNIST en `./data`.

## Salida esperada

Por cada época se imprime una línea con:

- `loss_train`, `loss_val`
- `acc_train`, `acc_val`
- `f1_train`, `f1_val`

Estos mismos valores se registrarán en **MLFlow** (Fase 1) y **Comet ML** (Fase 2) para generar las gráficas de la Guía.

## Fases siguientes

- **Fase 1:** Añadir `mlflow.start_run()`, `log_metric("loss_train", ...)` etc. en este script.
- **Fase 2:** Añadir registro en Comet ML en el mismo script.
- **Fases 3-5:** MLOps, Docker, pipeline de monitoreo.
