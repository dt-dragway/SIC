#!/bin/bash

echo "🛑 Deteniendo todos los servicios..."

# Kill Node (Frontend)
pkill -f "next-server" || true
pkill -f "next dev" || true
fuser -k 3000/tcp || true
fuser -k 3001/tcp || true

# Kill Python/Uvicorn (Backend)
pkill -f "uvicorn" || true
fuser -k 8000/tcp || true

# Stop Docker Containers
docker stop sic_postgres sic_redis || true
docker rm sic_postgres sic_redis || true

echo "✅ Todo detenido. Sistema limpio."
