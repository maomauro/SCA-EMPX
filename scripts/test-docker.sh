#!/bin/bash
# Script para probar la configuración Docker localmente

set -e

echo "🧪 Probando configuración Docker de SCA-EMPX"
echo "=============================================="

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 1. Verificar Docker instalado
echo ""
echo "1. Verificando Docker..."
if command -v docker &> /dev/null; then
    print_success "Docker instalado: $(docker --version)"
else
    print_error "Docker no está instalado"
    exit 1
fi

# 2. Verificar Docker Compose
echo ""
echo "2. Verificando Docker Compose..."
if command -v docker-compose &> /dev/null; then
    print_success "Docker Compose instalado: $(docker-compose --version)"
else
    print_error "Docker Compose no está instalado"
    exit 1
fi

# 3. Verificar archivo .env
echo ""
echo "3. Verificando archivo .env..."
if [ -f ".env" ]; then
    print_success "Archivo .env encontrado"
else
    print_warning "Archivo .env no encontrado. Copiando desde .env.docker..."
    cp .env.docker .env
    print_success "Archivo .env creado"
fi

# 4. Construir imágenes
echo ""
echo "4. Construyendo imágenes Docker..."
if docker-compose build; then
    print_success "Imágenes construidas exitosamente"
else
    print_error "Error al construir imágenes"
    exit 1
fi

# 5. Levantar contenedores
echo ""
echo "5. Levantando contenedores..."
if docker-compose up -d; then
    print_success "Contenedores levantados"
else
    print_error "Error al levantar contenedores"
    exit 1
fi

# 6. Esperar a que los servicios estén listos
echo ""
echo "6. Esperando a que los servicios estén listos..."
sleep 10

# 7. Verificar estado de contenedores
echo ""
echo "7. Verificando estado de contenedores..."
if docker-compose ps | grep -q "Up"; then
    print_success "Contenedores en ejecución"
    docker-compose ps
else
    print_error "Algunos contenedores no están corriendo"
    docker-compose ps
    exit 1
fi

# 8. Probar health check del backend
echo ""
echo "8. Probando health check del backend..."
sleep 5
if curl -f http://localhost:8000/health &> /dev/null; then
    print_success "Backend respondiendo correctamente"
else
    print_error "Backend no responde"
    echo "Logs del backend:"
    docker-compose logs backend
    exit 1
fi

# 9. Probar health check del frontend
echo ""
echo "9. Probando health check del frontend..."
if curl -f http://localhost/health &> /dev/null; then
    print_success "Frontend respondiendo correctamente"
else
    print_error "Frontend no responde"
    echo "Logs del frontend:"
    docker-compose logs frontend
    exit 1
fi

# 10. Probar endpoint de la API
echo ""
echo "10. Probando endpoint de la API..."
if curl -f http://localhost:8000/ &> /dev/null; then
    print_success "API respondiendo correctamente"
    curl http://localhost:8000/
else
    print_error "API no responde"
    exit 1
fi

# 11. Verificar volúmenes
echo ""
echo "11. Verificando volúmenes..."
if docker volume ls | grep -q "sca-sqlite-data"; then
    print_success "Volumen de SQLite creado"
else
    print_warning "Volumen de SQLite no encontrado"
fi

# 12. Verificar red
echo ""
echo "12. Verificando red..."
if docker network ls | grep -q "sca-network"; then
    print_success "Red Docker creada"
else
    print_warning "Red Docker no encontrada"
fi

# Resumen
echo ""
echo "=============================================="
echo -e "${GREEN}✓ Todas las pruebas pasaron exitosamente${NC}"
echo ""
echo "Accede a la aplicación en:"
echo "  - Frontend: http://localhost"
echo "  - Backend: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "Para ver logs: docker-compose logs -f"
echo "Para detener: docker-compose down"
echo "=============================================="
