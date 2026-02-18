# URLs de acceso - SCA-EMPX

Listado de URLs para acceder a la aplicación con la API en ejecución en **http://127.0.0.1:8000** (tras ejecutar `uv run uvicorn backend.app.main:app --reload` desde la raíz del proyecto).

---

## Páginas web (navegador)

| URL | Descripción |
|-----|-------------|
| http://127.0.0.1:8000/ | Health check (JSON) |
| http://127.0.0.1:8000/health | Estado para despliegue |
| http://127.0.0.1:8000/validate-access | Validar acceso por reconocimiento facial (HU-05) |
| http://127.0.0.1:8000/registro-empleado | Registrar empleado con foto (HU-01) |
| http://127.0.0.1:8000/registro-visitante | Registrar visitante con foto (HU-03) |
| http://127.0.0.1:8000/autorizacion-visita | Generar autorización de visita (HU-04) |
| http://127.0.0.1:8000/registrar-salida | Registrar salida por reconocimiento facial (HU-07) |
| http://127.0.0.1:8000/administracion-usuarios | Administración de usuarios: login, listado, alta, activar/desactivar (HU-09) |
| http://127.0.0.1:8000/listado-personas | Listado de personas con búsqueda y Desactivar/Activar (HU-02) |

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
| GET | http://127.0.0.1:8000/api/v1/personas | Listar personas (`?tipo=empleado\|visitante`, `?estado=activo\|inactivo\|todos`, `?q=nombre o documento`) |
| POST | http://127.0.0.1:8000/api/v1/personas | Registrar persona (empleado o visitante; multipart + foto) |
| PATCH | http://127.0.0.1:8000/api/v1/personas/{id} | Actualizar estado (JSON: estado activo\|inactivo). HU-02. |

### Acceso

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | http://127.0.0.1:8000/api/v1/access/validate | Validar acceso (imagen → permitido/denegado + registro entrada) |
| POST | http://127.0.0.1:8000/api/v1/access/register-exit | Registrar salida (imagen → identificar → registro salida) |

### Eventos

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | http://127.0.0.1:8000/api/v1/events | Listar eventos (`?tipo=ingreso`, `?tipo=salida`, `?limit=50`, `?offset=0`) |
| POST | http://127.0.0.1:8000/api/v1/events/exit | Stub (por implementar; usar `/access/register-exit`) |

### Autorizaciones

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | http://127.0.0.1:8000/api/v1/autorizaciones | Listar autorizaciones |
| POST | http://127.0.0.1:8000/api/v1/autorizaciones | Crear autorización (JSON: id_persona, fecha_inicio, fecha_fin) |

### Usuarios

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | http://127.0.0.1:8000/api/v1/usuarios/login | Login (JSON: username, password → JWT) |
| GET | http://127.0.0.1:8000/api/v1/usuarios | Listar usuarios (requiere Authorization: Bearer &lt;token&gt;) |
| POST | http://127.0.0.1:8000/api/v1/usuarios | Crear usuario (solo admin; JSON: nombre_usuario, password, rol) |
| PATCH | http://127.0.0.1:8000/api/v1/usuarios/{id} | Activar/desactivar usuario (solo admin; JSON: estado activo\|inactivo) |

---

**Documento:** URLs de acceso  
**Proyecto:** SCA-EMPX – STI S.A.S.
