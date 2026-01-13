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


class TradeStats(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    best_trade: Optional[float] = None
    worst_trade: Optional[float] = None


# === Helper Functions ===

def get_or_create_wallet(db: Session, user_id: int) -> VirtualWalletModel:
    """Obtener o crear wallet virtual para usuario desde BD"""
    wallet = db.query(VirtualWalletModel).filter(VirtualWalletModel.user_id == user_id).first()
    
    if not wallet:
        wallet = VirtualWalletModel(
            user_id=user_id,
            initial_capital=100.0,
            balances=json.dumps({"USDT": 100.0}),
            created_at=datetime.utcnow()
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        
    return wallet


def calculate_wallet_value(wallet: VirtualWalletModel, balances: dict) -> float:
    """Calcular valor total de la wallet virtual en USD"""
    binance = get_binance_client()
    prices = binance.get_all_prices()
    total = 0.0
    
    for asset, amount in balances.items():
        if asset in ["USDT", "BUSD", "USD"]:
            total += amount
        else:
            symbol = f"{asset}USDT"
            if symbol in prices:
                total += amount * prices[symbol]
    
    return total


# === Endpoints ===

@router.get("/wallet", response_model=VirtualWallet)
async def get_virtual_wallet(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Obtener wallet virtual para modo práctica.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(db, user_id)
    balances_dict = json.loads(wallet.balances)
    
    binance = get_binance_client()
    prices = binance.get_all_prices()
    
    # Calcular balances con valores USD
    balances_list = []
    total_usd = 0.0
    
    # Calcular precio promedio desde trades (simple approximation)
    # En una implementación más robusta, guardaríamos avg_price en el JSON de balances
    
    for asset, amount in balances_dict.items():
        if float(amount) <= 0:
            continue
            
        if asset in ["USDT", "BUSD", "USD"]:
            usd_value = float(amount)
        else:
            symbol = f"{asset}USDT"
            price = prices.get(symbol, 0)
            usd_value = float(amount) * price
        
        total_usd += usd_value
        
        balances_list.append({
            "asset": asset,
            "amount": round(float(amount), 8),
            "usd_value": round(usd_value, 2),
            "avg_buy_price": 0 # Simplificado por ahora
        })
    
    # Ordenar por valor
    balances_list.sort(key=lambda x: x["usd_value"], reverse=True)
    
    # Calcular P&L
    initial = wallet.initial_capital
    pnl = total_usd - initial
    pnl_percent = (pnl / initial) * 100 if initial > 0 else 0
    
    # Win rate
    trades = db.query(VirtualTradeModel).filter(VirtualTradeModel.wallet_id == wallet.id).all()
    winning = len([t for t in trades if (t.pnl or 0) > 0])
    win_rate = (winning / len(trades) * 100) if trades else None
    
    return {
        "initial_capital": initial,
        "current_value": round(total_usd, 2),
        "pnl": round(pnl, 2),
        "pnl_percent": round(pnl_percent, 2),
        "balances": balances_list,
        "trades_count": len(trades),
        "win_rate": round(win_rate, 1) if win_rate else None
    }


@router.post("/order")
async def create_virtual_order(
    order: VirtualOrder, 
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Crear orden virtual (simulada).
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(db, user_id)
    balances = json.loads(wallet.balances)
    
    binance = get_binance_client()
    
    symbol = order.symbol.upper()
    side = order.side.upper()
    
    # Extraer base y quote
    base = symbol.replace("USDT", "").replace("BUSD", "")
    quote = "USDT"
    
    # Obtener precio REAL
    current_price = order.price
    if not current_price:
        current_price = binance.get_price(symbol)
        if not current_price:
            raise HTTPException(status_code=400, detail=f"No se pudo obtener precio de {symbol}")
    
    pnl = None
    
    if side == "BUY":
        # === COMPRAR ===
        cost = order.quantity * current_price
        
        usdt_balance = float(balances.get(quote, 0))
        if usdt_balance < cost:
            raise HTTPException(
                status_code=400, 
                detail=f"Saldo USDT insuficiente. Tienes ${usdt_balance:.2f}, necesitas ${cost:.2f}"
            )
        
        # Actualizar balances
        balances[quote] = usdt_balance - cost
        balances[base] = float(balances.get(base, 0)) + order.quantity
        
    else:  # SELL
        # === VENDER ===
        crypto_balance = float(balances.get(base, 0))
        if crypto_balance < order.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Saldo {base} insuficiente. Tienes {crypto_balance:.8f}, quieres vender {order.quantity}"
            )
        
        # Calcular P&L aproximado (precio actual vs precio cuando se compró?)
        # Nota: Para P&L exacto necesitamos FIFO/LIFO o Avg Price guardado.
        # Por ahora simplificamos: PnL = (Precio Venta - Precio Mercado Anterior??)
        # Mejor aproximación: Usar un precio promedio estimado almacenado (TODO: implementar avg_price en JSON)
        
        # Restar cripto
        balances[base] = crypto_balance - order.quantity
        
        # Añadir USDT
        received = order.quantity * current_price
        balances[quote] = float(balances.get(quote, 0)) + received
        
        # Limpiar si es 0
        if balances[base] <= 0:
            balances.pop(base, None)
    
    # Guardar cambios en DB
    wallet.balances = json.dumps(balances)
    
    # Registrar trade
    new_trade = VirtualTradeModel(
        wallet_id=wallet.id,
        symbol=symbol,
        side=side,
        quantity=order.quantity,
        price=current_price,
        pnl=pnl if pnl else 0, # TODO: Calcular PNL real
        created_at=datetime.utcnow()
    )
    db.add(new_trade)
    db.commit()
    
    return {
        "message": f"✅ {side} {order.quantity} {base} @ ${current_price:,.2f}",
        "trade": {
            "id": new_trade.id,
            "symbol": new_trade.symbol,
            "side": new_trade.side,
            "quantity": new_trade.quantity,
            "price": new_trade.price
        },
        "new_balance": balances
    }


@router.get("/trades", response_model=List[VirtualTrade])
async def get_virtual_trades(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Obtener historial de trades virtuales.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(db, user_id)
    trades = db.query(VirtualTradeModel).filter(VirtualTradeModel.wallet_id == wallet.id).order_by(VirtualTradeModel.created_at.desc()).all()
    
    return [{
        "id": t.id,
        "symbol": t.symbol,
        "side": t.side,
        "quantity": t.quantity,
        "price": t.price,
        "total": t.quantity * t.price,
        "pnl": t.pnl,
        "timestamp": t.created_at
    } for t in trades]


@router.get("/stats", response_model=TradeStats)
async def get_trade_stats(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de trading del modo práctica.
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
            "worst_trade": None
        }
    
    # Solo trades con P&L (ventas) - en este modelo simple, asumimos PNL en ventas
    # TODO: Mejorar lógica de PnL en DB
    sell_trades = [t for t in trades if t.side == 'SELL']
    
    # Mock calculation for now as PnL isn't fully tracked yet in this refactor
    total_pnl = sum(t.pnl for t in sell_trades)
    winning = [t for t in sell_trades if t.pnl > 0]
    losing = [t for t in sell_trades if t.pnl < 0]
    
    win_rate = (len(winning) / len(sell_trades) * 100) if sell_trades else 0
    
    pnls = [t.pnl for t in sell_trades]
    
    return {
        "total_trades": len(trades),
        "winning_trades": len(winning),
        "losing_trades": len(losing),
        "win_rate": round(win_rate, 1),
        "total_pnl": round(total_pnl, 2),
        "best_trade": max(pnls) if pnls else None,
        "worst_trade": min(pnls) if pnls else None
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
