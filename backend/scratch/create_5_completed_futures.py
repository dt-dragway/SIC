import sys
from datetime import datetime, timedelta
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import VirtualWallet, VirtualTrade

def seed_futures():
    db = SessionLocal()
    try:
        # Buscar la primera wallet
        wallet = db.query(VirtualWallet).first()
        if not wallet:
            print("❌ No se encontró ninguna wallet virtual. Ejecuta primero un depósito o reset en la UI.")
            return

        print(f"🎯 Agregando 5 operaciones de futuros cerradas a la wallet ID: {wallet.id}")

        trades_data = [
            {
                "symbol": "BTCUSDT",
                "side": "SELL", # Cierre de un LONG
                "type": "MARKET",
                "strategy": "AI_AUTO",
                "reason": "Cierre automático de Contrato Futuro LONG 10x (Precio entrada: $67250, Precio salida: $68450)",
                "quantity": 0.015,
                "price": 68450.0,
                "pnl": 18.00,
                "market_type": "FUTURES",
                "offset_minutes": 10
            },
            {
                "symbol": "ETHUSDT",
                "side": "BUY", # Cierre de un SHORT
                "type": "MARKET",
                "strategy": "AI_AUTO",
                "reason": "Cierre automático de Contrato Futuro SHORT 20x (Precio entrada: $3480, Precio salida: $3410)",
                "quantity": 0.25,
                "price": 3410.0,
                "pnl": 17.50,
                "market_type": "FUTURES",
                "offset_minutes": 8
            },
            {
                "symbol": "SOLUSDT",
                "side": "SELL", # Cierre de LONG
                "type": "MARKET",
                "strategy": "AI_AUTO",
                "reason": "Cierre automático de Contrato Futuro LONG 5x (Precio entrada: $142.5, Precio salida: $145.8)",
                "quantity": 2.5,
                "price": 145.8,
                "pnl": 8.25,
                "market_type": "FUTURES",
                "offset_minutes": 6
            },
            {
                "symbol": "LINKUSDT",
                "side": "BUY", # Cierre de SHORT
                "type": "MARKET",
                "strategy": "AI_AUTO",
                "reason": "Cierre automático de Contrato Futuro SHORT 10x (Precio entrada: $15.40, Precio salida: $14.90)",
                "quantity": 10.0,
                "price": 14.90,
                "pnl": 5.00,
                "market_type": "FUTURES",
                "offset_minutes": 4
            },
            {
                "symbol": "BNBUSDT",
                "side": "SELL", # Cierre de LONG
                "type": "MARKET",
                "strategy": "AI_AUTO",
                "reason": "Cierre automático de Contrato Futuro LONG 15x (Precio entrada: $578.0, Precio salida: $588.5)",
                "quantity": 0.8,
                "price": 588.5,
                "pnl": 8.40,
                "market_type": "FUTURES",
                "offset_minutes": 2
            }
        ]

        now = datetime.utcnow()
        for idx, t in enumerate(trades_data):
            trade = VirtualTrade(
                wallet_id=wallet.id,
                symbol=t["symbol"],
                side=t["side"],
                type=t["type"],
                strategy=t["strategy"],
                reason=t["reason"],
                quantity=t["quantity"],
                price=t["price"],
                pnl=t["pnl"],
                market_type=t["market_type"],
                created_at=now - timedelta(minutes=t["offset_minutes"])
            )
            db.add(trade)
        
        db.commit()
        print("✅ ¡5 operaciones de futuros cerradas agregadas con éxito total!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error en seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_futures()
