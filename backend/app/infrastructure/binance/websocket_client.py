"""
SIC Ultra - Binance WebSocket Client

Conexión en tiempo real a Binance usando WebSockets.
Sustituye las peticiones REST por streams en vivo para:
- Precios (Ticks)
- Microestructura (Order Book parcial)
"""

import asyncio
from typing import Dict, List, Callable, Optional, Set
from loguru import logger
from binance import BinanceSocketManager
from app.infrastructure.binance.client import get_binance_client

class BinanceWebsocketClient:
    """
    Gestiona la conexión WebSocket para streams de mercado en vivo.
    """
    def __init__(self):
        self.bsm: Optional[BinanceSocketManager] = None
        self.active_streams: Dict[str, asyncio.Task] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        
        # Estado en memoria rápido (para acceso síncrono si se necesita)
        self.live_prices: Dict[str, float] = {}
        
    def _initialize(self):
        """Inicializa el manager usando el cliente REST existente."""
        if self.bsm is None:
            rest_client = get_binance_client().client
            if rest_client:
                self.bsm = BinanceSocketManager(rest_client)
            else:
                logger.error("❌ No se pudo inicializar WebSocket: REST Client no disponible.")
    
    def register_callback(self, stream_type: str, callback: Callable):
        """
        Registra una función a ejecutar cuando llegue un evento.
        stream_type: 'trade', 'depth'
        """
        if stream_type not in self.callbacks:
            self.callbacks[stream_type] = []
        self.callbacks[stream_type].append(callback)
        
    async def _notify_callbacks(self, stream_type: str, data: Dict):
        """Dispara los callbacks correspondientes asíncronamente."""
        callbacks = self.callbacks.get(stream_type, [])
        for cb in callbacks:
            try:
                # Si es asíncrono, lo esperamos, si no, lo llamamos directo
                if asyncio.iscoroutinefunction(cb):
                    await cb(data)
                else:
                    cb(data)
            except Exception as e:
                logger.error(f"Error en callback de WebSocket ({stream_type}): {e}")

    async def start_trade_socket(self, symbols: List[str]):
        """
        Inicia streams para Trades (Precio en tiempo real)
        symbols: lista de símbolos (ej. ["BTCUSDT", "ETHUSDT"])
        """
        self._initialize()
        if not self.bsm:
            return

        for symbol in symbols:
            task_name = f"trade_{symbol.lower()}"
            if task_name not in self.active_streams:
                logger.info(f"🔌 Conectando WebSocket de Trades para {symbol}...")
                task = asyncio.create_task(self._trade_listener(symbol))
                self.active_streams[task_name] = task

    async def _trade_listener(self, symbol: str):
        """Bucle para escuchar trades de un símbolo"""
        ts = self.bsm.trade_socket(symbol.upper())
        # BinanceSocketManager usa un async context manager en la v1.0+
        async with ts as tscm:
            while True:
                try:
                    res = await tscm.recv()
                    if res:
                        # Evento de Trade: e='trade', p='precio', q='cantidad', s='symbol'
                        price = float(res['p'])
                        self.live_prices[symbol.upper()] = price
                        
                        data = {
                            "symbol": symbol.upper(),
                            "price": price,
                            "quantity": float(res['q']),
                            "buyer_is_maker": res['m'],
                            "timestamp": res['T']
                        }
                        
                        await self._notify_callbacks('trade', data)
                except Exception as e:
                    logger.error(f"❌ Error en stream de Trades {symbol}: {e}")
                    await asyncio.sleep(5) # Reintentar tras error

    async def start_depth_socket(self, symbol: str, depth: int = 20):
        """
        Inicia un stream del Order Book (Depth)
        """
        self._initialize()
        if not self.bsm:
            return
            
        task_name = f"depth_{symbol.lower()}"
        if task_name not in self.active_streams:
            logger.info(f"🔌 Conectando WebSocket Depth ({depth}) para {symbol}...")
            task = asyncio.create_task(self._depth_listener(symbol, depth))
            self.active_streams[task_name] = task
            
    async def _depth_listener(self, symbol: str, depth: int):
        """Bucle para el order book de un símbolo"""
        ds = self.bsm.depth_socket(symbol.upper(), depth=depth)
        async with ds as dscm:
            while True:
                try:
                    res = await dscm.recv()
                    if res:
                        data = {
                            "symbol": symbol.upper(),
                            "bids": res.get('bids', []),
                            "asks": res.get('asks', [])
                        }
                        await self._notify_callbacks('depth', data)
                except Exception as e:
                    logger.error(f"❌ Error en stream Depth {symbol}: {e}")
                    await asyncio.sleep(5)

    def stop_all(self):
        """Detiene todas las tareas de WebSocket activas"""
        for name, task in self.active_streams.items():
            task.cancel()
        self.active_streams.clear()
        logger.info("🛑 Todos los WebSockets de Binance desconectados.")

# Singleton
_ws_client: Optional[BinanceWebsocketClient] = None

def get_websocket_client() -> BinanceWebsocketClient:
    global _ws_client
    if _ws_client is None:
        _ws_client = BinanceWebsocketClient()
    return _ws_client
