"""
SIC Ultra - Cliente P2P de Binance

Obtener ofertas del mercado P2P USDT/VES.
"""

import httpx
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger

from app.config import settings


class BinanceP2PClient:
    """
    Cliente para obtener datos del mercado P2P de Binance.
    
    Endpoint público que no requiere autenticación.
    """
    
    BASE_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def get_offers(
        self,
        fiat: str = "VES",
        asset: str = "USDT",
        trade_type: str = "BUY",
        page: int = 1,
        rows: int = 10
    ) -> List[Dict]:
        """
        Obtener ofertas P2P de Binance.
        
        Args:
            fiat: Moneda fiat (VES, USD, etc)
            asset: Cripto (USDT, BTC, etc)
            trade_type: BUY (comprar cripto) o SELL (vender cripto)
            page: Número de página
            rows: Ofertas por página
            
        Returns:
            Lista de ofertas con precio, límites, métodos de pago
        """
        payload = {
            "fiat": fiat.upper(),
            "asset": asset.upper(),
            "tradeType": trade_type.upper(),
            "page": page,
            "rows": rows,
            "payTypes": [],
            "publisherType": None
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.BASE_URL,
                    json=payload,
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                offers = []
                for item in data.get("data", []):
                    adv = item.get("adv", {})
                    advertiser = item.get("advertiser", {})
                    
                    offers.append({
                        "advertiser": advertiser.get("nickName", "Anónimo"),
                        "price": float(adv.get("price", 0)),
                        "available": float(adv.get("surplusAmount", 0)),
                        "min_amount": float(adv.get("minSingleTransAmount", 0)),
                        "max_amount": float(adv.get("maxSingleTransAmount", 0)),
                        "payment_methods": [p.get("identifier", "") for p in adv.get("tradeMethods", [])],
                        "completion_rate": float(advertiser.get("monthFinishRate", 0)) * 100,
                        "orders_count": advertiser.get("monthOrderCount", 0)
                    })
                
                return offers
                
        except Exception as e:
            logger.error(f"Error obteniendo ofertas P2P: {e}")
            return []
    
    async def get_buy_offers(self, fiat: str = "VES", asset: str = "USDT", rows: int = 10) -> List[Dict]:
        """Obtener ofertas para COMPRAR cripto (pagas fiat)"""
        return await self.get_offers(fiat, asset, "BUY", rows=rows)
    
    async def get_sell_offers(self, fiat: str = "VES", asset: str = "USDT", rows: int = 10) -> List[Dict]:
        """Obtener ofertas para VENDER cripto (recibes fiat)"""
        return await self.get_offers(fiat, asset, "SELL", rows=rows)
    
    async def get_market_summary(self, fiat: str = "VES", asset: str = "USDT") -> Dict:
        """
        Obtener resumen del mercado P2P con mejores precios y spread.
        """
        buy_offers = await self.get_buy_offers(fiat, asset, rows=5)
        sell_offers = await self.get_sell_offers(fiat, asset, rows=5)
        
        if not buy_offers and not sell_offers:
            return {
                "error": "No hay ofertas disponibles",
                "timestamp": datetime.utcnow()
            }
        
        # Mejor precio para comprar cripto (más bajo es mejor)
        best_buy = min(o["price"] for o in buy_offers) if buy_offers else 0
        avg_buy = sum(o["price"] for o in buy_offers) / len(buy_offers) if buy_offers else 0
        
        # Mejor precio para vender cripto (más alto es mejor)
        best_sell = max(o["price"] for o in sell_offers) if sell_offers else 0
        avg_sell = sum(o["price"] for o in sell_offers) / len(sell_offers) if sell_offers else 0
        
        # Spread (diferencia entre compra y venta)
        spread = ((best_sell - best_buy) / best_buy * 100) if best_buy > 0 else 0
        
        return {
            "fiat": fiat,
            "asset": asset,
            "best_buy_price": best_buy,
            "best_sell_price": best_sell,
            "avg_buy_price": round(avg_buy, 2),
            "avg_sell_price": round(avg_sell, 2),
            "spread_percent": round(spread, 2),
            "buy_offers_count": len(buy_offers),
            "sell_offers_count": len(sell_offers),
            "timestamp": datetime.utcnow()
        }


# Singleton
_p2p_client: Optional[BinanceP2PClient] = None


def get_p2p_client() -> BinanceP2PClient:
    """Obtener cliente P2P (singleton)"""
    global _p2p_client
    if _p2p_client is None:
        _p2p_client = BinanceP2PClient()
    return _p2p_client
