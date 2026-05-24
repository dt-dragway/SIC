import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import User, VirtualWallet, VirtualTrade

def debug_wallet():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@sic.com").first()
        if not user:
            print("❌ Usuario admin@sic.com no encontrado en la base de datos.")
            return

        print(f"👤 Usuario: {user.name} ({user.email}), ID: {user.id}")
        
        wallet = db.query(VirtualWallet).filter(VirtualWallet.user_id == user.id).first()
        if not wallet:
            print("❌ Billetera virtual no encontrada para este usuario.")
            return

        print("\n💼 Detalles de Billetera Virtual:")
        print(f"  - ID Billetera: {wallet.id}")
        print(f"  - Capital Inicial: ${wallet.initial_capital}")
        print(f"  - Balances JSON: {wallet.balances}")
        
        # Intentar parsear el balance
        try:
            balances = json.loads(wallet.balances) if wallet.balances else {}
            print("  - Balances Parseados:")
            for asset, amount in balances.items():
                print(f"    * {asset}: {amount}")
        except Exception as e:
            print(f"  - ❌ Error parseando balances JSON: {e}")

        trades = db.query(VirtualTrade).filter(VirtualTrade.wallet_id == wallet.id).all()
        print(f"\n📦 Cantidad de trades virtuales en DB: {len(trades)}")
        for idx, t in enumerate(trades[:10]):
            print(f"  {idx+1}. [{t.created_at}] {t.side} {t.symbol} | Cantidad: {t.quantity} | Precio: ${t.price} | PNL: ${t.pnl} | Estrategia: {t.strategy}")
            if t.reason:
                print(f"     Motivo: {t.reason}")

    finally:
        db.close()

if __name__ == "__main__":
    debug_wallet()
