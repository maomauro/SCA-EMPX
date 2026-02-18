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
| http://127.0.0.1:8000/historial-accesos | Historial de accesos: filtros, tabla y exportación CSV (HU-08) |
| http://127.0.0.1:8000/editar-persona | Editar persona (empleado/visitante). Usar ?id= (HU-10) |
| http://127.0.0.1:8000/dashboard | Dashboard de accesos: métricas y eventos recientes; actualización 30 s (HU-11) |
| http://127.0.0.1:8000/revocar-autorizacion | Listar autorizaciones vigentes y revocarlas (HU-13) |
| http://127.0.0.1:8000/personas-dentro | Personas actualmente dentro: nombre y hora de entrada (HU-14) |

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
| GET | http://127.0.0.1:8000/api/v1/personas | Listar personas. Query: tipo, estado, q. (`?tipo=empleado\|visitante`, `?estado=activo\|inactivo\|todos`, `?q=nombre o documento`) |
| GET | http://127.0.0.1:8000/api/v1/personas/dentro | Personas actualmente dentro: id_persona, nombre_completo, fecha_hora_entrada. HU-14. |
| GET | http://127.0.0.1:8000/api/v1/personas/{id} | Detalle de persona para edición (HU-10) |
| POST | http://127.0.0.1:8000/api/v1/personas | Registrar persona (empleado o visitante; multipart + foto) |
| PATCH | http://127.0.0.1:8000/api/v1/personas/{id} | Actualizar persona. JSON opcionales: nombre_completo, cargo, area, telefono, email, estado (activo\|inactivo). HU-02, HU-10. |

### Acceso

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | http://127.0.0.1:8000/api/v1/access/validate | Validar acceso (imagen → permitido/denegado + registro entrada) |
| POST | http://127.0.0.1:8000/api/v1/access/register-exit | Registrar salida (imagen → identificar → registro salida) |

### Eventos

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | http://127.0.0.1:8000/api/v1/events | Listar eventos. Query: `persona_id`, `documento`, `fecha_desde`, `fecha_hasta` (YYYY-MM-DD), `tipo` (ingreso\|salida), `resultado` (permitido\|denegado), `limit` (máx 100), `offset`. Orden: fecha_hora desc. HU-08. |
| GET | http://127.0.0.1:8000/api/v1/events/recientes | Eventos de los últimos N minutos. Query: `minutos` (1–120), `limit` (máx 100). HU-11. |
| GET | http://127.0.0.1:8000/api/v1/events/estadisticas | Métricas dashboard: total_dentro, accesos_hoy, denegaciones_hoy. HU-11. |
| GET | http://127.0.0.1:8000/api/v1/events/export | Exportar eventos a CSV. Mismos filtros que GET /events; `limit` (máx 5000). HU-08. |
| POST | http://127.0.0.1:8000/api/v1/events/exit | Stub (por implementar; usar `/access/register-exit`) |

### Autorizaciones

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | http://127.0.0.1:8000/api/v1/autorizaciones | Listar autorizaciones. Query: `estado` (vigente\|vencida\|cancelada\|revocada). HU-13. |
| POST | http://127.0.0.1:8000/api/v1/autorizaciones | Crear autorización (JSON: id_persona, fecha_inicio, fecha_fin) |
| PATCH | http://127.0.0.1:8000/api/v1/autorizaciones/{id} | Revocar autorización. JSON: estado=revocada, motivo (opcional). Solo si vigente. HU-13. |

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
