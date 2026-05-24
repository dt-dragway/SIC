"""
SIC Ultra - Modo Práctica

Trading con $100 virtuales para probar estrategias sin riesgo.
Usa precios REALES de Binance pero con dinero ficticio.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import json

from sqlalchemy.orm import Session, joinedload
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import User, VirtualWallet as VirtualWalletModel, VirtualTrade as VirtualTradeModel, VirtualPosition as VirtualPositionModel

from app.api.v1.auth import get_current_user, oauth2_scheme, verify_token
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
    initial_capital: float = 150.0
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


class FuturesOrder(BaseModel):
    symbol: str
    side: str  # LONG, SHORT
    size: float  # Cantidad en cripto
    leverage: int = 1  # Multiplicador

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
    initial_capital: float = 150.0
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
    Inicializa con $50 USDT + $10 en cada una de las 10 criptomonedas recomendadas ($150 USD total).
    """
    wallet = db.query(VirtualWalletModel).filter(VirtualWalletModel.user_id == user_id).first()
    
    if not wallet:
        logger.info(f"🆕 Creando wallet virtual para usuario {user_id}")
        binance = get_binance_client()
        initial_balances = {"USDT": 50.0}
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOTUSDT", "MATICUSDT", "DOGEUSDT", "LINKUSDT"]
        
        for sym in symbols:
            coin = sym.replace("USDT", "")
            try:
                price = binance.get_price(sym)
                if price and price > 0:
                    initial_balances[coin] = round(10.0 / price, 6)
                else:
                    raise ValueError()
            except Exception:
                fallback_prices = {
                    "BTC": 70000.0, "ETH": 3500.0, "BNB": 580.0, "SOL": 170.0,
                    "XRP": 0.50, "ADA": 0.45, "DOT": 6.5, "MATIC": 0.70,
                    "DOGE": 0.15, "LINK": 15.0
                }
                initial_balances[coin] = round(10.0 / fallback_prices.get(coin, 1.0), 6)
                
        wallet = VirtualWalletModel(
            user_id=user_id,
            initial_capital=150.0,
            balances=json.dumps(initial_balances),
            created_at=datetime.utcnow()
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        logger.success(f"✅ Wallet virtual creada con $50 USDT + $10 en c/u de las 10 cripto principales ($150 USD total)")
    
    return wallet


@router.get("/wallet", response_model=VirtualWallet)
async def get_virtual_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener balance de la wallet virtual (modo práctica).
    Retorna el balance actual y el historial del usuario.
    """
    user_id = current_user.id
    wallet = get_or_create_wallet(db, user_id)
    
    # Parse balances
    balances_dict = json.loads(wallet.balances) if wallet.balances else {"USDT": 50.0}
    
    # Ensure recommended coins are always visible in "Mis Activos", even if balance is 0 or missing
    recommended_coins = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOT", "MATIC", "DOGE", "LINK"]
    for coin in recommended_coins:
        if coin not in balances_dict:
            balances_dict[coin] = 0.0
            
    # Get ALL prices in ONE call (much faster than individual calls)
    binance = get_binance_client()
    all_prices = binance.get_all_prices()  # Returns {"BTCUSDT": 87000.0, "ETHUSDT": 2900.0, ...}
    
    formatted_balances = []
    total_usd = 0.0
    
    for asset, amount in balances_dict.items():
        # Only skip if it's NOT a recommended coin AND amount is <= 0
        if amount <= 0 and asset not in recommended_coins:
            continue
            
        if asset == "USDT":
            usd_value = amount
        else:
            symbol = f"{asset}USDT"
            price = all_prices.get(symbol, 0)
            
            # Fallback if get_all_prices failed or symbol missing
            if price == 0:
                try:
                    price = binance.get_price(symbol) or 0
                except:
                    price = 0
            
            usd_value = amount * price
        
        total_usd += usd_value
        formatted_balances.append(VirtualBalance(
            asset=asset,
            amount=amount,
            usd_value=round(usd_value, 2)
        ))
    
    # Calculate PNL
    initial_capital = wallet.initial_capital or 150.0
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de trading del modo práctica con ROI y métricas profesionales.
    """
    user_id = current_user.id
    
    wallet = get_or_create_wallet(db, user_id)
    trades = db.query(VirtualTradeModel).filter(VirtualTradeModel.wallet_id == wallet.id).all()
    balances = json.loads(wallet.balances) if wallet.balances else {"USDT": 50.0}
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
    initial_capital = wallet.initial_capital or 150.0
    
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Depositar fondos virtuales en modo práctica.
    Útil para testear operaciones de venta.
    """
    user_id = current_user.id
    
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Depositar $50 equivalentes en las principales criptomonedas.
    Ideal para configurar un ambiente de prueba completo.
    """
    user_id = current_user.id
    
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ejecutar una orden virtual (compra/venta) en modo práctica.
    """
    user_id = current_user.id
    
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
    
    # Validar monto mínimo $2
    if total_amount < 2:
        raise HTTPException(status_code=400, detail="El monto mínimo de inversión es $2 USD")
    
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
        pnl=0,  # Se calculará abajo si es venta
        market_type="SPOT"
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    symbol: Optional[str] = None
):
    """
    Obtener historial de órdenes virtuales.
    """
    user_id = current_user.id
    
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
            "created_at": trade.created_at.isoformat(),
            "market_type": trade.market_type if hasattr(trade, 'market_type') else "SPOT"
        })
    
    return {
        "orders": orders,
        "total": len(orders)
    }


@router.get("/trades", response_model=List[Dict[str, Any]])
async def get_virtual_trades(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    symbol: Optional[str] = None
):
    """
    Obtener historial de órdenes virtuales en formato de lista directa para compatibilidad con el frontend.
    """
    res = await get_virtual_orders(current_user=current_user, db=db, limit=limit, symbol=symbol)
    trades_list = []
    for o in res.get("orders", []):
        trades_list.append({
            "id": o["id"],
            "symbol": o["symbol"],
            "side": o["side"],
            "type": o["type"],
            "strategy": o.get("strategy", "MANUAL"),
            "quantity": o["quantity"],
            "price": o["entry_price"],
            "total": o["total"],
            "pnl": o["pnl"],
            "timestamp": o["created_at"],
            "status": o["status"],
            "market_type": o.get("market_type", "SPOT")
        })
    return trades_list



@router.post("/reset")
async def reset_virtual_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resetear wallet virtual a $50 USDT + $10 de cada criptomoneda ($150 USD total).
    """
    user_id = current_user.id
    
    wallet = get_or_create_wallet(db, user_id)
    binance = get_binance_client()
    
    initial_balances = {"USDT": 50.0}
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOTUSDT", "MATICUSDT", "DOGEUSDT", "LINKUSDT"]
    
    for sym in symbols:
        coin = sym.replace("USDT", "")
        try:
            price = binance.get_price(sym)
            if price and price > 0:
                initial_balances[coin] = round(10.0 / price, 6)
            else:
                fallback_prices = {
                    "BTC": 70000.0, "ETH": 3500.0, "BNB": 580.0, "SOL": 170.0,
                    "XRP": 0.50, "ADA": 0.45, "DOT": 6.5, "MATIC": 0.70,
                    "DOGE": 0.15, "LINK": 15.0
                }
                initial_balances[coin] = round(10.0 / fallback_prices.get(coin, 1.0), 6)
        except Exception:
            fallback_prices = {
                "BTC": 70000.0, "ETH": 3500.0, "BNB": 580.0, "SOL": 170.0,
                "XRP": 0.50, "ADA": 0.45, "DOT": 6.5, "MATIC": 0.70,
                "DOGE": 0.15, "LINK": 15.0
            }
            initial_balances[coin] = round(10.0 / fallback_prices.get(coin, 1.0), 6)
            
    # Reset balances
    wallet.balances = json.dumps(initial_balances)
    wallet.initial_capital = 150.0  # Reset capital reference to exactly $150
    wallet.reset_at = datetime.utcnow()
    
    # Delete trades
    db.query(VirtualTradeModel).filter(VirtualTradeModel.wallet_id == wallet.id).delete()
    
    db.commit()
    
    return {
        "message": "✅ Wallet virtual reseteada con éxito ($50 USDT + $10 en cada cripto)",
        "balance": 150.0
    }


@router.get("/position/{symbol}")
async def get_position(
    symbol: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener posición actual de un símbolo.
    """
    user_id = current_user.id
    
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


@router.get("/sentinel-logs")
async def get_sentinel_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20
):
    """
    Obtener los últimos logs/justificaciones del Centinela CIO.
    Fusiona las decisiones de la base de datos con los logs en tiempo real de sentinel_audit_logs.json.
    """
    user_id = current_user.id
    wallet = get_or_create_wallet(db, user_id)
    
    # 1. Intentar leer los logs de auditoría en tiempo real del JSON
    audit_file = "/DATA/Desarrollos  /SIC/backend/app/ml/sentinel_audit_logs.json"
    audit_logs = []
    try:
        import os
        if os.path.exists(audit_file):
            with open(audit_file, "r") as f:
                raw_logs = json.load(f)
                # Filtrar logs de este usuario específico
                audit_logs = [log for log in raw_logs if log.get("user_id") == user_id or log.get("wallet_id") == wallet.id]
    except Exception as e:
        logger.error(f"Error leyendo log de auditoría del Sentinel: {e}")
    
    # 2. Si no hay logs informativos en el JSON, devolvemos los reales de la base de datos
    if not audit_logs:
        logs = db.query(VirtualTradeModel).filter(
            VirtualTradeModel.wallet_id == wallet.id,
            VirtualTradeModel.strategy == "SENTINEL_CIO"
        ).order_by(VirtualTradeModel.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": log.id,
                "symbol": log.symbol,
                "side": log.side,
                "price": log.price,
                "quantity": log.quantity,
                "reason": log.reason,
                "timestamp": log.created_at.isoformat()
            } for log in logs
        ]
    
    # 3. Adaptamos las entradas de auditoría del JSON para ser totalmente compatibles con el formato esperado por el frontend
    formatted_logs = []
    for idx, log in enumerate(audit_logs[:limit]):
        action = log.get("action", "HOLD")
        side = "HOLD"
        if "COMPRA" in action or "BUY" in action:
            side = "BUY"
        elif "VENTA" in action or "SELL" in action:
            side = "SELL"
            
        # Determinar el precio del activo si está disponible en la razón, si no usar el de radar
        formatted_logs.append({
            "id": idx + 1,
            "symbol": log.get("symbol", "N/A"),
            "side": side,
            "price": log.get("usdt_balance", 0.0), # Pasamos balance USDT para visualización
            "quantity": log.get("radar_imbalance", 0.0), # Métrica de volumen
            "reason": f"({action}) {log.get('reason', '')} | Balance: ${log.get('portfolio_value', 0.0)} USD",
            "timestamp": log.get("timestamp", datetime.utcnow().isoformat())
        })
    
    return formatted_logs



@router.get("/futures/positions", response_model=List[FuturesPositionResponse])
async def get_futures_positions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las posiciones abiertas en futuros simulados con PNL no realizado dinámico.
    """
    user_id = current_user.id
    wallet = get_or_create_wallet(db, user_id)
    
    positions = db.query(VirtualPositionModel).filter(
        VirtualPositionModel.wallet_id == wallet.id
    ).all()
    
    binance = get_binance_client()
    response = []
    
    for pos in positions:
        try:
            current_price = binance.get_price(pos.symbol)
            if current_price is None:
                current_price = pos.entry_price
        except Exception:
            current_price = pos.entry_price  # Fallback si falla la API
            
        # Calcular uPNL dinámico
        if pos.side == "LONG":
            unrealized_pnl = (current_price - pos.entry_price) * pos.size
        else:  # SHORT
            unrealized_pnl = (pos.entry_price - current_price) * pos.size
            
        pnl_percent = (unrealized_pnl / pos.margin * 100) if pos.margin > 0 else 0
        
        response.append(
            FuturesPositionResponse(
                id=pos.id,
                symbol=pos.symbol,
                side=pos.side,
                size=pos.size,
                entry_price=pos.entry_price,
                leverage=pos.leverage,
                margin=pos.margin,
                liquidation_price=pos.liquidation_price,
                unrealized_pnl=round(unrealized_pnl, 4),
                pnl_percent=round(pnl_percent, 2),
                created_at=pos.created_at
            )
        )
        
    return response


@router.post("/futures/open", response_model=FuturesPositionResponse)
async def open_futures_position(
    order: FuturesOrder,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Abrir una posición virtual en LONG o SHORT con apalancamiento parametrizable.
    Descuenta el margen requerido del saldo de USDT.
    """
    user_id = current_user.id
    wallet = get_or_create_wallet(db, user_id)
    balances = json.loads(wallet.balances) if wallet.balances else {"USDT": 150.0}
    
    symbol = order.symbol.upper()
    side = order.side.upper()
    
    if side not in ["LONG", "SHORT"]:
        raise HTTPException(status_code=400, detail="El side debe ser LONG o SHORT")
        
    if order.size <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor que 0")
        
    if order.leverage < 1 or order.leverage > 20:
        raise HTTPException(status_code=400, detail="El apalancamiento debe estar entre 1x y 20x")
        
    # Consultar precio actual en Binance
    binance = get_binance_client()
    try:
        current_price = binance.get_price(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando precio del activo: {str(e)}")
        
    # Calcular margen requerido: (Cantidad * Precio) / Apalancamiento
    required_margin = (order.size * current_price) / order.leverage
    
    # Verificar fondos suficientes
    usdt_balance = float(balances.get("USDT", 0))
    if usdt_balance < required_margin:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente en USDT. Requerido: ${required_margin:.2f}, Disponible: ${usdt_balance:.2f}"
        )
        
    # Calcular precio de liquidación estimado
    if side == "LONG":
        liquidation_price = current_price * (1 - 0.9 / order.leverage)  # 10% buffer de seguridad de mantenimiento
    else:  # SHORT
        liquidation_price = current_price * (1 + 0.9 / order.leverage)
        
    # Descontar margen del saldo
    balances["USDT"] = round(usdt_balance - required_margin, 2)
    wallet.balances = json.dumps(balances)
    
    # Crear y guardar posición en DB
    new_position = VirtualPositionModel(
        wallet_id=wallet.id,
        symbol=symbol,
        side=side,
        size=order.size,
        entry_price=current_price,
        leverage=order.leverage,
        margin=round(required_margin, 2),
        liquidation_price=round(liquidation_price, 2)
    )
    db.add(new_position)
    db.flush()  # Para obtener el ID generado
    
    # Registrar el trade de apertura en el historial
    new_trade = VirtualTradeModel(
        wallet_id=wallet.id,
        symbol=symbol,
        side="BUY" if side == "LONG" else "SELL",
        type="MARKET",
        strategy="MANUAL",
        reason=f"Apertura de Contrato Futuro {side} {order.leverage}x",
        quantity=order.size,
        price=current_price,
        pnl=0.0,
        market_type="FUTURES"
    )
    db.add(new_trade)
    db.commit()
    
    return FuturesPositionResponse(
        id=new_position.id,
        symbol=new_position.symbol,
        side=new_position.side,
        size=new_position.size,
        entry_price=new_position.entry_price,
        leverage=new_position.leverage,
        margin=new_position.margin,
        liquidation_price=new_position.liquidation_price,
        unrealized_pnl=0.0,
        pnl_percent=0.0,
        created_at=new_position.created_at
    )


@router.post("/futures/close/{position_id}", response_model=Dict[str, Any])
async def close_futures_position(
    position_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cerrar una posición de futuros activa.
    Acredita el colateral original + PNL realizado de vuelta a la cuenta virtual.
    """
    user_id = current_user.id
    wallet = get_or_create_wallet(db, user_id)
    balances = json.loads(wallet.balances) if wallet.balances else {"USDT": 150.0}
    
    pos = db.query(VirtualPositionModel).filter(
        VirtualPositionModel.id == position_id,
        VirtualPositionModel.wallet_id == wallet.id
    ).first()
    
    if not pos:
        raise HTTPException(status_code=404, detail="Posición de futuros no encontrada")
        
    # Consultar precio actual en Binance
    binance = get_binance_client()
    try:
        current_price = binance.get_price(pos.symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando precio de cierre: {str(e)}")
        
    # Calcular realized PNL
    if pos.side == "LONG":
        realized_pnl = (current_price - pos.entry_price) * pos.size
    else:  # SHORT
        realized_pnl = (pos.entry_price - current_price) * pos.size
        
    # Devolver margen + PNL realizado al balance en USDT
    usdt_balance = float(balances.get("USDT", 0))
    returned_funds = pos.margin + realized_pnl
    
    # Prevenir saldo negativo por pérdidas superiores al margen (en caso de alto apalancamiento sin stop-loss)
    balances["USDT"] = round(max(0.0, usdt_balance + returned_funds), 2)
    wallet.balances = json.dumps(balances)
    
    # Guardar el trade de cierre en el historial
    new_trade = VirtualTradeModel(
        wallet_id=wallet.id,
        symbol=pos.symbol,
        side="SELL" if pos.side == "LONG" else "BUY",
        type="MARKET",
        strategy="MANUAL",
        reason=f"Cierre de Contrato Futuro {pos.side} {pos.leverage}x (Precio entrada: ${pos.entry_price}, Precio salida: ${current_price})",
        quantity=pos.size,
        price=current_price,
        pnl=round(realized_pnl, 4),
        market_type="FUTURES"
    )
    db.add(new_trade)
    
    # === AI LEARNING INTEGRATION FOR FUTURES ===
    try:
        from app.ml.trading_agent import get_trading_agent
        agent = get_trading_agent()
        
        signals_used = ["FUTURES_SIM", "EMA", "RSI"]  # Indicadores típicos
        patterns_detected = ["LONG" if pos.side == "LONG" else "SHORT"]
        
        agent.record_result(
            trade_id=f"FUTURES_{new_trade.id}_{datetime.utcnow().timestamp()}",
            symbol=pos.symbol,
            side=pos.side,  # LONG o SHORT
            entry_price=pos.entry_price,
            exit_price=current_price,
            pnl=realized_pnl,
            signals_used=signals_used,
            patterns_detected=patterns_detected,
            db_session=db
        )
        logger.info(f"🧠 [IA Aprendizaje Futuros] La IA aprendió del cierre de futuros virtual {pos.symbol} ({pos.side}): PnL realizado = ${realized_pnl:.4f}")
    except Exception as e:
        logger.error(f"⚠️ Error en aprendizaje AI al cerrar futuros: {e}")
        
    # Eliminar la posición de la DB
    db.delete(pos)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Contrato de futuros {pos.symbol} cerrado con éxito.",
        "realized_pnl": round(realized_pnl, 2),
        "returned_funds": round(returned_funds, 2),
        "new_usdt_balance": balances["USDT"]
    }


