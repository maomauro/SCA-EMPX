# Flujo MLOps: entrenamiento → registro → promoción → despliegue (Fase 3.5)

Este documento describe el **flujo completo** de modelo de clasificación MNIST en SCA-EMPX: desde el entrenamiento hasta el despliegue y el monitoreo, con criterios de promoción.

---

## 1. Entrenamiento

- **Entrada:** dataset MNIST (versionado como `mnist-v1`), hiperparámetros (por defecto en `training/config_default.json` o por argumentos).
- **Comando típico (reproducible):**
  ```bash
  uv run python training/train_classifier.py --config training/config_default.json
  ```
- **Salida:** modelo entrenado en memoria; métricas por época (loss, accuracy, F1 en train y validación); artefactos y métricas enviados a MLFlow y, si está configurado, a Comet ML.
- **Versionado:** cada run tiene `data_version`, `training_version` y el `run_id` de MLFlow que identifica de forma única ese entrenamiento.

---

## 2. Registro

- **MLFlow:** el script registra el modelo PyTorch con `mlflow.pytorch.log_model(..., registered_model_name="mnist-classifier")`. En el Model Registry (MLFlow UI o API) aparecen versiones del modelo `mnist-classifier`.
- **Comet ML:** mismo experimento con parámetros y métricas; útil para comparar runs y gráficas.
- Los **tags** `data_version` y `training_version` permiten filtrar runs y elegir solo los que usan un dataset o pipeline concretos.

---

## 3. Criterios de promoción

Un run está listo para **promoción** (candidato a producción) si se cumple:

1. **Métricas de validación por encima del mínimo:**
   - `accuracy_val` ≥ umbral (p. ej. 0.95).
   - `f1_val` ≥ umbral (p. ej. 0.95).
2. **Sin sobreajuste excesivo:** `loss_val` no debe ser mucho mayor que `loss_train` (p. ej. ratio `loss_val / loss_train` &lt; 1.5).
3. **Reproducibilidad:** el run se ha generado con un config o parámetros documentados (mismo `seed`, `data_version`).

En la práctica: en la UI de MLFlow se filtran los runs por experimento y tags, se comparan métricas y se **transiciona** la versión elegida a "Staging" o "Production" en el Model Registry (si se usa flujo de etapas).

---

## 4. Despliegue

- **Staging:** servir la versión promocionada en un entorno de preproducción (misma API que producción pero tráfico limitado). Validar latencia y errores.
- **Producción:** reemplazar el modelo actual por la nueva versión (p. ej. descargando desde MLFlow Model Registry o desde el artefacto del run).
- El **backend** SCA-EMPX puede cargar el modelo desde una ruta o desde la URI de MLFlow; la variable de entorno o config debe apuntar a la versión aprobada.

---

## 5. Monitoreo post-despliegue

Ver **docs/mlops-monitoreo-produccion.md**: latencia de inferencia, tasa de error y distribución de scores. Si las métricas se degradan, se puede programar un retrenamiento o hacer rollback a la versión anterior del modelo.

---

## Resumen

| Fase | Acción |
|------|--------|
| Entrenamiento | `train_classifier.py` con config o args; salida en MLFlow + Comet. |
| Registro | Modelo y métricas en MLFlow (y Comet); tags de versionado. |
| Promoción | Criterios: accuracy_val, f1_val, sobreajuste; transición en Model Registry. |
| Despliegue | Staging → Producción; API carga la versión aprobada. |
| Monitoreo | Latencia, errores, distribución de scores (ver guía de monitoreo). |
