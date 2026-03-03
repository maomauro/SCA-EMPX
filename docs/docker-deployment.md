# Guía de Despliegue con Docker

## Tabla de Contenidos
1. [Requisitos Previos](#requisitos-previos)
2. [Configuración Inicial](#configuración-inicial)
3. [Despliegue Local](#despliegue-local)
4. [Despliegue en Servidor](#despliegue-en-servidor)
5. [GitLab CI/CD](#gitlab-cicd)
6. [Mantenimiento](#mantenimiento)

## Requisitos Previos

### En tu máquina local
- Docker Engine 20.10+
- Docker Compose 2.0+
- Make (opcional, facilita comandos)
- Git

### En servidor de producción
- Docker Engine 20.10+
- Docker Compose 2.0+
- SSH configurado
- Puertos 80 y 8000 disponibles

## Configuración Inicial

### 1. Clonar repositorio
```bash
git clone <tu-repo>
cd sca-empx
```

### 2. Configurar variables de entorno
```bash
cp .env.docker .env
```

Editar `.env`:
```bash
# Docker Registry
DOCKER_USERNAME=tu-usuario-dockerhub

# Puertos
BACKEND_PORT=8000
FRONTEND_PORT=80

# Seguridad (CAMBIAR EN PRODUCCIÓN)
SECRET_KEY=$(openssl rand -hex 32)
SIMILARITY_THRESHOLD=0.6
```

### 3. Configurar Docker Hub
```bash
docker login
# Ingresar usuario y token de Docker Hub
```

## Despliegue Local

### Desarrollo con hot-reload
```bash
# Usar docker-compose.dev.yml
docker-compose -f docker-compose.dev.yml up

# O con Make
make docker-build
make docker-up
```

Acceder a:
- Frontend: http://localhost
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Producción local
```bash
docker-compose up -d
```

## Despliegue en Servidor

### Opción 1: Manual

#### 1. Preparar servidor
```bash
# Conectar por SSH
ssh usuario@servidor

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Copiar archivos
```bash
# En tu máquina local
scp docker-compose.yml usuario@servidor:/opt/sca-empx/
scp .env usuario@servidor:/opt/sca-empx/
```

#### 3. Desplegar
```bash
# En el servidor
cd /opt/sca-empx
docker-compose pull
docker-compose up -d
```

### Opción 2: Con GitLab CI/CD (Recomendado)

Ver sección [GitLab CI/CD](#gitlab-cicd)

## GitLab CI/CD

### 1. Configurar Variables en GitLab

Ir a: Settings > CI/CD > Variables

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `CI_DOCKER_USERNAME` | Usuario Docker Hub | `miusuario` |
| `CI_DOCKER_PASSWORD` | Token Docker Hub | `dckr_pat_xxx` |
| `SSH_PRIVATE_KEY` | Clave SSH privada | `-----BEGIN...` |
| `STAGING_SERVER` | IP/hostname staging | `staging.example.com` |
| `STAGING_USER` | Usuario SSH staging | `deploy` |
| `PRODUCTION_SERVER` | IP/hostname producción | `prod.example.com` |
| `PRODUCTION_USER` | Usuario SSH producción | `deploy` |
| `SECRET_KEY` | Clave secreta app | `random-32-chars` |

### 2. Generar Token de Docker Hub

1. Ir a https://hub.docker.com/settings/security
2. Crear "New Access Token"
3. Copiar token y guardarlo en `CI_DOCKER_PASSWORD`

### 3. Configurar SSH

```bash
# Generar par de claves
ssh-keygen -t ed25519 -C "gitlab-ci"

# Copiar clave pública al servidor
ssh-copy-id -i ~/.ssh/id_ed25519.pub usuario@servidor

# Copiar clave privada a GitLab CI/CD Variables
cat ~/.ssh/id_ed25519
# Pegar contenido en CI_DOCKER_PASSWORD
```

### 4. Pipeline Stages

El pipeline `.gitlab-ci.yml` tiene 4 stages:

#### Stage 1: Test
- Ejecuta tests unitarios con pytest
- Genera reporte de cobertura
- Ejecuta linter (ruff)
- Se ejecuta en cada push/MR

#### Stage 2: Build
- Construye imágenes Docker
- Etiqueta con commit SHA y `latest`
- Guarda imágenes como artefactos
- Solo en ramas `main`, `develop` y tags

#### Stage 3: Push
- Sube imágenes a Docker Hub
- Usa credenciales de CI/CD Variables
- Solo en ramas `main`, `develop` y tags

#### Stage 4: Deploy
- **Staging**: Deploy automático a staging (rama `develop`)
- **Production**: Deploy manual a producción (rama `main` o tags)

### 5. Workflow

```bash
# Desarrollo
git checkout -b feature/nueva-funcionalidad
git commit -m "feat: nueva funcionalidad"
git push origin feature/nueva-funcionalidad
# Crear Merge Request → Tests se ejecutan automáticamente

# Staging
git checkout develop
git merge feature/nueva-funcionalidad
git push origin develop
# Pipeline: test → build → push → deploy:staging (manual)

# Producción
git checkout main
git merge develop
git tag v1.0.0
git push origin main --tags
# Pipeline: test → build → push → deploy:production (manual)
```

## Mantenimiento

### Backups

#### Backup manual de SQLite
```bash
make backup-db
# O
docker run --rm -v sca-sqlite-data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/sqlite-$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

#### Backup automático (cron)
```bash
# En el servidor, agregar a crontab
0 2 * * * cd /opt/sca-empx && docker run --rm -v sca-sqlite-data:/data -v /backups:/backup alpine tar czf /backup/sqlite-$(date +\%Y\%m\%d).tar.gz -C /data .
```

### Restaurar backup
```bash
docker-compose down
docker run --rm -v sca-sqlite-data:/data -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/sqlite-20260301.tar.gz -C /data
docker-compose up -d
```

### Actualizar aplicación
```bash
# Pull nueva versión
docker-compose pull

# Recrear contenedores
docker-compose up -d

# Verificar
docker-compose ps
docker-compose logs -f
```

### Monitoreo

#### Ver logs
```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Últimas 100 líneas
docker-compose logs --tail=100
```

#### Ver estado
```bash
docker-compose ps
docker stats
```

#### Health checks
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost/health
```

### Limpieza

#### Limpiar contenedores detenidos
```bash
docker container prune
```

#### Limpiar imágenes no usadas
```bash
docker image prune -a
```

#### Limpiar todo (¡CUIDADO!)
```bash
make docker-clean
# O
docker-compose down -v --rmi local
```

## Troubleshooting

### Backend no inicia

```bash
# Ver logs detallados
docker-compose logs backend

# Verificar variables de entorno
docker-compose config

# Reiniciar contenedor
docker-compose restart backend
```

### Frontend no conecta con backend

```bash
# Verificar red
docker network inspect sca-network

# Probar conectividad
docker exec sca-frontend ping backend

# Verificar configuración nginx
docker exec sca-frontend cat /etc/nginx/conf.d/default.conf
```

### Base de datos corrupta

```bash
# Restaurar desde backup
docker-compose down
# Restaurar backup (ver sección Backups)
docker-compose up -d
```

### Problemas de permisos

```bash
# Verificar permisos del volumen
docker volume inspect sca-sqlite-data

# Recrear volumen
docker-compose down -v
docker-compose up -d
```

### Pipeline falla en GitLab

```bash
# Verificar variables configuradas
# Settings > CI/CD > Variables

# Ver logs del job fallido en GitLab UI

# Probar localmente
docker build -f backend/Dockerfile .
docker build -f frontend/Dockerfile .
```

## Seguridad

### Checklist de producción

- [ ] Cambiar `SECRET_KEY` por valor aleatorio fuerte
- [ ] No versionar archivo `.env`
- [ ] Usar tokens de Docker Hub, no contraseñas
- [ ] Configurar HTTPS con certificados SSL
- [ ] Restringir acceso SSH (solo IPs permitidas)
- [ ] Configurar firewall (ufw/iptables)
- [ ] Backups automáticos configurados
- [ ] Monitoreo de logs configurado
- [ ] Actualizar imágenes regularmente

### Configurar HTTPS (Nginx + Let's Encrypt)

```bash
# Instalar certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tudominio.com

# Renovación automática
sudo certbot renew --dry-run
```

## Recursos Adicionales

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Nginx Documentation](https://nginx.org/en/docs/)
