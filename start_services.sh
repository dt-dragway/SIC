#!/bin/bash

# start_services.sh
# Script de inicio manual para evadir problemas con docker-compose

echo "🚀 Iniciando servicios del Sistema SIC..."

# 1. Crear volúmenes si no existen
echo "📦 Verificando volúmenes..."
docker volume create postgres_data > /dev/null 2>&1
docker volume create redis_data > /dev/null 2>&1

# 2. Limpiar contenedores viejos
echo "🧹 Limpiando contenedores anteriores..."
docker stop sic_postgres sic_redis > /dev/null 2>&1
docker rm sic_postgres sic_redis > /dev/null 2>&1

# 3. Cargar variables de entorno
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "❌ Error: No se encuentra el archivo .env"
    exit 1
fi

# 4. Iniciar Redis
echo "🔴 Iniciando Redis..."
docker run -d \
  --name sic_redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:7-alpine

# 5. Iniciar Postgres
echo "🐘 Iniciando PostgreSQL..."
docker run -d \
  --name sic_postgres \
  -p 5432:5432 \
  -e POSTGRES_USER="$POSTGRES_USER" \
  -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
  -e POSTGRES_DB="$POSTGRES_DB" \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:16-alpine

echo "⏳ Esperando a que la base de datos esté lista (5s)..."
sleep 5

# 6. Iniciar Backend
echo "🐍 Iniciando Backend (Uvicorn)..."
echo "   -> http://localhost:8000"
echo "   (Presiona Ctrl+C para detener)"

cd backend
# Asegurar que el venv se usa
if [ -f "venv/bin/uvicorn" ]; then
    ./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    echo "❌ Error: No se encuentra uvicorn en backend/venv/bin/"
    echo "Intenta instalar dependencias primero."
    exit 1
fi
