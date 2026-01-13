"""
SIC Ultra - Trading Endpoints

Órdenes de trading con soporte para modo PRÁCTICA y REAL.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

from app.api.v1.auth import oauth2_scheme, verify_token
from app.infrastructure.binance.client import get_binance_client
from app.infrastructure.binance.real_executor import get_real_executor, OrderSide


router = APIRouter()


# === Enums ===

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderMode(str, Enum):
    PRACTICE = "practice"
    REAL = "real"


# === Schemas ===

class OrderCreate(BaseModel):
    symbol: str
    side: str  # BUY or SELL
    type: OrderType = OrderType.MARKET
    quantity: float
    price: Optional[float] = None  # Solo para LIMIT
    stop_loss: Optional[float] = None  # OBLIGATORIO para modo REAL
    take_profit: Optional[float] = None
    mode: OrderMode = OrderMode.PRACTICE  # Por defecto práctica


class OrderResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[str] = None
    mode: str
    checks: Optional[List] = None


# === Endpoints ===

@router.post("/order", response_model=OrderResponse)
async def create_order(order: OrderCreate, token: str = Depends(oauth2_scheme)):
    """
    Crear orden de trading.
    
    - mode: "practice" (virtual) o "real" (dinero real)
    - stop_loss: OBLIGATORIO para modo real
    
    ⚠️ MODO REAL: Ejecuta órdenes con dinero REAL en Binance
    """
    verify_token(token)
    
    symbol = order.symbol.upper()
    side = order.side.upper()
    
    if order.mode == OrderMode.REAL:
        # === MODO BATALLA REAL ===
        
        if not order.stop_loss:
            raise HTTPException(
                status_code=400,
                detail="🛡️ Stop-loss es OBLIGATORIO en modo real"
            )
        
        executor = get_real_executor()
        
        # Verificar estado de riesgo
        risk_status = executor.get_risk_status()
        if not risk_status["trading_enabled"]:
            raise HTTPException(
                status_code=429,
                detail=f"❌ Límite diario alcanzado ({risk_status['daily_orders']}/{risk_status['max_daily_orders']} órdenes)"
            )
        
        # Ejecutar orden real
        result = executor.execute_market_order(
            symbol=symbol,
            side=OrderSide(side),
            quantity=order.quantity,
            stop_loss=order.stop_loss
        )
        
        if not result["success"]:
            return {
                "success": False,
                "message": result.get("error", "Error desconocido"),
                "mode": "real",
                "checks": result.get("all_checks") or result.get("failed_checks")
            }
        
        return {
            "success": True,
            "message": f"✅ Orden REAL ejecutada: {side} {order.quantity} {symbol}",
            "order_id": result.get("order", {}).get("orderId"),
            "mode": "real",
            "checks": result.get("checks")
        }
    
    else:
        # === MODO PRÁCTICA ===
        # Redirigir a /practice/order
        return {
            "success": True,
            "message": f"🎮 Usa /api/v1/practice/order para órdenes virtuales",
            "mode": "practice",
            "checks": None
        }


@router.get("/risk-status")
async def get_risk_status(token: str = Depends(oauth2_scheme)):
    """
    Obtener estado actual de las protecciones de riesgo.
    """
    verify_token(token)
    
    executor = get_real_executor()
    status = executor.get_risk_status()
    
    return {
        **status,
        "timestamp": datetime.utcnow()
    }


@router.get("/orders")
async def get_orders(
    symbol: Optional[str] = None,
    limit: int = 50,
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener historial de órdenes de Binance.
    """
    verify_token(token)
    
    client = get_binance_client()
    
    if not client.is_connected():
        return {"orders": [], "message": "No conectado a Binance"}
    
    try:
        if symbol:
            orders = client.client.get_all_orders(symbol=symbol.upper(), limit=limit)
        else:
            # Obtener órdenes de símbolos principales
            orders = []
            for sym in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
                try:
                    sym_orders = client.client.get_all_orders(symbol=sym, limit=10)
                    orders.extend(sym_orders)
                except:
                    pass
        
        return {"orders": orders[:limit], "count": len(orders)}
    except Exception as e:
        return {"orders": [], "error": str(e)}


@router.delete("/order/{symbol}/{order_id}")
async def cancel_order(
    symbol: str,
    order_id: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Cancelar una orden pendiente.
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
        return {"success": True, "message": f"Orden {order_id} cancelada", "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/candles/{symbol}")
async def get_candles(
    symbol: str,
    interval: str = "1h",
    limit: int = 100,
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener velas/candlesticks REALES para gráficos.
    """
    verify_token(token)
    
    client = get_binance_client()
    symbol = symbol.upper()
    
    valid_intervals = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
    if interval not in valid_intervals:
        raise HTTPException(status_code=400, detail=f"Interval inválido. Usa: {valid_intervals}")
    
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
    
    symbols = [
        {"symbol": "BTCUSDT", "base": "BTC", "quote": "USDT", "name": "Bitcoin"},
        {"symbol": "ETHUSDT", "base": "ETH", "quote": "USDT", "name": "Ethereum"},
        {"symbol": "BNBUSDT", "base": "BNB", "quote": "USDT", "name": "Binance Coin"},
        {"symbol": "SOLUSDT", "base": "SOL", "quote": "USDT", "name": "Solana"},
        {"symbol": "XRPUSDT", "base": "XRP", "quote": "USDT", "name": "Ripple"},
        {"symbol": "ADAUSDT", "base": "ADA", "quote": "USDT", "name": "Cardano"},
    ]
    
    return {"symbols": symbols}


@router.get("/depth/{symbol}")
async def get_market_depth(
    symbol: str, 
    limit: int = 20, 
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener Profundidad de Mercado (Order Book).
    Retorna bids (compras) y asks (ventas).
    """
    verify_token(token)
    client = get_binance_client()
    
    depth = client.get_order_book(symbol, limit)
    
    # Procesar para mostrar acumulado? Por ahora raw.
    return {
        "symbol": symbol.upper(),
        "bids": depth.get("bids", []),
        "asks": depth.get("asks", []),
        "timestamp": datetime.utcnow()
    }


@router.get("/funding/{symbol}")
async def get_funding_data(
    symbol: str, 
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener Funding Rate y Precios de Marca (Futuros).
    Vital para detectar sentimiento y liquidaciones.
    """
    verify_token(token)
    client = get_binance_client()
    
    funding = client.get_funding_rate(symbol)
    
    if not funding:
        # Fallback si no hay datos de futuros (ej: par spot sin contratos)
        # O devolver error 404
        return {"symbol": symbol, "fundingRate": 0, "note": "No futures data"}
        
    return funding
