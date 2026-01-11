"""
SIC Ultra - Señales de Trading

Señales generadas por el agente de IA con análisis técnico real.
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
import asyncio

from app.api.v1.auth import oauth2_scheme, verify_token
from app.ml.signal_generator import get_signal_generator


router = APIRouter()


# === Schemas ===

class SignalType(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    HOLD = "HOLD"


class SignalStrength(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"


class TradingSignal(BaseModel):
    symbol: str
    interval: str
    type: SignalType
    strength: SignalStrength
    confidence: float
    current_price: float
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    reasoning: List[str]
    timestamp: datetime
    expires_at: datetime


class SignalIndicators(BaseModel):
    rsi: Optional[float]
    macd_histogram: Optional[float]
    trend: str
    atr: float


# === WebSocket Manager ===

class ConnectionManager:
    """Gestiona conexiones WebSocket para señales en tiempo real"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


# === Endpoints ===

@router.get("/analyze/{symbol}")
async def analyze_symbol(
    symbol: str,
    interval: str = "1h",
    token: str = Depends(oauth2_scheme)
):
    """
    Analizar un símbolo y generar señal de trading.
    
    Usa análisis técnico con múltiples indicadores:
    - RSI (sobreventa/sobrecompra)
    - MACD (momentum)
    - Bollinger Bands (volatilidad)
    - Trend (tendencia)
    
    Intervals: 1m, 5m, 15m, 1h, 4h, 1d
    """
    verify_token(token)
    
    generator = get_signal_generator()
    signal = generator.analyze(symbol.upper(), interval)
    
    if not signal:
        raise HTTPException(
            status_code=404,
            detail=f"No se pudo analizar {symbol}. Verifica que el par sea válido."
        )
    
    return signal


@router.get("/scan")
async def scan_market(token: str = Depends(oauth2_scheme)):
    """
    Escanear el mercado y retornar todas las señales activas.
    
    Analiza los principales pares y muestra solo señales de compra/venta.
    """
    verify_token(token)
    
    generator = get_signal_generator()
    signals = generator.scan_market()
    
    return {
        "count": len(signals),
        "signals": signals,
        "timestamp": datetime.utcnow()
    }


@router.get("/top")
async def get_top_signals(
    limit: int = 5,
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener las mejores señales del momento.
    
    Ordenadas por confianza (más alta primero).
    """
    verify_token(token)
    
    generator = get_signal_generator()
    signals = generator.scan_market()
    
    # Filtrar solo señales fuertes/moderadas
    strong_signals = [s for s in signals if s["strength"] in ["STRONG", "MODERATE"]]
    
    return {
        "count": min(len(strong_signals), limit),
        "signals": strong_signals[:limit],
        "timestamp": datetime.utcnow()
    }


@router.get("/indicators/{symbol}")
async def get_indicators(
    symbol: str,
    interval: str = "1h",
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener solo los indicadores técnicos de un símbolo.
    """
    verify_token(token)
    
    generator = get_signal_generator()
    signal = generator.analyze(symbol.upper(), interval)
    
    if not signal:
        raise HTTPException(status_code=404, detail=f"No se pudo analizar {symbol}")
    
    return {
        "symbol": symbol.upper(),
        "interval": interval,
        "indicators": signal.get("indicators", {}),
        "support": signal.get("support"),
        "resistance": signal.get("resistance"),
        "current_price": signal.get("current_price"),
        "timestamp": datetime.utcnow()
    }


# === WebSocket para Tiempo Real ===

@router.websocket("/ws")
async def websocket_signals(websocket: WebSocket):
    """
    WebSocket para recibir señales en tiempo real.
    
    El servidor envía nuevas señales automáticamente cada minuto.
    """
    await manager.connect(websocket)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Conectado a señales en tiempo real",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            try:
                # Esperar mensajes del cliente
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0  # Cada minuto
                )
                
                if data == "ping":
                    await websocket.send_text("pong")
                elif data == "scan":
                    # Escaneo bajo demanda
                    generator = get_signal_generator()
                    signals = generator.scan_market()
                    await websocket.send_json({
                        "type": "scan_result",
                        "count": len(signals),
                        "signals": signals,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            except asyncio.TimeoutError:
                # Enviar escaneo automático cada minuto
                generator = get_signal_generator()
                signals = generator.scan_market()
                
                if signals:
                    await websocket.send_json({
                        "type": "auto_scan",
                        "count": len(signals),
                        "signals": signals[:3],  # Top 3
                        "timestamp": datetime.utcnow().isoformat()
                    })
                else:
                    await websocket.send_json({"type": "heartbeat"})
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
