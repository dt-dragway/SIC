import sys
import os
import asyncio
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def scan_elite_6():
    from app.infrastructure.binance.client import get_binance_client
    from app.ml.indicators import calculate_rsi, calculate_atr
    
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
    client = get_binance_client()
    
    market_data = {}
    
    # 1. Fetch data
    for sym in symbols:
        candles = client.get_klines(sym, interval="15m", limit=100)
        if not candles:
            continue
            
        closes = np.array([c["close"] for c in candles])
        volumes = np.array([c["volume"] for c in candles])
        highs = np.array([c["high"] for c in candles])
        lows = np.array([c["low"] for c in candles])
        
        rsi = calculate_rsi(closes)
        atr = calculate_atr(highs, lows, closes)
        
        market_data[sym] = {
            "closes": closes,
            "volumes": volumes,
            "rsi": rsi[-1] if rsi else 50,
            "atr": atr[-1] if atr else 0,
            "current_price": closes[-1],
            "vol_avg": np.mean(volumes[-20:]),
            "vol_curr": volumes[-1]
        }
        
    if not market_data or "BTCUSDT" not in market_data:
        print("Fallo de red o no BTCUSDT.")
        return
        
    btc_returns = np.diff(market_data["BTCUSDT"]["closes"]) / market_data["BTCUSDT"]["closes"][:-1]
    
    print("\n--- INFORME DE MICROESTRUCTURA (ELITE 6) ---")
    
    best_candidate = None
    best_score = -999
    
    for sym in symbols:
        if sym not in market_data: continue
        d = market_data[sym]
        ret = np.diff(d["closes"]) / d["closes"][:-1]
        
        # Correlación con BTC
        if sym != "BTCUSDT":
            # Ensure lengths match in case of missing candles (they should match if limit=100)
            min_len = min(len(ret), len(btc_returns))
            corr = np.corrcoef(ret[-min_len:], btc_returns[-min_len:])[0, 1]
        else:
            corr = 1.0
            
        # Fuerza Relativa vs BTC (retorno acumulado último periodo)
        rs = (d["closes"][-1] / d["closes"][-20]) - (market_data["BTCUSDT"]["closes"][-1] / market_data["BTCUSDT"]["closes"][-20])
        
        # Imbalance de liquidez (abs)
        imbalance = d["vol_curr"] / d["vol_avg"] if d["vol_avg"] > 0 else 1
        
        print(f"[{sym}] Precio: {d['current_price']:.4f} | RSI: {d['rsi']:.1f} | Corr(BTC): {corr:.2f} | RS(20): {rs*100:.2f}% | Vol Surge: {imbalance:.2f}x")
        
        score = 0
        if imbalance > 2.0: score += 5
        if rs > 0.01: score += 3 # Fuerte > 1% outperformance
        if d['rsi'] < 30 or d['rsi'] > 70: score += 2
        
        if score > best_score:
            best_score = score
            best_candidate = sym
            
    print(f"\nTarget Lock Propuesto: {best_candidate} (Score: {best_score})")
    
if __name__ == "__main__":
    asyncio.run(scan_elite_6())
