#!/bin/bash
# Configuración completa de PostgreSQL para SIC Ultra
# Con memoria persistente PERMANENTE del agente IA

echo "=========================================="
echo "🐘 Configuración PostgreSQL - SIC Ultra"
echo "=========================================="
echo ""

# 1. Resetear password del usuario (por si ya existe)
echo "📋 Paso 1: Configurando usuario sic_user"
sudo -u postgres psql << EOF
-- Resetear password del usuario
ALTER USER sic_user WITH PASSWORD 'cb4490d4eb268a88cf242aaad441189f';
\q
EOF

# 2. Crear base de datos
echo ""
echo "📋 Paso 2: Creando base de datos sic_db"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS sic_db;" 2>/dev/null
sudo -u postgres psql -c "CREATE DATABASE sic_db OWNER sic_user;"

# 3. Otorgar privilegios
echo ""
echo "📋 Paso 3: Otorgando privilegios"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sic_db TO sic_user;"

# 4. Configurar permisos en schema public
echo ""
echo "📋 Paso 4: Configurando schema"
sudo -u postgres psql -d sic_db << EOF
GRANT ALL ON SCHEMA public TO sic_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO sic_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO sic_user;
\q
EOF

echo ""
echo "✅ Base de datos configurada correctamente"
echo ""
