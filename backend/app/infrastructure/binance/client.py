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

    def get_top_long_short_ratio(self, symbol: str, period: str = "5m") -> Optional[Dict]:
        """
        Obtener Ratio Long/Short de Top Traders (Binance Futures).
        
        Args:
            symbol: Par (ej: BTCUSDT)
            period: "5m", "15m", "1h", "4h", "1d"
            
        Returns:
            Dict con longAccount, shortAccount, longShortRatio
        """
        if not self.client:
            return None
            
        try:
            # Nota: Esto usa endpoint público de Futures
            data = self.client.futures_top_longshort_ratio(symbol=symbol.upper(), period=period, limit=1)
            if data and len(data) > 0:
                latest = data[0]
                return {
                    "long_ratio": float(latest["longAccount"]),
                    "short_ratio": float(latest["shortAccount"]),
                    "ratio": float(latest["longShortRatio"]),
                    "timestamp": datetime.fromtimestamp(latest["timestamp"] / 1000)
                }
            return None
            logger.warning(f"No se pudo obtener Long/Short ratio para {symbol}: {e}")
            return None

    def get_p2p_history(self, trade_type: str = "BUY") -> List[Dict]:
        """
        Obtener historial de órdenes P2P (C2C).
        REQUIERE API KEY con permisos.
        """
        if not self.client:
            return []
            
        try:
            # Endpoint SAPI: GET /sapi/v1/c2c/orderMatch/listUserOrderHistory
            # python-binance wrapper: get_c2c_trade_history
            trades = self.client.get_c2c_trade_history(tradeType=trade_type.upper())
            
            # Map common fields
            return [{
                "orderNumber": t.get("orderNumber"),
                "advertiser": t.get("counterPartNickName"),
                "asset": t.get("asset"),
                "amount": float(t.get("amount", 0)),
                "fiat": t.get("fiat"),
                "fiat_amount": float(t.get("totalPrice", 0)),
                "price": float(t.get("unitPrice", 0)),
                "status": t.get("orderStatus"),
                "timestamp": datetime.fromtimestamp(t.get("createTime", 0) / 1000),
                "type": trade_type.upper()
            } for t in trades.get("data", [])]
            
        except Exception as e:
            logger.warning(f"Error obteniendo historial P2P ({trade_type}): {e}")
            return []


# Singleton para reusar la conexión
_binance_client: Optional[BinanceClient] = None


def get_binance_client() -> BinanceClient:
    """Obtener cliente de Binance (singleton)"""
    global _binance_client
    if _binance_client is None:
        _binance_client = BinanceClient()
    return _binance_client
