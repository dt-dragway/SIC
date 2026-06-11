import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import engine
from sqlalchemy import text

def alter_database():
    print("🔧 Iniciando migración robusta de base de datos local...")
    
    sqls = [
        "ALTER TABLE virtual_trades ADD COLUMN IF NOT EXISTS market_type VARCHAR(20) DEFAULT 'SPOT';",
        "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS market_type VARCHAR(20) DEFAULT 'SPOT';",
        "ALTER TABLE automation_configs ADD COLUMN IF NOT EXISTS spot_enabled BOOLEAN DEFAULT TRUE;",
        "ALTER TABLE automation_configs ADD COLUMN IF NOT EXISTS futures_enabled BOOLEAN DEFAULT TRUE;"
    ]
    
    # Intentar ejecutar cada ALTER con timeout para evitar colgarse si hay locks activos
    for sql in sqls:
        success = False
        attempts = 0
        max_attempts = 15
        
        while not success and attempts < max_attempts:
            attempts += 1
            try:
                with engine.connect() as conn:
                    # Configurar lock_timeout de 1.5 segundos para no colgar el script
                    conn.execute(text("SET lock_timeout = 1500;"))
                    print(f"🚀 [Intento {attempts}] Ejecutando: {sql}")
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"✅ Éxito al ejecutar: {sql}")
                    success = True
            except Exception as e:
                if "timeout" in str(e).lower() or "lock" in str(e).lower() or "blocked" in str(e).lower():
                    print(f"⚠️ [Bloqueo detectado] Esperando a que se libere la tabla para reintentar (esperando 2s)...")
                    time.sleep(2)
                else:
                    print(f"❌ Error crítico no recuperable: {e}")
                    sys.exit(1)
        
        if not success:
            print(f"❌ Fallo al adquirir el lock exclusivo tras {max_attempts} intentos. Por favor, asegúrate de que elSentinel o Uvicorn no estén bloqueando la tabla.")
            sys.exit(1)

    print("🎉 ¡Base de datos migrada exitosamente al 100%!")

if __name__ == "__main__":
    alter_database()
