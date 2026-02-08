"""
SIC Ultra - Trade Markers API
Endpoints para gestionar marcadores de trades en gráficos
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.api.v1.auth import get_current_user
from app.infrastructure.database.session import get_db
from app.services.trade_markers import get_trade_marker_manager


# Schemas
class TradeMarkerRequest(BaseModel):
    symbol: str = Field(..., description="Símbolo del trade")
    side: str = Field(..., pattern="^(LONG|SHORT)$", description="Lado del trade")
    entry_price: float = Field(..., gt=0, description="Precio de entrada")
    stop_loss: float = Field(..., gt=0, description="Stop loss")
    take_profit: float = Field(..., gt=0, description="Take profit")
    quantity: float = Field(..., gt=0, description="Cantidad")
    confidence: Optional[float] = Field(None, ge=0, le=100, description="Confianza de la señal")
    tier: Optional[str] = Field(None, pattern="^(S|A|B|C)$", description="Tier de la señal")


class TradeMarkerResponse(BaseModel):
    id: str
    symbol: str
    side: str
    entry_price: float
    stop_loss: float
    take_profit: float
    quantity: float
    entry_time: datetime
    status: str
    pnl: Optional[float]
    exit_price: Optional[float]
    exit_time: Optional[datetime]
    confidence: Optional[float]
    tier: Optional[str]


class CloseTradeRequest(BaseModel):
    exit_price: float = Field(..., gt=0, description="Precio de salida")
    pnl: float = Field(..., description="P&L del trade")
    exit_reason: str = Field("MANUAL", pattern="^(MANUAL|STOP_LOSS|TAKE_PROFIT)$", description="Motivo de cierre")


router = APIRouter()


@router.post("/add-marker", response_model=Dict[str, Any])
async def add_trade_marker(
    request: TradeMarkerRequest,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Añade un nuevo marcador de trade al gráfico
    """
    try:
        manager = get_trade_marker_manager()
        
        trade_id = manager.add_trade_marker(
            symbol=request.symbol,
            side=request.side,
            entry_price=request.entry_price,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
            quantity=request.quantity,
            confidence=request.confidence,
            tier=request.tier
        )
        
        return {
            "success": True,
            "trade_id": trade_id,
            "message": f"Marcador de trade añadido para {request.symbol}",
            "marker_data": {
                "symbol": request.symbol,
                "side": request.side,
                "entry_price": request.entry_price,
                "stop_loss": request.stop_loss,
                "take_profit": request.take_profit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error añadiendo marcador: {str(e)}")


@router.post("/close-marker/{trade_id}", response_model=Dict[str, Any])
async def close_trade_marker(
    trade_id: str,
    request: CloseTradeRequest,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cierra un marcador de trade existente
    """
    try:
        manager = get_trade_marker_manager()
        
        success = manager.close_trade_marker(
            trade_id=trade_id,
            exit_price=request.exit_price,
            pnl=request.pnl,
            exit_reason=request.exit_reason
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Trade no encontrado")
        
        return {
            "success": True,
            "trade_id": trade_id,
            "message": f"Trade {trade_id} cerrado",
            "exit_data": {
                "exit_price": request.exit_price,
                "pnl": request.pnl,
                "exit_reason": request.exit_reason
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cerrando trade: {str(e)}")


@router.get("/active-markers/{symbol}", response_model=Dict[str, Any])
async def get_active_markers(
    symbol: str,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene marcadores activos para un símbolo
    """
    try:
        manager = get_trade_marker_manager()
        
        chart_data = manager.get_chart_data(symbol)
        
        return {
            "success": True,
            "symbol": symbol,
            "data": chart_data,
            "message": f"Marcadores activos para {symbol}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo marcadores: {str(e)}")


@router.get("/historical-markers/{symbol}", response_model=Dict[str, Any])
async def get_historical_markers(
    symbol: str,
    days: Optional[int] = 30,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene marcadores históricos para un símbolo
    """
    try:
        manager = get_trade_marker_manager()
        
        historical_trades = manager.get_historical_trades(symbol, days)
        
        # Convertir a dict para respuesta
        trades_data = []
        for trade in historical_trades:
            trade_dict = {
                "id": trade.id,
                "symbol": trade.symbol,
                "side": trade.side,
                "entry_price": trade.entry_price,
                "stop_loss": trade.stop_loss,
                "take_profit": trade.take_profit,
                "quantity": trade.quantity,
                "entry_time": trade.entry_time.isoformat(),
                "status": trade.status,
                "pnl": trade.pnl,
                "exit_price": trade.exit_price,
                "exit_time": trade.exit_time.isoformat() if trade.exit_time else None,
                "confidence": trade.confidence,
                "tier": trade.tier
            }
            trades_data.append(trade_dict)
        
        return {
            "success": True,
            "symbol": symbol,
            "days": days,
            "trades": trades_data,
            "count": len(trades_data),
            "stats": manager._calculate_symbol_stats(symbol)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo históricos: {str(e)}")


@router.get("/chart-data/{symbol}", response_model=Dict[str, Any])
async def get_chart_markers_data(
    symbol: str,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene datos completos para visualización en gráfico
    """
    try:
        manager = get_trade_marker_manager()
        
        chart_data = manager.get_chart_data(symbol)
        
        return {
            "success": True,
            "chart_data": chart_data,
            "message": f"Datos de gráfico para {symbol}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos de gráfico: {str(e)}")


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_trades_dashboard(
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene dashboard completo de trades
    """
    try:
        manager = get_trade_marker_manager()
        
        # Estadísticas generales
        all_active = manager.get_active_trades()
        all_historical = manager.get_historical_trades()
        
        # Calcular stats generales
        total_trades = len(all_active) + len(all_historical)
        completed_trades = [t for t in all_historical if t.pnl is not None]
        
        if completed_trades:
            winning_trades = [t for t in completed_trades if t.pnl > 0]
            win_rate = (len(winning_trades) / len(completed_trades)) * 100
            total_pnl = sum(t.pnl for t in completed_trades)
            avg_pnl = total_pnl / len(completed_trades)
        else:
            win_rate = 0
            total_pnl = 0
            avg_pnl = 0
        
        # Agrupar por símbolo
        symbol_stats = {}
        for trade in all_active + all_historical:
            if trade.symbol not in symbol_stats:
                symbol_stats[trade.symbol] = {
                    'active': 0,
                    'historical': 0,
                    'pnl': 0
                }
            
            if trade.id in manager.active_trades:
                symbol_stats[trade.symbol]['active'] += 1
            else:
                symbol_stats[trade.symbol]['historical'] += 1
                if trade.pnl:
                    symbol_stats[trade.symbol]['pnl'] += trade.pnl
        
        return {
            "success": True,
            "overview": {
                "total_trades": total_trades,
                "active_trades": len(all_active),
                "completed_trades": len(completed_trades),
                "win_rate": round(win_rate, 1),
                "total_pnl": round(total_pnl, 2),
                "avg_pnl": round(avg_pnl, 2)
            },
            "symbol_stats": symbol_stats,
            "recent_activity": [
                {
                    "id": t.id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "status": t.status,
                    "entry_time": t.entry_time.isoformat(),
                    "pnl": t.pnl
                }
                for t in all_historical[:10]  # Últimos 10 trades
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo dashboard: {str(e)}")


@router.delete("/marker/{trade_id}", response_model=Dict[str, Any])
async def delete_trade_marker(
    trade_id: str,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un marcador de trade (solo si está activo)
    """
    try:
        manager = get_trade_marker_manager()
        
        if trade_id in manager.active_trades:
            # Cerrar manualmente sin P&L
            marker = manager.active_trades[trade_id]
            manager.close_trade_marker(
                trade_id=trade_id,
                exit_price=marker.entry_price,
                pnl=0,
                exit_reason='MANUAL'
            )
            
            return {
                "success": True,
                "trade_id": trade_id,
                "message": "Marcador eliminado manualmente"
            }
        else:
            raise HTTPException(status_code=404, detail="Trade no encontrado o ya cerrado")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando marcador: {str(e)}")