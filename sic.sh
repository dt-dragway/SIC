#!/bin/bash
# SIC Ultra - Control Dashboard
# Este script levanta el backend, frontend, bases de datos (en Docker) y workers para MODO DEV.

# Colores para UI de terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Directorio del proyecto
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Validar que estemos en el directorio correcto
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: Este script debe ejecutarse desde la raíz del proyecto SIC.${NC}"
    exit 1
fi

mkdir -p logs

function show_help() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${CYAN}🚀 SIC Ultra - Control Dashboard (Dev Mode) 🚀${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo -e "Uso: ./sic.sh [comando]"
    echo -e ""
    echo -e "Comandos Disponibles:"
    echo -e "  ${YELLOW}dev${NC}       - Inicia en modo interactivo (se apaga automáticamente al cerrar la ventana)"
    echo -e "  ${GREEN}start${NC}     - Inicia todos los servicios (Bases de datos, Backend, Frontend, Sentinel)"
    echo -e "  ${RED}stop${NC}      - Detiene todos los servicios y contenedores"
    echo -e "  ${YELLOW}restart${NC}   - Detiene y vuelve a iniciar todos los servicios"
    echo -e "  ${CYAN}status${NC}    - Muestra el estado de los procesos y servicios"
    echo -e "  ${BLUE}logs${NC}      - Permite ver los logs en vivo (uso: ./sic.sh logs [backend|frontend|sentinel|all])"
    echo -e "  ${YELLOW}diagnose${NC}  - Ejecuta pruebas de conexión y endpoints rápidos"
    echo -e ""
}

function check_env() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️ No se encontró archivo .env. Copiando de .env.example...${NC}"
        if [ -f ".env.example" ]; then
            cp .env.example .env
        elif [ -f ".env.template" ]; then
            cp .env.template .env
        else
            echo -e "${RED}❌ Error fatal: No existe .env y no se encontraron plantillas.${NC}"
            exit 1
        fi
        echo -e "${GREEN}✅ Archivo .env generado. Asegúrate de configurarlo si es necesario.${NC}"
    fi
    # Cargar variables para el script (ignorando comentarios)
    export $(grep -v '^#' .env | xargs)
}

function start_services() {
    echo -e "${CYAN}=== Iniciando Sistema SIC (Modo Dev con Recarga Automática) ===${NC}\n"
    check_env

    # 1. Docker y Bases de Datos
    echo -e "${BLUE}📦 Preparando Bases de Datos (Docker)...${NC}"
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Error: Docker no está instalado o no está en el PATH.${NC}"
        exit 1
    fi
    
    docker volume create postgres_data > /dev/null 2>&1
    docker volume create redis_data > /dev/null 2>&1
    
    # Detener anteriores si existieran
    docker stop sic_postgres sic_redis > /dev/null 2>&1 || true
    docker rm sic_postgres sic_redis > /dev/null 2>&1 || true

    echo -e "   🐘 Iniciando PostgreSQL en puerto 5433..."
    docker run -d --name sic_postgres \
      -p 5433:5432 \
      -e POSTGRES_USER="${POSTGRES_USER:-postgres}" \
      -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-admin2425}" \
      -e POSTGRES_DB="${POSTGRES_DB:-sic_db}" \
      -v postgres_data:/var/lib/postgresql/data \
      postgres:16-alpine > /dev/null

    echo -e "   🔴 Iniciando Redis en puerto 6379..."
    docker run -d --name sic_redis \
      -p 6379:6379 \
      -v redis_data:/data \
      redis:7-alpine > /dev/null

    echo -e "   ⏳ Esperando a que las bases de datos estén listas (5s)..."
    sleep 5

    # 2. Ollama
    echo -e "\n${BLUE}🦙 Verificando Ollama...${NC}"
    if ! pgrep -x "ollama" > /dev/null; then
        echo -e "   Iniciando servidor de Ollama en background..."
        nohup ollama serve > logs/ollama.log 2>&1 &
    else
        echo -e "   ✅ Ollama ya está corriendo."
    fi

    # 3. Inicialización / Migración de DB (si es necesario)
    echo -e "\n${BLUE}⚙️  Verificando/Creando tablas de la Base de Datos...${NC}"
    cd backend
    if [ ! -d "venv" ]; then
        echo -e "   Creando entorno virtual de Python..."
        python3 -m venv venv
    fi
    source venv/bin/activate
    
    # Instalamos dependencias si uvicorn no existe
    if [ ! -f "venv/bin/uvicorn" ]; then
        echo -e "   Instalando dependencias de Python..."
        pip install -r requirements.txt > /dev/null
    fi

    # Script rápido para sincronizar DB usando SQLAlchemy
    python3 << EOF
import sys
try:
    from app.infrastructure.database.models import Base
    from app.infrastructure.database.session import engine
    Base.metadata.create_all(engine)
    print("   ✅ Tablas sincronizadas en PostgreSQL.")
except Exception as e:
    print(f"   ⚠️ Error sincronizando DB: {e}")
EOF
    cd ..

    # 4. Iniciar Backend
    echo -e "\n${BLUE}🐍 Iniciando Backend FastAPI...${NC}"
    cd backend
    source venv/bin/activate
    # Iniciamos en background y redirigimos output a log
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 > ../logs/backend.log 2>&1 < /dev/null &
    BACKEND_PID=$!
    echo -e "   ✅ Backend (Uvicorn) en ejecución (PID: $BACKEND_PID, Puerto: 8001)"
    cd ..

    # 5. Iniciar Sentinel Worker
    echo -e "\n${BLUE}🛡️  Iniciando Sentinel Worker (Watchdog 24/7)...${NC}"
    cd backend
    source venv/bin/activate
    export PYTHONPATH="$(pwd)"
    nohup python -m app.workers.sentinel > ../logs/sentinel.log 2>&1 < /dev/null &
    SENTINEL_PID=$!
    echo -e "   ✅ Sentinel Worker en ejecución (PID: $SENTINEL_PID)"
    cd ..

    # 6. Iniciar Frontend
    echo -e "\n${BLUE}⚛️  Iniciando Frontend Next.js...${NC}"
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo -e "   Instalando dependencias de Node.js..."
        npm install > /dev/null 2>&1
    fi
    # El package.json ya define: "dev": "next dev -p 3001"
    nohup npm run dev > ../logs/frontend.log 2>&1 < /dev/null &
    FRONTEND_PID=$!
    echo -e "   ✅ Frontend (Next.js) en ejecución (PID: $FRONTEND_PID, Puerto: 3001)"
    cd ..

    echo -e "\n${GREEN}====================================================${NC}"
    echo -e "${GREEN}✅ SISTEMA SIC INICIADO EXITOSAMENTE${NC}"
    echo -e "${GREEN}====================================================${NC}"
    echo -e "🌐 Frontend App:     ${CYAN}http://localhost:3001${NC}"
    echo -e "📡 Backend API:      ${CYAN}http://localhost:8001${NC}"
    echo -e "📖 Documentación API:${CYAN}http://localhost:8001/docs${NC}"
    echo -e "🐘 PostgreSQL:       ${CYAN}localhost:5433${NC}"
    echo -e "🔴 Redis Cache:      ${CYAN}localhost:6379${NC}"
    echo -e "\nPara ver logs en tiempo real: ${YELLOW}./sic.sh logs all${NC}"
}

function stop_services() {
    echo -e "${RED}🛑 Deteniendo todos los servicios de SIC...${NC}\n"
    
    # Frontend
    echo -e "Deteniendo Next.js (Frontend)..."
    pkill -f "next dev" || true
    pkill -f "next-server" || true
    fuser -k 3001/tcp > /dev/null 2>&1 || true

    # Backend
    echo -e "Deteniendo Uvicorn (Backend)..."
    pkill -f "uvicorn app.main:app" || true
    fuser -k 8001/tcp > /dev/null 2>&1 || true

    # Sentinel
    echo -e "Deteniendo Sentinel Worker..."
    pkill -f "python -m app.workers.sentinel" || true

    # Docker
    echo -e "Deteniendo contenedores Docker (Postgres/Redis)..."
    docker stop sic_postgres sic_redis > /dev/null 2>&1 || true
    docker rm sic_postgres sic_redis > /dev/null 2>&1 || true

    echo -e "\n${GREEN}✅ Todo detenido y sistema limpio.${NC}"
}

function status_services() {
    echo -e "${CYAN}📊 Estado del Sistema SIC${NC}\n"

    # PostgreSQL
    if docker ps --format '{{.Names}}' | grep -q "^sic_postgres$"; then
        echo -e "🐘 PostgreSQL: ${GREEN}🟢 ONLINE${NC} (Docker, 5433)"
    else
        echo -e "🐘 PostgreSQL: ${RED}🔴 OFFLINE${NC}"
    fi

    # Redis
    if docker ps --format '{{.Names}}' | grep -q "^sic_redis$"; then
        echo -e "🔴 Redis:      ${GREEN}🟢 ONLINE${NC} (Docker, 6379)"
    else
        echo -e "🔴 Redis:      ${RED}🔴 OFFLINE${NC}"
    fi

    # Ollama
    if pgrep -x "ollama" > /dev/null; then
        echo -e "🦙 Ollama:     ${GREEN}🟢 ONLINE${NC} (Local)"
    else
        echo -e "🦙 Ollama:     ${RED}🔴 OFFLINE${NC}"
    fi

    # Backend
    if pgrep -f "uvicorn app.main:app" > /dev/null; then
        PID=$(pgrep -f "uvicorn app.main:app" | head -n 1)
        echo -e "🐍 Backend:    ${GREEN}🟢 ONLINE${NC} (PID: $PID, Puerto: 8001)"
    else
        echo -e "🐍 Backend:    ${RED}🔴 OFFLINE${NC}"
    fi

    # Frontend
    if pgrep -f "next dev" > /dev/null || pgrep -f "next-server" > /dev/null; then
        PID=$(pgrep -f "next dev" | head -n 1 || pgrep -f "next-server" | head -n 1)
        echo -e "⚛️  Frontend:   ${GREEN}🟢 ONLINE${NC} (PID: $PID, Puerto: 3001)"
    else
        echo -e "⚛️  Frontend:   ${RED}🔴 OFFLINE${NC}"
    fi

    # Sentinel Worker
    if pgrep -f "python -m app.workers.sentinel" > /dev/null; then
        PID=$(pgrep -f "python -m app.workers.sentinel" | head -n 1)
        echo -e "🛡️  Sentinel:   ${GREEN}🟢 ONLINE${NC} (PID: $PID)"
    else
        echo -e "🛡️  Sentinel:   ${RED}🔴 OFFLINE${NC}"
    fi
    echo ""
}

function show_logs() {
    local target=$1
    echo -e "${BLUE}📖 Leyendo logs en vivo... (Ctrl+C para salir)${NC}"
    
    if [ "$target" == "backend" ]; then
        tail -f logs/backend.log
    elif [ "$target" == "frontend" ]; then
        tail -f logs/frontend.log
    elif [ "$target" == "sentinel" ]; then
        tail -f logs/sentinel.log
    elif [ "$target" == "all" ]; then
        tail -f logs/backend.log logs/frontend.log logs/sentinel.log
    else
        echo -e "${RED}Opción no válida.${NC} Usa: ./sic.sh logs [backend|frontend|sentinel|all]"
    fi
}

function diagnose_system() {
    echo -e "${CYAN}🔍 Diagnóstico de SIC...${NC}\n"
    
    # Endpoint Health Backend
    echo -e "1. Backend Health Check (Puerto 8001):"
    if curl -s -f http://localhost:8001/health > /dev/null; then
        RESPONSE=$(curl -s http://localhost:8001/health)
        echo -e "   ${GREEN}✅ Responde OK:${NC} $RESPONSE"
    else
        echo -e "   ${RED}❌ Backend no responde.${NC}"
    fi
    
    # Endpoint Frontend 
    echo -e "\n2. Frontend Availability (Puerto 3001):"
    if curl -s -f http://localhost:3001 > /dev/null; then
         echo -e "   ${GREEN}✅ Frontend Responde OK${NC}"
    else
         echo -e "   ${RED}❌ Frontend no responde.${NC}"
    fi

    echo -e "\n3. Docker Containers:"
    docker ps | grep sic_ || echo -e "   ${YELLOW}Sin contenedores activos.${NC}"
    echo ""
}

function dev_mode() {
    start_services
    echo -e "\n${YELLOW}====================================================${NC}"
    echo -e "${YELLOW}Mantén esta ventana abierta para mantener el sistema encendido.${NC}"
    echo -e "${RED}Cierra esta ventana (o presiona ENTER aquí) para APAGAR TODO.${NC}"
    echo -e "${YELLOW}====================================================${NC}"
    
    # Capturar el cierre de la terminal o Ctrl+C para apagar limpio
    trap stop_services EXIT SIGINT SIGTERM
    
    read -p ""
}

case "$1" in
    dev)
        dev_mode
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        ;;
    status)
        status_services
        ;;
    logs)
        if [ -z "$2" ]; then
            echo -e "${RED}Falta especificar el log.${NC}"
            echo "Uso: ./sic.sh logs [backend|frontend|sentinel|all]"
        else
            show_logs "$2"
        fi
        ;;
    diagnose)
        diagnose_system
        ;;
    *)
        show_help
        ;;
esac
