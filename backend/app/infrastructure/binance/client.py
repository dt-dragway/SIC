"""
SIC Ultra - Cliente de Binance

Conexión real a la API de Binance para:
- Ver balances de tu wallet
- Obtener precios en tiempo real
- Ejecutar órdenes (modo batalla real)
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger

from app.config import settings


class BinanceClient:
    """
    Cliente para interactuar con Binance API.
    
    Usa tus API Keys configuradas en .env
    """
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._connect()
    
    def _connect(self):
        """Conectar a Binance API"""
        try:
            if settings.binance_testnet:
                # Testnet para pruebas (no dinero real)
                self.client = Client(
                    api_key=settings.binance_api_key,
                    api_secret=settings.binance_api_secret,
                    testnet=True
                )
                logger.info("🔗 Conectado a Binance TESTNET")
            else:
                # API real
                self.client = Client(
                    api_key=settings.binance_api_key,
                    api_secret=settings.binance_api_secret
                )
                logger.info("🔗 Conectado a Binance REAL")
                
        except Exception as e:
            logger.error(f"❌ Error conectando a Binance: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Verificar si la conexión está activa"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def get_account_info(self) -> Optional[Dict]:
        """Obtener información de la cuenta"""
        if not self.client:
            return None
        try:
            return self.client.get_account()
        except BinanceAPIException as e:
            logger.error(f"Error obteniendo cuenta: {e}")
            return None
    
    def get_balances(self, hide_zero: bool = True) -> List[Dict]:
        """
        Obtener balances de todos los activos.
        
        Args:
            hide_zero: Si True, solo muestra activos con balance > 0
            
        Returns:
            Lista de balances: [{asset, free, locked, total}]
        """
        if not self.client:
            return []
            
        try:
            account = self.client.get_account()
            balances = []
            
            for asset in account.get('balances', []):
                free = float(asset['free'])
                locked = float(asset['locked'])
                total = free + locked
                
                if hide_zero and total == 0:
                    continue
                    
                balances.append({
                    'asset': asset['asset'],
                    'free': free,
                    'locked': locked,
                    'total': total
                })
            
            return balances
            
        except BinanceAPIException as e:
            logger.error(f"Error obteniendo balances: {e}")
            return []
    
    def get_balance(self, asset: str) -> Optional[Dict]:
        """Obtener balance de un activo específico"""
        if not self.client:
            return None
            
        try:
            balance = self.client.get_asset_balance(asset=asset.upper())
            if balance:
                return {
                    'asset': balance['asset'],
                    'free': float(balance['free']),
                    'locked': float(balance['locked']),
                    'total': float(balance['free']) + float(balance['locked'])
                }
            return None
        except BinanceAPIException as e:
            logger.error(f"Error obteniendo balance de {asset}: {e}")
            return None
    
    def get_price(self, symbol: str) -> Optional[float]:
        """
        Obtener precio actual de un par.
        
        Args:
            symbol: Par de trading, ej: "BTCUSDT"
        """
        if not self.client:
            return None
            
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol.upper())
            return float(ticker['price'])
        except BinanceAPIException as e:
            logger.error(f"Error obteniendo precio de {symbol}: {e}")
            return None
    
    def get_all_prices(self) -> Dict[str, float]:
        """Obtener todos los precios"""
        if not self.client:
            return {}
            
        try:
            tickers = self.client.get_all_tickers()
            return {t['symbol']: float(t['price']) for t in tickers}
        except BinanceAPIException as e:
            logger.error(f"Error obteniendo precios: {e}")
            return {}
    
    def get_24h_ticker(self, symbol: str) -> Optional[Dict]:
        """
        Obtener estadísticas de 24h de un par.
        Incluye: precio, cambio %, volumen, high, low
        """
        if not self.client:
            return None
            
        try:
            ticker = self.client.get_ticker(symbol=symbol.upper())
            return {
                'symbol': ticker['symbol'],
                'price': float(ticker['lastPrice']),
                'change_24h': float(ticker['priceChangePercent']),
                'high_24h': float(ticker['highPrice']),
                'low_24h': float(ticker['lowPrice']),
                'volume_24h': float(ticker['volume']),
                'quote_volume': float(ticker['quoteVolume'])
            }
        except BinanceAPIException as e:
            logger.error(f"Error obteniendo ticker 24h de {symbol}: {e}")
            return None
    
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> List[Dict]:
        """
        Obtener velas/candlesticks para gráficos.
        
        Args:
            symbol: Par de trading
            interval: 1m, 5m, 15m, 1h, 4h, 1d
            limit: Número de velas (máx 1000)
        """
        if not self.client:
            return []
            
        try:
            klines = self.client.get_klines(
                symbol=symbol.upper(),
                interval=interval,
                limit=limit
            )
            
            return [
                {
                    'timestamp': datetime.fromtimestamp(k[0] / 1000),
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4]),
                    'volume': float(k[5])
                }
                for k in klines
            ]
        except BinanceAPIException as e:
            logger.error(f"Error obteniendo klines de {symbol}: {e}")
            return []
    
    def get_wallet_value_usd(self) -> float:
        """
        Calcular valor total de la wallet en USD.
        Convierte todos los activos a USDT.
        """
        balances = self.get_balances(hide_zero=True)
        prices = self.get_all_prices()
        total_usd = 0.0
        
        for balance in balances:
            asset = balance['asset']
            amount = balance['total']
            
            if asset in ['USDT', 'BUSD', 'USD']:
                total_usd += amount
            else:
                # Buscar precio en USDT
                symbol = f"{asset}USDT"
                if symbol in prices:
                    total_usd += amount * prices[symbol]
                else:
                    # Intentar con BUSD
                    symbol = f"{asset}BUSD"
                    if symbol in prices:
                        total_usd += amount * prices[symbol]
        
        return total_usd


# Singleton para reusar la conexión
_binance_client: Optional[BinanceClient] = None


def get_binance_client() -> BinanceClient:
    """Obtener cliente de Binance (singleton)"""
    global _binance_client
    if _binance_client is None:
        _binance_client = BinanceClient()
    return _binance_client
