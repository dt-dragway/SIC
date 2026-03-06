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
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import VirtualWallet, VirtualTrade, User

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
    db = SessionLocal()
    
    # Elite 10
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOTUSDT", "MATICUSDT", "DOGEUSDT", "LINKUSDT"]
    
    # 1. Fetch Practice Wallet (User 1 by default for terminal demo)
    user_id = 1
    wallet = db.query(VirtualWallet).filter(VirtualWallet.user_id == user_id).first()
    
    if not wallet:
        logger.error(f"No virtual wallet found for user {user_id}. Please initialize practice mode first.")
        db.close()
        return

    logger.info(f"🛡️ Sentinel CIO conectado a PostgreSQL (Wallet ID: {wallet.id})")

    while True:
        try:
            now = datetime.utcnow()
            session = get_current_session()
            
            # Refresh wallet state from DB
            db.refresh(wallet)
            balances = json.loads(wallet.balances)
            
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
                if coin in balances:
                    total_portfolio_value += balances[coin] * prices[-1]
            
            total_portfolio_value += balances.get("USDT", 0)
            
            # 3. Radar Elite 10
            radar_target = max(market_summary.items(), key=lambda x: x[1]["vol_imbalance"])
            
            # 4. CIO Logic & REAL DB Action
            action = "HOLD"
            justification = "Mercado estable, liquidez en rangos de equilibrio."
            
            # Rule: Kill Switch (5% Drawdown from initial reference $5,787)
            if total_portfolio_value < 5498:
                action = "⚠️ KILL SWITCH ACTIVO"
                justification = f"Drawdown crítico detectado: ${total_portfolio_value:.2f}. Suspendiendo operaciones tácticas."
            
            # Rule: Tactical Trade (Only if RSI extreme and high volume surge)
            elif radar_target[1]["vol_imbalance"] > 3.0 and (radar_target[1]["rsi"] < 25 or radar_target[1]["rsi"] > 75):
                direction = "BUY" if radar_target[1]["rsi"] < 25 else "SELL"
                target_sym = radar_target[0]
                target_asset = target_sym.replace("USDT", "")
                entry_price = radar_target[1]["price"]
                
                # Risk Mgmt: 200 USDT per tactical strike
                qty = 200 / entry_price
                
                # Execute in DB
                if direction == "BUY" and balances.get("USDT", 0) >= 200:
                    balances["USDT"] -= 200
                    balances[target_asset] = balances.get(target_asset, 0) + qty
                    action = f"COMPRA TÁCTICA ({target_sym})"
                    justification = f"Captura de suelo por RSI ({radar_target[1]['rsi']:.1f}) y pico de volumen ({radar_target[1]['vol_imbalance']:.2f}x)."
                elif direction == "SELL" and balances.get(target_asset, 0) > 0:
                    sell_qty = balances[target_asset] # Sell all of that asset for simplicity in sentinel
                    balances["USDT"] += sell_qty * entry_price
                    del balances[target_asset]
                    action = f"VENTA TÁCTICA ({target_sym})"
                    justification = f"Toma de ganancias/Venta por agotamiento (RSI: {radar_target[1]['rsi']:.1f})."
                
                if action != "HOLD":
                    # Commit and Record Trade
                    wallet.balances = json.dumps(balances)
                    new_trade = VirtualTrade(
                        wallet_id=wallet.id,
                        symbol=target_sym,
                        side=direction,
                        type="MARKET",
                        strategy="SENTINEL_CIO",
                        reason=justification,
                        quantity=qty if direction == "BUY" else sell_qty,
                        price=entry_price,
                        pnl=0 # Sentinel trades are atomic
                    )
                    db.add(new_trade)
                    db.commit()
                    logger.success(f"🎯 Acción Ejecutada en DB: {action}")

            # 5. Output LOG DE VANGUARDIA
            print(f"\n🕒 [{now.strftime('%H:%M:%S')} UTC] | Sesión: {session} | [🔵 DB SYNC ACTIVE]", flush=True)
            print(f"💼 Portafolio Real-Time: [Valor: ${total_portfolio_value:,.2f} USD | {balances.get('USDT', 0):.2f} USDT]", flush=True)
            print(f"📡 Radar: {radar_target[0]} ({radar_target[1]['vol_imbalance']:.2f}x imbalance)", flush=True)
            print(f"🎯 Decisión CIO: {action}", flush=True)
            print(f"📉 Lógica: {justification}", flush=True)
            
            await asyncio.sleep(60) # Watchdog interval
            
        except Exception as e:
            logger.error(f"Sentinel Loop Error: {e}")
            db.rollback()
            await asyncio.sleep(10)

if __name__ == "__main__":
    print("🚀 Iniciando Protocolo CENTINELA OMNIPRESENTE (DB-Sync Mode)...", flush=True)
    asyncio.run(run_sentinel_cio())

