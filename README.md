# SCA-EMPX - Sistema de Control de Acceso

Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas con reconocimiento facial para STI S.A.S.

## 🚀 Inicio Rápido con Docker

### Requisitos
- Docker 20.10+
- Docker Compose 2.0+
- Make (opcional)

### Despliegue Local

```bash
# 1. Clonar repositorio
git clone <tu-repo>
cd sca-empx

# 2. Configurar variables
cp .env.docker .env
# Editar .env con tus valores

# 3. Levantar aplicación
make docker-build
make docker-up

# O sin Make
docker-compose build
docker-compose up -d
```

### Acceder a la aplicación
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📚 Documentación

- [Guía de Docker](README.Docker.md) - Arquitectura y comandos Docker
- [Guía de Despliegue](docs/docker-deployment.md) - Despliegue completo con CI/CD
- [Guía de Uso](docs/guia-uso-aplicacion.md) - Manual de usuario
- [Documentación Técnica](docs/) - Arquitectura, modelos, historias de usuario

## 🏗️ Arquitectura

```
Frontend (Nginx) ──▶ Backend (FastAPI + ML) ──▶ SQLite
     │                      │
     │                      └─▶ DeepFace (Reconocimiento Facial)
     │
     └─▶ Archivos Estáticos
```

### Componentes
- **Backend**: FastAPI + DeepFace + Facenet (Python 3.13)
- **Frontend**: Nginx + HTML/CSS/JS
- **Base de datos**: SQLite con volumen persistente
- **ML**: Reconocimiento facial con embeddings 128-d

## 🛠️ Desarrollo

### Configuración local (sin Docker)

```bash
# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependencias
make install

# Inicializar base de datos
make init-db

# Ejecutar aplicación
make run
```

### Tests

```bash
# Ejecutar tests
make test

# Con cobertura
make test-verbose

# Linting
make lint
```

## 🔧 Comandos Make

```bash
make help                 # Ver todos los comandos
make install              # Instalar dependencias
make test                 # Ejecutar tests
make lint                 # Linter
make docker-build         # Construir imágenes
make docker-up            # Levantar contenedores
make docker-down          # Detener contenedores
make docker-logs          # Ver logs
make backup-db            # Backup SQLite
```

## 🚢 CI/CD con GitLab

El proyecto incluye pipeline completo de GitLab CI/CD:

1. **Test**: Tests unitarios + linting
2. **Build**: Construcción de imágenes Docker
3. **Push**: Subida a Docker Hub
4. **Deploy**: Despliegue a staging/producción

### Variables requeridas en GitLab

```
CI_DOCKER_USERNAME       # Usuario Docker Hub
CI_DOCKER_PASSWORD       # Token Docker Hub
SSH_PRIVATE_KEY          # Clave SSH para deploy
STAGING_SERVER           # Servidor staging
PRODUCTION_SERVER        # Servidor producción
SECRET_KEY               # Clave secreta app
```

Ver [Guía de Despliegue](docs/docker-deployment.md) para más detalles.

## 📦 Estructura del Proyecto

```
sca-empx/
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints API
│   │   ├── core/         # Configuración
│   │   ├── db/           # Base de datos
│   │   ├── ml/           # Reconocimiento facial
│   │   ├── schemas/      # Modelos Pydantic
│   │   ├── services/     # Lógica de negocio
│   │   └── static/       # Archivos HTML
│   ├── tests/            # Tests
│   └── Dockerfile        # Imagen backend
├── frontend/
│   ├── nginx.conf        # Configuración Nginx
│   └── Dockerfile        # Imagen frontend
├── docs/                 # Documentación
├── scripts/              # Scripts utilidad
├── docker-compose.yml    # Orquestación
├── .gitlab-ci.yml        # Pipeline CI/CD
├── Makefile              # Comandos make
└── pyproject.toml        # Dependencias Python
```

## 🔒 Seguridad

### Producción
- Cambiar `SECRET_KEY` en `.env`
- Usar HTTPS con certificados SSL
- Configurar firewall
- Backups automáticos
- Actualizar imágenes regularmente

### Usuarios por defecto
Ver documentación para credenciales iniciales.

## 🐛 Troubleshooting

### Backend no inicia
```bash
docker-compose logs backend
docker-compose restart backend
```

### Frontend no conecta
```bash
docker network inspect sca-network
docker exec sca-frontend ping backend
```

### Limpiar y reiniciar
```bash
make docker-clean
make docker-build
make docker-up
```

## 📝 Licencia

Proyecto desarrollado para STI S.A.S.

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'feat: nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Merge Request

## 📞 Soporte

Para más información consultar la [documentación completa](docs/) o crear un issue.

