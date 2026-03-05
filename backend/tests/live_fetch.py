import sys
import os
import asyncio
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def run():
    from app.infrastructure.binance.client import get_binance_client
    from app.ml.indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_atr
    
    client = get_binance_client()
    # Let's get 15m candles for shorter term action
    candles = client.get_klines("BTCUSDT", interval="15m", limit=100)
    
    if not candles:
        print("No candles fetched")
        return
        
    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    volumes = [c["volume"] for c in candles]
    
    rsi = calculate_rsi(closes)
    macd = calculate_macd(closes)
    bollinger = calculate_bollinger_bands(closes)
    atr = calculate_atr(highs, lows, closes)
    
    data = {
        "symbol": "BTCUSDT",
        "current_price": closes[-1],
        "rsi": rsi[-1] if rsi else None,
        "macd_hist": macd.get("histogram", [None])[-1] if macd else None,
        "bollinger_lower": bollinger.get("lower", [None])[-1] if bollinger else None,
        "bollinger_upper": bollinger.get("upper", [None])[-1] if bollinger else None,
        "atr": atr[-1] if atr else None,
        "volume_curr": volumes[-1],
        "volume_avg": sum(volumes[-20:]) / 20 if len(volumes) >= 20 else None
    }
    
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    asyncio.run(run())
