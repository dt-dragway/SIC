"""
SIC Ultra - Señales de Trading

Señales generadas por el agente de IA.
Monitoreo en tiempo real.
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
import asyncio
import json

from app.api.v1.auth import oauth2_scheme, verify_token


router = APIRouter()


# === Enums ===

class SignalType(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    HOLD = "HOLD"


class SignalStrength(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"


# === Schemas ===

class TradingSignal(BaseModel):
    id: int
    symbol: str
    type: SignalType
    strength: SignalStrength
    confidence: float  # 0-100%
    entry_price: float
    take_profit: float
    stop_loss: float
    risk_reward: float
    reasoning: str
    timestamp: datetime
    expires_at: datetime


class SignalStats(BaseModel):
    total_signals: int
    win_rate: float
    avg_profit: float
    best_signal: Optional[TradingSignal]


# === WebSocket Manager ===

class ConnectionManager:
    """Gestiona conexiones WebSocket para señales en tiempo real"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Enviar mensaje a todos los clientes conectados"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


# === Endpoints REST ===

@router.get("/", response_model=List[TradingSignal])
async def get_signals(
    symbol: Optional[str] = None,
    active_only: bool = True,
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener señales de trading actuales.
    
    Las señales son generadas por el agente de IA.
    """
    verify_token(token)
    
    # TODO: Obtener señales reales del agente
    signals = [
        {
            "id": 1,
            "symbol": "BTCUSDT",
            "type": SignalType.LONG,
            "strength": SignalStrength.STRONG,
            "confidence": 87.5,
            "entry_price": 45000.0,
            "take_profit": 47500.0,
            "stop_loss": 44200.0,
            "risk_reward": 3.12,
            "reasoning": "Confluencia: Top 3 traders en LONG, RSI saliendo de sobreventa, volumen creciente",
            "timestamp": datetime.utcnow(),
            "expires_at": datetime.utcnow()
        }
    ]
    
    if symbol:
        signals = [s for s in signals if s["symbol"] == symbol.upper()]
    
    return signals


@router.get("/stats", response_model=SignalStats)
async def get_signal_stats(token: str = Depends(oauth2_scheme)):
    """
    Estadísticas de rendimiento de las señales.
    """
    verify_token(token)
    
    return {
        "total_signals": 156,
        "win_rate": 67.3,
        "avg_profit": 2.4,
        "best_signal": None
    }


@router.get("/history")
async def get_signal_history(
    limit: int = 50,
    token: str = Depends(oauth2_scheme)
):
    """
    Historial de señales pasadas con resultados.
    """
    verify_token(token)
    
    # TODO: Obtener de DB
    return {"signals": [], "total": 0}


# === WebSocket para Tiempo Real ===

@router.websocket("/ws")
async def websocket_signals(websocket: WebSocket):
    """
    WebSocket para recibir señales en tiempo real.
    
    Conectar desde frontend:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/signals/ws');
    ws.onmessage = (event) => {
        const signal = JSON.parse(event.data);
        console.log('Nueva señal:', signal);
    };
    ```
    """
    await manager.connect(websocket)
    
    try:
        # Enviar mensaje de bienvenida
        await websocket.send_json({
            "type": "connected",
            "message": "Conectado a señales en tiempo real",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Mantener conexión abierta
        while True:
            # Esperar mensajes del cliente (ping/pong, etc)
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                # Responder a ping
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except asyncio.TimeoutError:
                # Enviar heartbeat
                await websocket.send_json({"type": "heartbeat"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# === Función para emitir señales (llamada por el agente) ===

async def emit_signal(signal: dict):
    """
    Emitir nueva señal a todos los clientes WebSocket.
    
    Llamada por el agente de IA cuando genera una señal.
    """
    signal["type"] = "new_signal"
    signal["timestamp"] = datetime.utcnow().isoformat()
    await manager.broadcast(signal)
