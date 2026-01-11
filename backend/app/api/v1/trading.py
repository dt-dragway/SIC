"""
SIC Ultra - Trading Endpoints

Órdenes de trading y gráficos con datos REALES de Binance.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

from app.api.v1.auth import oauth2_scheme, verify_token
from app.infrastructure.binance.client import get_binance_client


router = APIRouter()


# === Enums ===

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


# === Schemas ===

class OrderCreate(BaseModel):
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: float
    price: Optional[float] = None  # Solo para LIMIT
    stop_price: Optional[float] = None  # Solo para STOP_LOSS


class OrderResponse(BaseModel):
    id: str
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: float
    price: float
    status: OrderStatus
    created_at: datetime


class CandleResponse(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


# === Endpoints ===

@router.post("/order", response_model=OrderResponse)
async def create_order(order: OrderCreate, token: str = Depends(oauth2_scheme)):
    """
    Crear orden de trading.
    
    ⚠️ SOLO FUNCIONA EN MODO BATALLA REAL
    En modo práctica usar /practice/order
    
    TODO: Implementar órdenes reales en Fase 7
    """
    verify_token(token)
    
    # TODO: Verificar modo (práctica vs real)
    # TODO: Verificar protecciones de riesgo (7 capas)
    # TODO: Enviar orden a Binance
    
    raise HTTPException(
        status_code=400, 
        detail="Modo Batalla Real no habilitado aún. Usa /practice/order para practicar."
    )


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    symbol: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener historial de órdenes.
    """
    verify_token(token)
    
    # TODO: Obtener de Binance
    return []


@router.delete("/order/{order_id}")
async def cancel_order(order_id: str, token: str = Depends(oauth2_scheme)):
    """
    Cancelar una orden pendiente.
    """
    verify_token(token)
    
    # TODO: Cancelar en Binance
    return {"message": f"Orden {order_id} cancelada"}


@router.get("/candles/{symbol}")
async def get_candles(
    symbol: str,
    interval: str = "1h",
    limit: int = 100,
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener velas/candlesticks REALES para gráficos.
    
    Intervals: 1m, 5m, 15m, 1h, 4h, 1d
    """
    verify_token(token)
    
    client = get_binance_client()
    symbol = symbol.upper()
    
    # Validar interval
    valid_intervals = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
    if interval not in valid_intervals:
        raise HTTPException(status_code=400, detail=f"Interval inválido. Usa: {valid_intervals}")
    
    # Obtener klines reales de Binance
    candles = client.get_klines(symbol, interval, limit)
    
    if not candles:
        raise HTTPException(status_code=404, detail=f"No se encontraron datos para {symbol}")
    
    return {
        "symbol": symbol,
        "interval": interval,
        "candles": candles,
        "count": len(candles)
    }


@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str, token: str = Depends(oauth2_scheme)):
    """
    Obtener información completa de un par de trading.
    """
    verify_token(token)
    
    client = get_binance_client()
    ticker = client.get_24h_ticker(symbol.upper())
    
    if not ticker:
        raise HTTPException(status_code=404, detail=f"Par {symbol} no encontrado")
    
    return ticker


@router.get("/symbols")
async def get_trading_symbols(token: str = Depends(oauth2_scheme)):
    """
    Obtener lista de pares de trading disponibles.
    """
    verify_token(token)
    
    # Pares principales soportados
    symbols = [
        {"symbol": "BTCUSDT", "base": "BTC", "quote": "USDT", "name": "Bitcoin"},
        {"symbol": "ETHUSDT", "base": "ETH", "quote": "USDT", "name": "Ethereum"},
        {"symbol": "BNBUSDT", "base": "BNB", "quote": "USDT", "name": "Binance Coin"},
        {"symbol": "SOLUSDT", "base": "SOL", "quote": "USDT", "name": "Solana"},
        {"symbol": "XRPUSDT", "base": "XRP", "quote": "USDT", "name": "Ripple"},
        {"symbol": "ADAUSDT", "base": "ADA", "quote": "USDT", "name": "Cardano"},
        {"symbol": "DOTUSDT", "base": "DOT", "quote": "USDT", "name": "Polkadot"},
        {"symbol": "MATICUSDT", "base": "MATIC", "quote": "USDT", "name": "Polygon"},
        {"symbol": "LINKUSDT", "base": "LINK", "quote": "USDT", "name": "Chainlink"},
        {"symbol": "AVAXUSDT", "base": "AVAX", "quote": "USDT", "name": "Avalanche"},
    ]
    
    return {"symbols": symbols}
