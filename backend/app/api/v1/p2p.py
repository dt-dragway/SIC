"""
SIC Ultra - Mercado P2P VES

Arbitraje USDT/VES con datos REALES del mercado P2P de Binance.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.api.v1.auth import oauth2_scheme, verify_token
from app.infrastructure.binance.p2p import get_p2p_client


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
    limit: int = 10,
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener solo ofertas para COMPRAR cripto (pagas VES).
    
    Ordenadas por precio (más bajo primero).
    """
    verify_token(token)
    
    client = get_p2p_client()
    offers = await client.get_buy_offers(fiat, asset, rows=limit)
    
    # Ordenar por precio
    offers.sort(key=lambda x: x["price"])
    
    return {
        "type": "BUY",
        "fiat": fiat.upper(),
        "asset": asset.upper(),
        "count": len(offers),
        "offers": offers,
        "timestamp": datetime.utcnow()
    }


@router.get("/sell")
async def get_sell_offers(
    fiat: str = "VES",
    asset: str = "USDT",
    limit: int = 10,
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener solo ofertas para VENDER cripto (recibes VES).
    
    Ordenadas por precio (más alto primero).
    """
    verify_token(token)
    
    client = get_p2p_client()
    offers = await client.get_sell_offers(fiat, asset, rows=limit)
    
    # Ordenar por precio (más alto primero)
    offers.sort(key=lambda x: x["price"], reverse=True)
    
    return {
        "type": "SELL",
        "fiat": fiat.upper(),
        "asset": asset.upper(),
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
