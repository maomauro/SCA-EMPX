# Resumen de Dockerización - SCA-EMPX

## ✅ Archivos Creados

### Configuración Docker
- `backend/Dockerfile` - Imagen backend (Python 3.13 + FastAPI + ML)
- `frontend/Dockerfile` - Imagen frontend (Nginx Alpine)
- `docker-compose.yml` - Orquestación producción
- `docker-compose.dev.yml` - Orquestación desarrollo con hot-reload
- `.dockerignore` - Exclusiones para build
- `frontend/nginx.conf` - Configuración Nginx + proxy reverso

### CI/CD
- `.gitlab-ci.yml` - Pipeline completo (test → build → push → deploy)
- `.gitlab/issue_templates/bug.md` - Template para issues
- `.gitlab/merge_request_templates/default.md` - Template para MRs

### Configuración
- `.env.docker` - Variables de entorno template
- `Makefile` - Comandos simplificados

### Scripts
- `scripts/docker-entrypoint.sh` - Inicialización backend
- `scripts/test-docker.sh` - Script de pruebas Docker

### Documentación
- `README.Docker.md` - Guía rápida Docker
- `docs/docker-deployment.md` - Guía completa de despliegue
- `README.md` - Actualizado con info Docker
- `DOCKER_SETUP.md` - Este archivo

## 🏗️ Arquitectura

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │ :80
       ▼
┌─────────────┐
│  Frontend   │  Nginx Alpine (~40MB)
│   (Nginx)   │  - Sirve estáticos
└──────┬──────┘  - Proxy reverso
       │
       │ :8000
       ▼
┌─────────────┐
│   Backend   │  Python 3.13 (~2.5GB)
│  (FastAPI)  │  - API REST
└──────┬──────┘  - ML (DeepFace)
       │          - Usuario no-root
       ▼
┌─────────────┐
│   SQLite    │  Volumen persistente
│  (Volume)   │  - sca-sqlite-data
└─────────────┘
```

## 🚀 Comandos Rápidos

### Desarrollo Local
```bash
# Setup inicial
cp .env.docker .env
make docker-build
make docker-up

# Ver logs
make docker-logs

# Detener
make docker-down
```

### Producción
```bash
# Build y push a Docker Hub
export DOCKER_USERNAME=tu-usuario
make docker-build
make docker-push

# En servidor
docker-compose pull
docker-compose up -d
```

### Tests
```bash
# Local
make test
make lint

# En CI/CD (automático en cada push)
git push origin feature/nueva-funcionalidad
```

## 📋 Checklist de Configuración

### 1. Docker Hub
- [ ] Crear cuenta en Docker Hub
- [ ] Generar Access Token
- [ ] Configurar en GitLab CI/CD Variables

### 2. GitLab CI/CD Variables
Configurar en: Settings > CI/CD > Variables

| Variable | Descripción |
|----------|-------------|
| `CI_DOCKER_USERNAME` | Usuario Docker Hub |
| `CI_DOCKER_PASSWORD` | Token Docker Hub |
| `SSH_PRIVATE_KEY` | Clave SSH para deploy |
| `STAGING_SERVER` | IP/hostname staging |
| `STAGING_USER` | Usuario SSH staging |
| `PRODUCTION_SERVER` | IP/hostname producción |
| `PRODUCTION_USER` | Usuario SSH producción |
| `SECRET_KEY` | Clave secreta app (32+ chars) |

### 3. Servidor de Producción
- [ ] Instalar Docker
- [ ] Instalar Docker Compose
- [ ] Configurar SSH
- [ ] Abrir puertos 80 y 8000
- [ ] Configurar firewall
- [ ] Copiar docker-compose.yml y .env

### 4. Seguridad
- [ ] Cambiar SECRET_KEY en .env
- [ ] No versionar .env
- [ ] Configurar HTTPS (Let's Encrypt)
- [ ] Configurar backups automáticos
- [ ] Restringir acceso SSH

## 🔄 Workflow GitLab CI/CD

### Pipeline Stages

1. **test** (automático en cada push)
   - Tests unitarios con pytest
   - Cobertura de código
   - Linting con ruff

2. **build** (solo main/develop/tags)
   - Construye imagen backend
   - Construye imagen frontend
   - Etiqueta con commit SHA

3. **push** (solo main/develop/tags)
   - Sube imágenes a Docker Hub
   - Tags: `latest` y `${CI_COMMIT_SHORT_SHA}`

4. **deploy** (manual)
   - **Staging**: rama `develop`
   - **Production**: rama `main` o tags

### Flujo de Trabajo

```bash
# 1. Desarrollo
git checkout -b feature/nueva-funcionalidad
# ... hacer cambios ...
git commit -m "feat: nueva funcionalidad"
git push origin feature/nueva-funcionalidad
# → Pipeline ejecuta: test

# 2. Merge Request
# Crear MR en GitLab
# → Pipeline ejecuta: test
# → Revisar y aprobar

# 3. Staging
git checkout develop
git merge feature/nueva-funcionalidad
git push origin develop
# → Pipeline ejecuta: test → build → push
# → Deploy manual a staging

# 4. Producción
git checkout main
git merge develop
git tag v1.0.0
git push origin main --tags
# → Pipeline ejecuta: test → build → push
# → Deploy manual a producción
```

## 📊 Características Implementadas

### Backend
- ✅ Multi-stage build (optimización tamaño)
- ✅ Usuario no-root (seguridad)
- ✅ Health checks
- ✅ Variables de entorno parametrizadas
- ✅ Volumen persistente para SQLite
- ✅ ML integrado (DeepFace + Facenet)
- ✅ Logs estructurados

### Frontend
- ✅ Nginx Alpine (imagen ligera)
- ✅ Proxy reverso al backend
- ✅ Caché de archivos estáticos
- ✅ Headers de seguridad
- ✅ Health checks
- ✅ Timeouts configurados para ML

### CI/CD
- ✅ Tests automáticos
- ✅ Linting automático
- ✅ Build multi-arquitectura
- ✅ Push a Docker Hub
- ✅ Deploy automatizado
- ✅ Caché de dependencias
- ✅ Reportes de cobertura

### Operaciones
- ✅ Makefile con comandos comunes
- ✅ Scripts de prueba
- ✅ Backups automatizables
- ✅ Monitoreo con health checks
- ✅ Logs centralizados
- ✅ Volúmenes persistentes

## 🎯 Próximos Pasos

### Inmediatos
1. Configurar variables en GitLab CI/CD
2. Crear cuenta Docker Hub y generar token
3. Probar build local: `make docker-build`
4. Probar despliegue local: `make docker-up`
5. Verificar acceso: http://localhost

### Corto Plazo
1. Configurar servidor de staging
2. Configurar servidor de producción
3. Ejecutar primer deploy a staging
4. Configurar backups automáticos
5. Configurar HTTPS con Let's Encrypt

### Largo Plazo
1. Implementar monitoreo (Prometheus + Grafana)
2. Implementar logging centralizado (ELK Stack)
3. Configurar alertas
4. Optimizar imágenes Docker
5. Implementar auto-scaling

## 📚 Recursos

### Documentación
- [README.Docker.md](README.Docker.md) - Guía rápida
- [docs/docker-deployment.md](docs/docker-deployment.md) - Guía completa
- [Makefile](Makefile) - Comandos disponibles

### Enlaces Útiles
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
- [Nginx](https://nginx.org/en/docs/)
- [FastAPI](https://fastapi.tiangolo.com/)

## 🐛 Troubleshooting Común

### Error: "Cannot connect to Docker daemon"
```bash
# Verificar Docker está corriendo
docker info

# En Windows, iniciar Docker Desktop
```

### Error: "Port already in use"
```bash
# Cambiar puertos en .env
BACKEND_PORT=8001
FRONTEND_PORT=8080

# O detener servicio que usa el puerto
```

### Error: "Permission denied" en volúmenes
```bash
# Verificar permisos
docker volume inspect sca-sqlite-data

# Recrear volumen
docker-compose down -v
docker-compose up -d
```

### Pipeline falla en GitLab
```bash
# Verificar variables configuradas
# Settings > CI/CD > Variables

# Probar build local
make docker-build
```

## ✨ Mejoras Implementadas

1. **Separación de concerns**: Frontend y backend en contenedores independientes
2. **Optimización**: Multi-stage builds, imágenes Alpine
3. **Seguridad**: Usuario no-root, variables de entorno, headers de seguridad
4. **Escalabilidad**: Arquitectura preparada para múltiples instancias
5. **Mantenibilidad**: Makefile, scripts, documentación completa
6. **CI/CD**: Pipeline completo automatizado
7. **Monitoreo**: Health checks, logs estructurados
8. **Persistencia**: Volúmenes para datos críticos

---

**¡Dockerización completada exitosamente!** 🎉

Para comenzar, ejecuta:
```bash
make docker-build && make docker-up
```
