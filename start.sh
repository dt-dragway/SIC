#!/bin/bash

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Iniciando SIC Ultra...${NC}"

# Verificar rutas
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: Debes ejecutar este script desde la carpeta raíz del proyecto (SIC).${NC}"
    exit 1
fi

# 1. Configurar Backend
echo -e "\n${BLUE}🐍 Configurando Backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Instalando dependencias..."
pip install -r requirements.txt > /dev/null 2>&1

# Verificar si se instaló correctamente
if ! python3 -c "import loguru" 2>/dev/null; then
    echo -e "${RED}⚠️ Error instalando dependencias. Intentando instalar loguru manualmente...${NC}"
    pip install loguru fastapi uvicorn sqlalchemy psycopg2-binary redis python-binance passlib pyjwt python-multipart > /dev/null
fi

# Iniciar Backend en segundo plano
echo -e "${GREEN}✅ Backend listo. Iniciando servidor...${NC}"
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# 2. Configurar Frontend
echo -e "\n${BLUE}⚛️ Configurando Frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Instalando dependencias de Node..."
    npm install > /dev/null 2>&1
fi

echo -e "${GREEN}✅ Frontend listo. Iniciando interfaz...${NC}"
echo -e "${BLUE}🌐 Abre tu navegador en: http://localhost:3000${NC}"

# Iniciar Frontend
npm run dev

# Al cerrar frontend, matar backend
kill $BACKEND_PID
