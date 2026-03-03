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
COPY frontend/src/*.html /usr/share/nginx/html/
COPY frontend/src/static /usr/share/nginx/html/static

# Copiar configuración de nginx
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Health check - verificar que nginx esté corriendo
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD pgrep nginx || exit 1

# Nginx se ejecuta como usuario nginx por defecto
CMD ["nginx", "-g", "daemon off;"]
