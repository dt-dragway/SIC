import asyncio
from datetime import datetime
import random
from loguru import logger
from sqlalchemy.orm import Session

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.binance.client import get_binance_client
from app.infrastructure.binance.websocket_client import get_websocket_client
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
        """Iniciar el escaneo en segundo plano usando WebSockets"""
        if self.running:
            return
            
        self.running = True
        logger.info("🚀 Iniciando Escáner de Mercado Institucional (WebSockets)...")
        
        ws_client = get_websocket_client()
        
        # Registrar callbacks para manejar eventos en tiempo real
        ws_client.register_callback('trade', self._on_trade_event)
        ws_client.register_callback('depth', self._on_depth_event)
        
        # Iniciar streams para las monedas principales
        await ws_client.start_trade_socket(self.symbols)
        for symbol in self.symbols:
            await ws_client.start_depth_socket(symbol, depth=10)
            
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self):
        """Detener el escaneo"""
        self.running = False
        get_websocket_client().stop_all()
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Escáner de Mercado detenido.")

    async def _run_loop(self):
        """Bucle secundario para métricas lentas (Funding Rate y Whale Alerts)"""
        while self.running:
            try:
                await self.scan_cycle_slow()
            except Exception as e:
                logger.error(f"❌ Error en ciclo de escaneo lento: {e}")
                
            await asyncio.sleep(self.scan_interval)

    async def scan_cycle_slow(self):
        """Un ciclo para Funding Rate y simulaciones (no requieren WebSocket rápido)"""
        db = SessionLocal()
        client = get_binance_client()
        
        logger.debug("🔍 Iniciando ciclo secundario (Funding/On-chain)...")
        
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

                # 2. El Order Book ahora se recolecta en vivo vía WebSocket
                pass

            # 3. Simular Alertas de Ballenas (Detección de flujos on-chain)
            if random.random() > 0.6:  # 40% de probabilidad por ciclo
                self._simulate_whale_alert(db)

            db.commit()
            
        except Exception as e:
            logger.error(f"❌ Error guardando datos de escaneo lento: {e}")
            db.rollback()
        finally:
            db.close()

    async def _on_trade_event(self, data: dict):
        """Maneja actualizaciones de trades en tiempo real (Tick)"""
        # Notificar al motor de AutoExecution si hay operaciones pendientes
        # o si se cruzan umbrales clave
        # Por ahora solo guardamos/logeamos si es un trade importante (volumen anómalo)
        pass
        
    async def _on_depth_event(self, data: dict):
        """Maneja actualizaciones de Order Book en tiempo real"""
        # Por rendimiento no lo guardamos todo en DB, solo mantenemos estado en RAM
        # y detectamos desequilibrios (Imbalance) al vuelo.
        bids = data.get("bids", [])
        asks = data.get("asks", [])
        
        if bids and asks:
            best_bid = float(bids[0][0])
            best_ask = float(asks[0][0])
            spread = best_ask - best_bid
            
            if spread > (best_bid * 0.005): # Si el spread es muy grande, hay baja liquidez
                logger.warning(f"⚠️ {data['symbol']} Spread inusualmente alto: {spread:.2f} detectado vía WebSocket")

    def _simulate_whale_alert(self, db: Session):
        """Simula una alerta de ballena detectada en la blockchain"""
        blockchains = ["BTC", "ETH", "SOL", "BNB", "NEAR", "SAGA", "NIL", "RIF", "LINK", "DOGE"]
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

