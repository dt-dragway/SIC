#!/usr/bin/env python
import os
import sys
import json
from datetime import datetime

# Añadir directorio raíz al PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import VirtualWallet
from app.infrastructure.binance.client import get_binance_client
from loguru import logger

def migrate_wallets():
    logger.info("🔄 INICIANDO MIGRACIÓN DE BILLETERA VIRTUAL DE PRÁCTICA A $150 USD...")
    db = SessionLocal()
    try:
        binance = get_binance_client()
        
        # Criptomonedas recomendadas
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOTUSDT", "MATICUSDT", "DOGEUSDT", "LINKUSDT"]
        initial_balances = {"USDT": 50.0}
        
        logger.info("📈 Obteniendo precios en tiempo real desde Binance...")
        for sym in symbols:
            coin = sym.replace("USDT", "")
            try:
                price = binance.get_price(sym)
                if price and price > 0:
                    initial_balances[coin] = round(10.0 / price, 6)
                    logger.info(f"   - {coin}: ${price:.4f} USD -> {initial_balances[coin]} {coin}")
                else:
                    raise ValueError("Precio inválido o 0")
            except Exception as e:
                logger.warning(f"   ⚠️ No se pudo obtener precio de {sym}: {e}. Usando fallback...")
                fallback_prices = {
                    "BTC": 70000.0, "ETH": 3500.0, "BNB": 580.0, "SOL": 170.0,
                    "XRP": 0.50, "ADA": 0.45, "DOT": 6.5, "MATIC": 0.70,
                    "DOGE": 0.15, "LINK": 15.0
                }
                price = fallback_prices.get(coin, 1.0)
                initial_balances[coin] = round(10.0 / price, 6)
                logger.info(f"   - {coin}: ${price:.4f} USD (Fallback) -> {initial_balances[coin]} {coin}")

        # Buscar billeteras existentes
        wallets = db.query(VirtualWallet).all()
        if not wallets:
            logger.warning("⚠️ No se encontraron billeteras virtuales en la base de datos.")
            return

        for wallet in wallets:
            logger.info(f"💼 Actualizando billetera del Usuario ID: {wallet.user_id}...")
            wallet.balances = json.dumps(initial_balances)
            wallet.initial_capital = 150.0
            wallet.reset_at = datetime.utcnow()
            db.add(wallet)
            logger.success(f"✅ Billetera del Usuario ID: {wallet.user_id} actualizada correctamente a $150 USD.")
            
        db.commit()
        logger.success("🚀 MIGRACIÓN DE BILLETERAS COMPLETADA CON ÉXITO.")
        
    except Exception as e:
        logger.error(f"❌ Error durante la migración de billeteras: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_wallets()
