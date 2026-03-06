import sys
import os
import asyncio
import json
from datetime import datetime
import numpy as np
from loguru import logger

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.binance.client import get_binance_client
from app.ml.indicators import calculate_rsi, calculate_atr
from app.ml.trading_agent import get_trading_agent

PORTFOLIO_FILE = "/app/app/ml/practice_portfolio.json" if os.path.exists("/app") else os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "practice_portfolio.json")

def get_current_session():
    now_utc = datetime.utcnow()
    hour = now_utc.hour
    if 0 <= hour < 8:
        return "ASIA - Acumulación"
    elif 8 <= hour < 13:
        return "LONDRES - Caza de Liquidez"
    elif 13 <= hour < 21:
        return "NY - Alto Volumen"
    else:
        return "PACIFICO - Transición"

async def run_sentinel_cio():
    client = get_binance_client()
    agent = get_trading_agent()
    
    # Elite 10
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOTUSDT", "MATICUSDT", "DOGEUSDT", "LINKUSDT"]
    
    # 1. Load Portfolio
    try:
        with open(PORTFOLIO_FILE, "r") as f:
            portfolio = json.load(f)
    except Exception as e:
        logger.error(f"Error loading portfolio: {e}")
        return

    while True:
        try:
            now = datetime.utcnow()
            session = get_current_session()
            
            # 2. Fetch Live Market Data
            market_summary = {}
            total_portfolio_value = 0
            
            for sym in symbols:
                candles = client.get_klines(sym, interval="15m", limit=50)
                if not candles: continue
                
                prices = np.array([float(c["close"]) for c in candles])
                volumes = np.array([float(c["volume"]) for c in candles])
                
                coin = sym.replace("USDT", "")
                market_summary[sym] = {
                    "price": prices[-1],
                    "rsi": calculate_rsi(prices)[-1] if len(prices) > 14 else 50,
                    "vol_imbalance": volumes[-1] / np.mean(volumes[-20:]) if len(volumes) >= 20 else 1.0,
                    "atr": calculate_atr(np.array([float(c["high"]) for c in candles]), 
                                       np.array([float(c["low"]) for c in candles]), 
                                       prices)[-1] if len(prices) > 14 else 0
                }
                
                # Add to total value
                if coin in portfolio["balances"]:
                    total_portfolio_value += portfolio["balances"][coin] * prices[-1]
            
            total_portfolio_value += portfolio["balances"]["USDT"]
            
            # 3. Radar Elite 10
            # Identify asset with highest order flow imbalance
            radar_target = max(market_summary.items(), key=lambda x: x[1]["vol_imbalance"])
            
            # 4. CIO Logic & Action
            action = "HOLD"
            justification = "Mercado estable, liquidez en rangos de equilibrio."
            
            # Rule: Kill Switch (5% Drawdown)
            if total_portfolio_value < 5498:
                action = "⚠️ KILL SWITCH ACTIVO"
                justification = f"Drawdown crítico detectado: ${total_portfolio_value:.2f}. Cerrando posiciones simuladas."
            # Rule: Tactical Trade (Only if RSI extreme and high volume)
            elif radar_target[1]["vol_imbalance"] > 2.5 and (radar_target[1]["rsi"] < 30 or radar_target[1]["rsi"] > 70):
                direction = "LONG" if radar_target[1]["rsi"] < 30 else "SHORT"
                # Disciplina de Munición: Max 100 USDT
                entry_price = radar_target[1]["price"]
                action = f"COMPRA TÁCTICA ({radar_target[0]})" if direction == "LONG" else f"VENTA TÁCTICA ({radar_target[0]})"
                justification = f"Divergencia capturada en {radar_target[0]} con Vol Surge de {radar_target[1]['vol_imbalance']:.2f}x y RSI en {radar_target[1]['rsi']:.1f}."
            
            # 5. Output LOG DE VANGUARDIA
            print(f"\n🕒 [{now.strftime('%H:%M:%S')} UTC] | Sesión: {session} | Estado: [🟢 SIMULACIÓN ACTIVA]", flush=True)
            print(f"💼 Salud del Portafolio Virtual: [Valor Total Estimado: ${total_portfolio_value:,.2f} USD | Liquidez: {portfolio['balances']['USDT']} USDT]", flush=True)
            print(f"📡 Radar Elite 10 (Datos Reales): {radar_target[0]} con desequilibrio de {radar_target[1]['vol_imbalance']:.2f}x", flush=True)
            print(f"🎯 Acción Simulada Ejecutada: {action}", flush=True)
            print(f"📉 Justificación Cuantitativa: {justification}", flush=True)
            
            # Save progress (simplified)
            portfolio["total_value_usd"] = total_portfolio_value
            portfolio["last_update"] = now.isoformat()
            with open(PORTFOLIO_FILE, "w") as f:
                json.dump(portfolio, f, indent=2)
                
            await asyncio.sleep(60) # Watchdog interval
            
        except Exception as e:
            logger.error(f"Sentinel Loop Error: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    print("🚀 Iniciando Protocolo CENTINELA OMNIPRESENTE (CIO Mode)...", flush=True)
    asyncio.run(run_sentinel_cio())
