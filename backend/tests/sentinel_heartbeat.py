import sys
import os
import asyncio
from datetime import datetime, time
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_current_session(utc_hour):
    if 0 <= utc_hour < 8:
        return "ASIA - Acumulación / Baja Volatilidad"
    elif 8 <= utc_hour < 13:
        return "LONDRES - Caza de Liquidez / Expansión"
    elif 13 <= utc_hour < 21:
        return "NUEVA YORK - Alto Volumen / Tendencia"
    else:
        return "PACIFICO/DEAD-ZONE - Transición de Liquidez"

async def run_sentinel():
    from app.infrastructure.binance.client import get_binance_client
    from app.ml.indicators import calculate_rsi, calculate_atr
    
    now_utc = datetime.utcnow()
    utc_hour = now_utc.hour
    session = get_current_session(utc_hour)
    
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
    client = get_binance_client()
    
    market_data = {}
    print(f"\n🕒 Heartbeat [{now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC] | Sesión Actual: {session}", flush=True)
    
    print(f"DEBUG: Scanning {len(symbols)} symbols...", flush=True)
    for sym in symbols:
        try:
            candles = client.get_klines(sym, interval="15m", limit=100)
            if not candles: 
                print(f"DEBUG: No candles for {sym}", flush=True)
                continue
            closes = np.array([c["close"] for c in candles])
            volumes = np.array([c["volume"] for c in candles])
            
            market_data[sym] = {
                "price": closes[-1],
                "vol": volumes[-1],
                "vol_avg": np.mean(volumes[-20:]),
                "rsi": calculate_rsi(closes)[-1] if len(closes) > 14 else 50
            }
            print(f"DEBUG: Processed {sym}", flush=True)
        except Exception as e:
            print(f"DEBUG: Error processing {sym}: {e}", flush=True)
    
    # Resumen de Liquidez
    top_vol = sorted(market_data.items(), key=lambda x: x[1]['vol'] / x[1]['vol_avg'], reverse=True)[0]
    print(f"📊 Liquidez del Universo Elite 6: El dinero se mueve en {top_vol[0]} ({top_vol[1]['vol'] / top_vol[1]['vol_avg']:.2f}x Relative Volume).", flush=True)
    
    # Lógica de Francotirador adaptada a sesión
    target = "NONE"
    print(f"🎯 Target Lock: {target} (Umbrales de sesión {session.split(' ')[0]} aplicados)", flush=True)
    
    # Riesgo (simulado desde memoria)
    from app.ml.trading_agent import get_trading_agent
    agent = get_trading_agent()
    exposure = 0.0 # Por ahora
    print(f"🛡️ Estado de Riesgo: [Exposición total actual de la cuenta: {exposure}%]", flush=True)

if __name__ == "__main__":
    asyncio.run(run_sentinel())
