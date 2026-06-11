"""
SIC Ultra - Script de diagnóstico para localizar el origen de los registros de BNB de 645 y 648
"""

import sys
import os
from sqlalchemy import text

# Añadir el backend al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import VirtualTrade, AgentTrade, Transaction

def diagnose():
    print("⏳ Buscando registros en la base de datos...")
    db = SessionLocal()
    try:
        # 1. Buscar en VirtualTrade
        v_trades = db.query(VirtualTrade).filter(VirtualTrade.price.between(640, 650)).all()
        print(f"🔍 Encontrados en virtual_trades (Práctica): {len(v_trades)} registros.")
        for t in v_trades:
            print(f"   - ID: {t.id} | Simbolo: {t.symbol} | Lado: {t.side} | Precio: {t.price} | Estrategia: {t.strategy} | Creado: {t.created_at}")

        # 2. Buscar en AgentTrade
        a_trades = db.query(AgentTrade).filter(AgentTrade.entry_price.between(640, 650)).all()
        print(f"🔍 Encontrados en agent_trades (IA): {len(a_trades)} registros.")
        for t in a_trades:
            print(f"   - ID: {t.id} | Simbolo: {t.symbol} | Lado: {t.side} | Precio: {t.entry_price} | Creado: {t.created_at}")

        # 3. Buscar en Transaction
        t_trades = db.query(Transaction).filter(Transaction.price.between(640, 650)).all()
        print(f"🔍 Encontrados en transactions (Reales Spot): {len(t_trades)} registros.")
        for t in t_trades:
            print(f"   - ID: {t.id} | Simbolo: {t.symbol} | Lado: {t.side} | Precio: {t.price} | Creado: {t.created_at}")

    except Exception as e:
        print(f"❌ Error al consultar la base de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    diagnose()
