# Nginx para servir archivos estáticos y proxy reverso
FROM nginx:1.25-alpine

# Variables de build
ARG APP_VERSION=latest
ARG BUILD_DATE
ARG VCS_REF

# Metadata
LABEL maintainer="STI S.A.S." \
      version="${APP_VERSION}" \
      description="SCA-EMPX Frontend - Interfaz Web" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}"

# Copiar archivos estáticos
COPY backend/app/static /usr/share/nginx/html

# Copiar configuración de nginx
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Nginx se ejecuta como usuario nginx por defecto
CMD ["nginx", "-g", "daemon off;"]
