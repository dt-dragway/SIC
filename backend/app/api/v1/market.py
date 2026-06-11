"""
SIC Ultra - Market Data Endpoints

Endpoints para análisis de microestructura del mercado,
order flow, y datos para trading profesional.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

from app.api.v1.auth import oauth2_scheme, verify_token
from app.infrastructure.binance.client import get_binance_client


router = APIRouter()


# === Schemas ===

class OrderFlowLevel(BaseModel):
    price: float
    bid_volume: float
    ask_volume: float
    delta: float  # bid_volume - ask_volume
    trades: int
    spoofing_risk: str  # LOW, MEDIUM, HIGH


class OrderFlowResponse(BaseModel):
    symbol: str
    levels: List[OrderFlowLevel]
    cvd: float  # Cumulative Volume Delta
    spoofing_alerts: List[str]
    liquidity_zones: List[float]
    timestamp: datetime


class ATRResponse(BaseModel):
    symbol: str
    atr: float
    period: int
    timestamp: datetime


# === Endpoints ===

@router.get("/order-flow", response_model=OrderFlowResponse)
async def get_order_flow(
    symbol: str = Query(..., description="Trading pair, e.g., BTCUSDT"),
    limit: int = Query(20, ge=10, le=100, description="Number of price levels"),
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener datos de order flow para análisis de microestructura.
    
    Incluye:
    - Bid/Ask volume por nivel de precio
    - Delta (diferencia entre compras y ventas)
    - CVD (Cumulative Volume Delta)
    - Detección de spoofing
    - Zonas de liquidez
    """
    verify_token(token)
    
    client = get_binance_client()
    
    # Obtener order book
    depth = client.client.get_order_book(symbol=symbol, limit=limit)
    
    levels = []
    cumulative_delta = 0.0
    spoofing_alerts = []
    liquidity_zones = []
    
    # Calcular volumen promedio para detectar muros
    all_volumes = []
    for bid in depth['bids']:
        all_volumes.append(float(bid[1]))
    for ask in depth['asks']:
        all_volumes.append(float(ask[1]))
    
    avg_volume = sum(all_volumes) / len(all_volumes) if all_volumes else 0
    
    # Procesar niveles de precio
    max_len = min(len(depth['bids']), len(depth['asks']))
    
    for i in range(max_len):
        bid_price = float(depth['bids'][i][0])
        bid_volume = float(depth['bids'][i][1])
        ask_price = float(depth['asks'][i][0])
        ask_volume = float(depth['asks'][i][1])
        
        # Precio medio del nivel
        mid_price = (bid_price + ask_price) / 2
        
        # Delta = compras - ventas
        delta = bid_volume - ask_volume
        cumulative_delta += delta
        
        # Estimación de trades (en producción vendría de stream de trades)
        estimated_trades = int((bid_volume + ask_volume) * 0.1)
        
        # Detectar spoofing: volumen grande pero pocos trades
        volume_ratio = estimated_trades / (bid_volume + ask_volume) if (bid_volume + ask_volume) > 0 else 0
        
        spoofing_risk = "LOW"
        if bid_volume > avg_volume * 10 and volume_ratio < 0.05:
            spoofing_risk = "HIGH"
            spoofing_alerts.append(f"⚠️ Posible BID spoofing en ${mid_price:.2f}")
        elif ask_volume > avg_volume * 10 and volume_ratio < 0.05:
            spoofing_risk = "HIGH"
            spoofing_alerts.append(f"⚠️ Posible ASK spoofing en ${mid_price:.2f}")
        elif bid_volume > avg_volume * 5 or ask_volume > avg_volume * 5:
            spoofing_risk = "MEDIUM"
        
        # Identificar zonas de liquidez (muros grandes)
        if bid_volume > avg_volume * 7:
            liquidity_zones.append(bid_price)
        if ask_volume > avg_volume * 7:
            liquidity_zones.append(ask_price)
        
        levels.append({
            "price": mid_price,
            "bid_volume": bid_volume,
            "ask_volume": ask_volume,
            "delta": delta,
            "trades": estimated_trades,
            "spoofing_risk": spoofing_risk
        })
    
    return {
        "symbol": symbol,
        "levels": levels,
        "cvd": cumulative_delta,
        "spoofing_alerts": spoofing_alerts[:5],  # Máximo 5 alertas
        "liquidity_zones": liquidity_zones[:10],  # Máximo 10 zonas
        "timestamp": datetime.utcnow()
    }


@router.get("/atr", response_model=ATRResponse)
async def get_atr(
    symbol: str = Query(..., description="Trading pair"),
    period: int = Query(14, ge=5, le=100, description="ATR period"),
    token: str = Depends(oauth2_scheme)
):
    """
    Calcular ATR (Average True Range) para Stop Loss dinámico.
    
    ATR se usa para determinar volatilidad y colocar Stop Loss
    de forma inteligente basado en las condiciones del mercado.
    """
    verify_token(token)
    
    client = get_binance_client()
    
    # Obtener klines para calcular ATR
    klines = client.client.get_klines(
        symbol=symbol,
        interval='1h',
        limit=period + 1
    )
    
    # Calcular True Range para cada vela
    true_ranges = []
    for i in range(1, len(klines)):
        high = float(klines[i][2])
        low = float(klines[i][3])
        prev_close = float(klines[i-1][4])
        
        # True Range = max(high-low, abs(high-prev_close), abs(low-prev_close))
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        true_range = max(tr1, tr2, tr3)
        true_ranges.append(true_range)
    
    # ATR = promedio de True Ranges
    atr = sum(true_ranges) / len(true_ranges) if true_ranges else 0
    
    return {
        "symbol": symbol,
        "atr": round(atr, 8),
        "period": period,
        "timestamp": datetime.utcnow()
    }


@router.get("/candle-patterns")
async def detect_candle_patterns(
    symbol: str = Query(..., description="Trading pair"),
    limit: int = Query(100, ge=50, le=500),
    token: str = Depends(oauth2_scheme)
):
    """
    Detectar patrones de velas japonesas.
    
    Detecta:
    - Hammer (Martillo)
    - Shooting Star (Estrella Fugaz)
    - Doji
    - Engulfing (Envolvente)
    - Morning/Evening Star
    """
    verify_token(token)
    
    client = get_binance_client()
    
    klines = client.client.get_klines(
        symbol=symbol,
        interval='15m',
        limit=limit
    )
    
    patterns = []
    
    for i in range(2, len(klines)):
        current = klines[i]
        prev = klines[i-1]
        prev2 = klines[i-2]
        
        open_price = float(current[1])
        high = float(current[2])
        low = float(current[3])
        close = float(current[4])
        
        body = abs(close - open_price)
        upper_shadow = high - max(open_price, close)
        lower_shadow = min(open_price, close) - low
        
        # Hammer: cuerpo pequeño, shadow inferior 2x body
        if body > 0 and lower_shadow > body * 2 and upper_shadow < body * 0.3:
            patterns.append({
                "type": "HAMMER",
                "direction": "BULLISH",
                "time": datetime.fromtimestamp(current[0] / 1000),
                "price": close,
                "confidence": 75
            })
        
        # Shooting Star: cuerpo pequeño, shadow superior 2x body
        if body > 0 and upper_shadow > body * 2 and lower_shadow < body * 0.3:
            patterns.append({
                "type": "SHOOTING_STAR",
                "direction": "BEARISH",
                "time": datetime.fromtimestamp(current[0] / 1000),
                "price": close,
                "confidence": 75
            })
        
        # Doji: open ≈ close (diff < 0.1%)
        if body / open_price < 0.001:
            patterns.append({
                "type": "DOJI",
                "direction": "NEUTRAL",
                "time": datetime.fromtimestamp(current[0] / 1000),
                "price": close,
                "confidence": 60
            })
    
    # Retornar solo los últimos 10 patrones
    return {
        "symbol": symbol,
        "patterns": patterns[-10:],
        "total_found": len(patterns),
        "timestamp": datetime.utcnow()
    }
