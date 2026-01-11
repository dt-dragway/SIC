"""
SIC Ultra - Mercado P2P VES

Arbitraje USDT/VES en el mercado P2P de Binance.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.api.v1.auth import oauth2_scheme, verify_token


router = APIRouter()


# === Schemas ===

class P2POffer(BaseModel):
    advertiser: str
    price: float  # VES por USDT
    available: float  # USDT disponible
    min_amount: float
    max_amount: float
    payment_methods: List[str]
    completion_rate: float  # %


class P2PMarket(BaseModel):
    buy_offers: List[P2POffer]  # Comprar USDT (pagar VES)
    sell_offers: List[P2POffer]  # Vender USDT (recibir VES)
    best_buy_price: float  # Precio más bajo para comprar
    best_sell_price: float  # Precio más alto para vender
    spread: float  # Diferencia porcentual
    last_update: datetime


class P2PStats(BaseModel):
    avg_buy_price: float
    avg_sell_price: float
    spread_percent: float
    volume_24h: float
    offers_count: int


# === Endpoints ===

@router.get("/market", response_model=P2PMarket)
async def get_p2p_market(token: str = Depends(oauth2_scheme)):
    """
    Obtener ofertas del mercado P2P USDT/VES.
    
    Muestra las mejores ofertas para comprar y vender USDT con Bolívares.
    """
    verify_token(token)
    
    # TODO: Scraper real de Binance P2P
    # Por ahora datos de ejemplo
    
    buy_offers = [
        {
            "advertiser": "CryptoVzla",
            "price": 36.50,
            "available": 1500.0,
            "min_amount": 10,
            "max_amount": 500,
            "payment_methods": ["Banesco", "Mercantil"],
            "completion_rate": 98.5
        },
        {
            "advertiser": "BolívarExchange",
            "price": 36.45,
            "available": 2000.0,
            "min_amount": 50,
            "max_amount": 1000,
            "payment_methods": ["Provincial", "Banesco"],
            "completion_rate": 99.1
        }
    ]
    
    sell_offers = [
        {
            "advertiser": "VESTrader",
            "price": 37.20,
            "available": 800.0,
            "min_amount": 10,
            "max_amount": 300,
            "payment_methods": ["Pago Móvil"],
            "completion_rate": 97.8
        },
        {
            "advertiser": "CryptoVzla",
            "price": 37.15,
            "available": 1200.0,
            "min_amount": 20,
            "max_amount": 600,
            "payment_methods": ["Banesco", "Mercantil"],
            "completion_rate": 98.5
        }
    ]
    
    best_buy = min(o["price"] for o in buy_offers)
    best_sell = max(o["price"] for o in sell_offers)
    spread = ((best_sell - best_buy) / best_buy) * 100
    
    return {
        "buy_offers": buy_offers,
        "sell_offers": sell_offers,
        "best_buy_price": best_buy,
        "best_sell_price": best_sell,
        "spread": spread,
        "last_update": datetime.utcnow()
    }


@router.get("/stats", response_model=P2PStats)
async def get_p2p_stats(token: str = Depends(oauth2_scheme)):
    """
    Estadísticas del mercado P2P VES.
    """
    verify_token(token)
    
    # TODO: Calcular de datos reales
    return {
        "avg_buy_price": 36.48,
        "avg_sell_price": 37.18,
        "spread_percent": 1.92,
        "volume_24h": 125000,
        "offers_count": 45
    }


@router.get("/history")
async def get_p2p_history(
    days: int = 7,
    token: str = Depends(oauth2_scheme)
):
    """
    Historial de precios P2P VES de los últimos días.
    
    Útil para ver tendencia de la tasa.
    """
    verify_token(token)
    
    # TODO: Datos históricos reales
    from datetime import timedelta
    import random
    
    history = []
    base_price = 36.50
    now = datetime.utcnow()
    
    for i in range(days):
        date = now - timedelta(days=days-i-1)
        variation = random.uniform(-0.5, 0.5)
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "avg_buy": base_price + variation,
            "avg_sell": base_price + variation + 0.7,
            "volume": random.randint(80000, 150000)
        })
    
    return {"history": history}


@router.post("/alert")
async def create_p2p_alert(
    target_price: float,
    side: str,  # "buy" o "sell"
    token: str = Depends(oauth2_scheme)
):
    """
    Crear alerta de precio P2P.
    
    Te notifica cuando el precio llegue al objetivo.
    """
    verify_token(token)
    
    # TODO: Guardar alerta en DB
    # TODO: Sistema de notificaciones
    
    return {
        "message": f"Alerta creada: notificar cuando {side} llegue a {target_price} VES",
        "active": True
    }
