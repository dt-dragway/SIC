"""
SIC Ultra - Trading Endpoints

Órdenes de trading con soporte para modo PRÁCTICA y REAL.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
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


@router.get("/stats")
async def get_real_trading_stats(token: str = Depends(oauth2_scheme)):
    """
    Obtener estadísticas de trading REAL desde Binance.
    Incluye ROI, P&L, Win Rate basado en órdenes ejecutadas.
    """
    verify_token(token)
    
    client = get_binance_client()
    
    if not client.is_connected():
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "unrealized_pnl": 0,
            "roi_percent": 0,
            "initial_capital": 0,
            "current_value": 0,
            "best_trade": None,
            "worst_trade": None,
            "avg_trade": None,
            "mode": "real",
            "error": "No conectado a Binance"
        }
    
    try:
        # Obtener balance total actual en USD
        current_value = client.get_wallet_value_usd()
        
        # Obtener historial de órdenes de símbolos principales
        all_orders = []
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
        
        for sym in symbols:
            try:
                orders = client.client.get_all_orders(symbol=sym, limit=100)
                # Solo órdenes FILLED
                filled = [o for o in orders if o.get("status") == "FILLED"]
                all_orders.extend(filled)
            except:
                pass
        
        # Calcular estadísticas de trades
        total_trades = len(all_orders)
        
        # Agrupar trades por símbolo y calcular P&L
        pnls = []
        buy_orders = [o for o in all_orders if o.get("side") == "BUY"]
        sell_orders = [o for o in all_orders if o.get("side") == "SELL"]
        
        # Calcular P&L simple basado en ventas
        for sell in sell_orders:
            try:
                sell_total = float(sell.get("cummulativeQuoteQty", 0))
                if sell_total > 0:
                    # Buscar la compra correspondiente más reciente antes de esta venta
                    matching_buys = [b for b in buy_orders 
                                    if b.get("symbol") == sell.get("symbol")
                                    and b.get("time", 0) < sell.get("time", 0)]
                    if matching_buys:
                        # Usar la compra más reciente
                        buy = max(matching_buys, key=lambda x: x.get("time", 0))
                        buy_total = float(buy.get("cummulativeQuoteQty", 0))
                        pnl = sell_total - buy_total
                        pnls.append(pnl)
            except:
                pass
        
        winning = [p for p in pnls if p > 0]
        losing = [p for p in pnls if p < 0]
        total_pnl = sum(pnls)
        win_rate = (len(winning) / len(pnls) * 100) if pnls else 0
        
        # Capital inicial estimado (basado en depósitos) - usamos un valor por defecto
        # En producción, esto debería leerse de los depósitos históricos
        if not pnls:
            initial_capital = current_value
            roi_percent = 0.0
        else:
            initial_capital = max(100, current_value - total_pnl)  # Estimación
            roi_percent = ((current_value - initial_capital) / initial_capital * 100) if initial_capital > 0 else 0
        
        # Calcular nivel de experiencia (Replicando lógica de práctica)
        def calculate_level(total_trades: int, total_pnl: float, win_rate: float) -> dict:
            # XP base por trade
            base_xp = total_trades * 50
            # XP por rentabilidad (1 XP por cada $10 de profit, pero no negativo)
            pnl_xp = max(0, int(total_pnl / 10))
            # Bonus XP por winrate sostenido (si > 50%)
            win_rate_bonus = int(total_trades * win_rate) if win_rate > 50 else 0
            
            total_xp = base_xp + pnl_xp + win_rate_bonus
            
            # Nivel formula: XP = Level^2 * 100
            import math
            level = int(math.sqrt(total_xp / 100)) + 1
            next_level_xp_req = (level ** 2) * 100
            
            return {
                "level": level,
                "xp": total_xp,
                "next_level_xp": next_level_xp_req
            }

        level_stats = calculate_level(total_trades, total_pnl, win_rate)

        return {
            "total_trades": total_trades,
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "win_rate": round(win_rate, 1),
            "total_pnl": round(total_pnl, 2),
            "unrealized_pnl": 0,
            "roi_percent": round(roi_percent, 2),
            "initial_capital": round(initial_capital, 2),
            "current_value": round(current_value, 2),
            "best_trade": round(max(pnls), 2) if pnls else None,
            "worst_trade": round(min(pnls), 2) if pnls else None,
            "avg_trade": round(sum(pnls) / len(pnls), 2) if pnls else None,
            "mode": "real",
            "level": level_stats["level"],
            "xp": level_stats["xp"],
            "next_level_xp": level_stats["next_level_xp"]
        }
        
    except Exception as e:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "unrealized_pnl": 0,
            "roi_percent": 0,
            "initial_capital": 0,
            "current_value": 0,
            "best_trade": None,
            "worst_trade": None,
            "avg_trade": None,
            "mode": "real",
            "error": str(e)
        }


@router.get("/pending-orders")
async def get_pending_orders(
    symbol: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener órdenes abiertas (LIMIT, STOP, etc) desde Binance.
    """
    verify_token(token)
    
    client = get_binance_client()
    
    if not client.is_connected():
        return {"orders": [], "message": "No conectado a Binance"}
    
    try:
        if symbol:
            orders = client.client.get_open_orders(symbol=symbol.upper())
        else:
            orders = client.client.get_open_orders()
            
        # Formatear la respuesta para que coincida con la interfaz PendingOrder
        formatted_orders = [{
            "id": str(o["orderId"]),
            "symbol": o["symbol"],
            "type": o["type"],
            "side": o["side"],
            "quantity": float(o["origQty"]),
            "price": float(o["price"]),
            "stop_price": float(o.get("stopPrice", 0)),
            "status": o["status"],
            "created_at": datetime.fromtimestamp(o["time"] / 1000).isoformat()
        } for o in orders]
        
        return {"orders": formatted_orders, "count": len(formatted_orders)}
    except Exception as e:
        return {"orders": [], "error": str(e)}


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


@router.get("/signals/dashboard")
async def get_signals_dashboard(token: str = Depends(oauth2_scheme)):
    """
    Obtener señales de trading activas para el Dashboard.
    Mapea las direcciones BUY/SELL a LONG/SHORT para compatibilidad con el frontend.
    """
    verify_token(token)
    
    # Obtener el generador de señales
    from app.ml.signal_generator import get_signal_generator
    generator = get_signal_generator()
    
    # Pares principales
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT", "MATICUSDT", "DOGEUSDT"]
    dashboard_signals = []
    
    for symbol in symbols:
        try:
            signal = generator.analyze(symbol)
            if signal and signal.get("type") in ["BUY", "SELL"]:
                direction = "LONG" if signal.get("type") == "BUY" else "SHORT"
                dashboard_signals.append({
                    "symbol": symbol,
                    "type": direction,
                    "entry_price": signal.get("entry_price", 0),
                    "stop_loss": signal.get("stop_loss", 0),
                    "take_profit": signal.get("take_profit", 0),
                    "confidence": signal.get("confidence", 50),
                    "reasoning": signal.get("reasoning", [])
                })
        except:
            pass
            
    return dashboard_signals


class FuturesPositionResponse(BaseModel):
    id: int
    symbol: str
    side: str
    size: float
    entry_price: float
    leverage: int
    margin: float
    liquidation_price: float
    unrealized_pnl: float
    pnl_percent: float
    created_at: datetime


@router.get("/futures/positions", response_model=List[FuturesPositionResponse])
async def get_real_futures_positions(token: str = Depends(oauth2_scheme)):
    """
    Obtener todas las posiciones abiertas en futuros reales de Binance en caliente.
    """
    verify_token(token)
    client = get_binance_client()
    
    if not client.is_connected() or not client.client:
        return []
        
    try:
        # Llamar a la API oficial de futuros de Binance en caliente de forma segura
        raw_positions = client.client.futures_position_information()
        active_positions = []
        
        for idx, pos in enumerate(raw_positions):
            amt = float(pos.get("positionAmt", 0.0))
            if amt != 0.0:
                symbol = pos.get("symbol")
                entry_price = float(pos.get("entryPrice", 0.0))
                leverage = int(pos.get("leverage", 1))
                liquidation_price = float(pos.get("liquidationPrice", 0.0))
                unrealized_pnl = float(pos.get("unrealizedProfit", 0.0))
                
                # Dirección y tamaño absoluto
                side = "LONG" if amt > 0 else "SHORT"
                size = abs(amt)
                
                # Margen aproximado
                margin = float(pos.get("isolatedWallet", 0.0))
                if margin == 0.0:
                    margin = (size * entry_price) / leverage if leverage > 0 else 0.0
                    
                pnl_percent = (unrealized_pnl / margin * 100) if margin > 0 else 0.0
                
                active_positions.append(
                    FuturesPositionResponse(
                        id=idx,
                        symbol=symbol,
                        side=side,
                        size=size,
                        entry_price=entry_price,
                        leverage=leverage,
                        margin=round(margin, 2),
                        liquidation_price=liquidation_price,
                        unrealized_pnl=round(unrealized_pnl, 4),
                        pnl_percent=round(pnl_percent, 2),
                        created_at=datetime.now(timezone.utc).replace(tzinfo=None)
                    )
                )
        return active_positions
    except Exception as e:
        # Silenciar y retornar lista vacía para máxima robustez en producción
        return []
