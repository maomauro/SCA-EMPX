# Plan: Roadmap General SCA-EMPX

**Fecha:** 1 de marzo de 2026 · **Estado:** DRAFT — Pendiente validación  
**Rama:** `docs/plan-roadmap`  
**Contexto:** Ejercicio educativo y aplicado — el docente solicita la implementación de **todo**: modelos/base, MLFlow, Comet ML, MLOps, Docker y pipeline de monitoreo.

---

## Cómo usar este documento

| Si quieres… | Ve a la sección |
|-------------|------------------|
| **Crear la rama** antes de cada fase y actualizar local/remoto | [Estrategia de ramas](#13-estrategia-de-ramas-una-rama-por-fase) |
| Ver el orden de las fases (recomendado para la entrega) | [Orden del roadmap](#23-orden-del-roadmap-recomendado) |
| Seguir el plan **paso a paso** desde el inicio | [Parte 2: Roadmap completo](#2-roadmap-completo-paso-a-paso) |
| Ver qué debe cumplir la **Guía de Monitoreo ML-IA** | [Coherencia con la Guía](#21-coherencia-con-la-guía-monitoreo-ml-ia) |
| Entender el estado actual del proyecto | [Parte 1: Contexto](#parte-1-contexto-y-estado-actual) |
| Detalle de tareas por fase | [Anexo A](#anexo-a-detalle-de-fases-0-a-5) |

---

## Índice

1. **Parte 1: Contexto y estado actual**
   - 1.1 Resumen ejecutivo
   - 1.2 Punto de retorno seguro (git tag)
   - 1.3 Estrategia de ramas (una rama por fase)
   - 1.4 Validación del plan (auditoría 2 mar 2026)

2. **Parte 2: Roadmap completo — Paso a paso**
   - 2.1 Coherencia con la Guía Monitoreo ML-IA
   - 2.2 Objetivo del ejercicio
   - 2.3 Orden del roadmap recomendado (Fases 0 → 5)
   - 2.4 Resumen de cada fase

3. **Resumen visual del roadmap**

4. **Anexos**
   - A. Detalle de cada fase (0, 1, 2, 3, 4, 5)
   - B. Requisitos y checklist de la Guía ML-IA
   - C. Tabla de validación de bloqueadores

---

# Parte 1: Contexto y estado actual

## 1.1 Resumen ejecutivo

**SCA-EMPX** es un sistema FastAPI de control de acceso con reconocimiento facial que **funciona**, pero con deuda técnica. Este plan aborda:

- **Seis bloqueadores técnicos** (modelos faltantes, pipelines ML inconsistentes, endpoints duplicados, Python 3.13, dependencias ML sin grupo modular, favicon faltante).
- **Objetivo MLOps:** pipeline de monitoreo del entrenamiento de modelos IA-ML (Docker, MLFlow, Comet ML, MLOps).

Las correcciones recientes ya resolvieron parte del punto 1 (modelos); el resto del plan sigue vigente. Ver [1.4 Validación](#14-validación-del-plan-2-marzo-2026) para el estado actual de cada bloqueador.

---

## 1.2 Punto de retorno seguro

Antes de cambios grandes, crear un tag desde la rama `develop`:

```bash
git checkout develop
git tag pre-refactor-2026-03-01
```

**Confirmado:** ya ejecutaste `git tag pre-refactor-2026-03-01` desde `develop`. Ese tag queda como punto de retorno.

---

## 1.3 Estrategia de ramas (una rama por fase)

Antes de iniciar cada fase, se crea una **rama independiente** desde `develop`. Así se mantiene el historial ordenado y se actualiza tanto el Git local como el remoto por tema.

### Ramas por fase

| Fase | Nombre de la rama | Uso |
|------|-------------------|-----|
| 0 | `feature/fase-0-modelos-implementaciones` | Base: modelos e implementaciones, script de clasificador. |
| 1 | `feature/fase-1-mlflow` | Instrumentación MLFlow, métricas y gráficas. |
| 2 | `feature/fase-2-comet-ml` | Instrumentación Comet ML en el mismo entrenamiento. |
| 3 | `feature/fase-3-mlops` | MLOps: versionado, pipeline reproducible, CI/CD. |
| 4 | `feature/fase-4-docker` | Dockerfile y docker-compose. |
| 5 | `feature/fase-5-pipeline-monitoreo` | Integración del pipeline de monitoreo. |

### Flujo por fase (repetir para cada fase)

**1. Crear la rama desde `develop` y cambiarse a ella:**

```bash
git checkout develop
git pull origin develop
git checkout -b feature/fase-0-modelos-implementaciones
```

*(Sustituir el nombre de la rama por la de la fase que toque: `feature/fase-1-mlflow`, `feature/fase-2-comet-ml`, etc.)*

**2. Trabajar en la fase:** commits locales en esa rama.

```bash
git add .
git commit -m "Fase 0: descripción breve de lo hecho"
```

**3. Subir la rama al remoto:**

```bash
git push -u origin feature/fase-0-modelos-implementaciones
```

*(En fases siguientes, si la rama ya tiene upstream: `git push`.)*

**4. Al terminar la fase (opcional):** integrar en `develop` y seguir con la siguiente.

```bash
git checkout develop
git pull origin develop
git merge feature/fase-0-modelos-implementaciones -m "Merge Fase 0: modelos e implementaciones"
git push origin develop
```

**5. Siguiente fase:** volver al paso 1 creando la nueva rama desde `develop`.

### Resumen rápido de comandos por fase

| Acción | Comando |
|--------|--------|
| Empezar fase N | `git checkout develop` → `git pull` → `git checkout -b feature/fase-N-nombre` |
| Subir trabajo | `git add .` → `git commit -m "..."` → `git push -u origin feature/fase-N-nombre` |
| Integrar en develop | `git checkout develop` → `git merge feature/fase-N-nombre` → `git push origin develop` |

---

## 1.4 Validación del plan (2 marzo 2026)

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

# 2. Roadmap completo — Paso a paso

Este plan está pensado como **ejercicio educativo y aplicado**. El docente pide implementar **todo** lo siguiente: base de modelos e implementaciones, MLFlow, Comet ML, MLOps, Docker y pipeline de monitoreo. Ninguna de estas fases es opcional para la entrega.

---

## 2.1 Coherencia con la Guía Monitoreo ML-IA

La **Guía de Monitoreo en Proyectos de ML-IA** exige:

- Un **modelo de clasificación** con entrenamiento instrumentado.
- **Una gráfica** de la función de costo (train y validación, dos trazas).
- **Dos gráficas** de métricas de desempeño (Accuracy, Precision, F1 o Recall), cada una con train y validación (dos trazas).

**Cómo se cumple con este roadmap:**

1. **Fase 0** deja lista la base (modelo e implementación coherente) para entrenar.
2. **Fases 1 y 2** (MLFlow y Comet ML) son donde se instrumenta el entrenamiento: se registran en **ambas** herramientas la función de costo y las dos métricas (train y val) por época. Las UIs de MLFlow y Comet generan las tres gráficas que pide la Guía.
3. **Fases 3, 4 y 5** (MLOps, Docker, Pipeline) completan el ejercicio: versionado, contenedorización y un flujo único de monitoreo.

**Checklist de entrega (Guía):** Ver [Anexo B](#anexo-b-requisitos-y-checklist-guía-ml-ia). Antes de entregar, confirmar: (1) gráfica de costo train+val, (2) primera gráfica de métrica train+val, (3) segunda gráfica de métrica train+val.

---

## 2.2 Objetivo del ejercicio

Construir un **pipeline de monitoreo del entrenamiento de modelos IA-ML** que integre de forma aplicada:

- Base sólida de **modelos e implementaciones** (entrenamiento de un clasificador).
- **MLFlow** para experimentación y registro de métricas y modelos.
- **Comet ML** para experimentación y visualización de las mismas métricas.
- **MLOps** para versionado, reproducibilidad y monitoreo.
- **Docker** para contenerizar la aplicación y el entorno de entrenamiento.
- **Pipeline** final que una todo y permita ver el monitoreo de punta a punta.

---

## 2.3 Orden del roadmap recomendado

El orden sugerido es **lineal**: primero se resuelve la base, luego las herramientas de monitoreo, después las prácticas MLOps, luego la contenedorización y por último la integración en un solo pipeline.

| Orden | Fase | Nombre | Qué se hace |
|-------|------|--------|-------------|
| **0** | Base | Modelos e implementaciones | Resolver bloqueadores que afecten al entrenamiento (modelos de BD, coherencia del código de ML). Tener un script de entrenamiento de un **modelo de clasificación** que funcione localmente. |
| **1** | MLFlow | Experimentación y registro | Instalar y configurar MLFlow. Instrumentar el entrenamiento: registrar en cada época loss y dos métricas (train y val). Registrar el modelo. |
| **2** | Comet ML | Experimentación y visualización | Instalar y configurar Comet ML. En el **mismo** script de entrenamiento, registrar las mismas métricas en Comet. Obtener las gráficas (costo + 2 métricas) también desde Comet. |
| **3** | MLOps | Prácticas y automatización | Versionado de datos y modelo, pipeline de entrenamiento reproducible, monitoreo en producción, CI/CD para ML. |
| **4** | Docker | Contenerización | Dockerfile y docker-compose para la app y, si aplica, para el entorno de entrenamiento y MLFlow. |
| **5** | Pipeline | Integración | Un solo flujo que ejecute entrenamiento registrando en MLFlow y Comet, con dashboard y criterios para elegir el modelo a desplegar. Documentar el pipeline de monitoreo de punta a punta. |

**Resumen en una línea:**  
**Fase 0 (base) → Fase 1 (MLFlow) → Fase 2 (Comet ML) → Fase 3 (MLOps) → Fase 4 (Docker) → Fase 5 (Pipeline).**

---

## 2.4 Resumen de cada fase

| Fase | Nombre | En una frase |
|------|--------|----------------|
| **0** | Modelos e implementaciones | Dejar coherente la base: modelos de BD y código de entrenamiento de un clasificador. |
| **1** | MLFlow | Registrar experimentos, métricas (costo + 2 de desempeño) y modelo; usar la UI para las gráficas. |
| **2** | Comet ML | Registrar en Comet las mismas métricas del entrenamiento; usar el dashboard para las gráficas. |
| **3** | MLOps | Versionado, pipeline reproducible, monitoreo en producción, CI/CD para ML. |
| **4** | Docker | Contenerizar la aplicación y el entorno de entrenamiento (Dockerfile + docker-compose). |
| **5** | Pipeline de monitoreo | Integrar todo: un flujo único que entrene, registre en MLFlow y Comet, y documente el monitoreo. |

El **detalle de tareas y entregables** de cada fase está en [Anexo A](#anexo-a-detalle-de-fases-0-a-5).

---

# 3. Resumen visual del roadmap

```
  ┌──────────────────────────────────────────────────────────────────────────────────────────┐
  │              OBJETIVO: Pipeline de monitoreo de entrenamiento IA-ML (Guía)                 │
  └──────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
  ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
  │ Fase 0  │ ─► │ Fase 1   │ ─► │ Fase 2   │ ─► │ Fase 3  │ ─► │ Fase 4  │ ─► │ Fase 5  │
  │ Base    │    │ MLFlow   │    │ Comet ML │    │ MLOps   │    │ Docker  │    │Pipeline │
  │ Modelos │    │          │    │          │    │         │    │         │    │         │
  └─────────┘    └──────────┘    └──────────┘    └─────────┘    └─────────┘    └─────────┘
       │               │               │               │               │               │
       ▼               ▼               ▼               ▼               ▼               ▼
  Clasificador    Métricas +      Métricas +      Versionado     Contenedores    Monitoreo
  listo para      registro       gráficas        + CI/CD        y despliegue    end-to-end
  entrenar        (UI gráficas)   (dashboard)    + producción
```

**Para la Guía:** Las gráficas de la entrega (costo + 2 métricas, train y val) se obtienen en **Fase 1 (MLFlow)** y **Fase 2 (Comet ML)**. El resto de fases completa el ejercicio aplicado.

---

# Anexos

## Anexo A: Detalle de fases 0 a 5

### Fase 0 — Modelos e implementaciones (base)

**Objetivo:** Dejar una base coherente para el entrenamiento: resolver bloqueadores que afecten al modelo y tener un script de entrenamiento de un **modelo de clasificación** que funcione localmente.

| Paso | Tarea |
|------|--------|
| 0.1 | Revisar y, si hace falta, corregir modelos de BD y coherencia del código de ML (según [Anexo C](#anexo-c-validación-de-bloqueadores)). |
| 0.2 | Definir el **modelo de clasificación** y el dataset (ej.: red neuronal sobre MNIST/CIFAR, clasificador facial por identidad, etc.). |
| 0.3 | Implementar script de entrenamiento: loop por épocas, cálculo de pérdida y al menos dos métricas de desempeño (Accuracy, Precision, F1, Recall) en train y en validación. |
| 0.4 | Verificar que el entrenamiento corre de punta a punta y que se obtienen loss y métricas por época (aún sin MLFlow/Comet). |

**Entregables:** Base de código coherente; script de entrenamiento de un clasificador que calcule loss y 2 métricas en train y val.

---

### Fase 1 — MLFlow

**Objetivo:** Registrar experimentos, métricas (función de costo + dos de desempeño) y modelo; usar la UI de MLFlow para las gráficas que pide la Guía.

| Paso | Tarea |
|------|--------|
| 1.1 | Instalar `mlflow` (dependencia o grupo `[mlops]` en el proyecto). |
| 1.2 | Configurar MLFlow Tracking Server (local o contenedor) y definir `MLFLOW_TRACKING_URI`. |
| 1.3 | En el script de entrenamiento: `mlflow.start_run()`, registrar parámetros (`log_params`), y en cada época registrar `loss_train`, `loss_val` y las dos métricas en train y val (`log_metric(..., step=epoch)`). |
| 1.4 | Registrar el modelo con `mlflow.<flavor>.log_model()` (PyTorch, scikit-learn, ONNX, etc.). |
| 1.5 | Ejecutar un entrenamiento, abrir la UI de MLFlow y verificar las tres gráficas: costo (train/val), métrica 1 (train/val), métrica 2 (train/val). |

**Entregables:** Servidor MLFlow accesible; script de entrenamiento instrumentado con MLFlow; capturas o exportación de las gráficas para la Guía.

---

### Fase 2 — Comet ML

**Objetivo:** Registrar en Comet ML las mismas métricas del entrenamiento y usar el dashboard para las gráficas (cumplimiento de la Guía también desde Comet).

| Paso | Tarea |
|------|--------|
| 2.1 | Instalar `comet-ml`; configurar `COMET_API_KEY` y proyecto/workspace. |
| 2.2 | En el **mismo** script de entrenamiento (junto con MLFlow), inicializar experimento Comet (`comet_ml.Experiment`) y registrar en cada época: loss train/val y las dos métricas train/val. |
| 2.3 | Registrar hiperparámetros y artefactos (checkpoints o modelo) en Comet. |
| 2.4 | Ejecutar un entrenamiento, abrir el dashboard de Comet y verificar las tres gráficas (costo + 2 métricas, cada una con train y val). |

**Entregables:** Integración Comet en el script de entrenamiento; documentación de configuración; gráficas desde Comet para la entrega si se desea.

---

### Fase 3 — MLOps

**Objetivo:** Aplicar prácticas MLOps: versionado, pipeline reproducible, monitoreo en producción y CI/CD para ML.

| Paso | Tarea |
|------|--------|
| 3.1 | Definir convención de versionado para datos y modelo; integrar con MLFlow (tags o Model Registry). |
| 3.2 | Tener un pipeline de entrenamiento reproducible: script o job que cargue datos/config, entrene y registre en MLFlow y Comet. |
| 3.3 | Definir métricas de monitoreo en producción (latencia, errores, distribución de scores) y dónde registrarlas. |
| 3.4 | Configurar CI/CD para ML: tests y, si aplica, job de entrenamiento o evaluación vs baseline. |
| 3.5 | Documentar el flujo: entrenamiento → registro → criterios de promoción → despliegue. |

**Entregables:** Pipeline de entrenamiento documentado y ejecutable; criterios de promoción de modelo; guía de monitoreo.

---

### Fase 4 — Docker

**Objetivo:** Contenerizar la aplicación y el entorno de entrenamiento para despliegue y reproducibilidad.

| Paso | Tarea |
|------|--------|
| 4.1 | Definir `Dockerfile` para la API FastAPI: Python 3.12+, dependencias, puerto 8000, comando uvicorn. |
| 4.2 | Crear `docker-compose.yml`: servicio `api`; servicios para MLFlow y, si aplica, BD. |
| 4.3 | Configurar volúmenes y variables de entorno (SQLite/datos, `SECRET_KEY`, `DATABASE_URL`, `MLFLOW_TRACKING_URI`, etc.). |
| 4.4 | Asegurar que el script de entrenamiento (o una imagen dedicada) pueda ejecutarse dentro de Docker con acceso a MLFlow y Comet. |
| 4.5 | Documentar: build, `docker compose up`, variables necesarias. |

**Entregables:** `Dockerfile`, `docker-compose.yml`, documentación (README o `docs/despliegue-docker.md`).

---

### Fase 5 — Pipeline de monitoreo (integración)

**Objetivo:** Un solo flujo de monitoreo que integre base, MLFlow, Comet ML, MLOps y Docker; documentar el pipeline de punta a punta.

| Paso | Tarea |
|------|--------|
| 5.1 | Definir el flujo único de entrenamiento: entrada (datos/config), salida (modelo registrado + métricas), registro en MLFlow y en Comet. |
| 5.2 | Usar los dashboards de MLFlow y Comet para comparar runs y decidir qué modelo promover. |
| 5.3 | Definir criterios y umbrales (pérdida, accuracy u otras métricas) para marcar runs como exitosos o en revisión. |
| 5.4 | Ejecutar el pipeline completo dentro de Docker (entrenamiento + registro en MLFlow y Comet). |
| 5.5 | Documentar el pipeline de monitoreo de punta a punta: qué se monitorea, dónde se visualiza, cómo se elige el modelo a desplegar. |

**Entregables:** Pipeline de monitoreo end-to-end ejecutable; documentación del pipeline; runbook si aplica.

---

## Anexo B: Requisitos y checklist Guía ML-IA

**Referencia:** Guía *Monitoreo en Proyectos de ML-IA* (Desarrollo de Proyectos de IA).

La Guía se cumple implementando el roadmap completo (Fases 0 a 5). Las **gráficas** que se entregan se obtienen en **Fase 1 (MLFlow)** y **Fase 2 (Comet ML)**; en ambas herramientas se registran las mismas métricas (costo + 2 de desempeño, train y val).

### Requisitos de la Guía

| Requisito | Descripción |
|-----------|-------------|
| Modelo | Clasificación (elección libre). |
| Instrumentar | Función de costo + dos métricas de desempeño (Accuracy, Precision, F1, Recall, etc.). |
| Trazas | Cada gráfica: dos trazas (training y validación/testing). |
| Entrega | 1) Gráfica de costo train+val; 2) Dos gráficas de métricas, cada una train+val. |

### Checklist antes de entregar

| # | Entregable | Verificación |
|---|------------|--------------|
| 1 | Gráfica **función de costo** (train + validación) | Captura desde MLFlow y/o Comet: loss vs época, dos curvas. |
| 2 | Gráfica **primera métrica** (train + validación) | Captura: métrica vs época, dos curvas. |
| 3 | Gráfica **segunda métrica** (train + validación) | Captura: métrica vs época, dos curvas. |

### Cómo se implementa en el roadmap

1. **Fase 0:** Modelo de clasificación + script que calcula loss y 2 métricas en train y val por época.
2. **Fase 1 (MLFlow):** Registrar en cada época `loss_train`, `loss_val`, `accuracy_train`, `accuracy_val`, `f1_train`, `f1_val` (o las 2 métricas elegidas). La UI de MLFlow genera las 3 gráficas.
3. **Fase 2 (Comet ML):** Registrar las mismas métricas en Comet en el mismo script. El dashboard de Comet genera las 3 gráficas.
4. Capturar o exportar las gráficas desde MLFlow o Comet (o ambas) para la entrega.

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
---
