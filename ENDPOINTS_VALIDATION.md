# Validación de Endpoints API vs Frontend

## Endpoints usados por el Frontend

### ✅ Personas
- `POST /api/v1/personas/registro-completo` - Registro con foto (IMPLEMENTADO)
- `GET /api/v1/personas` - Listar personas con filtros (IMPLEMENTADO)
- `GET /api/v1/personas/{id}` - Obtener persona (EXISTE)
- `PATCH /api/v1/personas/{id}` - Actualizar persona (IMPLEMENTADO)
- `POST /api/v1/personas/` - Crear persona sin foto (EXISTE)
- `POST /api/v1/personas/identificar` - Identificar por foto (EXISTE)
- `POST /api/v1/personas/{id}/registros` - Agregar embedding (EXISTE)
- `GET /api/v1/personas/dentro` - Personas actualmente dentro (❌ FALTA)

### ✅ Acceso
- `POST /api/v1/access/validate` - Validar acceso (IMPLEMENTADO)
- `POST /api/v1/access/register-exit` - Registrar salida (EXISTE)
- `POST /api/v1/acceso/validar` - Validar acceso (español) (EXISTE)

### ✅ Visitas
- `POST /api/v1/visitas/` - Crear visita (EXISTE)
- `GET /api/v1/visitas/` - Listar visitas (EXISTE)
- `PATCH /api/v1/visitas/{id}/salida` - Registrar salida (EXISTE)

### ✅ Eventos
- `GET /api/v1/events/` - Listar eventos (EXISTE)
- `GET /api/v1/events/hoy` - Accesos de hoy (EXISTE)
- `GET /api/v1/events/estadisticas` - Estadísticas (❌ FALTA)
- `GET /api/v1/events/recientes` - Eventos recientes (❌ FALTA)

### ✅ Catálogos
- `GET /api/v1/catalogos/tipos-persona` - Tipos de persona (EXISTE)
- `GET /api/v1/catalogos/areas` - Áreas (EXISTE)
- `GET /api/v1/catalogos/areas/{id}/cargos` - Cargos por área (EXISTE)
- `GET /api/v1/catalogos/cargos` - Todos los cargos (EXISTE)

### ✅ Autorizaciones
- `GET /api/v1/autorizaciones` - Listar autorizaciones (EXISTE)
- `POST /api/v1/autorizaciones` - Crear autorización (EXISTE)
- `PATCH /api/v1/autorizaciones/{id}` - Actualizar autorización (EXISTE)

### ✅ Usuarios
- `POST /api/v1/usuarios/login` - Login (EXISTE)
- `GET /api/v1/usuarios` - Listar usuarios (EXISTE)
- `POST /api/v1/usuarios` - Crear usuario (EXISTE)
- `PATCH /api/v1/usuarios/{id}` - Actualizar usuario (EXISTE)

### ✅ Configuración
- `POST /api/v1/config/reset-db` - Resetear BD (EXISTE)

## Endpoints que FALTAN implementar

1. **GET /api/v1/personas/dentro** - Personas actualmente dentro del edificio
2. **GET /api/v1/events/estadisticas** - Estadísticas de accesos
3. **GET /api/v1/events/recientes** - Eventos recientes con filtro de minutos

## Archivos HTML que necesitan revisión

- `dashboard.html` - Usa endpoints de estadísticas que faltan
- `personas-dentro.html` - Usa endpoint /personas/dentro que falta
- `historial-accesos.html` - Verificar parámetros de filtro
- `reporte-accesos.html` - Verificar endpoint de reportes
