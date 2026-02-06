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
from app.middleware.rate_limit import rate_limit_middleware
from app.middleware.security_headers import security_headers_middleware


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
    
    # Auto-crear cuenta admin si no existe
    try:
        from app.infrastructure.database.session import SessionLocal
        from app.infrastructure.database.models import User, VirtualWallet
        # from passlib.context import CryptContext  # REMOVED: Broken with new bcrypt
        from app.api.v1.auth import hash_password # FIXED: Use uniform hashing function
        import json
        
        # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # REMOVED
        db = SessionLocal()
        
        try:
            # Buscar admin existente
            admin = db.query(User).filter(User.email == settings.admin_email).first()
            
            if not admin:
                # Crear usuario admin
                admin = User(
                    email=settings.admin_email,
                    password_hash=hash_password(settings.admin_password),
                    name="Administrator" # FIXED: Required field
                )
                db.add(admin)
                db.commit()
                db.refresh(admin)
                logger.success(f"👤 Usuario admin creado: {settings.admin_email}")
            else:
                # Actualizar contraseña si cambió
                admin.password_hash = hash_password(settings.admin_password) # FIXED
                db.commit()
                logger.info(f"👤 Usuario admin existente: {settings.admin_email}")
            
            # Auto-crear wallet virtual con fondos de prueba
            wallet = db.query(VirtualWallet).filter(VirtualWallet.user_id == admin.id).first()
            
            if not wallet:
                # Crear wallet con criptos de prueba
                initial_balances = {
                    "USDT": 1000.0,
                    "BTC": 0.01,
                    "ETH": 0.5,
                    "BNB": 0.1,      # Añadido: usado en señales
                    "SOL": 10.0,
                    "XRP": 500.0,
                    "ADA": 1000.0,
                    "DOT": 100.0,
                    "MATIC": 100.0,  # Añadido: usado en señales
                    "DOGE": 5000.0,
                    "LINK": 50.0
                }
                wallet = VirtualWallet(
                    user_id=admin.id,
                    balances=json.dumps(initial_balances),
                    initial_capital=5000.0
                )
                db.add(wallet)
                db.commit()
                logger.success(f"💰 Wallet de práctica creada para admin con fondos de prueba")
            
            db.close()
        except Exception as e:
            logger.warning(f"⚠️ Error creando admin: {e}")
            db.close()
    except Exception as e:
        logger.warning(f"⚠️ No se pudo crear usuario admin: {e}")
    
    # Iniciar Escáner de Mercado Institucional
    try:
        from app.services.market_scanner import get_market_scanner
        scanner = get_market_scanner()
        await scanner.start()
        logger.success("📡 Escáner de Mercado Institucional activado")
    except Exception as e:
        logger.error(f"❌ No se pudo iniciar el escáner de mercado: {e}")

    logger.success("✅ SIC Ultra iniciado correctamente")
    
    yield  # App running
    
    # === SHUTDOWN ===
    logger.info("🛑 Cerrando SIC Ultra...")
    
    # Guardar memoria del agente IA (Persistencia)
    try:
        from app.ml.trading_agent import get_trading_agent
        agent = get_trading_agent()
        agent.memory.save()
        logger.success("✅ Memoria de IA guardada en disco")
    except Exception as e:
        logger.error(f"❌ Error guardando memoria de IA: {e}")
        
    # Detener Escáner de Mercado
    try:
        from app.services.market_scanner import get_market_scanner
        scanner = get_market_scanner()
        await scanner.stop()
    except:
        pass

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


# CORS - Configuración segura
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# En producción, cambiar a dominio real
if settings.app_env == "production":
    allowed_origins = [
        "https://sic-ultra.com",
        "https://app.sic-ultra.com",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)

# Security Middlewares
try:
    from app.middleware.rate_limit import rate_limit_middleware
    from app.middleware.security_headers import security_headers_middleware
    
    app.middleware("http")(rate_limit_middleware)
    app.middleware("http")(security_headers_middleware)
    logger.info("✅ Security middlewares loaded")
except ImportError as e:
    logger.warning(f"⚠️ Security middlewares not loaded: {e}")


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
