"""
Script de inicialización de Base de Datos para SIC Ultra.
Crea todas las tablas definidas en los modelos si no existen.
"""
import sys
import os

# Agregar directorio actual al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import engine
from app.infrastructure.database.models import Base

def init_db():
    print("🚀 Inicializando base de datos PostgreSQL...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas correctamente.")
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        print("Asegúrate de que PostgreSQL esté corriendo: docker-compose up -d postgres")

if __name__ == "__main__":
    init_db()
