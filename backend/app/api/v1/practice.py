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


# === Storage en memoria (en producción usar Redis/DB) ===

virtual_wallets: Dict[int, dict] = {}


def get_or_create_wallet(user_id: int) -> dict:
    """Obtener o crear wallet virtual para usuario"""
    if user_id not in virtual_wallets:
        virtual_wallets[user_id] = {
            "initial_capital": 100.0,
            "balances": {"USDT": 100.0},
            "avg_prices": {},  # Para calcular P&L por posición
            "trades": [],
            "created_at": datetime.utcnow().isoformat()
        }
    return virtual_wallets[user_id]


def calculate_wallet_value(wallet: dict) -> float:
    """Calcular valor total de la wallet virtual en USD"""
    binance = get_binance_client()
    prices = binance.get_all_prices()
    total = 0.0
    
    for asset, amount in wallet["balances"].items():
        if asset in ["USDT", "BUSD", "USD"]:
            total += amount
        else:
            symbol = f"{asset}USDT"
            if symbol in prices:
                total += amount * prices[symbol]
    
    return total


# === Endpoints ===

@router.get("/wallet", response_model=VirtualWallet)
async def get_virtual_wallet(token: str = Depends(oauth2_scheme)):
    """
    Obtener wallet virtual para modo práctica.
    
    Empiezas con $100 USDT virtuales.
    Los precios son REALES de Binance.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(user_id)
    binance = get_binance_client()
    prices = binance.get_all_prices()
    
    # Calcular balances con valores USD
    balances = []
    total_usd = 0.0
    
    for asset, amount in wallet["balances"].items():
        if amount <= 0:
            continue
            
        if asset in ["USDT", "BUSD", "USD"]:
            usd_value = amount
        else:
            symbol = f"{asset}USDT"
            price = prices.get(symbol, 0)
            usd_value = amount * price
        
        total_usd += usd_value
        
        balances.append({
            "asset": asset,
            "amount": round(amount, 8),
            "usd_value": round(usd_value, 2),
            "avg_buy_price": wallet["avg_prices"].get(asset)
        })
    
    # Ordenar por valor
    balances.sort(key=lambda x: x["usd_value"], reverse=True)
    
    # Calcular P&L
    initial = wallet["initial_capital"]
    pnl = total_usd - initial
    pnl_percent = (pnl / initial) * 100 if initial > 0 else 0
    
    # Win rate
    trades = wallet["trades"]
    winning = len([t for t in trades if t.get("pnl", 0) > 0])
    win_rate = (winning / len(trades) * 100) if trades else None
    
    return {
        "initial_capital": initial,
        "current_value": round(total_usd, 2),
        "pnl": round(pnl, 2),
        "pnl_percent": round(pnl_percent, 2),
        "balances": balances,
        "trades_count": len(trades),
        "win_rate": round(win_rate, 1) if win_rate else None
    }


@router.post("/order")
async def create_virtual_order(order: VirtualOrder, token: str = Depends(oauth2_scheme)):
    """
    Crear orden virtual (simulada).
    
    Se ejecuta instantáneamente con precio REAL de Binance.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(user_id)
    binance = get_binance_client()
    
    symbol = order.symbol.upper()
    side = order.side.upper()
    
    # Extraer base y quote (ej: BTCUSDT -> BTC, USDT)
    base = symbol.replace("USDT", "").replace("BUSD", "")
    quote = "USDT"
    
    # Obtener precio REAL de Binance
    current_price = order.price
    if not current_price:
        current_price = binance.get_price(symbol)
        if not current_price:
            raise HTTPException(status_code=400, detail=f"No se pudo obtener precio de {symbol}")
    
    if side == "BUY":
        # === COMPRAR: Gastar USDT, recibir cripto ===
        cost = order.quantity * current_price
        
        usdt_balance = wallet["balances"].get(quote, 0)
        if usdt_balance < cost:
            raise HTTPException(
                status_code=400, 
                detail=f"Saldo USDT insuficiente. Tienes ${usdt_balance:.2f}, necesitas ${cost:.2f}"
            )
        
        # Restar USDT
        wallet["balances"][quote] = usdt_balance - cost
        
        # Añadir cripto
        old_amount = wallet["balances"].get(base, 0)
        new_amount = old_amount + order.quantity
        wallet["balances"][base] = new_amount
        
        # Calcular precio promedio de compra
        if base not in wallet["avg_prices"]:
            wallet["avg_prices"][base] = current_price
        else:
            old_avg = wallet["avg_prices"][base]
            wallet["avg_prices"][base] = ((old_avg * old_amount) + (current_price * order.quantity)) / new_amount
        
        pnl = None  # No hay P&L en compra
        
    else:  # SELL
        # === VENDER: Gastar cripto, recibir USDT ===
        crypto_balance = wallet["balances"].get(base, 0)
        if crypto_balance < order.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Saldo {base} insuficiente. Tienes {crypto_balance:.8f}, quieres vender {order.quantity}"
            )
        
        # Calcular P&L
        avg_price = wallet["avg_prices"].get(base, current_price)
        pnl = (current_price - avg_price) * order.quantity
        
        # Restar cripto
        wallet["balances"][base] = crypto_balance - order.quantity
        
        # Añadir USDT
        received = order.quantity * current_price
        wallet["balances"][quote] = wallet["balances"].get(quote, 0) + received
        
        # Limpiar avg_price si vendimos todo
        if wallet["balances"][base] <= 0:
            wallet["balances"].pop(base, None)
            wallet["avg_prices"].pop(base, None)
    
    # Registrar trade
    trade = {
        "id": len(wallet["trades"]) + 1,
        "symbol": symbol,
        "side": side,
        "quantity": order.quantity,
        "price": current_price,
        "total": order.quantity * current_price,
        "pnl": round(pnl, 2) if pnl else None,
        "timestamp": datetime.utcnow().isoformat()
    }
    wallet["trades"].append(trade)
    
    return {
        "message": f"✅ {side} {order.quantity} {base} @ ${current_price:,.2f}",
        "trade": trade,
        "new_balance": {
            base: wallet["balances"].get(base, 0),
            quote: wallet["balances"].get(quote, 0)
        }
    }


@router.get("/trades", response_model=List[VirtualTrade])
async def get_virtual_trades(token: str = Depends(oauth2_scheme)):
    """
    Obtener historial de trades virtuales.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(user_id)
    
    trades = []
    for t in wallet["trades"]:
        trades.append({
            **t,
            "timestamp": datetime.fromisoformat(t["timestamp"]) if isinstance(t["timestamp"], str) else t["timestamp"]
        })
    
    # Más recientes primero
    trades.reverse()
    return trades


@router.get("/stats", response_model=TradeStats)
async def get_trade_stats(token: str = Depends(oauth2_scheme)):
    """
    Obtener estadísticas de trading del modo práctica.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(user_id)
    trades = wallet["trades"]
    
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
    
    # Solo trades con P&L (ventas)
    sell_trades = [t for t in trades if t.get("pnl") is not None]
    
    winning = [t for t in sell_trades if t["pnl"] > 0]
    losing = [t for t in sell_trades if t["pnl"] < 0]
    
    total_pnl = sum(t["pnl"] for t in sell_trades)
    win_rate = (len(winning) / len(sell_trades) * 100) if sell_trades else 0
    
    pnls = [t["pnl"] for t in sell_trades]
    
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
async def reset_virtual_wallet(token: str = Depends(oauth2_scheme)):
    """
    Resetear wallet virtual a $100 USDT iniciales.
    
    ⚠️ Borra todo el historial de trades.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    virtual_wallets[user_id] = {
        "initial_capital": 100.0,
        "balances": {"USDT": 100.0},
        "avg_prices": {},
        "trades": [],
        "created_at": datetime.utcnow().isoformat()
    }
    
    return {
        "message": "✅ Wallet virtual reseteada a $100 USDT",
        "balance": 100.0
    }


@router.get("/position/{symbol}")
async def get_position(symbol: str, token: str = Depends(oauth2_scheme)):
    """
    Obtener posición actual de un símbolo con P&L no realizado.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(user_id)
    binance = get_binance_client()
    
    symbol = symbol.upper()
    base = symbol.replace("USDT", "").replace("BUSD", "")
    
    amount = wallet["balances"].get(base, 0)
    if amount <= 0:
        return {"symbol": symbol, "position": None, "message": "Sin posición"}
    
    current_price = binance.get_price(symbol)
    avg_price = wallet["avg_prices"].get(base, current_price)
    
    unrealized_pnl = (current_price - avg_price) * amount
    unrealized_pnl_percent = ((current_price - avg_price) / avg_price) * 100 if avg_price else 0
    
    return {
        "symbol": symbol,
        "amount": amount,
        "avg_buy_price": avg_price,
        "current_price": current_price,
        "value_usd": amount * current_price,
        "unrealized_pnl": round(unrealized_pnl, 2),
        "unrealized_pnl_percent": round(unrealized_pnl_percent, 2)
    }
