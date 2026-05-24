"""
SIC Ultra - Migración en caliente para añadir columna 'enabled' a 'automation_configs'
"""

import sys
import os
from sqlalchemy import text

# Añadir el backend al path para poder importar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.infrastructure.database.session import engine

def migrate():
    print("⏳ Iniciando migración en caliente...")
    
    # Consulta SQL directa para añadir la columna si no existe
    query = text("ALTER TABLE automation_configs ADD COLUMN IF NOT EXISTS enabled BOOLEAN DEFAULT FALSE;")
    
    try:
        with engine.connect() as connection:
            connection.execute(query)
            # SQLAlchemy requiere un commit explícito si no está en modo autocommit
            connection.commit()
            print("✅ ¡Migración completada con éxito! Columna 'enabled' añadida a 'automation_configs'.")
    except Exception as e:
        print(f"❌ Error al ejecutar la migración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()
