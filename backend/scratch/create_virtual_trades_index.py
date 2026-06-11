"""
SIC Ultra - Migración en caliente para añadir índice compuesto a 'virtual_trades'
"""

import sys
import os
from sqlalchemy import text

# Añadir el backend al path para poder importar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.infrastructure.database.session import engine

def migrate():
    print("⏳ Iniciando migración en caliente para el índice...")
    
    # Crear índice compuesto si no existe
    query = text("CREATE INDEX IF NOT EXISTS idx_virtual_trades_wallet_strategy ON virtual_trades (wallet_id, strategy);")
    
    try:
        with engine.connect() as connection:
            connection.execute(query)
            connection.commit()
            print("✅ ¡Migración completada con éxito! Índice compuesto 'idx_virtual_trades_wallet_strategy' creado en 'virtual_trades'.")
    except Exception as e:
        print(f"❌ Error al ejecutar la migración del índice: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()
