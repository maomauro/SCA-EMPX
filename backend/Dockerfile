# Multi-stage build para optimizar tamaño de imagen
FROM python:3.13-slim as builder

# Variables de build
ARG APP_VERSION=latest
ARG BUILD_DATE
ARG VCS_REF

# Metadata
LABEL maintainer="STI S.A.S." \
      version="${APP_VERSION}" \
      description="SCA-EMPX Backend - Sistema de Control de Acceso" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}"

# Instalar dependencias del sistema necesarias para DeepFace y OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv para gestión de dependencias
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copiar proyecto para instalar con extra [ml] (DeepFace, etc.)
COPY pyproject.toml uv.lock* ./
COPY backend/ ./backend/
COPY main.py ./

# Instalar dependencias base + ML (reconocimiento facial en producción)
RUN uv pip install --system --no-cache ".[ml]"

# Stage final
FROM python:3.13-slim

# Instalar solo las librerías runtime necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar dependencias instaladas desde builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código de la aplicación
COPY backend/ ./backend/
COPY main.py ./

# Crear directorio para la base de datos con permisos
RUN mkdir -p /app/backend/app/db && \
    chmod -R 755 /app/backend/app/db

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBUG=false \
    DATABASE_URL=sqlite:///./backend/app/db/sqlite.db \
    SECRET_KEY=change-me-in-production \
    ALGORITHM=HS256 \
    ACCESS_TOKEN_EXPIRE_MINUTES=60 \
    SIMILARITY_THRESHOLD=0.6

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Usuario no-root para seguridad
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Comando de inicio
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
