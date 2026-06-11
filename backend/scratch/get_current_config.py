"""
SIC Ultra - Obtener Configuración Actual del Bot
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import AutomationConfig

def get_config():
    db = SessionLocal()
    try:
        config = db.query(AutomationConfig).filter(AutomationConfig.user_id == 1).first()
        if config:
            print("⚙️ Configuración actual del bot IA 24/7 en DB:")
            print(f"  - Tamaño Máximo de Posición: ${config.max_position_size} USD")
            print(f"  - Confianza Mínima de Señal: {config.min_signal_confidence}%")
            print(f"  - Límite de Trades Diarios: {config.max_daily_trades}")
            print(f"  - Nivel de Riesgo: {config.risk_level.upper()}")
            print(f"  - Modo Práctica Únicamente: {config.practice_mode_only}")
            print(f"  - Tiers de Señal Permitidos: {config.allowed_tiers}")
            print(f"  - Pausar en Alta Volatilidad: {config.pause_on_high_volatility}")
            print(f"  - Intervalo de Revisión: {config.check_interval_seconds} segundos")
            print(f"  - Estado de Persistencia (Enabled): {config.enabled}")
        else:
            print("⚠️ No se encontró configuración de automatización para el usuario 1.")
    except Exception as e:
        print(f"❌ Error al consultar configuración: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    get_config()
