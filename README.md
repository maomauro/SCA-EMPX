# 🏢 Sistema de Control de Acceso Físico - STI S.A.S.

## 📋 Descripción General

Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (SCA-EMPX) desarrollado para **Soluciones Tecnológicas Integrales S.A.S. (STI S.A.S.)**, una compañía colombiana dedicada al diseño, desarrollo e implementación de soluciones tecnológicas.

Este sistema permite gestionar el acceso físico a las instalaciones de la empresa, garantizando que solo personas registradas, autorizadas y en estado activo puedan ingresar, registrando además todas las entradas y salidas con trazabilidad completa.

## 🎯 Objetivos del Sistema

- ✅ Control estricto de quién entra y sale de las instalaciones
- ✅ **Reconocimiento facial como método principal** (ArcFace + YOLOv8)
- ✅ Registro de visitantes con trazabilidad completa
- ✅ Validación automática de autorizaciones
- ✅ Integración con cámaras y torniquetes automáticos
- ✅ Auditoría completa para incidentes de seguridad

## 📚 Documentación

Toda la documentación está en **[`docs/`](./docs/)**. Punto de entrada único:

- **[📑 Índice de documentación](./docs/00-indice.md)** — mapa de todos los documentos y guía de lectura por rol (desarrollador, profesor, analista).

El índice agrupa los documentos en:

| Grupo | Contenido |
|-------|-----------|
| **Negocio y proyecto** | Contexto empresarial, caso de negocio, definición del proyecto, requerimientos (SRS), arquitectura, modelo de datos, historias de usuario, procesos BPMN, tareas por HU. |
| **Desarrollo y operación** | Orden de desarrollo y features, bitácora de desarrollo, URLs de acceso, Guía de Git. |
| **MLOps y pipeline** | [Plan y roadmap](./docs/plan-roadmap.md) (Fases 0–5), [flujo MLOps](./docs/mlops-flujo.md), [monitoreo en producción](./docs/mlops-monitoreo-produccion.md), [despliegue con Docker](./docs/despliegue-docker.md). |
| **Guías de uso** | [Guía de uso de la aplicación](./docs/guia-uso-aplicacion.md) (pantallas y flujos desde el navegador). |

**Entrenamiento ML (clasificador MNIST, MLFlow, Comet):** ver **[`training/README.md`](./training/README.md)**. Para ejecutar todo con Docker: **[Despliegue Docker](./docs/despliegue-docker.md)**.

## 🗄️ Base de datos para este ejercicio

**Para este ejercicio se utiliza SQLite** como base de datos. Queda así establecido para todo el desarrollo del MVP (backend, migraciones, scripts y documentación de implementación). Otras opciones (PostgreSQL, etc.) no se consideran en el alcance actual.

## 🏗️ Estructura del Proyecto

Organización en capas tipo **MVC**: Controller (`api/`), Service (`services/`), Model (`db/` + `schemas/`), **SQLite** en `db/`, y módulo **ML** para reconocimiento facial.

| Capa | Carpeta | Rol |
|------|---------|-----|
| **Controller** | `backend/app/api/` | Endpoints REST; valida con schemas y llama a services. |
| **Service** | `backend/app/services/` | Lógica de aplicación; orquesta db y ml. |
| **Model** | `backend/app/db/` + `schemas/` | SQLite, ORM, migraciones; Pydantic request/response. |
| **ML** | `backend/app/ml/` | Reconocimiento facial (DeepFace / Facenet). |
| **Core** | `backend/app/core/` | Config, seguridad (JWT), logging. |

```
SCA-EMPX/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── routes/
│   │   │           ├── acceso.py       # validar acceso, registrar salida
│   │   │           ├── personas.py     # CRUD personas (empleados/visitantes)
│   │   │           ├── visitas.py      # autorizaciones de visita
│   │   │           ├── events.py       # historial de eventos
│   │   │           ├── catalogos.py    # tipos de persona
│   │   │           ├── config.py       # configuración dinámica
│   │   │           └── ws.py           # WebSocket feed en tiempo real
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   └── migrations/
│   │   ├── ml/
│   │   │   └── face_model.py           # DeepFace Facenet embeddings
│   │   └── main.py
│   └── tests/
├── docs/                               # Documentación completa del proyecto
├── frontend/
│   └── src/
│       ├── index.html                  # Página principal / nav
│       ├── registro.html               # Registro empleado y visitante
│       ├── acceso.html                 # Validar acceso / registrar salida
│       ├── visitante.html              # Autorización de visita
│       ├── configuracion.html          # Configuración del sistema
│       └── static/
│           └── ws-client.js            # Cliente WebSocket
├── scripts/
│   ├── init_db.py                      # Crear tablas y usuario admin
│   ├── clear_personas.py               # Limpiar personas para pruebas
│   └── fix_registro_acceso_table.py    # Migración correctiva tabla acceso
├── tests/
├── main.py                             # Punto de entrada (arranca uvicorn)
├── pyproject.toml
└── README.md
```

Flujo: **petición** → `api/` → `services/` → `db/` (SQLite) y/o `ml/` → **respuesta**.

*`.venv/` y `.env` no se versionan. Archivos `*.db` están en `.gitignore`.*

## 👥 Actores del Sistema

- **Empleado**: Persona de planta o contratista con acceso recurrente
- **Visitante**: Persona externa que ingresa por una visita específica
- **Recepcionista**: Registra visitantes y gestiona autorizaciones puntuales
- **Administrador de Seguridad**: Configura reglas, consulta auditoría, gestiona accesos
- **RRHH**: Gestiona altas/bajas de empleados
- **Sistema de Torniquetes/Control Físico**: Dispositivo que valida acceso

## 🚀 Instalación y ejecución

1. **Requisitos**: Python 3.13+, [uv](https://docs.astral.sh/uv/) (o `pip`).

2. **Clonar y entrar al proyecto**:
   ```bash
   cd SCA-EMPX
   ```

3. **Instalar dependencias**:
   ```bash
   uv sync
   ```
   (o `pip install -e .` si no usas uv.)

4. **Variables de entorno** (opcional): copiar `.env.example` a `.env` y ajustar. Por defecto la BD es `sqlite:///./backend/app/db/sca.db` (véase `backend/app/config/config.py`).

5. **Inicializar la base de datos** (crear tablas y usuario admin):
   ```bash
   uv run python scripts/init_db.py
   ```
   Se crean las tablas y un usuario **admin** con contraseña **admin** (cambiar en producción).

6. **Arrancar la API**:
   ```bash
   uv run python main.py
   ```
   La API queda en `http://0.0.0.0:8000`.
   - UI principal: `http://localhost:8000/` (dashboard); `/registro`, `/acceso`, `/visitante`, `/configuracion`
   - Documentación interactiva (Swagger): `http://localhost:8000/docs`

7. **Login**: `POST /api/v1/usuarios/login` con body `{"username": "admin", "password": "admin"}`. Respuesta: `{"access_token": "...", "token_type": "bearer"}`. Usar el token en cabecera `Authorization: Bearer <token>` para rutas protegidas.

8. **Páginas disponibles** (servidas por la API en `http://localhost:8000`):

   | URL | Descripción |
   |-----|-------------|
   | `/` | Página principal (dashboard) |
   | `/registro` | Registro de empleados y visitantes (captura facial) |
   | `/acceso` | Validar acceso / registrar salida (reconocimiento facial) |
   | `/visitante` | Autorización de visita |
   | `/configuracion` | Configuración del sistema |
   | `/docs` | Documentación interactiva de la API (Swagger) |
   | `/health` | Health check (JSON) para despliegue |

   Listado completo de URLs: [docs/urls-acceso.md](./docs/urls-acceso.md).

## 🚀 Estado del Proyecto

| Paso | Feature | HU | Estado |
|------|---------|----|--------|
| 0 | setup-mvp | — | ✅ Hecho |
| 1 | hu-05-validar-acceso-facial | HU-05 | ✅ Hecho |
| 2 | hu-01-registrar-empleado | HU-01 | ✅ Hecho |
| 3 | hu-03-registrar-visitante | HU-03 | ✅ Hecho |
| 4 | hu-04-autorizacion-visita | HU-04 | ✅ Hecho |
| 5 | hu-06-registro-evento-entrada | HU-06 | ✅ Hecho |
| 6 | hu-07-registro-evento-salida | HU-07 | ✅ Hecho |
| 7 | hu-09-gestionar-usuarios | HU-09 | ⏳ Pendiente |
| 8 | hu-02-desactivar-empleado | HU-02 | ⏳ Pendiente |
| 9 | hu-08-historial-accesos | HU-08 | ⏳ Pendiente |
| 10 | hu-10-actualizar-empleado | HU-10 | ⏳ Pendiente |
| 11 | hu-11-dashboard-accesos | HU-11 | ⏳ Pendiente |
| 12 | hu-13-revocar-autorizacion | HU-13 | ⏳ Pendiente |
| 13 | hu-14-personas-dentro | HU-14 | ⏳ Pendiente |
| 14 | hu-12-reporte-accesos | HU-12 | ⏳ Pendiente |

Ver detalle completo en [docs/bitacora-desarrollo.md](./docs/bitacora-desarrollo.md).

**Roadmap de monitoreo ML (Fases 0–5):** ver [docs/plan-roadmap.md](./docs/plan-roadmap.md) para el plan de MLFlow, Comet, MLOps, Docker y pipeline de monitoreo.

## 📝 Licencia

Documentación interna de STI S.A.S. - Uso confidencial.

---

**Desarrollado para**: Soluciones Tecnológicas Integrales S.A.S.  
**Ubicación**: Bogotá, Colombia  
**Año**: 2026
