import sys
import os

# Raíz en el path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import engine
from app.infrastructure.database.models import Base

def migrate():
    print("🔌 Conectando a PostgreSQL sic_db...")
    try:
        # Esto creará solo las tablas faltantes (en este caso, virtual_positions)
        Base.metadata.create_all(bind=engine)
        print("✅ Migración exitosa: La tabla `virtual_positions` ha sido creada en la base de datos.")
    except Exception as e:
        print(f"❌ Error creando la tabla: {e}")

if __name__ == "__main__":
    migrate()
