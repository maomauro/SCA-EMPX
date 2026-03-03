# Guía de Dockerización - SCA-EMPX

Sistema de Control de Acceso con arquitectura multi-contenedor.

## Arquitectura

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Cliente   │─────▶│   Frontend   │─────▶│   Backend   │
│  (Browser)  │      │    (Nginx)   │      │  (FastAPI)  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            │                      ▼
                            │              ┌─────────────┐
                            │              │   SQLite    │
                            │              │  (Volume)   │
                            │              └─────────────┘
                            ▼
                     ┌──────────────┐
                     │   Archivos   │
                     │   Estáticos  │
                     └──────────────┘
```

## Componentes

### Backend
- Imagen: Python 3.13-slim
- Framework: FastAPI + Uvicorn
- ML: DeepFace + Facenet (reconocimiento facial)
- Base de datos: SQLite con volumen persistente
- Puerto: 8000

### Frontend
- Imagen: Nginx 1.25-alpine
- Función: Servir estáticos + proxy reverso
- Puerto: 80

## Inicio Rápido

### 1. Configurar variables de entorno

```bash
cp .env.docker .env
# Editar .env con tus valores
```

### 2. Construir y levantar contenedores

```bash
# Con Make
make docker-build
make docker-up

# O con Docker Compose directamente
docker-compose build
docker-compose up -d
```

### 3. Verificar estado

```bash
make docker-ps
# O
docker-compose ps
```

### 4. Acceder a la aplicación

- Frontend: http://localhost
- Backend API: http://localhost:8000
- Docs API: http://localhost:8000/docs

## Comandos Make

```bash
make help                 # Ver todos los comandos disponibles
make install              # Instalar dependencias localmente
make test                 # Ejecutar tests
make lint                 # Ejecutar linter
make docker-build         # Construir imágenes
make docker-up            # Levantar contenedores
make docker-down          # Detener contenedores
make docker-logs          # Ver logs
make docker-clean         # Limpiar todo
make backup-db            # Backup de SQLite
```

## GitLab CI/CD

### Variables requeridas en GitLab

Configurar en: Settings > CI/CD > Variables

```
CI_DOCKER_USERNAME       # Usuario de Docker Hub
CI_DOCKER_PASSWORD       # Token de Docker Hub
SSH_PRIVATE_KEY          # Clave SSH para deploy
STAGING_SERVER           # IP/hostname staging
STAGING_USER             # Usuario SSH staging
PRODUCTION_SERVER        # IP/hostname producción
PRODUCTION_USER          # Usuario SSH producción
SECRET_KEY               # Clave secreta de la app
```

### Pipeline stages

1. **test**: Tests unitarios + linting
2. **build**: Construcción de imágenes Docker
3. **push**: Subida a Docker Hub
4. **deploy**: Despliegue a staging/producción (manual)

## Volúmenes

### sqlite-data
Almacena la base de datos SQLite de forma persistente.

```bash
# Backup manual
docker run --rm -v sca-sqlite-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/sqlite-backup.tar.gz -C /data .

# Restore
docker run --rm -v sca-sqlite-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/sqlite-backup.tar.gz -C /data
```

### backend-logs
Logs de la aplicación backend (opcional).

## Desarrollo Local

### Opción 1: Con Docker (recomendado)
```bash
make docker-build
make docker-up
make docker-logs
```

### Opción 2: Sin Docker
```bash
make install
make init-db
make run
```

## Producción

### 1. Preparar servidor

```bash
# Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Crear directorio de la app
mkdir -p /opt/sca-empx
cd /opt/sca-empx
```

### 2. Copiar archivos necesarios

```bash
# docker-compose.yml
# .env (con valores de producción)
```

### 3. Desplegar

```bash
docker-compose pull
docker-compose up -d
```

### 4. Monitoreo

```bash
docker-compose logs -f
docker-compose ps
```

## Troubleshooting

### Backend no inicia
```bash
# Ver logs detallados
docker-compose logs backend

# Verificar health check
docker inspect sca-backend | grep -A 10 Health
```

### Frontend no conecta con backend
```bash
# Verificar red
docker network inspect sca-network

# Probar conectividad
docker exec sca-frontend ping backend
```

### Base de datos corrupta
```bash
# Restaurar desde backup
make backup-db  # Primero hacer backup del estado actual
# Copiar backup bueno a backend/app/db/sqlite.db
docker-compose restart backend
```

### Limpiar y reiniciar
```bash
make docker-clean
make docker-build
make docker-up
```

## Seguridad

### Recomendaciones para producción

1. **Variables de entorno**
   - Cambiar SECRET_KEY por valor aleatorio fuerte
   - No versionar archivo .env

2. **Nginx**
   - Configurar HTTPS con certificados SSL
   - Ajustar headers de seguridad

3. **Backend**
   - Ejecuta como usuario no-root (appuser)
   - Sin privilegios elevados

4. **Base de datos**
   - Backups automáticos regulares
   - Volumen con permisos restrictivos

5. **Docker Hub**
   - Usar tokens de acceso en lugar de contraseñas
   - Imágenes privadas si es necesario

## Optimizaciones

### Reducir tamaño de imágenes

Las imágenes ya usan multi-stage builds y alpine cuando es posible:
- Backend: ~2.5GB (incluye TensorFlow para ML)
- Frontend: ~40MB (nginx-alpine)

### Caché de builds

GitLab CI usa caché para dependencias Python:
```yaml
cache:
  key: ${CI_COMMIT_REF_SLUG}-python
  paths:
    - .venv/
```

## Monitoreo y Logs

### Ver logs en tiempo real
```bash
docker-compose logs -f --tail=100
```

### Logs específicos
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Exportar logs
```bash
docker-compose logs > logs_$(date +%Y%m%d).txt
```

## Actualización

### Actualizar a nueva versión
```bash
# Pull nueva versión
docker-compose pull

# Recrear contenedores
docker-compose up -d

# Verificar
docker-compose ps
```

## Soporte

Para más información consultar:
- [Documentación del proyecto](docs/)
- [Guía de uso](docs/guia-uso-aplicacion.md)
- [Bitácora de desarrollo](docs/bitacora-desarrollo.md)
