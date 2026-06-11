
import sys
import os
from datetime import datetime, timedelta
import random

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import P2PRate, Signal

def populate_data():
    db = SessionLocal()
    try:
        print("📊 Generando datos históricos de prueba...")
        
        # 1. P2P Rates (últimas 24 horas, cada 15 min)
        if db.query(P2PRate).count() == 0:
            print("   -> Generando historial P2P...")
            base_price = 45.0
            for i in range(96): # 24h * 4
                time = datetime.utcnow() - timedelta(minutes=15 * (96 - i))
                variation = random.uniform(-0.5, 0.5)
                buy_price = base_price + variation
                sell_price = buy_price * 1.02 # 2% spread
                
                rate = P2PRate(
                    avg_buy_price=buy_price,
                    avg_sell_price=sell_price,
                    best_buy_price=buy_price - 0.1,
                    best_sell_price=sell_price + 0.1,
                    spread_percent=2.0,
                    offers_count=random.randint(20, 50),
                    volume=random.uniform(1000, 5000),
                    recorded_at=time
                )
                db.add(rate)
            print("   ✅ P2P Rates generados.")
        else:
            print("   ⚠️  Ya existen datos P2P.")

        # 2. Señales IA Recientes
        if db.query(Signal).count() == 0:
            print("   -> Generando señales de prueba...")
            symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
            for i in range(10):
                symbol = random.choice(symbols)
                price = 70000 if symbol == "BTCUSDT" else 3500 if symbol == "ETHUSDT" else 150
                is_long = random.choice([True, False])
                
                sig = Signal(
                    symbol=symbol,
                    type="LONG" if is_long else "SHORT",
                    strength="STRONG" if random.random() > 0.5 else "MODERATE",
                    confidence=random.uniform(70, 95),
                    entry_price=price,
                    take_profit=price * 1.05 if is_long else price * 0.95,
                    stop_loss=price * 0.98 if is_long else price * 1.02,
                    risk_reward=2.5,
                    reasoning='["Tendencia fuerte", "RSI en zona óptima", "Alineación MTF"]',
                    ml_data='{"patterns": ["Hammer", "Engulfing"], "indicators": ["RSI", "MACD"]}',
                    created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
                    expires_at=datetime.utcnow() + timedelta(hours=2),
                    result=random.choice(["WIN", "LOSS", "PENDING"])
                )
                db.add(sig)
            print("   ✅ Señales generadas.")

        # 3. Whale Alerts (Últimas 24h)
        from app.infrastructure.database.institutional_models import WhaleAlert
        if db.query(WhaleAlert).count() == 0:
            print("   -> Generando alertas de ballenas...")
            blockchains = ["BTC", "ETH", "SOL", "BNB"]
            flow_types = ["exchange_inflow", "exchange_outflow", "whale_to_whale"]
            
            for _ in range(30):
                blockchain = random.choice(blockchains)
                flow = random.choice(flow_types)
                sentiment = "bullish" if flow == "exchange_outflow" else "bearish" if flow == "exchange_inflow" else "neutral"
                
                whale = WhaleAlert(
                    blockchain=blockchain,
                    tx_hash=f"0x{random.getrandbits(256):064x}",
                    amount=random.uniform(100, 1000),
                    amount_usd=random.uniform(5000000, 50000000),
                    from_label="Binance Hot Wallet" if flow == "exchange_outflow" else "Whale Wallet",
                    to_label="Whale Wallet" if flow == "exchange_outflow" else "Binance Hot Wallet",
                    flow_type=flow,
                    sentiment=sentiment,
                    timestamp=datetime.utcnow() - timedelta(minutes=random.randint(5, 1440))
                )
                db.add(whale)
            print("   ✅ Whale Alerts generados.")
        
        db.commit()
        print("✨ Proceso completado exitosamente.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_data()
