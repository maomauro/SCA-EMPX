# URLs de acceso - SCA-EMPX

Listado de URLs para acceder a la aplicación con la API en ejecución en **http://127.0.0.1:8000** (tras ejecutar `uv run uvicorn backend.app.main:app --reload` desde la raíz del proyecto).

---

## Páginas web (navegador)

| URL | Descripción |
|-----|-------------|
| http://127.0.0.1:8000/ | Página principal (dashboard) |
| http://127.0.0.1:8000/health | Health check (JSON) para despliegue |
| http://127.0.0.1:8000/registro | Registrar persona (empleado/visitante) con captura facial |
| http://127.0.0.1:8000/acceso | Validar acceso por reconocimiento facial — entrada/salida (HU-05, HU-06, HU-07) |
| http://127.0.0.1:8000/visitante | Registro de visitante y autorización de visita |
| http://127.0.0.1:8000/configuracion | Configuración del sistema |

---

## Documentación de la API

| URL | Descripción |
|-----|-------------|
| http://127.0.0.1:8000/docs | Swagger UI (OpenAPI) |
| http://127.0.0.1:8000/redoc | ReDoc (si está habilitado) |

---

## API REST (`/api/v1/...`)

### Personas

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | http://127.0.0.1:8000/api/v1/personas | Listar personas (opcional: `?tipo=Empleado`, `?tipo=Visitante`, `?tipo=Contratista`) |
| POST | http://127.0.0.1:8000/api/v1/personas | Crear persona (JSON: tipo_documento, nro_documento, nombres, id_tipo_persona, id_cargo opcional) |
| GET | http://127.0.0.1:8000/api/v1/personas/{id} | Obtener detalle de una persona |
| POST | http://127.0.0.1:8000/api/v1/personas/{id}/registros | Añadir embedding facial de registro (multipart: foto) |
| POST | http://127.0.0.1:8000/api/v1/personas/identificar | Identificar persona por imagen (visitante recurrente) |

### Acceso

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | http://127.0.0.1:8000/api/v1/acceso/validar | Validar acceso facial (imagen → permitido/denegado, registro entrada o salida automático) |

### Eventos

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | http://127.0.0.1:8000/api/v1/events | Listar eventos (`?tipo=ingreso`, `?tipo=salida`, `?limit=50`, `?offset=0`) |
| POST | http://127.0.0.1:8000/api/v1/events/exit | Stub (por implementar; entrada/salida se registran vía `/acceso/validar`) |

### Autorizaciones

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | http://127.0.0.1:8000/api/v1/autorizaciones | Listar autorizaciones |
| POST | http://127.0.0.1:8000/api/v1/autorizaciones | Crear autorización (JSON: id_persona, fecha_inicio, fecha_fin) |

### Usuarios

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | http://127.0.0.1:8000/api/v1/usuarios/login | Login (JSON: `username`, `password` → JWT) |
| GET | http://127.0.0.1:8000/api/v1/usuarios | Listar usuarios (por implementar) |
| POST | http://127.0.0.1:8000/api/v1/usuarios | Crear usuario (por implementar) |

---

**Documento:** URLs de acceso  
**Proyecto:** SCA-EMPX – STI S.A.S.
