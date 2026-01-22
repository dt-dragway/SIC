"""
Script para crear tablas institucionales en PostgreSQL.
"""

import sys
import os

# Agregar ruta del backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.database.session import engine
from app.infrastructure.database.institutional_models import Base

def create_tables():
    """Crear tablas institucionales"""
    print("🏗️  Creando tablas institucionales...")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente:")
        print("   - order_book_snapshots")
        print("   - whale_alerts")  
        print("   - funding_rate_history")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        raise

if __name__ == "__main__":
    create_tables()
