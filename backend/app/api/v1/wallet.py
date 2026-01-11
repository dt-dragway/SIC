"""
SIC Ultra - Wallet Endpoints

Ver tu cartera de Binance en tiempo real con datos REALES.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.api.v1.auth import oauth2_scheme, verify_token
from app.infrastructure.binance.client import get_binance_client


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
    connected: bool


class PriceResponse(BaseModel):
    symbol: str
    price: float
    change_24h: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    timestamp: datetime


# === Endpoints ===

@router.get("/", response_model=WalletResponse)
async def get_wallet(token: str = Depends(oauth2_scheme)):
    """
    Obtener tu cartera de Binance REAL.
    
    Muestra todos los activos con balance > 0 y su valor en USD.
    """
    verify_token(token)
    
    client = get_binance_client()
    
    if not client.is_connected():
        return {
            "total_usd": 0,
            "balances": [],
            "last_update": datetime.utcnow(),
            "connected": False
        }
    
    # Obtener balances reales
    raw_balances = client.get_balances(hide_zero=True)
    prices = client.get_all_prices()
    
    balances = []
    total_usd = 0.0
    
    for b in raw_balances:
        asset = b['asset']
        usd_value = 0.0
        
        # Calcular valor en USD
        if asset in ['USDT', 'BUSD', 'USD']:
            usd_value = b['total']
        else:
            symbol = f"{asset}USDT"
            if symbol in prices:
                usd_value = b['total'] * prices[symbol]
        
        total_usd += usd_value
        
        balances.append({
            "asset": asset,
            "free": b['free'],
            "locked": b['locked'],
            "total": b['total'],
            "usd_value": round(usd_value, 2)
        })
    
    # Ordenar por valor USD descendente
    balances.sort(key=lambda x: x['usd_value'] or 0, reverse=True)
    
    return {
        "total_usd": round(total_usd, 2),
        "balances": balances,
        "last_update": datetime.utcnow(),
        "connected": True
    }


@router.get("/balance/{asset}")
async def get_balance(asset: str, token: str = Depends(oauth2_scheme)):
    """
    Obtener balance de un activo específico.
    """
    verify_token(token)
    
    client = get_binance_client()
    balance = client.get_balance(asset.upper())
    
    if not balance:
        raise HTTPException(status_code=404, detail=f"Activo {asset} no encontrado")
    
    # Calcular valor en USD
    price = client.get_price(f"{asset.upper()}USDT")
    usd_value = balance['total'] * price if price else None
    
    return {
        **balance,
        "usd_value": round(usd_value, 2) if usd_value else None
    }


@router.get("/price/{symbol}", response_model=PriceResponse)
async def get_price(symbol: str, token: str = Depends(oauth2_scheme)):
    """
    Obtener precio actual y estadísticas 24h de un par.
    
    Ejemplo: /price/BTCUSDT
    """
    verify_token(token)
    
    client = get_binance_client()
    ticker = client.get_24h_ticker(symbol.upper())
    
    if not ticker:
        raise HTTPException(status_code=404, detail=f"Par {symbol} no encontrado")
    
    return {
        "symbol": ticker['symbol'],
        "price": ticker['price'],
        "change_24h": ticker['change_24h'],
        "high_24h": ticker['high_24h'],
        "low_24h": ticker['low_24h'],
        "volume_24h": ticker['volume_24h'],
        "timestamp": datetime.utcnow()
    }


@router.get("/prices")
async def get_main_prices(token: str = Depends(oauth2_scheme)):
    """
    Obtener precios de los principales pares de trading.
    """
    verify_token(token)
    
    client = get_binance_client()
    
    # Pares principales
    main_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT']
    
    prices = []
    for symbol in main_symbols:
        ticker = client.get_24h_ticker(symbol)
        if ticker:
            prices.append({
                "symbol": ticker['symbol'],
                "price": ticker['price'],
                "change_24h": ticker['change_24h']
            })
    
    return {
        "prices": prices,
        "timestamp": datetime.utcnow()
    }


@router.get("/status")
async def get_connection_status(token: str = Depends(oauth2_scheme)):
    """
    Verificar estado de conexión con Binance.
    """
    verify_token(token)
    
    client = get_binance_client()
    
    return {
        "connected": client.is_connected(),
        "testnet": True,  # TODO: Leer de settings
        "timestamp": datetime.utcnow()
    }
