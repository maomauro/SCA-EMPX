# Despliegue con Docker (Fase 4)

Este documento describe cómo construir y ejecutar SCA-EMPX con **Docker** y **Docker Compose**: API FastAPI, servidor MLFlow y entorno de entrenamiento.

**Pipeline CI/CD (archivo .yml para despliegue):** El proyecto incluye **`.gitlab-ci.yml`** en la raíz, que define el pipeline GitLab (Preparation → Build → Tests → Deploy). Si usas GitLab, cada push dispara ese pipeline; la etapa *Build* construye la imagen Docker y la sube al Container Registry; *Deploy* se puede configurar con Variables de GitLab. Para Azure DevOps se usa **`azure-pipelines.yml`** (tests y smoke test ML).

---

## Arquitectura del despliegue: cómo se reparte todo

SCA-EMPX es una **aplicación web** (backend + frontend), más **entrenamiento de modelos** y **registro de experimentos**. En Docker cada parte se reparte así:

### Una sola imagen, tres usos

Se construye **una única imagen** que contiene:

- Código del **backend** (FastAPI, rutas REST, WebSockets, lógica de negocio).
- Archivos del **frontend** (HTML, JS, CSS en `frontend/src`): no hay servidor Node ni build aparte; el backend **sirve** esas páginas y estáticos.
- Código de **entrenamiento** (`training/`) y dependencias ML (PyTorch, MLFlow, Comet, etc.).
- Dependencias del **modelo en producción** (DeepFace, TensorFlow/ONNX, etc.) usadas por la API para reconocimiento facial.

Esa imagen se usa para tres **servicios** cambiando solo el **comando** que se ejecuta en el contenedor:

| Servicio | Comando | Qué hace |
|----------|---------|-----------|
| **api** | `uvicorn backend.app.main:app ...` | Arranca la aplicación web (backend + frontend + modelo facial). |
| **mlflow** | `mlflow server ...` | Arranca el servidor de MLFlow (registro de experimentos). |
| **train** | `python training/train_classifier.py ...` | Ejecuta el script de entrenamiento (bajo demanda). |

### Dónde está cada cosa en runtime

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    TU MÁQUINA / SERVIDOR                 │
                    │                                                          │
  Navegador         │   ┌──────────────┐         ┌──────────────┐             │
  (usuario)         │   │   Contenedor  │         │   Contenedor  │             │
       │            │   │     api      │         │    mlflow     │             │
       │  :8000     │   │  (puerto 8000)│         │  (puerto 5000)│             │
       └────────────┼──►│              │         │              │             │
                    │   │ • FastAPI    │         │ • MLFlow      │             │
                    │   │ • REST/WS    │         │   server      │             │
                    │   │ • HTML/JS/CSS│         │ • Guarda runs │             │
                    │   │   (frontend) │         │   en volumen  │             │
                    │   │ • Modelo     │         │   mlruns      │             │
                    │   │   facial     │         └──────┬───────┘             │
                    │   │   (DeepFace) │                │                      │
                    │   │ • SQLite     │                │ :5000                │
                    │   │   (volumen   │                │ (red interna)         │
                    │   │   api_db)    │                │                      │
                    │   └──────┬───────┘                │                      │
                    │          │                        │                      │
                    │          │    ┌──────────────────┴──────────┐            │
                    │          │    │   Contenedor train (bajo demanda)         │
                    │          │    │   • training/train_classifier.py         │
                    │          │    │   • Envía métricas ──────────┼──► mlflow  │
                    │          │    │   • Opcional: Comet ML (nube)             │
                    │          │    │   • Datos MNIST en volumen training_data  │
                    │          │    └──────────────────────────────────────────┘
                    └─────────────────────────────────────────────────────────┘
```

- **Backend + frontend juntos en el contenedor `api`**  
  El backend (FastAPI) sirve las páginas HTML desde `frontend/src` y los estáticos desde `frontend/src/static`. No hay un contenedor “frontend” aparte: todo lo que ve el usuario en el navegador en `http://localhost:8000` lo sirve este único proceso (uvicorn).

- **Modelo en producción (reconocimiento facial)**  
  Vive dentro del contenedor `api`: al arrancar se carga el modelo (DeepFace, etc.) en memoria y lo usan los endpoints de acceso/registro. No se usa el clasificador MNIST del `training/` en la API.

- **Modelos de entrenamiento (MNIST / pipeline ML)**  
  El script `training/train_classifier.py` corre en el contenedor `train`. Entrena el clasificador MNIST y envía métricas a **MLFlow** (contenedor `mlflow`) y, si configuras la key, a **Comet ML** (servicio en la nube). Los artefactos de modelo quedan en MLFlow, no en el contenedor de la API.

- **Base de datos**  
  La API usa SQLite (por defecto) dentro del contenedor `api`; el archivo se persiste en el volumen `api_db` para que no se pierda al reiniciar.

- **MLFlow**  
  Es un servicio separado (`mlflow`) para registrar experimentos y modelos del pipeline de entrenamiento. La API puede tener `MLFLOW_TRACKING_URI` apuntando a él si en el futuro quieres registrar métricas desde la app; hoy el uso principal es el contenedor `train`.

### Resumen rápido

| Componente | Dónde corre | Puerto / acceso |
|------------|-------------|------------------|
| Aplicación web (backend + frontend) | Contenedor **api** | 8000 |
| Modelo de reconocimiento facial (producción) | Dentro de **api** | — |
| Base de datos (SQLite) | Dentro de **api**, datos en volumen **api_db** | — |
| Registro de experimentos ML | Contenedor **mlflow** | 5000 |
| Entrenamiento (script MNIST) | Contenedor **train** (bajo demanda) | Se conecta a mlflow por red interna |

Así, la “app web” (backend + frontend + BD + modelo facial) está en un solo contenedor; el entrenamiento y el registro de experimentos están en contenedores separados que comparten la misma imagen.

---

## Requisitos

- **Docker** y **Docker Compose** (v2) instalados.
- Opcional: variable de entorno `COMET_API_KEY` si quieres que el entrenamiento en Docker envíe experimentos a Comet ML.

---

## Build de la imagen

Desde la **raíz del proyecto**:

```bash
docker compose build
```

Se construye una única imagen que sirve para los servicios `api`, `mlflow` y `train`. La imagen incluye Python 3.13, dependencias del proyecto (FastAPI, uvicorn, MLFlow, Comet, PyTorch, etc.), y el código de `backend/`, `frontend/` y `training/`.

---

## Levantar API y MLFlow

```bash
docker compose up -d
```

- **API:** http://localhost:8000 (docs: http://localhost:8000/docs)
- **MLFlow UI:** http://localhost:5000

Para ver logs:

```bash
docker compose logs -f api
docker compose logs -f mlflow
```

Para detener:

```bash
docker compose down
```

---

## Variables de entorno

Se pueden definir en un archivo `.env` en la raíz o exportarlas en el shell.

| Variable | Servicio | Descripción | Por defecto |
|----------|----------|-------------|-------------|
| `SECRET_KEY` | api | Clave para JWT y sesiones | `cambiar-en-produccion` |
| `DATABASE_URL` | api | URL de BD (SQLite o PostgreSQL) | `sqlite:///./backend/app/db/sca.db` |
| `DEBUG` | api | Modo debug (true/false) | `false` |
| `MLFLOW_TRACKING_URI` | api, train | URI del servidor MLFlow | En compose: `http://mlflow:5000` |
| `COMET_API_KEY` | train | API key de Comet ML (opcional) | — |

Ejemplo `.env`:

```env
SECRET_KEY=mi-clave-secreta-muy-larga
DEBUG=false
COMET_API_KEY=tu_api_key_si_usas_comet
```

La base de datos SQLite y los runs de MLFlow se persisten en **volúmenes** Docker (`api_db`, `mlruns`), de modo que no se pierden al hacer `docker compose down`.

---

## Ejecutar entrenamiento dentro de Docker

Con la API y MLFlow en marcha (`docker compose up -d`), ejecuta el script de entrenamiento en un contenedor que usa la misma imagen y se conecta al MLFlow del compose:

```bash
docker compose run --rm train
```

Por defecto corre 3 épocas y envía métricas a MLFlow. Para pasar argumentos al script:

```bash
docker compose run --rm train --epochs 5 --config training/config_default.json
```

Para registrar también en Comet ML, pasa la API key:

```bash
docker compose run --rm -e COMET_API_KEY=tu_api_key train
```

Para no usar Comet:

```bash
docker compose run --rm train --no-comet
```

Los experimentos aparecen en la UI de MLFlow (http://localhost:5000). Los datos de MNIST se descargan la primera vez y se cachean en el volumen `training_data`.

---

## Resumen de servicios y puertos

| Servicio | Puerto | Comando por defecto |
|---------|--------|---------------------|
| **api** | 8000 | `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000` |
| **mlflow** | 5000 | `mlflow server --host 0.0.0.0 --port 5000` |
| **train** | — | Se ejecuta bajo demanda con `docker compose run --rm train` |

---

## Fase 5

En la siguiente fase se integra el pipeline de monitoreo de punta a punta y se documenta el flujo completo de entrenamiento → registro → criterios de promoción → despliegue usando estos contenedores.
