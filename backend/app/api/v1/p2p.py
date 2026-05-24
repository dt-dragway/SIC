"""
SIC Ultra - Mercado P2P VES

Arbitraje USDT/VES con datos REALES del mercado P2P de Binance.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

from app.api.v1.auth import oauth2_scheme, verify_token
from app.infrastructure.binance.p2p import get_p2p_client
from app.ml.p2p_analyzer import get_opportunity_finder


router = APIRouter()


# === Schemas ===

class P2POffer(BaseModel):
    advertiser: str
    price: float
    available: float
    min_amount: float
    max_amount: float
    payment_methods: List[str]
    completion_rate: float
    orders_count: Optional[int] = None


class P2PMarket(BaseModel):
    fiat: str
    asset: str
    buy_offers: List[P2POffer]
    sell_offers: List[P2POffer]
    best_buy_price: float
    best_sell_price: float
    spread_percent: float
    timestamp: datetime


class P2PStats(BaseModel):
    fiat: str
    asset: str
    avg_buy_price: float
    avg_sell_price: float
    spread_percent: float
    buy_offers_count: int
    sell_offers_count: int
    timestamp: datetime


# === Endpoints ===

@router.get("/market", response_model=P2PMarket)
async def get_p2p_market(
    fiat: str = "VES",
    asset: str = "USDT",
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener ofertas REALES del mercado P2P de Binance.
    
    Muestra las mejores ofertas para comprar y vender USDT con Bolívares.
    
    - **fiat**: Moneda fiat (VES, USD, COP, etc)
    - **asset**: Criptomoneda (USDT, BTC, etc)
    """
    verify_token(token)
    
    client = get_p2p_client()
    
    # Obtener ofertas reales
    buy_offers = await client.get_buy_offers(fiat, asset, rows=10)
    sell_offers = await client.get_sell_offers(fiat, asset, rows=10)
    
    if not buy_offers and not sell_offers:
        raise HTTPException(
            status_code=404, 
            detail=f"No hay ofertas P2P disponibles para {asset}/{fiat}"
        )
    
    # Calcular mejores precios
    best_buy = min(o["price"] for o in buy_offers) if buy_offers else 0
    best_sell = max(o["price"] for o in sell_offers) if sell_offers else 0
    spread = ((best_sell - best_buy) / best_buy * 100) if best_buy > 0 else 0
    
    return {
        "fiat": fiat.upper(),
        "asset": asset.upper(),
        "buy_offers": buy_offers,
        "sell_offers": sell_offers,
        "best_buy_price": best_buy,
        "best_sell_price": best_sell,
        "spread_percent": round(spread, 2),
        "timestamp": datetime.utcnow()
    }


@router.get("/stats", response_model=P2PStats)
async def get_p2p_stats(
    fiat: str = "VES",
    asset: str = "USDT",
    token: str = Depends(oauth2_scheme)
):
    """
    Estadísticas del mercado P2P.
    """
    verify_token(token)
    
    client = get_p2p_client()
    summary = await client.get_market_summary(fiat, asset)
    
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    
    return summary


@router.get("/buy")
async def get_buy_offers(
    fiat: str = "VES",
    asset: str = "USDT",
    crypto: Optional[str] = None,  # Fallback for frontend compatibility
    limit: int = 50,
    amount: Optional[float] = None, # Alias for transAmount
    payment_methods: Optional[str] = None, # Comma separated: "Banesco,Mercantil"
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener solo ofertas para COMPRAR cripto (pagas VES).
    
    Ordenadas por precio (más bajo primero).
    - **payment_methods**: Lista separada por comas (ej: "Banesco,Mercantil")
    - **amount**: Monto específico a transaccionar (ej: 1000 VES)
    """
    verify_token(token)
    
    # Handle crypto fallback
    target_asset = crypto if crypto else asset
    
    pay_types = []
    if payment_methods:
        pay_types = payment_methods.split(",")
    
    client = get_p2p_client()
    offers = await client.get_buy_offers(fiat, target_asset, rows=limit, pay_types=pay_types, trans_amount=amount)
    
    # Ordenar por precio
    offers.sort(key=lambda x: x["price"])
    
    return {
        "type": "BUY",
        "fiat": fiat.upper(),
        "asset": target_asset.upper(),
        "count": len(offers),
        "offers": offers,
        "timestamp": datetime.utcnow()
    }


@router.get("/sell")
async def get_sell_offers(
    fiat: str = "VES",
    asset: str = "USDT",
    crypto: Optional[str] = None,  # Fallback for frontend compatibility
    limit: int = 50,
    amount: Optional[float] = None,
    payment_methods: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener solo ofertas para VENDER cripto (recibes VES).
    
    Ordenadas por precio (más alto primero).
    """
    verify_token(token)
    
    # Handle crypto fallback
    target_asset = crypto if crypto else asset
    
    pay_types = []
    if payment_methods:
        pay_types = payment_methods.split(",")
    
    client = get_p2p_client()
    offers = await client.get_sell_offers(fiat, target_asset, rows=limit, pay_types=pay_types, trans_amount=amount)
    
    # Ordenar por precio (más alto primero)
    offers.sort(key=lambda x: x["price"], reverse=True)
    
    return {
        "type": "SELL",
        "fiat": fiat.upper(),
        "asset": target_asset.upper(),
        "count": len(offers),
        "offers": offers,
        "timestamp": datetime.utcnow()
    }


@router.get("/spread")
async def get_spread(
    fiat: str = "VES",
    asset: str = "USDT",
    token: str = Depends(oauth2_scheme)
):
    """
    Calcular spread actual del mercado P2P.
    
    El spread es la diferencia entre el mejor precio de compra y venta.
    Un spread alto indica oportunidad de arbitraje.
    """
    verify_token(token)
    
    client = get_p2p_client()
    summary = await client.get_market_summary(fiat, asset)
    
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    
    arbitrage_opportunity = summary["spread_percent"] > 1.5
    
    return {
        "fiat": fiat.upper(),
        "asset": asset.upper(),
        "best_buy_price": summary["best_buy_price"],
        "best_sell_price": summary["best_sell_price"],
        "spread_percent": summary["spread_percent"],
        "arbitrage_opportunity": arbitrage_opportunity,
        "message": "🔥 Oportunidad de arbitraje!" if arbitrage_opportunity else "Spread normal",
        "timestamp": datetime.utcnow()
    }


class P2PCriteria(BaseModel):
    min_completion_rate: Optional[float] = 90.0
    min_orders_count: Optional[int] = 10
    only_verified: Optional[bool] = False
    price_weight: Optional[float] = 0.5
    safety_weight: Optional[float] = 0.5
    target_amount: Optional[float] = None
    preferred_payment_methods: Optional[List[str]] = []


class P2PAnalysisRequest(BaseModel):
    offers: List[P2POffer]
    criteria: Optional[P2PCriteria] = None


@router.post("/analyze")
async def analyze_p2p_offers(
    payload: Union[P2PAnalysisRequest, List[P2POffer]],
    token: str = Depends(oauth2_scheme)
):
    """
    🧠 IA P2P: Analiza una lista de ofertas y detecta la mejor opción según criterios.
    
    Soporta scoring ponderado y filtros personalizados de seguridad y límites.
    """
    verify_token(token)
    
    # Extraer ofertas y criterios del payload (soporta backward-compatibility)
    criteria = None
    if isinstance(payload, P2PAnalysisRequest):
        offers = payload.offers
        criteria = payload.criteria
    else:
        offers = payload

    if not offers:
        raise HTTPException(status_code=400, detail="No offers provided")
        
    if not criteria:
        criteria = P2PCriteria()
        
    finder = get_opportunity_finder()
    
    best_offer = None
    best_score = -1.0
    risky_offers = []
    
    # 1. Identificar mejores y peores precios para normalización
    prices = [float(offer.price) for offer in offers if offer.price > 0]
    if not prices:
        min_price = max_price = 1.0
    else:
        min_price = min(prices)
        max_price = max(prices)
        
    # Detectar dinámicamente si es un mercado de COMPRA (precios ordenados ascendentes) o VENTA (descendentes)
    is_buy = True
    if len(prices) >= 2:
        descending_count = sum(1 for i in range(len(prices)-1) if prices[i] >= prices[i+1])
        if descending_count >= len(prices) / 2:
            is_buy = False

    for offer in offers:
        # Extraer atributos de la oferta
        offer_dict = offer.dict() if hasattr(offer, 'dict') else offer
        
        price = float(offer.price)
        completion_rate = float(offer.completion_rate)
        orders_count = int(offer.orders_count or 0)
        is_verified = bool(offer_dict.get('is_verified', False))
        payment_methods = [m.lower() for m in (offer.payment_methods or [])]
        
        # A. Filtros estrictos de seguridad de la IA
        if completion_rate < 80.0 or orders_count < 5:
            risky_offers.append(offer.advertiser)
            continue
            
        # B. Filtros de criterios del usuario
        if completion_rate < criteria.min_completion_rate:
            continue
            
        if orders_count < criteria.min_orders_count:
            continue
            
        if criteria.only_verified and not is_verified:
            continue
            
        # C. Alineación de límites transaccionales
        if criteria.target_amount is not None and criteria.target_amount > 0:
            if criteria.target_amount < offer.min_amount or criteria.target_amount > offer.max_amount:
                continue

        # 2. Calcular componentes del score
        # A. Score de Precio (0-100)
        if max_price == min_price:
            price_score = 100.0
        else:
            if is_buy:
                # Comprar: menor precio es mejor (100 puntos al mínimo)
                price_score = 100.0 * (max_price - price) / (max_price - min_price)
            else:
                # Vender: mayor precio es mejor (100 puntos al máximo)
                price_score = 100.0 * (price - min_price) / (max_price - min_price)

        # B. Score de Tasa de Finalización (0-100)
        completion_score = completion_rate

        # C. Score de Volumen de Órdenes (0-100, cap a 1000 órdenes)
        orders_score = min(100.0, (orders_count / 10.0))

        # D. Score de Verificación (insignia dorada de comerciante)
        merchant_score = 100.0 if is_verified else 0.0

        # E. Boost por métodos de pago preferidos
        payment_boost = 0.0
        if criteria.preferred_payment_methods:
            preferred_set = set(p.lower() for p in criteria.preferred_payment_methods)
            matching_methods = [m for m in payment_methods if any(p in m for p in preferred_set)]
            if matching_methods:
                payment_boost = 10.0  # 10 puntos de bonificación

        # 3. Ponderación final (Weights)
        w_price = criteria.price_weight
        w_safety = criteria.safety_weight
        
        # Ponderación interna de la seguridad: 60% completion rate, 30% orders count, 10% merchant badge
        safety_score = (completion_score * 0.6) + (orders_score * 0.3) + (merchant_score * 0.1)
        
        total_score = (price_score * w_price) + (safety_score * w_safety) + payment_boost
        total_score = min(100.0, max(0.0, total_score))
        
        if total_score > best_score:
            best_score = total_score
            best_offer = offer_dict

    # Si no se encuentra oferta que cumpla los criterios estrictos del usuario, relajar criterios usando defaults
    if not best_offer and offers:
        for offer in offers:
            offer_dict = offer.dict() if hasattr(offer, 'dict') else offer
            if offer.completion_rate >= 80.0 and (offer.orders_count or 0) >= 5:
                # Lógica simplificada de fallback
                completion_score = offer.completion_rate 
                orders_score = min(100.0, (offer.orders_count or 0) / 10.0) 
                total_score = (completion_score * 0.7) + (orders_score * 0.3)
                if total_score > best_score:
                    best_score = total_score
                    best_offer = offer_dict

    if not best_offer:
        return {
            "best_offer": None,
            "risky_advertisers": risky_offers,
            "reason": "No se encontraron ofertas que cumplan con los criterios mínimos de seguridad.",
            "timestamp": datetime.utcnow()
        }

    # 4. Razonamiento dinámico con IA
    market_context = {
        "fiat": "VES",
        "buy": {"best": min_price},
        "sell": {"best": max_price},
        "spread": {"percent": round(((max_price - min_price) / min_price * 100) if min_price > 0 else 0, 2)}
    }
    
    # Pasar los criterios al analizador para contextualizar
    ai_reason = await finder.analyze_offer_context(
        best_offer, 
        market_context, 
        criteria=criteria.dict() if hasattr(criteria, 'dict') else criteria
    )
            
    return {
        "best_offer": best_offer,
        "score": round(best_score, 1),
        "risky_advertisers": risky_offers,
        "reason": ai_reason,
        "timestamp": datetime.utcnow()
    }


@router.get("/calculator")
async def calculate_arbitrage(
    amount_usdt: float = 100,
    fiat: str = "VES",
    token: str = Depends(oauth2_scheme)
):
    """
    Calculadora de arbitraje P2P.
    
    Calcula la ganancia potencial si compras y vendes USDT.
    """
    verify_token(token)
    
    client = get_p2p_client()
    summary = await client.get_market_summary(fiat, "USDT")
    
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    
    buy_price = summary["best_buy_price"]
    sell_price = summary["best_sell_price"]
    
    # Costo de comprar USDT
    cost_fiat = amount_usdt * buy_price
    
    # Ganancia al vender USDT
    revenue_fiat = amount_usdt * sell_price
    
    # Ganancia neta
    profit_fiat = revenue_fiat - cost_fiat
    profit_percent = (profit_fiat / cost_fiat) * 100 if cost_fiat > 0 else 0
    
    return {
        "amount_usdt": amount_usdt,
        "fiat": fiat.upper(),
        "buy_price": buy_price,
        "sell_price": sell_price,
        "cost_fiat": round(cost_fiat, 2),
        "revenue_fiat": round(revenue_fiat, 2),
        "profit_fiat": round(profit_fiat, 2),
        "profit_percent": round(profit_percent, 2),
        "profitable": profit_fiat > 0,
        "timestamp": datetime.utcnow()
    }


@router.get("/history")
async def get_p2p_history_endpoint(
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener historial COMPLETO de P2P (Compras y Ventas).
    Requiere API Key válida en el backend.
    """
    verify_token(token)
    
    from app.infrastructure.binance.client import get_binance_client
    client = get_binance_client()
    
    if not client.is_connected():
         return {"trades": [], "message": "No conectado a Binance"}
    
    # Fetch both BUY and SELL
    buys = client.get_p2p_history("BUY")
    sells = client.get_p2p_history("SELL")
    
    all_trades = buys + sells
    # Sort by timestamp desc
    all_trades.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "count": len(all_trades),
        "trades": all_trades
    }


@router.get("/opportunities")
async def get_p2p_opportunities(
    amount_usdt: float = 100,
    min_score: int = 60,
    token: str = Depends(oauth2_scheme)
):
    """
    💎 Obtener Oportunidades de Oro de P2P en tiempo real usando IA.
    """
    verify_token(token)
    
    finder = get_opportunity_finder()
    opportunities = await finder.find_opportunities(amount_usdt, min_score)
    
    serializable_opportunities = []
    for opp in opportunities:
        serializable_opportunities.append({
            "type": opp.type,
            "score": opp.score,
            "action": opp.action,
            "current_price": opp.current_price,
            "target_price": opp.target_price,
            "potential_profit_percent": opp.potential_profit_percent,
            "risk_level": opp.risk_level,
            "risk_factors": opp.risk_factors,
            "valid_until": opp.valid_until.isoformat(),
            "best_time": opp.best_time,
            "reasoning": opp.reasoning
        })
        
    return {
        "count": len(opportunities),
        "opportunities": serializable_opportunities
    }
