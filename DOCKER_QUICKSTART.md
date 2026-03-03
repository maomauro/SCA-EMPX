# 🚀 Quick Start - Docker Multi-Contenedor

## Arquitectura Nueva

```
Frontend (Nginx) ──▶ Backend (FastAPI) ──▶ SQLite
     :80                  :8000               (volume)
                            │
                            ▼
                      MLflow Server ──▶ MLflow Data
                          :5000           (volume)
                            ▲
                            │
                      Training Service
                       (on-demand)
```

## 🎯 Inicio Rápido (3 pasos)

### 1. Configurar variables
```bash
cp .env.docker .env
# Editar DOCKER_USERNAME con tu usuario de Docker Hub
```

### 2. Levantar servicios
```bash
make docker-build
make docker-up
```

### 3. Verificar
```bash
# Ver estado
make docker-ps

# Acceder a:
# - Frontend: http://localhost
# - Backend: http://localhost:8000
# - MLflow: http://localhost:5000
```

## 📦 Servicios Disponibles

### Backend (API + ML)
- **Puerto**: 8000
- **Propósito**: API REST + Reconocimiento facial
- **Logs**: `make docker-logs-backend`

### Frontend (Nginx)
- **Puerto**: 80
- **Propósito**: Interfaz web + Proxy reverso
- **Logs**: `make docker-logs-frontend`

### MLflow (Tracking Server) ⭐ NUEVO
- **Puerto**: 5000
- **Propósito**: Tracking de experimentos ML
- **UI**: http://localhost:5000
- **Logs**: `make docker-logs-mlflow`

### Training (On-demand) ⭐ NUEVO
- **Propósito**: Entrenamiento de modelos
- **Uso**: `make docker-train`
- **No se levanta con `docker-compose up`**

## 🎓 Comandos de Entrenamiento

### Entrenamiento básico
```bash
# Con parámetros por defecto (3 épocas)
make docker-train

# O directamente
docker-compose run --rm train
```

### Entrenamiento personalizado
```bash
# 5 épocas
docker-compose run --rm train --epochs 5

# Con batch size personalizado
docker-compose run --rm train --epochs 10 --batch-size 256

# Con configuración JSON
docker-compose run --rm train --config training/config_default.json
```

### Con Comet ML
```bash
# Agregar COMET_API_KEY a .env
COMET_API_KEY=tu_api_key_aqui

# Ejecutar entrenamiento
docker-compose run --rm train --epochs 5
```

## 📊 Ver Resultados en MLflow

1. Ejecutar entrenamiento:
   ```bash
   make docker-train
   ```

2. Abrir MLflow UI:
   ```
   http://localhost:5000
   ```

3. Ver experimento `mnist-classifier`
4. Explorar métricas: loss, accuracy, f1-score

## 🔧 Comandos Útiles

### Gestión de servicios
```bash
make docker-up          # Levantar servicios
make docker-down        # Detener servicios
make docker-restart     # Reiniciar servicios
make docker-ps          # Ver estado
make docker-logs        # Ver todos los logs
```

### Logs específicos
```bash
make docker-logs-backend
make docker-logs-frontend
make docker-logs-mlflow
```

### Limpieza
```bash
make docker-clean       # Limpiar todo (¡cuidado!)
make clean              # Limpiar archivos temporales
```

## 🗂️ Volúmenes Persistentes

```bash
# Ver volúmenes
docker volume ls | grep sca

# Volúmenes creados:
sca-sqlite-data              # Base de datos
sca-mlflow-data              # Runs de MLflow
sca-mlflow-artifacts         # Modelos y artefactos
sca-training-data            # Dataset MNIST
sca-training-checkpoints     # Checkpoints del modelo
```

## 💾 Backups

### Backup de SQLite
```bash
make backup-db
```

### Backup de MLflow
```bash
docker run --rm -v sca-mlflow-data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/mlflow-$(date +%Y%m%d).tar.gz -C /data .
```

## 🐛 Troubleshooting

### MLflow no inicia
```bash
docker-compose logs mlflow
docker-compose restart mlflow
```

### Training falla
```bash
# Ver logs detallados
docker-compose run --rm train --epochs 1

# Verificar conectividad con MLflow
docker exec sca-backend ping mlflow
```

### Limpiar y reiniciar
```bash
make docker-clean
make docker-build
make docker-up
```

## 📝 Diferencias con Configuración Anterior

### ❌ Antes (Dockerfile monolítico)
- Un solo contenedor con todo
- Difícil de escalar
- Mezcla de responsabilidades

### ✅ Ahora (Multi-contenedor)
- Backend separado (API + ML)
- Frontend separado (Nginx)
- MLflow separado (Tracking)
- Training on-demand
- Fácil de escalar y mantener

## 🔄 Migración

Si vienes de la configuración anterior:

1. El `Dockerfile` de la raíz fue renombrado a `Dockerfile.deprecated`
2. Ahora hay 4 Dockerfiles específicos:
   - `backend/Dockerfile`
   - `frontend/Dockerfile`
   - `mlflow/Dockerfile`
   - `training/Dockerfile`

Ver [MIGRATION_DOCKER.md](MIGRATION_DOCKER.md) para detalles completos.

## 🎯 Workflow Típico

### Desarrollo
```bash
# 1. Levantar infraestructura
make docker-up

# 2. Verificar servicios
make docker-ps

# 3. Experimentar con modelos
make docker-train

# 4. Ver resultados
# http://localhost:5000

# 5. Ver logs si hay problemas
make docker-logs
```

### Producción
```bash
# 1. Build y push
make docker-build
make docker-push

# 2. En servidor
docker-compose pull
docker-compose up -d

# 3. Verificar
docker-compose ps
```

## 📚 Documentación Completa

- [README.Docker.md](README.Docker.md) - Guía completa Docker
- [MIGRATION_DOCKER.md](MIGRATION_DOCKER.md) - Detalles de migración
- [docs/docker-deployment.md](docs/docker-deployment.md) - Despliegue producción
- [training/README.md](training/README.md) - Guía de entrenamiento

## ✅ Checklist de Validación

- [ ] `make docker-build` ejecuta sin errores
- [ ] `make docker-up` levanta 3 servicios (backend, frontend, mlflow)
- [ ] http://localhost responde (frontend)
- [ ] http://localhost:8000/health responde (backend)
- [ ] http://localhost:5000 responde (mlflow)
- [ ] `make docker-train` ejecuta entrenamiento
- [ ] MLflow UI muestra experimentos
- [ ] `make docker-logs` muestra logs sin errores críticos

---

**¡Listo para usar!** 🎉

Para más detalles, consulta la documentación completa.
