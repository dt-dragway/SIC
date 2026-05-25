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
from app.infrastructure.database.models import VirtualWallet, VirtualTrade, User, Transaction, AutomationConfig

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
    
    # Elite 12 - Optimizado para alta volatilidad y volumen
    symbols = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", 
        "LINKUSDT", "DOGEUSDT", "NEARUSDT", "SAGAUSDT", 
        "NILUSDT", "RIFUSDT", "DEXEUSDT"
    ]
    
    # 1. Fetch Practice Wallets
    wallets = db.query(VirtualWallet).all()
    logger.info(f"🛡️ Sentinel CIO conectado a PostgreSQL (Total de Wallets virtuales encontradas: {len(wallets)})")

    # Función auxiliar para guardar logs de auditoría en JSON
    def save_audit_log(log_entry):
        audit_file = "/DATA/Desarrollos  /SIC/backend/app/ml/sentinel_audit_logs.json"
        try:
            import os
            if os.path.exists(audit_file):
                with open(audit_file, "r") as f:
                    logs = json.load(f)
            else:
                logs = []
        except Exception:
            logs = []
        
        logs.insert(0, log_entry)
        logs = logs[:100]  # Mantener los últimos 100
        try:
            with open(audit_file, "w") as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            logger.error(f"Error escribiendo log de auditoría del Sentinel: {e}")

    while True:
        sleep_interval = 60
        try:
            now = datetime.utcnow()
            session = get_current_session()
            
            # 2. Fetch Live Market Data (Una sola vez para todas las wallets por ciclo)
            market_summary = {}
            for sym in symbols:
                candles = client.get_klines(sym, interval="15m", limit=50)
                if not candles: continue
                
                prices = np.array([float(c["close"]) for c in candles])
                volumes = np.array([float(c["volume"]) for c in candles])
                
                market_summary[sym] = {
                    "price": prices[-1],
                    "rsi": calculate_rsi(prices)[-1] if len(prices) > 14 else 50,
                    "vol_imbalance": volumes[-1] / np.mean(volumes[-20:]) if len(volumes) >= 20 else 1.0,
                    "atr": calculate_atr(np.array([float(c["high"]) for c in candles]), 
                                       np.array([float(c["low"]) for c in candles]), 
                                       prices)[-1] if len(prices) > 14 else 0
                }
            
            if not market_summary:
                logger.warning("📡 Radar: No se pudieron obtener datos de mercado (¿API bloqueada o problemas de red?)")
                await asyncio.sleep(sleep_interval)
                continue
                
            radar_target = max(market_summary.items(), key=lambda x: x[1]["vol_imbalance"])
            target_sym = radar_target[0]
            target_asset = target_sym.replace("USDT", "")
            radar_data = radar_target[1]
            
            # 3. CIO Logic & REAL DB Action para CADA Wallet
            wallets = db.query(VirtualWallet).all()
            
            for wallet in wallets:
                try:
                    db.refresh(wallet)
                    balances = json.loads(wallet.balances) if wallet.balances else {"USDT": 150.0}
                    
                    # Calcular valor actual de este portafolio en particular
                    total_portfolio_value = balances.get("USDT", 0.0)
                    for coin, amount in balances.items():
                        if coin != "USDT" and amount > 0:
                            sym = f"{coin}USDT"
                            if sym in market_summary:
                                total_portfolio_value += amount * market_summary[sym]["price"]
                    
                    action = "HOLD"
                    justification = "Mercado estable, liquidez en rangos de equilibrio."
                    
                    # Rule: Kill Switch (20% Drawdown)
                    initial_capital = wallet.initial_capital or 150.0
                    if initial_capital <= 0:
                        initial_capital = 150.0
                    drawdown_percent = (initial_capital - total_portfolio_value) / initial_capital
                    
                    if drawdown_percent > 0.20:
                        action = "⚠️ KILL SWITCH ACTIVO"
                        justification = f"Drawdown crítico detectado: {drawdown_percent*100:.1f}% (${total_portfolio_value:.2f} / ${initial_capital:.2f}). Suspendiendo operaciones tácticas."
                    
                    # Rule: Tactical Trade (RSI extrema e imbalance de volumen)
                    elif radar_data["vol_imbalance"] > 3.0 and (radar_data["rsi"] < 25 or radar_data["rsi"] > 75):
                        direction = "BUY" if radar_data["rsi"] < 25 else "SELL"
                        entry_price = radar_data["price"]
                        
                        # Risk Mgmt: 20% of USDT balance or 10 USDT minimum
                        strike_amount = max(10.0, balances.get("USDT", 0) * 0.20)
                        qty = strike_amount / entry_price
                        
                        # Execute in DB
                        if direction == "BUY" and balances.get("USDT", 0) >= strike_amount:
                            balances["USDT"] -= strike_amount
                            balances[target_asset] = balances.get(target_asset, 0) + qty
                            action = f"COMPRA TÁCTICA ({target_sym})"
                            justification = f"Captura de suelo por RSI ({radar_data['rsi']:.1f}) y pico de volumen ({radar_data['vol_imbalance']:.2f}x)."
                        elif direction == "SELL" and balances.get(target_asset, 0) > 0:
                            sell_qty = balances[target_asset]
                            balances["USDT"] += sell_qty * entry_price
                            del balances[target_asset]
                            action = f"VENTA TÁCTICA ({target_sym})"
                            justification = f"Toma de ganancias/Venta por agotamiento (RSI: {radar_data['rsi']:.1f})."
                        
                        if action != "HOLD":
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
                                pnl=0
                            )
                            db.add(new_trade)
                            db.commit()
                            logger.success(f"🎯 Acción Ejecutada en DB (Práctica) para Wallet ID {wallet.id}: {action}")
                            
                            # MODO FUEGO REAL (DUAL)
                            config = db.query(AutomationConfig).filter(AutomationConfig.user_id == wallet.user_id).first()
                            is_real_mode = False if config is None else not config.practice_mode_only
                            
                            if is_real_mode:
                                logger.warning(f"🔥 MODO REAL ACTIVADO para User ID {wallet.user_id}. Evaluando Binance...")
                                
                                if direction == "BUY":
                                    real_usdt_info = client.get_balance("USDT")
                                    real_usdt = real_usdt_info["free"] if real_usdt_info else 0.0
                                    real_strike = max(10.0, real_usdt * 0.20)
                                    
                                    if real_usdt >= real_strike:
                                        real_qty = real_strike / entry_price
                                        order_resp = client.execute_real_order(symbol=target_sym, side="BUY", quantity=real_qty)
                                        
                                        if order_resp:
                                            real_trade = Transaction(
                                                user_id=wallet.user_id,
                                                symbol=target_sym,
                                                side="BUY",
                                                type="MARKET",
                                                quantity=real_qty,
                                                price=entry_price,
                                                total=real_strike,
                                                order_id=str(order_resp.get("orderId", "")),
                                                status=order_resp.get("status", "COMPLETED")
                                            )
                                            db.add(real_trade)
                                            db.commit()
                                            action = f"🔥 REAL BUY ({target_sym})"
                                    else:
                                        logger.warning(f"⚠️ Saldo real USDT insuficiente ({real_usdt:.2f} < {real_strike:.2f})")
                                        action += " (REAL BLOQUEADO: SALDO)"
                                        
                                elif direction == "SELL":
                                    asset_info = client.get_balance(target_asset)
                                    real_asset = asset_info["free"] if asset_info else 0.0
                                    
                                    # Necesitamos un mínimo para vender en Binance (notional value > $5 o $10)
                                    if real_asset * entry_price >= 10.0:
                                        order_resp = client.execute_real_order(symbol=target_sym, side="SELL", quantity=real_asset)
                                        
                                        if order_resp:
                                            real_trade = Transaction(
                                                user_id=wallet.user_id,
                                                symbol=target_sym,
                                                side="SELL",
                                                type="MARKET",
                                                quantity=real_asset,
                                                price=entry_price,
                                                total=real_asset * entry_price,
                                                order_id=str(order_resp.get("orderId", "")),
                                                status=order_resp.get("status", "COMPLETED")
                                            )
                                            db.add(real_trade)
                                            db.commit()
                                            action = f"🔥 REAL SELL ({target_sym})"
                                    else:
                                        logger.warning(f"⚠️ Saldo real de {target_asset} insuficiente para venta (Valor: {real_asset * entry_price:.2f})")
                                        action += " (REAL BLOQUEADO: SALDO)"
                            
                    # Guardar log de auditoría para este ciclo en JSON (asociado a la wallet)
                    audit_entry = {
                        "wallet_id": wallet.id,
                        "user_id": wallet.user_id,
                        "timestamp": now.isoformat(),
                        "session": session,
                        "portfolio_value": round(total_portfolio_value, 2),
                        "usdt_balance": round(balances.get("USDT", 0), 2),
                        "symbol": target_sym,
                        "radar_imbalance": round(radar_data["vol_imbalance"], 2),
                        "rsi": round(radar_data["rsi"], 1),
                        "action": action,
                        "reason": justification
                    }
                    save_audit_log(audit_entry)
                    
                except Exception as w_err:
                    logger.error(f"Error procesando Wallet ID {wallet.id} en Sentinel: {w_err}")
                    db.rollback()
            
            # Obtener intervalo dinámico de refresco del watchdog usando la config del primer usuario
            config = db.query(AutomationConfig).first()
            sleep_interval = config.check_interval_seconds if config and config.check_interval_seconds else 25
            
            print(f"\n🕒 [{now.strftime('%H:%M:%S')} UTC] | Sesión: {session} | [🔵 DB SYNC ACTIVE]", flush=True)
            print(f"💼 Total Wallets Sincronizadas: {len(wallets)}", flush=True)
            print(f"📡 Radar Elite 10: {target_sym} ({radar_data['vol_imbalance']:.2f}x imbalance)", flush=True)
            print(f"🎯 Última Decisión CIO: {action}", flush=True)
            print(f"📉 Lógica: {justification} | Watchdog Sync: {sleep_interval}s", flush=True)
            
            await asyncio.sleep(sleep_interval)
            
        except Exception as e:
            logger.error(f"Sentinel Loop Error: {e}")
            db.rollback()
            await asyncio.sleep(10)

if __name__ == "__main__":
    print("🚀 Iniciando Protocolo CENTINELA OMNIPRESENTE (DB-Sync Mode)...", flush=True)
    asyncio.run(run_sentinel_cio())
