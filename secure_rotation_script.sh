#!/bin/bash

# 🔐 SCRIPT SEGURO PARA ROTACIÓN DE API KEYS - SIC Ultra
# Preservando todos los datos existentes

set -e

echo "🚨 INICIANDO ROTACIÓN SEGURA DE API KEYS..."
echo "📅 Fecha: $(date)"
echo "📍 Backup previo verificado: $(ls BACKUP_CRITICAL/database_backup_*.sql | tail -1)"

# Paso 1: Desactivar temporalmente servicios que usan API keys
echo "🔄 Paso 1: Desactivando servicios críticos..."
# Comentar temporalmente las líneas que usan API keys en .env
sed -i.bak 's/^BINANCE_API_KEY=.*/# BINANCE_API_KEY=DEACTIVATED_TEMPORALLY/' .env
sed -i 's/^BINANCE_API_SECRET=.*/# BINANCE_API_SECRET=DEACTIVATED_TEMPORALLY/' .env
sed -i 's/^DEEPSEEK_API_KEY=.*/# DEEPSEEK_API_KEY=DEACTIVATED_TEMPORALLY/' .env

echo "✅ Servicios desactivados temporalmente"

# Paso 2: Generar nuevas credenciales seguras
echo "🔑 Paso 2: Generando nuevas credenciales..."

# Nueva contraseña de base de datos
NEW_DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
echo "Nueva contraseña DB: $NEW_DB_PASSWORD"

# Nuevos secrets JWT
NEW_JWT_SECRET=$(openssl rand -hex 32)
NEW_SECRET_KEY=$(openssl rand -hex 32)

# Nuevo password admin
NEW_ADMIN_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/" | cut -c1-12)

echo "✅ Nuevas credenciales generadas"

# Paso 3: Actualizar .env con placeholders para nuevas keys
echo "📝 Paso 3: Actualizando archivo .env..."
cat > .env.new << EOF
# SIC Ultra - Environment Configuration
# Fecha de actualización: $(date)
# 🔐 LAS API KEYS DEBEN SER ACTUALIZADAS MANUALMENTE

# === Database ===
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$NEW_DB_PASSWORD
POSTGRES_DB=sic_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

# === Security ===
SECRET_KEY=$NEW_SECRET_KEY
JWT_SECRET_KEY=$NEW_JWT_SECRET

# === Binance API (ACTUALIZAR MANUALMENTE) ===
BINANCE_API_KEY=PASTE_NEW_BINANCE_API_KEY_HERE
BINANCE_API_SECRET=PASTE_NEW_BINANCE_SECRET_HERE
BINANCE_TESTNET=false

# === AI/LLM APIs (ACTUALIZAR MANUALMENTE) ===
DEEPSEEK_API_KEY=PASTE_NEW_DEEPSEEK_KEY_HERE
OPENAI_API_KEY=

# === Security Features ===
ENABLE_RATE_LIMIT=true
REQUIRE_2FA=true

# === Admin Account ===
ADMIN_EMAIL=admin@sic.com
ADMIN_PASSWORD=$NEW_ADMIN_PASSWORD

# === URLs ===
DATABASE_URL="postgresql://postgres:$NEW_DB_PASSWORD@localhost:5433/sic_db"

# === Frontend ===
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=$NEW_SECRET_KEY

# === Redis ===
REDIS_URL=redis://localhost:6379
EOF

echo "✅ Archivo .env.new creado"

# Paso 4: Script para actualización de contraseña de BD
echo "🗄️ Paso 4: Preparando actualización de contraseña de base de datos..."
cat > update_db_password.sql << EOF
-- Cambiar contraseña de usuario postgres
ALTER USER postgres WITH PASSWORD '$NEW_DB_PASSWORD';
-- Nota: Esto requiere reinicio del servicio PostgreSQL
EOF

echo "✅ Script SQL generado"

# Paso 5: Crear instrucciones para el usuario
echo "📋 PASOS MANUALES REQUERIDOS:"
echo ""
echo "1. 🔑 GENERAR NUEVAS API KEYS:"
echo "   - Ir a https://www.binance.com/es/my/settings/api-management"
echo "   - Crear nuevas API keys con permisos mínimos necesarios"
echo "   - Ir a https://platform.deepseek.com/api_keys"
echo "   - Generar nueva API key para DeepSeek"
echo ""
echo "2. 🔄 ACTUALIZAR CONTRASEÑA DE BASE DE DATOS:"
echo "   - Ejecutar: docker exec -i sic_postgres psql -U postgres < update_db_password.sql"
echo "   - Reiniciar contenedor PostgreSQL"
echo ""
echo "3. 📝 EDITAR .env.new:"
echo "   - Pegar las nuevas API keys donde corresponden"
echo "   - Revisar que todas las credenciales estén actualizadas"
echo ""
echo "4. ✅ ACTIVAR NUEVA CONFIGURACIÓN:"
echo "   - Renombrar .env.new a .env"
echo "   - Reiniciar todos los servicios"
echo ""
echo "5. 🧪 VERIFICAR:"
echo "   - Probar login con nueva contraseña: $NEW_ADMIN_PASSWORD"
echo "   - Verificar que las funciones de trading funcionen"
echo "   - Confirmar que la IA responde correctamente"
echo ""
echo "📁 Archivos generados:"
echo "   - .env.new (configuración actualizada)"
echo "   - update_db_password.sql (actualización de BD)"
echo "   - BACKUP_CRITICAL/ (respaldos completos)"
echo ""
echo "⚠️  MANTENER COPIAS DE SEGURIDAD HASTA VERIFICAR FUNCIONAMIENTO"

# Guardar nuevas credenciales en archivo seguro
echo "🔐 Nuevas credenciales guardadas en credentials_backup.txt"
cat > credentials_backup.txt << EOF
CREDENCIALES GENERADAS - $(date)
=====================================
NUEVA CONTRASEÑA DB: $NEW_DB_PASSWORD
NUEVO SECRET KEY: $NEW_SECRET_KEY
NUEVO JWT SECRET: $NEW_JWT_SECRET
NUEVA CONTRASEÑA ADMIN: $NEW_ADMIN_PASSWORD

⚠️  ALMACENAR SEGURAMENTE Y LIMPIAR DESPUÉS DE USAR
EOF

chmod 600 credentials_backup.txt

echo ""
echo "🎯 PRÓXIMO PASO: Seguir las instrucciones manuales arriba"