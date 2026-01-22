"""
SIC Ultra - Database Session
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Crear motor de base de datos
engine = create_engine(settings.database_url)

# Crear fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependencia para obtener sesión de base de datos.
    Cierra la sesión automáticamente al terminar el request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
