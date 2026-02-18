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

La documentación completa del proyecto se encuentra en la carpeta [`docs/`](./docs/):

- **[📑 Índice de Documentación](./docs/00-indice.md)** - Guía de navegación y mapa de documentos
- **[🏢 Contexto Empresarial](./docs/01-contexto-empresarial.md)** - Información sobre STI S.A.S. y el contexto del proyecto
- **[💼 Caso de Negocio](./docs/02-caso-de-negocio.md)** - Justificación y beneficios de la inversión
- **[📊 Definición del Proyecto](./docs/08-definicion-proyecto.md)** - Objetivos, alcance y cronograma del proyecto
- **[📋 Requerimientos (SRS)](./docs/03-requerimientos-srs.md)** - Especificación completa de requerimientos funcionales y no funcionales
- **[🏗️ Arquitectura del Sistema](./docs/04-arquitectura.md)** - Diseño arquitectónico y componentes
- **[🗄️ Modelo de Datos](./docs/05-modelo-datos.md)** - Esquema de base de datos y relaciones
- **[👥 Historias de Usuario](./docs/06-historias-usuario.md)** - Backlog ágil con historias de usuario
- **[🔄 Procesos BPMN](./docs/07-procesos-bpmn.md)** - Flujos de negocio de ingreso y salida
- **[📋 Tareas por HU](./docs/09-tareas-por-hu.md)** - Tareas de desarrollo por historia de usuario
- **[📌 Orden desarrollo y features](./docs/orden-desarrollo-features.md)** - Orden para desarrollar y registrar features (Git / backlog)
- **[📘 Guía de Uso de Git](./docs/guia-git.md)** - Flujo de trabajo con Git (ramas, ambientes, commits, sincronización)
- **[📱 Guía de Uso de la Aplicación](./docs/guia-uso-aplicacion.md)** - Cómo usar la aplicación (pantallas, flujos, instalación y ejecución)

**💡 Recomendación**: Comienza por el [Índice de Documentación](./docs/00-indice.md) para una guía completa de lectura.

## 🗄️ Base de datos para este ejercicio

**Para este ejercicio se utiliza SQLite** como base de datos. Queda así establecido para todo el desarrollo del MVP (backend, migraciones, scripts y documentación de implementación). Otras opciones (PostgreSQL, etc.) no se consideran en el alcance actual.

## 🏗️ Estructura del Proyecto

### Estructura actual (raíz del repositorio)

Organización en capas tipo **MVC**: Controller (`api/`), Service (`services/`), Model (`db/` + `schemas/`), **SQLite** en `db/`, y módulo **ML** para reconocimiento facial.

| Capa | Carpeta | Rol |
|------|---------|-----|
| **Controller** | `backend/app/api/` | Endpoints REST; valida con schemas y llama a services. |
| **Service** | `backend/app/services/` | Lógica de aplicación; orquesta db y ml. |
| **Model** | `backend/app/db/` + `schemas/` | SQLite, ORM, migraciones; Pydantic request/response. |
| **ML** | `backend/app/ml/` | Reconocimiento facial: inferencia, preprocessing. |
| **Core** | `backend/app/core/` | Config, seguridad, logging. |

```
SCA-EMPX/
├── backend/
│   ├── app/
│   │   ├── api/                     # Controller: endpoints REST
│   │   │   └── v1/
│   │   │       └── routes/
│   │   │           ├── personas.py
│   │   │           ├── access.py
│   │   │           ├── events.py
│   │   │           ├── autorizaciones.py
│   │   │           └── usuarios.py
│   │   ├── core/                    # Config, seguridad, logging
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── logging.py
│   │   ├── db/                      # Model: SQLite, ORM, migraciones
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   └── migrations/
│   │   ├── schemas/                 # Pydantic request/response
│   │   ├── services/                # Lógica de aplicación
│   │   ├── ml/                      # Reconocimiento facial
│   │   │   ├── inference.py
│   │   │   └── preprocessing/
│   │   └── main.py
│   └── tests/
├── docs/
│   ├── 00-indice.md
│   ├── 01-contexto-empresarial.md
│   ├── 02-caso-de-negocio.md
│   ├── 03-requerimientos-srs.md
│   ├── 04-arquitectura.md
│   ├── 05-modelo-datos.md
│   ├── 06-historias-usuario.md
│   ├── 07-procesos-bpmn.md
│   ├── 08-definicion-proyecto.md
│   ├── 09-tareas-por-hu.md
│   ├── orden-desarrollo-features.md
│   └── guia-git.md
├── frontend/
│   └── src/
│       └── index.html
├── scripts/
│   ├── init_db.py
│   └── README.md
├── tests/
├── main.py                          # Punto de entrada (arranca API)
├── pyproject.toml
├── .python-version
├── .gitignore
├── uv.lock
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

4. **Variables de entorno** (opcional): copiar `.env.example` a `.env` y ajustar. Por defecto la BD es `sqlite:///./backend/app/db/sqlite.db`.

5. **Inicializar la base de datos** (crear tablas y usuario admin):
   ```bash
   uv run python scripts/init_db.py
   ```
   Se crean las tablas y un usuario **admin** con contraseña **admin** (cambiar en producción).

6. **Arrancar la API**:
   ```bash
   uv run python main.py
   ```
   La API queda en `http://0.0.0.0:8000`. Documentación interactiva: `http://localhost:8000/docs`.

7. **Login**: `POST /api/v1/usuarios/login` con body `{"username": "admin", "password": "admin"}`. Respuesta: `{"access_token": "...", "token_type": "bearer"}`. Usar el token en cabecera `Authorization: Bearer <token>` para rutas protegidas.

8. **Validar acceso (HU-05)**: `POST /api/v1/access/validate` con imagen (form-data, campo `file`). O abrir en el navegador `http://localhost:8000/validate-access` para subir una foto. Reconocimiento facial usa **DeepFace (Facenet)**; al registrar personas (HU-01) debe usarse el mismo modelo para generar embeddings.

## 🚀 Estado del Proyecto

**Fase actual**: Setup MVP implementado (estructura, SQLite, auth básica). Siguiente: feature HU-05 (validar acceso facial).

## 📝 Licencia

Documentación interna de STI S.A.S. - Uso confidencial.

---

**Desarrollado para**: Soluciones Tecnológicas Integrales S.A.S.  
**Ubicación**: Bogotá, Colombia  
**Año**: 2026
