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
    # Métricas de Trading
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # P&L y ROI
    total_pnl: float  # P&L realizado (de trades cerrados)
    unrealized_pnl: float = 0  # P&L no realizado (posiciones abiertas)
    roi_percent: float = 0  # Return on Investment %
    
    # Capital
    initial_capital: float = 100.0
    current_value: float = 0  # Valor actual del portafolio
    
    # Detalles de trades
    best_trade: Optional[float] = None
    worst_trade: Optional[float] = None
    avg_trade: Optional[float] = None
    
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
# === Wallet Functions ===

def get_or_create_wallet(db: Session, user_id: int) -> VirtualWalletModel:
    """
    Obtener o crear wallet virtual para un usuario.
    Inicializa con $100 USD virtuales.
    """
    wallet = db.query(VirtualWalletModel).filter(VirtualWalletModel.user_id == user_id).first()
    
    if not wallet:
        logger.info(f"🆕 Creando wallet virtual para usuario {user_id}")
        wallet = VirtualWalletModel(
            user_id=user_id,
            balances=json.dumps({"USDT": 100.0}),
            created_at=datetime.utcnow()
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        logger.success(f"✅ Wallet virtual creada con $100 USDT")
    
    return wallet


@router.get("/wallet", response_model=VirtualWallet)
async def get_virtual_wallet(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Obtener balance de la wallet virtual (modo práctica).
    Retorna el balance actual y el historial del usuario.
    """
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    user_id = payload.get("user_id", 1)
    wallet = get_or_create_wallet(db, user_id)
    
    # Parse balances
    balances_dict = json.loads(wallet.balances) if wallet.balances else {"USDT": 100.0}
    
    # Get ALL prices in ONE call (much faster than individual calls)
    binance = get_binance_client()
    all_prices = binance.get_all_prices()  # Returns {"BTCUSDT": 87000.0, "ETHUSDT": 2900.0, ...}
    
    formatted_balances = []
    total_usd = 0.0
    
    for asset, amount in balances_dict.items():
        if amount <= 0:
            continue
            
        if asset == "USDT":
            usd_value = amount
        else:
            symbol = f"{asset}USDT"
            price = all_prices.get(symbol, 0)
            usd_value = amount * price
        
        total_usd += usd_value
        formatted_balances.append(VirtualBalance(
            asset=asset,
            amount=amount,
            usd_value=round(usd_value, 2)
        ))
    
    # Calculate PNL
    initial_capital = 100.0
    pnl = total_usd - initial_capital
    pnl_percent = (pnl / initial_capital) * 100 if initial_capital > 0 else 0
    
    # Count trades
    trades_count = db.query(VirtualTradeModel).filter(VirtualTradeModel.wallet_id == wallet.id).count()
    
    # Calculate win rate
    sell_trades = db.query(VirtualTradeModel).filter(
        VirtualTradeModel.wallet_id == wallet.id,
        VirtualTradeModel.side == "SELL"
    ).all()
    winning = [t for t in sell_trades if (t.pnl or 0) > 0]
    win_rate = (len(winning) / len(sell_trades) * 100) if sell_trades else 0
    
    return VirtualWallet(
        initial_capital=initial_capital,
        current_value=round(total_usd, 2),
        total_usd=round(total_usd, 2),  # Alias for frontend
        pnl=round(pnl, 2),
        pnl_percent=round(pnl_percent, 2),
        balances=formatted_balances,
        trades_count=trades_count,
        win_rate=round(win_rate, 1)
    )


def require_valid_token(token: str) -> dict:
    """Verifica token y lanza excepción si es inválido."""
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return payload


@router.get("/stats", response_model=TradeStats)
async def get_trade_stats(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de trading del modo práctica con ROI y métricas profesionales.
    """
    payload = require_valid_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(db, user_id)
    trades = db.query(VirtualTradeModel).filter(VirtualTradeModel.wallet_id == wallet.id).all()
    balances = json.loads(wallet.balances) if wallet.balances else {"USDT": 100.0}
    binance = get_binance_client()
    
    # Calcular valor actual del portafolio
    current_value = float(balances.get("USDT", 0))
    unrealized_pnl = 0
    
    for asset, amount in balances.items():
        if asset != "USDT" and float(amount) > 0:
            try:
                price = binance.get_price(f"{asset}USDT")
                asset_value = float(amount) * price
                current_value += asset_value
            except:
                pass
    
    # Capital inicial
    initial_capital = wallet.initial_capital or 100.0
    
    # Calcular ROI
    roi_percent = ((current_value - initial_capital) / initial_capital) * 100 if initial_capital > 0 else 0
    total_pnl = current_value - initial_capital
    
    if not trades:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_pnl": round(total_pnl, 2),
            "unrealized_pnl": 0,
            "roi_percent": round(roi_percent, 2),
            "initial_capital": initial_capital,
            "current_value": round(current_value, 2),
            "best_trade": None,
            "worst_trade": None,
            "avg_trade": None,
            "level": 1,
            "xp": 0,
            "next_level_xp": 100,
            "mastered_patterns": []
        }
    
    # Calcular P&L no realizado para posiciones abiertas (BUY sin SELL correspondiente)
    buy_trades = [t for t in trades if t.side == 'BUY']
    sell_trades = [t for t in trades if t.side == 'SELL']
    
    for buy in buy_trades:
        try:
            current_price = binance.get_price(buy.symbol)
            unrealized_pnl += (current_price - buy.price) * buy.quantity
        except:
            pass
    
    # Calcular estadísticas de trades cerrados (ventas)
    realized_pnl = sum(t.pnl for t in sell_trades if t.pnl)
    winning = [t for t in sell_trades if t.pnl and t.pnl > 0]
    losing = [t for t in sell_trades if t.pnl and t.pnl < 0]
    
    win_rate = (len(winning) / len(sell_trades) * 100) if sell_trades else 0
    
    pnls = [t.pnl for t in sell_trades if t.pnl]
    
    # Calcular Gamificación
    gamification = calculate_level(len(trades), total_pnl, win_rate)
    patterns = analyze_patterns(sell_trades)
    
    return {
        "total_trades": len(trades),
        "winning_trades": len(winning),
        "losing_trades": len(losing),
        "win_rate": round(win_rate, 1),
        "total_pnl": round(total_pnl, 2),
        "unrealized_pnl": round(unrealized_pnl, 2),
        "roi_percent": round(roi_percent, 2),
        "initial_capital": initial_capital,
        "current_value": round(current_value, 2),
        "best_trade": round(max(pnls), 2) if pnls else None,
        "worst_trade": round(min(pnls), 2) if pnls else None,
        "avg_trade": round(sum(pnls) / len(pnls), 2) if pnls else None,
        "level": gamification["level"],
        "xp": gamification["xp"],
        "next_level_xp": gamification["next_level_xp"],
        "mastered_patterns": patterns
    }


class DepositRequest(BaseModel):
    asset: str
    amount: float


@router.post("/deposit")
async def deposit_funds(
    deposit: DepositRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Depositar fondos virtuales en modo práctica.
    Útil para testear operaciones de venta.
    """
    payload = require_valid_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(db, user_id)
    balances = json.loads(wallet.balances) if wallet.balances else {"USDT": 100.0}
    
    asset = deposit.asset.upper()
    current = float(balances.get(asset, 0))
    balances[asset] = current + deposit.amount
    
    wallet.balances = json.dumps(balances)
    db.commit()
    
    logger.success(f"💰 Depositado {deposit.amount} {asset} en wallet de usuario {user_id}")
    
    return {
        "message": f"✅ Depositado {deposit.amount} {asset}",
        "asset": asset,
        "new_balance": balances[asset],
        "all_balances": balances
    }


@router.post("/deposit-all-cryptos")
async def deposit_all_cryptos(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Depositar $50 equivalentes en las principales criptomonedas.
    Ideal para configurar un ambiente de prueba completo.
    """
    payload = require_valid_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(db, user_id)
    balances = json.loads(wallet.balances) if wallet.balances else {"USDT": 100.0}
    binance = get_binance_client()
    
    # Cryptos principales con $20 cada una (Solicitud usuario)
    cryptos = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOT", "DOGE", "LINK", "BNB", "MATIC"]
    deposited = {}
    
    for crypto in cryptos:
        try:
            price = binance.get_price(f"{crypto}USDT")
            amount = 20.0 / price  # $20 equivalente
            current = float(balances.get(crypto, 0))
            balances[crypto] = round(current + amount, 8)
            deposited[crypto] = {
                "amount": round(amount, 8),
                "usd_value": 20.0,
                "price": price
            }
        except Exception as e:
            logger.warning(f"No se pudo obtener precio de {crypto}: {e}")
            continue
    
    # Añadir USDT adicional
    balances["USDT"] = float(balances.get("USDT", 100)) + 500
    deposited["USDT"] = {"amount": 500, "usd_value": 500}
    
    wallet.balances = json.dumps(balances)
    db.commit()
    
    logger.success(f"💰 Depositadas {len(deposited)} criptos para usuario {user_id}")
    
    return {
        "message": f"✅ Depositadas {len(deposited)} criptomonedas",
        "deposited": deposited,
        "total_deposited_usd": sum(d.get("usd_value", 0) for d in deposited.values()),
        "all_balances": balances
    }


class OrderRequest(BaseModel):
    symbol: str
    side: str  # BUY or SELL
    type: str = "MARKET"  # MARKET, LIMIT, OCO
    quantity: float
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@router.post("/order")
async def execute_virtual_order(
    order: OrderRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Ejecutar una orden virtual (compra/venta) en modo práctica.
    """
    payload = require_valid_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(db, user_id)
    balances = json.loads(wallet.balances) if wallet.balances else {"USDT": 100.0}
    binance = get_binance_client()
    
    symbol = order.symbol.upper()
    base_asset = symbol.replace("USDT", "").replace("BUSD", "")
    
    # Obtener precio actual si es orden de mercado
    current_price = binance.get_price(symbol)
    execution_price = order.price if order.type == "LIMIT" and order.price else current_price
    
    # Calcular monto total
    total_amount = order.quantity * execution_price
    fee = total_amount * 0.001  # 0.1% fee
    
    # Validar monto mínimo $5
    if total_amount < 5:
        raise HTTPException(status_code=400, detail="El monto mínimo de inversión es $5 USD")
    
    if order.side.upper() == "BUY":
        # Verificar saldo USDT
        usdt_balance = float(balances.get("USDT", 0))
        if usdt_balance < total_amount + fee:
            raise HTTPException(status_code=400, detail=f"Saldo insuficiente. Necesitas ${total_amount + fee:.2f} USDT")
        
        # Ejecutar compra
        balances["USDT"] = round(usdt_balance - total_amount - fee, 2)
        current_asset_balance = float(balances.get(base_asset, 0))
        balances[base_asset] = round(current_asset_balance + order.quantity, 8)
        
        action = "Compra"
        
    elif order.side.upper() == "SELL":
        # Verificar saldo del activo
        asset_balance = float(balances.get(base_asset, 0))
        if asset_balance < order.quantity:
            raise HTTPException(status_code=400, detail=f"Saldo insuficiente. Solo tienes {asset_balance:.8f} {base_asset}")
        
        # Ejecutar venta
        balances[base_asset] = round(asset_balance - order.quantity, 8)
        usdt_balance = float(balances.get("USDT", 0))
        balances["USDT"] = round(usdt_balance + total_amount - fee, 2)
        
        # Limpiar activos con saldo 0
        if balances[base_asset] <= 0.00000001:
            del balances[base_asset]
        
        action = "Venta"
    else:
        raise HTTPException(status_code=400, detail="Side debe ser BUY o SELL")
    
    # Guardar balances actualizados
    wallet.balances = json.dumps(balances)
    
    # Guardar el trade en historial
    # Guardar el trade en historial
    new_trade = VirtualTradeModel(
        wallet_id=wallet.id,
        symbol=symbol,
        side=order.side.upper(),
        type=order.type,
        strategy="AI_SIGNAL" if order.stop_loss or order.take_profit else "MANUAL",
        reason=f"SL: {order.stop_loss}, TP: {order.take_profit}" if order.stop_loss else None,
        quantity=order.quantity,
        price=execution_price,
        pnl=0  # Se calculará abajo si es venta
    )
    
    # === AI LEARNING INTEGRATION ===
    if order.side.upper() == "SELL":
        # Calcular P&L Realizado buscando el trade de compra correspondiente
        # Simplificación FIFO: Buscamos el último BUY de este símbolo
        last_buy = db.query(VirtualTradeModel).filter(
            VirtualTradeModel.wallet_id == wallet.id,
            VirtualTradeModel.symbol == symbol,
            VirtualTradeModel.side == "BUY"
        ).order_by(VirtualTradeModel.created_at.desc()).first()
        
        if last_buy:
            entry_price = last_buy.price
            pnl_amount = (execution_price - entry_price) * order.quantity
            new_trade.pnl = pnl_amount
            
            # Notificar al Agente para que aprenda
            try:
                from app.ml.trading_agent import get_trading_agent
                agent = get_trading_agent()
                
                # Intentar recuperar metadatos de señal si existen
                signals_used = ["MANUAL"]
                patterns_detected = []
                
                # Si el BUY tenía estrategia AI, intentar deducir (mejorar en v2 con ID de señal)
                if last_buy.strategy == "AI_SIGNAL":
                    signals_used = ["AI_SIGNAL", "RSI", "MACD"] # Placeholder
                
                agent.record_result(
                    trade_id=f"VIRTUAL_{new_trade.id}_{datetime.utcnow().timestamp()}",
                    symbol=symbol,
                    side="LONG", # Asumimos LONG para práctica spot
                    entry_price=entry_price,
                    exit_price=execution_price,
                    pnl=pnl_amount,
                    signals_used=signals_used,
                    patterns_detected=patterns_detected,
                    db_session=db
                )
                logger.info(f"🧠 AI aprendió del trade virtual {symbol}: PnL ${pnl_amount:.2f}")
            except Exception as e:
                logger.error(f"⚠️ Error en aprendizaje AI: {e}")
            
    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)
    
    logger.success(f"📈 {action} virtual: {order.quantity} {base_asset} @ ${execution_price:.2f} (Total: ${total_amount:.2f})")
    
    return {
        "success": True,
        "message": f"✅ {action} ejecutada: {order.quantity:.6f} {base_asset} @ ${execution_price:.2f}",
        "order": {
            "id": new_trade.id,
            "symbol": symbol,
            "side": order.side.upper(),
            "type": order.type,
            "quantity": order.quantity,
            "price": execution_price,
            "total": round(total_amount, 2),
            "fee": round(fee, 2),
            "created_at": new_trade.created_at.isoformat()
        },
        "balances": {
            "USDT": balances.get("USDT", 0),
            base_asset: balances.get(base_asset, 0)
        }
    }


@router.get("/orders")
async def get_virtual_orders(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    limit: int = 50,
    symbol: Optional[str] = None
):
    """
    Obtener historial de órdenes virtuales.
    """
    payload = require_valid_token(token)
    user_id = payload.get("user_id", 1)
    
    wallet = get_or_create_wallet(db, user_id)
    
    # Query base
    query = db.query(VirtualTradeModel).filter(VirtualTradeModel.wallet_id == wallet.id)
    
    # Filtrar por símbolo si se especifica
    if symbol:
        query = query.filter(VirtualTradeModel.symbol == symbol.upper())
    
    # Ordenar por fecha más reciente y limitar
    trades = query.order_by(VirtualTradeModel.created_at.desc()).limit(limit).all()
    
    # Obtener precios actuales para calcular P&L no realizado
    binance = get_binance_client()
    
    orders = []
    for trade in trades:
        try:
            current_price = binance.get_price(trade.symbol)
            # Calcular P&L
            if trade.side == "BUY":
                unrealized_pnl = (current_price - trade.price) * trade.quantity
            else:
                unrealized_pnl = (trade.price - current_price) * trade.quantity
            pnl_percent = (unrealized_pnl / (trade.price * trade.quantity)) * 100
        except:
            current_price = trade.price
            unrealized_pnl = 0
            pnl_percent = 0
        
        orders.append({
            "id": trade.id,
            "symbol": trade.symbol,
            "side": trade.side,
            "type": trade.type,
            "strategy": trade.strategy,
            "quantity": trade.quantity,
            "entry_price": trade.price,
            "current_price": current_price,
            "total": round(trade.price * trade.quantity, 2),
            "pnl": round(unrealized_pnl, 2),
            "pnl_percent": round(pnl_percent, 2),
            "status": "FILLED",
            "created_at": trade.created_at.isoformat()
        })
    
    return {
        "orders": orders,
        "total": len(orders)
    }


@router.post("/reset")
async def reset_virtual_wallet(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Resetear wallet virtual a $100 USDT iniciales.
    """
    payload = require_valid_token(token)
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
    payload = require_valid_token(token)
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
