# Migración de Docker Monolítico a Multi-Contenedor

## Cambios Realizados

### ❌ Deprecado
- `Dockerfile` (raíz) → Renombrado a `Dockerfile.deprecated`
  - Era un contenedor monolítico que incluía API + Training + MLflow
  - No seguía las mejores prácticas de separación de concerns

### ✅ Nueva Arquitectura

#### 1. Backend (API + ML)
- **Dockerfile**: `backend/Dockerfile`
- **Propósito**: API FastAPI + Reconocimiento facial
- **Puerto**: 8000
- **Imagen**: `sca-empx-backend`

#### 2. Frontend (Nginx)
- **Dockerfile**: `frontend/Dockerfile`
- **Propósito**: Servir estáticos + Proxy reverso
- **Puerto**: 80
- **Imagen**: `sca-empx-frontend`

#### 3. MLflow (Tracking Server) ⭐ NUEVO
- **Dockerfile**: `mlflow/Dockerfile`
- **Propósito**: Servidor de tracking para experimentos ML
- **Puerto**: 5000
- **Imagen**: `sca-empx-mlflow`
- **Volúmenes**:
  - `mlflow-data`: Almacena runs y métricas
  - `mlflow-artifacts`: Almacena modelos y artefactos

#### 4. Training (Servicio bajo demanda) ⭐ NUEVO
- **Dockerfile**: `training/Dockerfile`
- **Propósito**: Entrenamiento de modelos (MNIST classifier)
- **Imagen**: `sca-empx-train`
- **Uso**: No se levanta con `docker-compose up`, solo con `docker-compose run`
- **Volúmenes**:
  - `training-data`: Dataset MNIST
  - `training-checkpoints`: Checkpoints del modelo

## Arquitectura Actualizada

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │ :80
       ▼
┌─────────────┐
│  Frontend   │  Nginx
│   (Nginx)   │  
└──────┬──────┘
       │ :8000
       ▼
┌─────────────┐      ┌─────────────┐
│   Backend   │─────▶│   MLflow    │
│  (FastAPI)  │      │  (Tracking) │
└──────┬──────┘      └─────────────┘
       │                    ▲ :5000
       ▼                    │
┌─────────────┐             │
│   SQLite    │      ┌──────┴──────┐
│  (Volume)   │      │   Training  │
└─────────────┘      │  (On-demand)│
                     └─────────────┘
```

## Comandos Actualizados

### Levantar servicios principales
```bash
# Backend + Frontend + MLflow
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver MLflow UI
# Abrir: http://localhost:5000
```

### Ejecutar entrenamiento
```bash
# Entrenamiento con parámetros por defecto (3 épocas)
docker-compose run --rm train

# Entrenamiento personalizado
docker-compose run --rm train --epochs 5 --batch-size 256

# Con configuración JSON
docker-compose run --rm train --config training/config_default.json

# Con Comet ML (requiere API key en .env)
docker-compose run --rm -e COMET_API_KEY=tu_api_key train
```

### Comandos Make actualizados
```bash
make docker-train              # Entrenamiento por defecto
make docker-train-custom ARGS="--epochs 5"  # Personalizado
make docker-logs-mlflow        # Ver logs de MLflow
```

## Variables de Entorno Nuevas

Agregar a `.env`:

```bash
# MLflow
MLFLOW_PORT=5000
MLFLOW_TRACKING_URI=http://mlflow:5000

# Comet ML (opcional)
COMET_API_KEY=tu_api_key_aqui
COMET_PROJECT_NAME=sca-empx-mnist
```

## Volúmenes Nuevos

```bash
# Ver volúmenes
docker volume ls | grep sca

# Volúmenes creados:
sca-mlflow-data           # Runs y métricas de MLflow
sca-mlflow-artifacts      # Modelos y artefactos
sca-training-data         # Dataset MNIST
sca-training-checkpoints  # Checkpoints del modelo
```

## Backup de Datos ML

### Backup de MLflow
```bash
# Backup de runs
docker run --rm -v sca-mlflow-data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/mlflow-runs-$(date +%Y%m%d).tar.gz -C /data .

# Backup de artifacts
docker run --rm -v sca-mlflow-artifacts:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/mlflow-artifacts-$(date +%Y%m%d).tar.gz -C /data .
```

### Backup de checkpoints
```bash
docker run --rm -v sca-training-checkpoints:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/training-checkpoints-$(date +%Y%m%d).tar.gz -C /data .
```

## Integración con GitLab CI/CD

El pipeline `.gitlab-ci.yml` ya está actualizado para construir las 4 imágenes:
- `sca-empx-backend`
- `sca-empx-frontend`
- `sca-empx-mlflow`
- `sca-empx-train`

### Variables adicionales en GitLab

Agregar en Settings > CI/CD > Variables:

```
COMET_API_KEY           # API key de Comet ML (opcional)
MLFLOW_TRACKING_URI     # URI del servidor MLflow (producción)
```

## Workflow de Desarrollo ML

### 1. Desarrollo local
```bash
# Levantar infraestructura
docker-compose up -d

# Verificar MLflow
curl http://localhost:5000/health

# Ejecutar entrenamiento
docker-compose run --rm train --epochs 3

# Ver resultados en MLflow UI
# http://localhost:5000
```

### 2. Experimentación
```bash
# Probar diferentes hiperparámetros
docker-compose run --rm train --epochs 5 --batch-size 128 --lr 0.001
docker-compose run --rm train --epochs 10 --batch-size 256 --lr 0.0001

# Comparar en MLflow UI
```

### 3. Producción
```bash
# En servidor de producción
docker-compose pull
docker-compose up -d

# Ejecutar entrenamiento programado (cron)
0 2 * * * cd /opt/sca-empx && docker-compose run --rm train --config training/config_prod.json
```

## Troubleshooting

### MLflow no inicia
```bash
# Ver logs
docker-compose logs mlflow

# Verificar volúmenes
docker volume inspect sca-mlflow-data

# Recrear contenedor
docker-compose up -d --force-recreate mlflow
```

### Training falla
```bash
# Ver logs detallados
docker-compose run --rm train --epochs 1

# Verificar conectividad con MLflow
docker-compose run --rm train python -c "import mlflow; print(mlflow.get_tracking_uri())"

# Verificar volúmenes
docker volume inspect sca-training-data
```

### Backend no conecta con MLflow
```bash
# Verificar variable de entorno
docker-compose config | grep MLFLOW_TRACKING_URI

# Probar conectividad
docker exec sca-backend ping mlflow
```

## Ventajas de la Nueva Arquitectura

### ✅ Separación de Concerns
- Cada servicio tiene su propósito específico
- Fácil escalar servicios independientemente

### ✅ Desarrollo Independiente
- Cambios en training no afectan la API
- MLflow puede actualizarse sin tocar backend

### ✅ Recursos Optimizados
- Training solo corre cuando se necesita
- MLflow siempre disponible para consultas

### ✅ Seguridad
- Cada contenedor con usuario no-root
- Volúmenes aislados por servicio

### ✅ Mantenibilidad
- Dockerfiles más simples y enfocados
- Fácil debugging por servicio

## Próximos Pasos

1. ✅ Probar localmente: `make docker-build && make docker-up`
2. ✅ Ejecutar entrenamiento: `make docker-train`
3. ✅ Verificar MLflow UI: http://localhost:5000
4. ⏳ Configurar Comet ML (opcional)
5. ⏳ Actualizar CI/CD con nuevas imágenes
6. ⏳ Documentar flujo de experimentación ML

## Limpieza

### Eliminar configuración antigua
```bash
# El Dockerfile.deprecated puede eliminarse después de validar
rm Dockerfile.deprecated

# Limpiar imágenes antiguas
docker image prune -a
```

### Limpiar volúmenes de prueba
```bash
# ¡CUIDADO! Esto elimina todos los datos
docker-compose down -v
```

---

**Migración completada** ✅

La arquitectura multi-contenedor está lista para desarrollo y producción.
