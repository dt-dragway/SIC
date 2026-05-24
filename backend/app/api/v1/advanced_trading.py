"""
SIC Ultra - Advanced Trading Endpoints

Endpoints para órdenes avanzadas: LIMIT, OCO, TRAILING STOP
y gestión de órdenes pendientes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Session

from app.api.v1.auth import oauth2_scheme, verify_token
from app.infrastructure.binance.client import get_binance_client
from app.infrastructure.database.session import get_db


router = APIRouter()


# === Schemas ===

class LimitOrderCreate(BaseModel):
    symbol: str
    side: str  # BUY or SELL
    price: float  # Precio límite
    quantity: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    time_in_force: str = "GTC"  # GTC, IOC, FOK


class OCOOrderCreate(BaseModel):
    symbol: str
    side: str  # SELL generalmente
    quantity: float
    price: float  # Precio limit (take profit)
    stop_price: float  # Precio stop (stop loss)
    stop_limit_price: Optional[float] = None  # Si no se provee, usa stop_price


class PendingOrder(BaseModel):
    order_id: str
    symbol: str
    side: str
    type: str  # LIMIT, STOP_LOSS_LIMIT, etc.
    price: float
    quantity: float
    filled_qty: float
    status: str
    created_at: datetime


# === Endpoints ===

@router.post("/limit-order")
async def create_limit_order(
    order: LimitOrderCreate,
    token: str = Depends(oauth2_scheme)
):
    """
    Crear orden LIMIT.
    
    Espera a que el precio alcance el nivel especificado antes de ejecutar.
    Ideal para entradas optimizadas y evitar slippage.
    """
    verify_token(token)
    
    client = get_binance_client()
    
    if not client.is_connected():
        raise HTTPException(status_code=503, detail="No conectado a Binance")
    
    try:
        # Crear orden LIMIT en Binance
        result = client.client.create_order(
            symbol=order.symbol.upper(),
            side=order.side.upper(),
            type='LIMIT',
            timeInForce=order.time_in_force,
            quantity=order.quantity,
            price=str(order.price)
        )
        
        # Si hay stop loss o take profit, crear órdenes OCO
        # (esto se haría en un endpoint separado o con lógica más compleja)
        
        return {
            "success": True,
            "message": f"✅ Orden LIMIT creada: {order.side} {order.quantity} {order.symbol} @ ${order.price}",
            "order_id": result['orderId'],
            "status": result['status'],
            "fills": result.get('fills', [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando orden LIMIT: {str(e)}")


@router.post("/oco-order")
async def create_oco_order(
    order: OCOOrderCreate,
    token: str = Depends(oauth2_scheme)
):
    """
    Crear orden OCO (One Cancels the Other).
    
    Configura simultáneamente:
    - Take Profit (orden LIMIT_MAKER)
    - Stop Loss (orden STOP_LOSS_LIMIT)
    
    Cuando una se ejecuta, la otra se cancela automáticamente.
    """
    verify_token(token)
    
    client = get_binance_client()
    
    if not client.is_connected():
        raise HTTPException(status_code=503, detail="No conectado a Binance")
    
    try:
        # OCO = Take Profit + Stop Loss simultáneos
        result = client.client.create_oco_order(
            symbol=order.symbol.upper(),
            side=order.side.upper(),
            quantity=order.quantity,
            price=str(order.price),  # Take Profit price
            stopPrice=str(order.stop_price),  # Stop Loss trigger
            stopLimitPrice=str(order.stop_limit_price or order.stop_price),
            stopLimitTimeInForce='GTC'
        )
        
        return {
            "success": True,
            "message": f"✅ Orden OCO creada: TP @ ${order.price}, SL @ ${order.stop_price}",
            "order_list_id": result['orderListId'],
            "orders": result['orderReports']
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando orden OCO: {str(e)}")


@router.get("/pending-orders", response_model=List[PendingOrder])
async def get_pending_orders(
    symbol: Optional[str] = Query(None, description="Filtrar por símbolo"),
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener todas las órdenes pendientes (no ejecutadas).
    
    Estados válidos: NEW, PARTIALLY_FILLED
    """
    verify_token(token)
    
    client = get_binance_client()
    
    if not client.is_connected():
        return []
    
    try:
        # Obtener órdenes abiertas
        if symbol:
            orders = client.client.get_open_orders(symbol=symbol.upper())
        else:
            orders = client.client.get_open_orders()
        
        pending = []
        for o in orders:
            pending.append({
                "order_id": str(o['orderId']),
                "symbol": o['symbol'],
                "side": o['side'],
                "type": o['type'],
                "price": float(o['price']) if o['type'] != 'MARKET' else 0,
                "quantity": float(o['origQty']),
                "filled_qty": float(o['executedQty']),
                "status": o['status'],
                "created_at": datetime.fromtimestamp(o['time'] / 1000)
            })
        
        return pending
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error obteniendo órdenes pendientes: {str(e)}")


@router.delete("/cancel-order/{symbol}/{order_id}")
async def cancel_pending_order(
    symbol: str,
    order_id: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Cancelar una orden pendiente específica.
    """
    verify_token(token)
    
    client = get_binance_client()
    
    if not client.is_connected():
        raise HTTPException(status_code=503, detail="No conectado a Binance")
    
    try:
        result = client.client.cancel_order(
            symbol=symbol.upper(),
            orderId=int(order_id)
        )
        
        return {
            "success": True,
            "message": f"✅ Orden {order_id} cancelada",
            "order_id": result['orderId'],
            "symbol": result['symbol'],
            "status": result['status']
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error cancelando orden: {str(e)}")


@router.delete("/cancel-all-orders/{symbol}")
async def cancel_all_pending_orders(
    symbol: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Cancelar TODAS las órdenes pendientes de un símbolo.
    
    ⚠️ Usar con precaución!
    """
    verify_token(token)
    
    client = get_binance_client()
    
    if not client.is_connected():
        raise HTTPException(status_code=503, detail="No conectado a Binance")
    
    try:
        result = client.client.cancel_open_orders(symbol=symbol.upper())
        
        return {
            "success": True,
            "message": f"✅ Todas las órdenes de {symbol} canceladas",
            "cancelled_orders": len(result) if isinstance(result, list) else 1
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error cancelando órdenes: {str(e)}")
