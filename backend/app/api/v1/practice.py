"""
SIC Ultra - Modo Práctica

Trading con $100 virtuales para probar estrategias sin riesgo.
Usa precios REALES de Binance pero con dinero ficticio.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import json

from sqlalchemy.orm import Session, joinedload
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import VirtualWallet as VirtualWalletModel, VirtualTrade as VirtualTradeModel

from app.api.v1.auth import oauth2_scheme, verify_token
from app.infrastructure.binance.client import get_binance_client
from loguru import logger


router = APIRouter()


# === Schemas ===

class VirtualBalance(BaseModel):
    asset: str
    amount: float
    usd_value: float
    avg_buy_price: Optional[float] = None


class VirtualWallet(BaseModel):
    initial_capital: float = 100.0
    current_value: float
    total_usd: Optional[float] = None  # Alias for frontend compatibility
    pnl: float
    pnl_percent: float
    balances: List[VirtualBalance]
    trades_count: int
    win_rate: Optional[float] = None


class VirtualOrder(BaseModel):
    symbol: str
    side: str  # BUY/SELL
    quantity: float
    price: Optional[float] = None  # None = precio de mercado actual


class VirtualTrade(BaseModel):
    id: int
    symbol: str
    side: str
    quantity: float
    price: float
    total: float
    pnl: Optional[float] = None
    timestamp: datetime


class VirtualPendingOrderResponse(BaseModel):
    id: str
    symbol: str
    type: str
    side: str
    quantity: float
    price: Optional[float]
    stop_price: Optional[float]
    status: str
    created_at: str


class TradeStats(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    best_trade: Optional[float] = None
    worst_trade: Optional[float] = None
    # Gamification Fields
    level: int = 1
    xp: int = 0
    next_level_xp: int = 100
    mastered_patterns: List[str] = []
    
    
# === Helper Functions ===

def calculate_level(total_trades: int, total_pnl: float, win_rate: float) -> dict:
    """Calcular nivel y XP basado en stats"""
    # XP base por trade
    base_xp = total_trades * 50
    
    # XP por rentabilidad (1 XP por cada $10 de profit, pero no negativo)
    pnl_xp = max(0, int(total_pnl / 10))
    
    # Bonus XP por winrate sostenido (si > 50%)
    win_rate_bonus = int(total_trades * win_rate) if win_rate > 50 else 0
    
    total_xp = base_xp + pnl_xp + win_rate_bonus
    
    # Nivel formula: XP = Level^2 * 100
    # Level = Sqrt(XP / 100)
    import math
    level = int(math.sqrt(total_xp / 100)) + 1
    
    # XP para siguiente nivel
    current_level_xp_start = ((level - 1) ** 2) * 100
    next_level_xp_req = (level ** 2) * 100
    
    points_in_level = total_xp - current_level_xp_start
    points_needed = next_level_xp_req - current_level_xp_start
    
    # Progreso absoluto
    return {
        "level": level,
        "xp": total_xp,
        "next_level_xp": next_level_xp_req,
        "progress_percent": (points_in_level / points_needed * 100) if points_needed > 0 else 0
    }

def analyze_patterns(trades: List[VirtualTradeModel]) -> List[str]:
    """
    Analizar patrones dominados basado en historial.
    Por ahora mock-logic inteligente: Si tiene > 3 trades ganadores, asumimos dominio de básicos.
    En v2, esto leería tags de los trades si existieran.
    """
    patterns = []
    winning = [t for t in trades if (t.pnl or 0) > 0]
    
    if len(winning) >= 3:
        patterns.append("RSI Divergence")
    if len(winning) >= 10:
        patterns.append("MACD Cross")
    if len(winning) >= 20:
        patterns.append("Support/Resistance")
    if len(winning) >= 50:
        patterns.append("Breakout Master")
        
    return patterns


# ... (get_or_create_wallet remains the same) ...


@router.get("/stats", response_model=TradeStats)
async def get_trade_stats(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de trading del modo práctica con Gamificación.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(db, user_id)
    trades = db.query(VirtualTradeModel).filter(VirtualTradeModel.wallet_id == wallet.id).all()
    
    if not trades:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "best_trade": None,
            "worst_trade": None,
            "level": 1,
            "xp": 0,
            "next_level_xp": 100,
            "mastered_patterns": []
        }
    
    # Solo trades con P&L (ventas) - en este modelo simple, asumimos PNL en ventas
    sell_trades = [t for t in trades if t.side == 'SELL']
    
    total_pnl = sum(t.pnl for t in sell_trades)
    winning = [t for t in sell_trades if t.pnl > 0]
    losing = [t for t in sell_trades if t.pnl < 0]
    
    win_rate = (len(winning) / len(sell_trades) * 100) if sell_trades else 0
    
    pnls = [t.pnl for t in sell_trades]
    
    # Calcular Gamificación
    gamification = calculate_level(len(sell_trades), total_pnl, win_rate)
    patterns = analyze_patterns(sell_trades)
    
    return {
        "total_trades": len(trades), # Contamos todos (buy+sell) para volumen
        "winning_trades": len(winning),
        "losing_trades": len(losing),
        "win_rate": round(win_rate, 1),
        "total_pnl": round(total_pnl, 2),
        "best_trade": max(pnls) if pnls else None,
        "worst_trade": min(pnls) if pnls else None,
        "level": gamification["level"],
        "xp": gamification["xp"],
        "next_level_xp": gamification["next_level_xp"],
        "mastered_patterns": patterns
    }


@router.post("/reset")
async def reset_virtual_wallet(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Resetear wallet virtual a $100 USDT iniciales.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(db, user_id)
    
    # Reset balances
    wallet.balances = json.dumps({"USDT": 100.0})
    wallet.reset_at = datetime.utcnow()
    
    # Delete trades
    db.query(VirtualTradeModel).filter(VirtualTradeModel.wallet_id == wallet.id).delete()
    
    db.commit()
    
    return {
        "message": "✅ Wallet virtual reseteada a $100 USDT",
        "balance": 100.0
    }


@router.get("/position/{symbol}")
async def get_position(
    symbol: str, 
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Obtener posición actual de un símbolo.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(db, user_id)
    balances = json.loads(wallet.balances)
    binance = get_binance_client()
    
    symbol = symbol.upper()
    base = symbol.replace("USDT", "").replace("BUSD", "")
    
    amount = float(balances.get(base, 0))
    if amount <= 0:
        return {"symbol": symbol, "position": None, "message": "Sin posición"}
    
    current_price = binance.get_price(symbol)
    
    # TODO: Implementar Avg Price real
    avg_price = current_price 
    
    unrealized_pnl = (current_price - avg_price) * amount
    unrealized_pnl_percent = 0.0
    
    return {
        "symbol": symbol,
        "amount": amount,
        "avg_buy_price": avg_price,
        "current_price": current_price,
        "value_usd": amount * current_price,
        "unrealized_pnl": round(unrealized_pnl, 2),
        "unrealized_pnl_percent": round(unrealized_pnl_percent, 2)
    }
