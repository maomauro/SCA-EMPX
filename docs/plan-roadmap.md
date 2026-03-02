# Plan: Roadmap General SCA-EMPX

**Fecha:** 1 de marzo de 2026 · **Estado:** DRAFT — Pendiente validación  
**Rama:** `docs/plan-roadmap`

---

## Cómo usar este documento

| Si quieres… | Ve a la sección |
|-------------|------------------|
| Ver todo el plan de un vistazo | [Índice](#índice) |
| Entender el estado actual del proyecto | [Parte 1: Contexto](#parte-1-contexto-y-estado-actual) |
| **Cumplir la Guía de Monitoreo ML-IA** (entrega académica) | [Parte 2: Ruta Guía ML-IA](#22-ruta-guía-monitoreo-ml-ia-entrega-académica) |
| Ejecutar el roadmap completo paso a paso | [Parte 2: Roadmap completo](#23-roadmap-completo-fases-a-e) |
| Ver el orden recomendado de las fases | [Resumen visual del roadmap](#3-resumen-visual-del-roadmap) |

---

## Índice

1. **Parte 1: Contexto y estado actual**
   - 1.1 Resumen ejecutivo
   - 1.2 Punto de retorno seguro (git tag)
   - 1.3 Validación del plan (auditoría 2 mar 2026)

2. **Parte 2: Qué hacer — Paso a paso**
   - 2.1 Objetivo general
   - 2.2 Ruta Guía Monitoreo ML-IA (entrega académica)
   - 2.3 Roadmap completo (Fases A → E)

3. **Resumen visual del roadmap**

4. **Anexos**
   - A. Detalle de cada fase (A, B, C, D, E)
   - B. Requisitos y checklist de la Guía ML-IA
   - C. Tabla de validación de bloqueadores

---

# Parte 1: Contexto y estado actual

## 1.1 Resumen ejecutivo

**SCA-EMPX** es un sistema FastAPI de control de acceso con reconocimiento facial que **funciona**, pero con deuda técnica. Este plan aborda:

- **Seis bloqueadores técnicos** (modelos faltantes, pipelines ML inconsistentes, endpoints duplicados, Python 3.13, dependencias ML sin grupo modular, favicon faltante).
- **Objetivo MLOps:** pipeline de monitoreo del entrenamiento de modelos IA-ML (Docker, MLFlow, Comet ML, MLOps).

Las correcciones recientes ya resolvieron parte del punto 1 (modelos); el resto del plan sigue vigente. Ver [1.3 Validación](#13-validación-del-plan-2-marzo-2026) para el estado actual de cada bloqueador.

---

## 1.2 Punto de retorno seguro

Antes de cambios grandes, crear un tag para poder volver atrás:

```bash
git tag pre-refactor-2026-03-01
```

---

## 1.3 Validación del plan (2 marzo 2026)

Auditoría cruzada con el código y con `docs/informe-coherencia-implementacion.md`. Resumen:

| # | Bloqueador | ¿Correcto? | Estado actual |
|---|------------|------------|---------------|
| 1 | Modelos BD faltantes (UsuarioSistema, ReconocimientoFacial) | Sí | UsuarioSistema y Autorizacion ya añadidos. ReconocimientoFacial no se usa; embeddings van en `Registro`. |
| 2 | Pipelines ML (512-d vs 128-d) | Sí | Vigente. Activo: face_model 512-d; inference 128-d solo en código no montado. |
| 3 | Endpoints duplicados (acceso vs access) | Sí | Vigente. Solo montado `acceso.py`; `access.py` es legacy. |
| 4 | Python ≥3.13 restrictivo | Sí | Vigente. Relajar a ≥3.11 o ≥3.12 si hace falta. |
| 5 | Dependencias ML sin grupo modular | Sí | Vigente. No hay grupo opcional `[ml]`. |
| 6 | favicon.ico → 404 | Sí | Vigente. Añadir favicon en frontend. |

Tabla completa en [Anexo C](#anexo-c-validación-de-bloqueadores).

---

# Parte 2: Qué hacer — Paso a paso

## 2.1 Objetivo general

Tener un **pipeline de monitoreo del entrenamiento de modelos IA-ML** que integre:

- Contenedorización (Docker)
- Experimentación y registro (MLFlow y/o Comet ML)
- Prácticas MLOps (versionado, pipeline reproducible, monitoreo)

---

## 2.2 Ruta Guía Monitoreo ML-IA (entrega académica)

**Objetivo:** Cumplir la *Guía Monitoreo en Proyectos de ML-IA* (clasificación, función de costo + 2 métricas, dos trazas train/val).

### Paso 1 — Modelo de clasificación

- Elegir un **modelo de clasificación** (red neuronal, Random Forest, XGBoost, etc.) y un dataset (MNIST, CIFAR, facial por identidades, etc.).

### Paso 2 — Instrumentar el entrenamiento

En cada época registrar:

- **Función de costo:** `loss_train`, `loss_val`
- **Métrica 1 (p. ej. Accuracy):** `accuracy_train`, `accuracy_val`
- **Métrica 2 (p. ej. F1):** `f1_train`, `f1_val`

### Paso 3 — Usar MLFlow o Comet ML

- Instalar `mlflow` o `comet-ml` y configurar (tracking URI o API key).
- En el loop de entrenamiento: `mlflow.log_metric("loss_train", valor, step=epoch)`, e igual para las demás métricas.
- Las UIs de MLFlow/Comet generan las gráficas con dos trazas (train vs val) por métrica.

### Paso 4 — Verificar entregables

| # | Entregable | Cómo verificarlo |
|---|------------|------------------|
| 1 | Gráfica de **función de costo** (train + validación) | Captura desde MLFlow/Comet: loss vs época, dos curvas. |
| 2 | Gráfica de **primera métrica** de desempeño (train + validación) | Captura: p. ej. accuracy vs época, dos curvas. |
| 3 | Gráfica de **segunda métrica** de desempeño (train + validación) | Captura: p. ej. F1 vs época, dos curvas. |

Requisitos detallados y checklist en [Anexo B](#anexo-b-requisitos-y-checklist-guía-ml-ia).

**Fases del plan que cubren esta ruta:** B (MLFlow) y/o C (Comet ML); opcionalmente E para integrar todo.

---

## 2.3 Roadmap completo (Fases A → E)

Orden recomendado para seguir **paso a paso**:

```
Fase A (Docker) → Fase B (MLFlow) → [Fase C (Comet) opcional] → Fase D (MLOps) → Fase E (Integración)
```

### Resumen de cada fase

| Fase | Nombre | En una frase |
|------|--------|----------------|
| **A** | Docker | Contenerizar la app (Dockerfile + docker-compose). |
| **B** | MLFlow | Registrar experimentos, métricas y modelos (tracking + UI). |
| **C** | Comet ML | Experimentación y gráficas (alternativa o complemento a MLFlow). |
| **D** | MLOps | Versionado, pipeline reproducible, monitoreo en producción, CI/CD. |
| **E** | Pipeline de monitoreo | Unificar todo: entrenamiento + dashboard + criterios de promoción. |

El **detalle de tareas y entregables** de cada fase está en [Anexo A](#anexo-a-detalle-de-fases-a-b-c-d-e).

### Orden paso a paso (lista)

1. **Fase A — Docker:** Crear `Dockerfile` y `docker-compose.yml`; documentar uso.
2. **Fase B — MLFlow:** Instalar MLFlow, configurar tracking, instrumentar el script de entrenamiento (métricas por época).
3. **Fase C — Comet ML (opcional):** Instalar Comet, configurar API key, registrar métricas en el mismo entrenamiento; decidir si se usa solo MLFlow, solo Comet o ambos.
4. **Fase D — MLOps:** Versionado de datos/modelo, script de entrenamiento reproducible, monitoreo en producción, CI/CD para ML.
5. **Fase E — Integración:** Un solo flujo de entrenamiento que registre en MLFlow/Comet, dashboard para decidir modelo a desplegar, documentación del pipeline.

---

# 3. Resumen visual del roadmap

```
                    ┌─────────────────────────────────────────────────────────┐
                    │           OBJETIVO: Pipeline de monitoreo IA-ML           │
                    └─────────────────────────────────────────────────────────┘
                                              │
        ┌─────────────────────────────────────┼─────────────────────────────────────┐
        ▼                 ▼                   ▼                   ▼                 ▼
   ┌─────────┐      ┌──────────┐        ┌──────────┐       ┌─────────┐       ┌─────────┐
   │ Fase A  │ ──► │  Fase B  │ ──►    │  Fase C  │  ──►  │ Fase D  │ ──►   │ Fase E  │
   │ Docker  │     │ MLFlow   │        │ Comet ML │       │ MLOps   │       │Pipeline │
   └─────────┘     └──────────┘        └──────────┘       └─────────┘       └─────────┘
        │                 │                   │                   │                 │
        ▼                 ▼                   ▼                   ▼                 ▼
   Contenedores    Experimentos         Visualización      Versionado +      Monitoreo
   y despliegue    y métricas           y comparación      CI/CD + prod      end-to-end
```

**Ruta corta (solo Guía ML-IA):** Fase B (o C) → checklist Anexo B → entregar gráficas.

---

# Anexos

## Anexo A: Detalle de fases A, B, C, D, E

### Fase A — Docker

**Objetivo:** Contenerizar SCA-EMPX para despliegue reproducible.

| Paso | Tarea |
|------|--------|
| A.1 | Definir `Dockerfile`: Python 3.12+, dependencias (uv/pip), puerto 8000, comando uvicorn. |
| A.2 | Crear `docker-compose.yml`: servicio `api`; opcional `mlflow` y BD. |
| A.3 | Volúmenes y variables de entorno (SQLite, `SECRET_KEY`, `DATABASE_URL`). |
| A.4 | Documentar: build, `docker compose up`, variables necesarias. |
| A.5 | (Opcional) Imagen multi-stage para reducir tamaño. |

**Entregables:** `Dockerfile`, `docker-compose.yml`, documentación (README o `docs/despliegue-docker.md`).

---

### Fase B — MLFlow

**Objetivo:** Registrar experimentos, métricas, artefactos y modelo (model registry).

| Paso | Tarea |
|------|--------|
| B.1 | Instalar `mlflow` (dependencia o grupo `[mlops]`). |
| B.2 | Configurar MLFlow Tracking Server; definir `MLFLOW_TRACKING_URI`. |
| B.3 | En el código de entrenamiento: `mlflow.start_run()`, `log_params`, `log_metrics` por época, artefactos. |
| B.4 | Registrar modelo con `mlflow.<flavor>.log_model()` (PyTorch, ONNX, etc.). |
| B.5 | (Opcional) Servicio MLFlow en `docker-compose`. |

**Entregables:** Servidor MLFlow accesible; script de entrenamiento instrumentado; documentación.

---

### Fase C — Comet ML

**Objetivo:** Experimentación y visualización (alternativa o complemento a MLFlow).

| Paso | Tarea |
|------|--------|
| C.1 | Instalar `comet-ml`; configurar `COMET_API_KEY` y proyecto. |
| C.2 | En el entrenamiento: `comet_ml.Experiment`, registrar hiperparámetros y métricas por época. |
| C.3 | Registrar artefactos (checkpoints, modelos) e imágenes si aplica. |
| C.4 | Decidir: solo MLFlow, solo Comet o ambos; documentar. |

**Entregables:** Integración Comet; documentación; criterio MLFlow vs Comet.

---

### Fase D — MLOps

**Objetivo:** Ciclo de vida trazable: versionado, pipeline reproducible, monitoreo en producción.

| Paso | Tarea |
|------|--------|
| D.1 | Versionado de datos y modelo (convención + MLFlow/tags). |
| D.2 | Pipeline de entrenamiento reproducible (script/job que entrene y registre). |
| D.3 | Monitoreo en producción (latencia, errores, distribución de scores). |
| D.4 | CI/CD para ML (tests, smoke train o evaluación vs baseline). |
| D.5 | Documentar flujo: entrenamiento → registro → despliegue. |

**Entregables:** Pipeline documentado y ejecutable; criterios de promoción; guía de monitoreo.

---

### Fase E — Pipeline de monitoreo (integración)

**Objetivo:** Un solo flujo de monitoreo que integre Docker, MLFlow/Comet y MLOps.

| Paso | Tarea |
|------|--------|
| E.1 | Flujo de entrenamiento único: entrada (datos/config), salida (modelo + métricas), registro en MLFlow/Comet. |
| E.2 | Dashboard (MLFlow/Comet) para comparar runs y elegir modelo. |
| E.3 | Criterios y umbrales (pérdida, accuracy, etc.); opcional: alertas. |
| E.4 | Ejecutar el pipeline en Docker (imagen `api` o `train`). |
| E.5 | Documentar pipeline de monitoreo de punta a punta. |

**Entregables:** Pipeline end-to-end; documentación; opcional runbook.

---

## Anexo B: Requisitos y checklist Guía ML-IA

**Referencia:** Guía *Monitoreo en Proyectos de ML-IA* (Desarrollo de Proyectos de IA).

### Requisitos

| Requisito | Descripción |
|-----------|-------------|
| Modelo | Clasificación (elección libre). |
| Instrumentar | Función de costo + dos métricas de desempeño (Accuracy, Precision, F1, Recall, etc.). |
| Trazas | Cada gráfica: dos trazas (training y validación/testing). |
| Entrega | 1) Gráfica de costo train+val; 2) Dos gráficas de métricas, cada una train+val. |

### Checklist antes de entregar

| # | Entregable | Verificación |
|---|------------|--------------|
| 1 | Gráfica **función de costo** (train + validación) | Captura MLFlow/Comet: loss vs época, dos curvas. |
| 2 | Gráfica **primera métrica** (train + validación) | Captura: métrica vs época, dos curvas. |
| 3 | Gráfica **segunda métrica** (train + validación) | Captura: métrica vs época, dos curvas. |

### Implementación mínima

1. Modelo de clasificación + dataset.
2. Por época: calcular y registrar loss y 2 métricas en train y en val.
3. Usar MLFlow o Comet: `log_metric("loss_train", ...)`, `"loss_val"`, y lo mismo para las 2 métricas.
4. Abrir UI (MLFlow o Comet), exportar o capturar las 3 gráficas.

---

## Anexo C: Validación de bloqueadores

| # | Bloqueador | ¿Estaba en lo cierto? | Estado actual |
|---|---------------------------|------------------------|---------------|
| 1 | Modelos de BD faltantes (UsuarioSistema, ReconocimientoFacial) | Sí | UsuarioSistema y Autorizacion añadidos. ReconocimientoFacial no se usa; embeddings en Registro. |
| 2 | Pipelines ML inconsistentes (512-d vs 128-d) | Sí | face_model 512-d en uso; inference 128-d solo en código no montado. |
| 3 | Endpoints duplicados (acceso vs access) | Sí | Solo montado acceso.py; access.py legacy. |
| 4 | Python ≥3.13 restrictivo | Sí | Relajar a ≥3.11 o ≥3.12 si hace falta. |
| 5 | Dependencias ML sin grupo modular | Sí | Sin grupo opcional [ml]. |
| 6 | favicon.ico → 404 | Sí | Añadir favicon en frontend/src/static. |

---
