# Monitoreo en producción (MLOps — Fase 3.3)

Este documento define **qué métricas** monitorear cuando el modelo de clasificación (o el de reconocimiento facial en SCA-EMPX) está en producción, y **dónde registrarlas**.

## Objetivo

Detectar degradación del modelo, fallos del servicio y desvíos de la distribución de entradas o scores para poder actuar (retrenar, rollback, ajustar umbrales).

---

## Métricas recomendadas

| Métrica | Descripción | Dónde registrarla |
|--------|-------------|-------------------|
| **Latencia de inferencia** | Tiempo (ms) por predicción o por batch (p50, p95, p99). | MLFlow (métricas custom), APM (Application Performance Monitoring), o logs estructurados (JSON) que luego se agreguen en un dashboard. |
| **Tasa de error** | Proporción de solicitudes que fallan (excepciones, timeouts). | Mismo que arriba; idealmente mismo sistema que el resto de la API (p. ej. contadores de errores por endpoint). |
| **Distribución de scores** | Histograma o percentiles de la confianza/scores por clase (p. ej. max softmax). Detecta si las predicciones se vuelven más inciertas o sesgadas. | MLFlow (log distribución como métrica o artefacto), Comet, o sistema de métricas (Prometheus/Grafana) con histogramas. |
| **Accuracy/errores en producción** | Si hay etiquetas reales (feedback), comparar predicciones vs realidad para accuracy o error rate por clase. | MLFlow, Comet o tabla de evaluación que alimente un reporte. |

Para el **clasificador MNIST** del entrenamiento: en producción se podría exponer un endpoint que reciba una imagen, devuelva la clase y el score; la latencia y la distribución de scores son las métricas más fáciles de obtener sin etiquetas.

Para el **reconocimiento facial** (DeepFace/backend SCA-EMPX): latencia por comparación, tasa de rechazo/error por intento de acceso, y distribución de scores de similitud.

---

## Dónde registrarlas

1. **MLFlow:** `mlflow.log_metric()` (o API REST) para métricas agregadas por ventana de tiempo; opcionalmente artefactos para distribuciones o reportes.
2. **Comet ML:** métricas de producción en un proyecto separado (p. ej. `sca-empx-prod`) para no mezclar con experimentos de entrenamiento.
3. **Logs estructurados:** el backend FastAPI puede escribir JSON con `latency_ms`, `score`, `endpoint`, `error`; luego un pipeline (Logstash, Fluentd, o servicio en la nube) agrega y dibuja en un dashboard.
4. **Sistema de métricas existente:** si ya usas Prometheus, Grafana o el APM del proveedor cloud, registrar ahí latencia y errores; las distribuciones de scores pueden ser histogramas o percentiles.

Recomendación mínima: **logs estructurados** con latencia y score por inferencia, y un job periódico (o dashboard) que calcule percentiles y tasas de error. Para integración con el flujo ML, enviar agregados a MLFlow o Comet (p. ej. una vez al día).

---

## Próximos pasos (Fases 4–5)

- Contenerizar la API y el entorno de entrenamiento (Docker).
- Integrar en un pipeline único: entrenamiento → registro → criterios de promoción → despliegue, con monitoreo documentado de punta a punta.
