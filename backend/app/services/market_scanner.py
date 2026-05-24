import asyncio
from datetime import datetime
import random
from loguru import logger
from sqlalchemy.orm import Session

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.binance.client import get_binance_client
from app.infrastructure.database.institutional_models import FundingRateHistory, OrderBookSnapshot, WhaleAlert

class MarketScanner:
    """
    Escáner de Mercado Institucional.
    Recolecta datos de Microestructura, On-chain y Funding Rates en segundo plano.
    """
    
    def __init__(self):
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
        self.scan_interval = 600  # Escanear cada 10 minutos
        self.running = False
        self._task = None

    async def start(self):
        """Iniciar el escaneo en segundo plano"""
        if self.running:
            return
            
        self.running = True
        logger.info("🚀 Iniciando Escáner de Mercado Institucional...")
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self):
        """Detener el escaneo"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Escáner de Mercado detenido.")

    async def _run_loop(self):
        """Bucle principal de escaneo"""
        while self.running:
            try:
                await self.scan_cycle()
            except Exception as e:
                logger.error(f"❌ Error en ciclo de escaneo: {e}")
                
            await asyncio.sleep(self.scan_interval)

    async def scan_cycle(self):
        """Un ciclo completo de recolección de datos"""
        db = SessionLocal()
        client = get_binance_client()
        
        logger.info("🔍 Iniciando ciclo de recolección de datos institucionales...")
        
        try:
            for symbol in self.symbols:
                # 1. Recolectar Funding Rate
                try:
                    funding = client.get_funding_rate(symbol)
                    if funding:
                        fr_entry = FundingRateHistory(
                            symbol=symbol,
                            funding_rate=funding["fundingRate"],
                            mark_price=funding["markPrice"],
                            index_price=funding["indexPrice"],
                            timestamp=datetime.utcnow()
                        )
                        db.add(fr_entry)
                        logger.debug(f"📊 {symbol} Funding Rate registrado: {funding['fundingRate']}")
                except Exception as e:
                    logger.warning(f"No se pudo obtener funding para {symbol}: {e}")

                # 2. Recolectar Snapshot de Order Book (Microestructura)
                try:
                    depth = client.get_order_book(symbol, limit=20)
                    if depth:
                        best_bid = float(depth['bids'][0][0]) if depth['bids'] else 0
                        best_ask = float(depth['asks'][0][0]) if depth['asks'] else 0
                        
                        snapshot = OrderBookSnapshot(
                            symbol=symbol,
                            best_bid=best_bid,
                            best_ask=best_ask,
                            spread=best_ask - best_bid,
                            bids_json=str(depth['bids']),
                            asks_json=str(depth['asks']),
                            timestamp=datetime.utcnow()
                        )
                        db.add(snapshot)
                except Exception as e:
                    logger.warning(f"No se pudo obtener order book para {symbol}: {e}")

            # 3. Simular Alertas de Ballenas (Detección de flujos on-chain)
            # En una implementación real, esto consultaría una API de Whale Tracking
            if random.random() > 0.6:  # 40% de probabilidad por ciclo
                self._simulate_whale_alert(db)

            db.commit()
            logger.success("✅ Ciclo institucional completado y guardado en DB")
            
        except Exception as e:
            logger.error(f"❌ Error guardando datos de escaneo: {e}")
            db.rollback()
        finally:
            db.close()

    def _simulate_whale_alert(self, db: Session):
        """Simula una alerta de ballena detectada en la blockchain"""
        blockchains = ["BTC", "ETH", "SOL", "BNB"]
        flow_types = ["exchange_inflow", "exchange_outflow", "whale_to_whale"]
        blockchain = random.choice(blockchains)
        flow = random.choice(flow_types)
        
        # Sentimiento basado en el flujo
        if flow == "exchange_outflow":
            sentiment = "bullish" 
        elif flow == "exchange_inflow":
            sentiment = "bearish"
        else:
            sentiment = "neutral"
            
        whale = WhaleAlert(
            blockchain=blockchain,
            tx_hash=f"0x{random.getrandbits(256):064x}",
            amount=random.uniform(500, 5000),
            amount_usd=random.uniform(10_000_000, 250_000_000),
            from_label="Whale Wallet" if flow != "exchange_inflow" else "Binance Hot",
            to_label="Binance Hot" if flow == "exchange_inflow" else "Whale Wallet",
            flow_type=flow,
            sentiment=sentiment,
            timestamp=datetime.utcnow()
        )
        db.add(whale)
        logger.info(f"🐋 Whale Alert detectada y registrada: {blockchain} {flow}")

# Instancia global
market_scanner = MarketScanner()

def get_market_scanner() -> MarketScanner:
    """Obtener instancia del escáner"""
    return market_scanner
