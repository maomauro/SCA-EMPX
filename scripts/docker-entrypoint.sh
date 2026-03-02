#!/bin/bash
# Entrypoint script para inicialización del backend

set -e

echo "🚀 Iniciando SCA-EMPX Backend..."

# Verificar si la base de datos existe, si no, inicializarla
if [ ! -f "/app/backend/app/db/sqlite.db" ]; then
    echo "📦 Base de datos no encontrada. Inicializando..."
    python scripts/init_db.py
    echo "✅ Base de datos inicializada"
else
    echo "✅ Base de datos encontrada"
fi

# Ejecutar migraciones si existen
if [ -d "/app/backend/app/db/migrations" ]; then
    echo "🔄 Verificando migraciones..."
    # Aquí puedes agregar lógica de migraciones si usas Alembic
fi

echo "🎯 Iniciando servidor..."
exec "$@"
