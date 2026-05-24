import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import engine

def alter_schema():
    print("🔧 Iniciando actualización de esquema de base de datos...")
    
    # SQL para agregar la columna avg_price si no existe
    sql = "ALTER TABLE algorithmic_orders ADD COLUMN IF NOT EXISTS avg_price DOUBLE PRECISION NULL;"
    
    try:
        with engine.connect() as conn:
            # Ejecutar consulta SQL
            from sqlalchemy import text
            print("🚀 Ejecutando ALTER TABLE en base de datos...")
            conn.execute(text(sql))
            conn.commit()
            print("✅ Columna 'avg_price' agregada exitosamente a la tabla 'algorithmic_orders' (o ya existía).")
            
    except Exception as e:
        print(f"❌ Error al actualizar el esquema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    alter_schema()
