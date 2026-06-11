#!/bin/bash
# Script de Inicialización de PostgreSQL para SIC Ultra
# Ejecutar DESPUÉS de instalar PostgreSQL

set -e

echo "=========================================="
echo "🐘 Configuración de PostgreSQL - SIC Ultra"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuración desde .env
DB_USER="sic_user"
DB_NAME="sic_db"
DB_PASSWORD="sic2024secure"  # Cambiar por el password del .env

echo "📋 Paso 1: Crear usuario de base de datos"
echo "----------------------------------------"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "⚠️  Usuario ya existe"

echo ""
echo "📋 Paso 2: Crear base de datos"
echo "----------------------------------------"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || echo "⚠️  Base de datos ya existe"

echo ""
echo "📋 Paso 3: Otorgar privilegios"
echo "----------------------------------------"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo ""
echo "📋 Paso 4: Crear extensiones"
echo "----------------------------------------"
sudo -u postgres psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

echo ""
echo "📋 Paso 5: Crear tablas"
echo "----------------------------------------"
cd "$(dirname "$0")/backend"
source venv/bin/activate

python << EOF
from app.infrastructure.database.models import Base
from app.infrastructure.database.session import engine

print("Creando todas las tablas...")
Base.metadata.create_all(engine)
print("✅ Tablas creadas exitosamente")

# Listar tablas creadas
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"\n📊 Tablas creadas ({len(tables)}):")
for table in tables:
    print(f"   • {table}")
EOF

echo ""
echo "=========================================="
echo "✅ PostgreSQL configurado exitosamente"
echo "=========================================="
echo ""
echo "📌 Información de conexión:"
echo "   Host: localhost"
echo "   Puerto: 5432"
echo "   Base de datos: $DB_NAME"
echo "   Usuario: $DB_USER"
echo ""
echo "🔄 Próximo paso: Reiniciar el backend"
echo "   cd backend"
echo "   uvicorn app.main:app --reload"
echo ""
