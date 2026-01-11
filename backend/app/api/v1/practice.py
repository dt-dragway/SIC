"""
SIC Ultra - Modo Práctica

Trading con $100 virtuales para probar estrategias sin riesgo.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

from app.api.v1.auth import oauth2_scheme, verify_token


router = APIRouter()


# === Schemas ===

class VirtualBalance(BaseModel):
    asset: str
    amount: float
    usd_value: float


class VirtualWallet(BaseModel):
    initial_capital: float = 100.0  # Siempre empezamos con $100
    current_value: float
    pnl: float
    pnl_percent: float
    balances: List[VirtualBalance]
    trades_count: int


class VirtualOrder(BaseModel):
    symbol: str
    side: str  # BUY/SELL
    quantity: float
    price: Optional[float] = None  # None = market price


class VirtualTrade(BaseModel):
    id: int
    symbol: str
    side: str
    quantity: float
    price: float
    pnl: float
    timestamp: datetime


# === Storage temporal (en producción usar Redis/DB) ===
# TODO: Mover a Redis o DB

virtual_wallets = {}  # user_id -> wallet data


def get_or_create_wallet(user_id: int) -> dict:
    """Obtener o crear wallet virtual para usuario"""
    if user_id not in virtual_wallets:
        virtual_wallets[user_id] = {
            "initial_capital": 100.0,
            "balances": {"USDT": 100.0},  # Empezamos con $100 USDT
            "trades": []
        }
    return virtual_wallets[user_id]


# === Endpoints ===

@router.get("/wallet", response_model=VirtualWallet)
async def get_virtual_wallet(token: str = Depends(oauth2_scheme)):
    """
    Obtener wallet virtual para modo práctica.
    
    Empiezas con $100 USDT virtuales.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(user_id)
    
    # Calcular valor actual
    # TODO: Multiplicar por precios reales
    balances = []
    total_usd = 0
    
    for asset, amount in wallet["balances"].items():
        price = 1.0 if asset == "USDT" else 45000.0 if asset == "BTC" else 2500.0
        usd_value = amount * price
        total_usd += usd_value
        balances.append({
            "asset": asset,
            "amount": amount,
            "usd_value": usd_value
        })
    
    pnl = total_usd - wallet["initial_capital"]
    pnl_percent = (pnl / wallet["initial_capital"]) * 100
    
    return {
        "initial_capital": wallet["initial_capital"],
        "current_value": total_usd,
        "pnl": pnl,
        "pnl_percent": pnl_percent,
        "balances": balances,
        "trades_count": len(wallet["trades"])
    }


@router.post("/order")
async def create_virtual_order(order: VirtualOrder, token: str = Depends(oauth2_scheme)):
    """
    Crear orden virtual (simulada).
    
    Se ejecuta instantáneamente con precio de mercado real.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(user_id)
    symbol = order.symbol.upper()
    
    # Extraer base y quote del par (ej: BTCUSDT -> BTC, USDT)
    base = symbol.replace("USDT", "").replace("BUSD", "")
    quote = "USDT"
    
    # TODO: Obtener precio real de Binance
    current_price = order.price or 45000.0  # Placeholder
    
    if order.side.upper() == "BUY":
        # Comprar: gastar USDT, recibir cripto
        cost = order.quantity * current_price
        
        if wallet["balances"].get(quote, 0) < cost:
            raise HTTPException(status_code=400, detail="Saldo USDT insuficiente")
        
        wallet["balances"][quote] = wallet["balances"].get(quote, 0) - cost
        wallet["balances"][base] = wallet["balances"].get(base, 0) + order.quantity
        
    else:  # SELL
        # Vender: gastar cripto, recibir USDT
        if wallet["balances"].get(base, 0) < order.quantity:
            raise HTTPException(status_code=400, detail=f"Saldo {base} insuficiente")
        
        wallet["balances"][base] = wallet["balances"].get(base, 0) - order.quantity
        wallet["balances"][quote] = wallet["balances"].get(quote, 0) + (order.quantity * current_price)
    
    # Registrar trade
    trade = {
        "id": len(wallet["trades"]) + 1,
        "symbol": symbol,
        "side": order.side.upper(),
        "quantity": order.quantity,
        "price": current_price,
        "timestamp": datetime.utcnow().isoformat()
    }
    wallet["trades"].append(trade)
    
    return {
        "message": f"Orden virtual ejecutada: {order.side.upper()} {order.quantity} {base} @ ${current_price}",
        "trade": trade
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
            "pnl": 0,  # TODO: Calcular P&L por trade
            "timestamp": datetime.fromisoformat(t["timestamp"]) if isinstance(t["timestamp"], str) else t["timestamp"]
        })
    
    return trades


@router.post("/reset")
async def reset_virtual_wallet(token: str = Depends(oauth2_scheme)):
    """
    Resetear wallet virtual a $100 USDT iniciales.
    
    Borra todo el historial de trades.
    """
    payload = verify_token(token)
    user_id = payload.get("user_id", 1)
    
    virtual_wallets[user_id] = {
        "initial_capital": 100.0,
        "balances": {"USDT": 100.0},
        "trades": []
    }
    
    return {"message": "Wallet virtual reseteada a $100 USDT"}
