"""
SIC Ultra - Trading Endpoints

Órdenes de trading en Binance.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum

from app.api.v1.auth import oauth2_scheme, verify_token


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
    """
    verify_token(token)
    
    # TODO: Verificar modo (práctica vs real)
    # TODO: Verificar protecciones de riesgo
    # TODO: Enviar orden a Binance
    
    return {
        "id": "12345",
        "symbol": order.symbol.upper(),
        "side": order.side,
        "type": order.type,
        "quantity": order.quantity,
        "price": order.price or 45000.0,
        "status": OrderStatus.PENDING,
        "created_at": datetime.utcnow()
    }


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
    Obtener velas/candlesticks para gráficos.
    
    Intervals: 1m, 5m, 15m, 1h, 4h, 1d
    """
    verify_token(token)
    
    symbol = symbol.upper()
    
    # TODO: Obtener de Binance
    # Datos de ejemplo
    from datetime import timedelta
    import random
    
    candles = []
    base_price = 45000
    now = datetime.utcnow()
    
    for i in range(limit):
        variance = random.uniform(-500, 500)
        open_price = base_price + variance
        close_price = open_price + random.uniform(-200, 200)
        
        candles.append({
            "timestamp": now - timedelta(hours=limit-i),
            "open": open_price,
            "high": max(open_price, close_price) + random.uniform(0, 100),
            "low": min(open_price, close_price) - random.uniform(0, 100),
            "close": close_price,
            "volume": random.uniform(100, 1000)
        })
    
    return {"symbol": symbol, "interval": interval, "candles": candles}
