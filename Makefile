# Makefile para SCA-EMPX
# Facilita comandos comunes de desarrollo y despliegue

.PHONY: help install test lint run docker-build docker-up docker-down docker-logs clean

# Variables
PYTHON := python
UV := uv
DOCKER_COMPOSE := docker-compose
APP_VERSION ?= latest
DOCKER_USERNAME ?= your-dockerhub-username

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias con uv
	$(UV) venv
	$(UV) pip install -r pyproject.toml
	$(UV) pip install pytest pytest-cov pytest-asyncio httpx ruff

test: ## Ejecutar tests unitarios
	$(PYTHON) -m pytest backend/tests/ -v --cov=backend --cov-report=term --cov-report=html

test-verbose: ## Ejecutar tests con salida detallada
	$(PYTHON) -m pytest backend/tests/ -vv --cov=backend --cov-report=term-missing

lint: ## Ejecutar linter (ruff)
	ruff check backend/

lint-fix: ## Ejecutar linter y auto-corregir
	ruff check backend/ --fix

format: ## Formatear código con ruff
	ruff format backend/

run: ## Ejecutar aplicación en modo desarrollo
	$(PYTHON) main.py

run-prod: ## Ejecutar aplicación en modo producción
	$(PYTHON) -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

init-db: ## Inicializar base de datos
	$(PYTHON) scripts/init_db.py

docker-build: ## Construir imágenes Docker
	@echo "Building Docker images..."
	export BUILD_DATE=$$(date -u +'%Y-%m-%dT%H:%M:%SZ') && \
	export VCS_REF=$$(git rev-parse --short HEAD 2>/dev/null || echo "unknown") && \
	$(DOCKER_COMPOSE) build \
		--build-arg APP_VERSION=$(APP_VERSION) \
		--build-arg BUILD_DATE=$$BUILD_DATE \
		--build-arg VCS_REF=$$VCS_REF

docker-up: ## Levantar contenedores
	$(DOCKER_COMPOSE) up -d

docker-down: ## Detener contenedores
	$(DOCKER_COMPOSE) down

docker-restart: ## Reiniciar contenedores
	$(DOCKER_COMPOSE) restart

docker-logs: ## Ver logs de contenedores
	$(DOCKER_COMPOSE) logs -f

docker-logs-backend: ## Ver logs del backend
	$(DOCKER_COMPOSE) logs -f backend

docker-logs-frontend: ## Ver logs del frontend
	$(DOCKER_COMPOSE) logs -f frontend

docker-ps: ## Ver estado de contenedores
	$(DOCKER_COMPOSE) ps

docker-clean: ## Limpiar contenedores, imágenes y volúmenes
	$(DOCKER_COMPOSE) down -v --rmi local

docker-push: ## Subir imágenes a Docker Hub
	docker tag sca-empx-backend:latest $(DOCKER_USERNAME)/sca-empx-backend:$(APP_VERSION)
	docker tag sca-empx-frontend:latest $(DOCKER_USERNAME)/sca-empx-frontend:$(APP_VERSION)
	docker push $(DOCKER_USERNAME)/sca-empx-backend:$(APP_VERSION)
	docker push $(DOCKER_USERNAME)/sca-empx-frontend:$(APP_VERSION)

docker-pull: ## Descargar imágenes desde Docker Hub
	docker pull $(DOCKER_USERNAME)/sca-empx-backend:$(APP_VERSION)
	docker pull $(DOCKER_USERNAME)/sca-empx-frontend:$(APP_VERSION)

clean: ## Limpiar archivos temporales
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache htmlcov .ruff_cache

clean-db: ## Limpiar base de datos (¡CUIDADO!)
	rm -f backend/app/db/*.db

backup-db: ## Hacer backup de la base de datos
	@mkdir -p backups
	@cp backend/app/db/sqlite.db backups/sqlite_$$(date +%Y%m%d_%H%M%S).db
	@echo "Backup creado en backups/"

dev-setup: install init-db ## Setup completo para desarrollo
	@echo "Entorno de desarrollo configurado"

prod-deploy: docker-build docker-push ## Build y push para producción
	@echo "Imágenes construidas y subidas a Docker Hub"
