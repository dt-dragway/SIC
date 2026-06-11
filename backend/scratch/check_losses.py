"""
SIC Ultra - Listar Todos los Trades para Auditoría Completa
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import VirtualTrade, AgentTrade

def check_all_trades():
    db = SessionLocal()
    try:
        print("🔍 Listando TODOS los trades en la base de datos para auditoría completa...")
        
        # 1. Todos los trades virtuales
        v_trades = db.query(VirtualTrade).order_by(VirtualTrade.created_at.desc()).all()
        print(f"\n📋 Historial de Trades Virtuales (VirtualTrade): {len(v_trades)}")
        for vt in v_trades:
            print(f"  - [{vt.created_at.strftime('%Y-%m-%d %H:%M')}] {vt.symbol} {vt.side} | Cantidad: {vt.quantity} | Entrada: ${vt.price} | PnL: ${vt.pnl} | Estrategia: {vt.strategy} | Razón: {vt.reason}")
            
        # 2. Todos los trades del Agente
        a_trades = db.query(AgentTrade).order_by(AgentTrade.created_at.desc()).all()
        print(f"\n📋 Historial de Trades del Agente IA (AgentTrade): {len(a_trades)}")
        for at in a_trades:
            print(f"  - [{at.created_at.strftime('%Y-%m-%d %H:%M')}] {at.symbol} {at.side} | Entrada: ${at.entry_price} | Salida: ${at.exit_price} | PnL: ${at.pnl} | Señales: {at.signals_used}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_all_trades()
