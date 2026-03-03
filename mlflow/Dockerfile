# Dockerfile para MLflow Tracking Server
FROM python:3.13-slim

# Variables de build
ARG APP_VERSION=latest
ARG BUILD_DATE
ARG VCS_REF

# Metadata
LABEL maintainer="STI S.A.S." \
      version="${APP_VERSION}" \
      description="SCA-EMPX MLflow Tracking Server" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}"

WORKDIR /app

# Instalar MLflow y dependencias
RUN pip install --no-cache-dir \
    mlflow==3.10.0 \
    psycopg2-binary \
    boto3

# Crear directorios para artifacts y mlruns
RUN mkdir -p /app/mlruns /app/mlartifacts

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Comando por defecto
CMD ["mlflow", "server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--backend-store-uri", "file:///app/mlruns", \
     "--default-artifact-root", "file:///app/mlartifacts"]
