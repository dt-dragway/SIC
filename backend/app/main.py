"""
SIC Ultra - FastAPI Main Entry Point

Punto de entrada principal de la aplicación.
Configura middleware, routers y eventos de startup/shutdown.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.config import settings
from app.api.v1 import router as api_v1_router


# Configurar logging con loguru
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.debug else "INFO"
)
logger.add(
    "logs/sic_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Eventos de startup y shutdown.
    Se ejecuta al iniciar y cerrar la aplicación.
    """
    # === STARTUP ===
    logger.info("🚀 Iniciando SIC Ultra...")
    logger.info(f"📊 Entorno: {settings.app_env}")
    logger.info(f"🔗 Database: {settings.database_url.split('@')[-1]}")
    
    # TODO: Conectar a PostgreSQL
    # TODO: Conectar a Redis
    # TODO: Inicializar cliente Binance
    
    logger.success("✅ SIC Ultra iniciado correctamente")
    
    yield  # App running
    
    # === SHUTDOWN ===
    logger.info("🛑 Cerrando SIC Ultra...")
    # TODO: Cerrar conexiones
    logger.info("👋 SIC Ultra cerrado")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description="Sistema Integral Criptofinanciero - Trading Inteligente con IA",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)


# CORS - Permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Montar routers
app.include_router(api_v1_router, prefix="/api/v1")


# === Health Check ===
@app.get("/health", tags=["System"])
async def health_check():
    """
    Verificar que el sistema está funcionando.
    Usado por Docker y load balancers.
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "env": settings.app_env
    }


@app.get("/", tags=["System"])
async def root():
    """Ruta raíz - Información básica"""
    return {
        "message": f"🪙 Bienvenido a {settings.app_name}",
        "docs": "/docs" if settings.debug else "Disabled in production",
        "health": "/health"
    }
