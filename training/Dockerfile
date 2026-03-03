# Dockerfile para servicio de entrenamiento
FROM python:3.13-slim

# Variables de build
ARG APP_VERSION=latest
ARG BUILD_DATE
ARG VCS_REF

# Metadata
LABEL maintainer="STI S.A.S." \
      version="${APP_VERSION}" \
      description="SCA-EMPX Training Service" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    mv /root/.local/bin/uvx /usr/local/bin/uvx

# Copiar archivos de dependencias
COPY pyproject.toml ./

# Instalar dependencias con uv
RUN uv pip install --system --no-cache -r pyproject.toml

# Copiar código necesario
COPY training/ ./training/
COPY backend/app/ml/ ./backend/app/ml/

# Crear directorios para datos y checkpoints
RUN mkdir -p /app/data /app/training/checkpoints

# Usuario no-root
RUN useradd -m -u 1000 trainuser && \
    chown -R trainuser:trainuser /app
USER trainuser

# Comando por defecto
CMD ["python", "training/train_classifier.py", \
     "--mlflow-uri", "http://mlflow:5000", \
     "--epochs", "3"]
