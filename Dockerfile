# Fase 4 — Docker: imagen para la API FastAPI y para entrenamiento/MLFlow
# Python 3.12+ según plan; el proyecto usa >=3.13 en pyproject.toml
FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias del sistema que pueden necesitar opencv/DeepFace (opcional, reducir si no se usa reconocimiento facial)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar definición de dependencias e instalar (sin dev)
COPY pyproject.toml ./
RUN pip install --no-cache-dir ".[ml]"

# Copiar código de la aplicación
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY training/ ./training/

# Resolver imports tipo "backend.app" desde la raíz del proyecto
ENV PYTHONPATH=/app

# Directorio para SQLite y para MLFlow/mlruns si se montan después
RUN mkdir -p backend/app/db

EXPOSE 8000

# Por defecto arranca la API; para MLFlow o entrenamiento se sobrescribe en docker-compose
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
