"""
SIC Ultra - Ver historial reciente de VirtualTrades para validar la inyección
"""

import sys
import os

# Añadir el backend al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import VirtualTrade

def show_trades():
    print("⏳ Consultando trades de práctica recientes...")
    db = SessionLocal()
    try:
        trades = db.query(VirtualTrade).order_by(VirtualTrade.created_at.desc()).limit(5).all()
        if not trades:
            print("📭 No hay trades registrados recientemente.")
            return
            
        print(f"📈 Encontrados {len(trades)} trades de práctica recientes:")
        for t in trades:
            print(f"   - ID: {t.id} | Símbolo: {t.symbol} | Tipo: {t.side} | Precio: ${t.price} | Cantidad: {t.quantity} | Estrategia: {t.strategy} | Razón: {t.reason} | Fecha: {t.created_at}")
    except Exception as e:
        print(f"❌ Error al consultar la base de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    show_trades()
