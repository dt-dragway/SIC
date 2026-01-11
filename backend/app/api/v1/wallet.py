"""
SIC Ultra - Wallet Endpoints

Ver tu cartera de Binance en tiempo real.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.api.v1.auth import oauth2_scheme, verify_token


router = APIRouter()


# === Schemas ===

class Balance(BaseModel):
    asset: str
    free: float
    locked: float
    total: float
    usd_value: Optional[float] = None


class WalletResponse(BaseModel):
    total_usd: float
    balances: List[Balance]
    last_update: datetime


class PriceResponse(BaseModel):
    symbol: str
    price: float
    change_24h: float
    timestamp: datetime


# === Endpoints ===

@router.get("/", response_model=WalletResponse)
async def get_wallet(token: str = Depends(oauth2_scheme)):
    """
    Obtener tu cartera de Binance.
    
    Muestra todos los activos con balance > 0.
    """
    verify_token(token)
    
    # TODO: Conectar a Binance API
    # TODO: Obtener balances reales
    
    # Datos de ejemplo
    return {
        "total_usd": 1234.56,
        "balances": [
            {"asset": "USDT", "free": 500.0, "locked": 0, "total": 500.0, "usd_value": 500.0},
            {"asset": "BTC", "free": 0.015, "locked": 0, "total": 0.015, "usd_value": 675.0},
            {"asset": "ETH", "free": 0.25, "locked": 0, "total": 0.25, "usd_value": 59.56},
        ],
        "last_update": datetime.utcnow()
    }


@router.get("/balance/{asset}")
async def get_balance(asset: str, token: str = Depends(oauth2_scheme)):
    """
    Obtener balance de un activo específico.
    """
    verify_token(token)
    
    asset = asset.upper()
    
    # TODO: Conectar a Binance
    return {
        "asset": asset,
        "free": 500.0,
        "locked": 0,
        "total": 500.0
    }


@router.get("/price/{symbol}", response_model=PriceResponse)
async def get_price(symbol: str, token: str = Depends(oauth2_scheme)):
    """
    Obtener precio actual de un par.
    
    Ejemplo: /price/BTCUSDT
    """
    verify_token(token)
    
    symbol = symbol.upper()
    
    # TODO: Conectar a Binance
    return {
        "symbol": symbol,
        "price": 45000.0,
        "change_24h": 2.5,
        "timestamp": datetime.utcnow()
    }


@router.get("/prices")
async def get_all_prices(token: str = Depends(oauth2_scheme)):
    """
    Obtener precios de los principales pares.
    """
    verify_token(token)
    
    # TODO: Conectar a Binance
    return {
        "prices": [
            {"symbol": "BTCUSDT", "price": 45000.0, "change_24h": 2.5},
            {"symbol": "ETHUSDT", "price": 2500.0, "change_24h": -1.2},
            {"symbol": "BNBUSDT", "price": 320.0, "change_24h": 0.8},
        ],
        "timestamp": datetime.utcnow()
    }
