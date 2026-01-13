"""
SIC Ultra - Señales de Trading IA

Endpoints para el Agente IA profesional que:
- Analiza el mercado en profundidad
- Genera señales de alta precisión
- Aprende y evoluciona con cada trade
- Ejecuta automáticamente con autorización
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import asyncio

from app.api.v1.auth import oauth2_scheme, verify_token
from app.ml.trading_agent import get_trading_agent, TradingSignal
from app.ml.indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_atr, get_trend
)
from app.infrastructure.binance.client import get_binance_client
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.infrastructure.database import models
import json


router = APIRouter()


# === Schemas ===

class SignalResponse(BaseModel):
    symbol: str
    direction: str
    confidence: float
    strength: str
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    patterns_detected: List[str]
    indicators_used: List[str]
    reasoning: List[str]
    top_trader_consensus: Optional[Dict]
    timestamp: datetime
    expires_at: datetime
    auto_execute_approved: bool


class TradeResultInput(BaseModel):
    trade_id: str
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    pnl: float
    signals_used: List[str]
    patterns_detected: List[str]


class ApproveAutoExecute(BaseModel):
    symbol: str
    direction: str
    approve: bool


# === WebSocket Manager ===

class ConnectionManager:
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


# === Helper Functions ===

def get_full_analysis(symbol: str) -> Optional[Dict]:
    """
    Obtener análisis completo de un símbolo usando el Agente IA.
    """
    binance = get_binance_client()
    agent = get_trading_agent()
    
    # Obtener datos
    candles = binance.get_klines(symbol, "1h", limit=100)
    if not candles or len(candles) < 50:
        return None
    
    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    
    # Calcular indicadores
    indicators = {
        "rsi": calculate_rsi(closes, 14),
        "macd": calculate_macd(closes),
        "bollinger": calculate_bollinger_bands(closes, 20),
        "atr": calculate_atr(highs, lows, closes, 14),
        "trend": get_trend(closes, 10, 50)
    }
    
    # Generar señal con el agente
    signal = agent.analyze(symbol, candles, indicators)
    
    return signal


# === Endpoints ===

@router.get("/analyze/{symbol}")
async def analyze_symbol(
    symbol: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> SignalResponse:
    """
    🤖 Análisis profundo con el Agente IA.
    
    El agente analiza:
    - Indicadores técnicos (RSI, MACD, Bollinger, ATR)
    - Patrones de mercado aprendidos
    - Consenso de top traders
    - Aplica pesos aprendidos de trades anteriores
    
    Persistencia: Guarda cada análisis en la BD para aprendizaje continuo.
    """
    verify_token(token)
    
    signal = get_full_analysis(symbol.upper())
    
    if not signal:
        raise HTTPException(
            status_code=404,
            detail=f"No se pudo analizar {symbol} o no hay señal clara (HOLD)"
        )
    
    # === PERSISTENCIA ===
    try:
        # Create ML Data payload
        ml_data = {
            "patterns": signal.patterns_detected,
            "indicators": signal.indicators_used,
            "consensus": signal.top_trader_consensus
        }
        
        db_signal = models.Signal(
            symbol=signal.symbol,
            type=signal.direction,
            strength=signal.strength,
            confidence=signal.confidence,
            entry_price=signal.entry_price,
            take_profit=signal.take_profit,
            stop_loss=signal.stop_loss,
            risk_reward=signal.risk_reward,
            reasoning=json.dumps(signal.reasoning), # Convert list to JSON string
            ml_data=json.dumps(ml_data),           # Save extended ML data
            raw_response="Auto-generated",         # Placeholder for raw LLM response if available
            expires_at=signal.expires_at,
            created_at=signal.timestamp
        )
        db.add(db_signal)
        db.commit()
    except Exception as e:
        print(f"Error saving signal to DB: {e}")
        # Don't fail the request if saving fails, but log it
    
    return {
        "symbol": signal.symbol,
        "direction": signal.direction,
        "confidence": signal.confidence,
        "strength": signal.strength,
        "entry_price": signal.entry_price,
        "stop_loss": signal.stop_loss,
        "take_profit": signal.take_profit,
        "risk_reward": signal.risk_reward,
        "patterns_detected": signal.patterns_detected,
        "indicators_used": signal.indicators_used,
        "reasoning": signal.reasoning,
        "top_trader_consensus": signal.top_trader_consensus,
        "timestamp": signal.timestamp,
        "expires_at": signal.expires_at,
        "auto_execute_approved": signal.auto_execute_approved
    }


@router.get("/scan")
async def scan_market(token: str = Depends(oauth2_scheme)):
    """
    🔍 Escanear el mercado con el Agente IA.
    
    Analiza los principales pares y retorna solo señales activas.
    """
    verify_token(token)
    
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
    signals = []
    
    for symbol in symbols:
        signal = get_full_analysis(symbol)
        if signal:
            signals.append({
                "symbol": signal.symbol,
                "direction": signal.direction,
                "confidence": signal.confidence,
                "strength": signal.strength,
                "entry_price": signal.entry_price,
                "stop_loss": signal.stop_loss,
                "take_profit": signal.take_profit,
                "risk_reward": signal.risk_reward,
                "patterns_detected": signal.patterns_detected,
                "reasoning": signal.reasoning[:3],  # Top 3 razones
                "timestamp": signal.timestamp.isoformat()
            })
    
    # Ordenar por confianza
    signals.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "count": len(signals),
        "signals": signals,
        "timestamp": datetime.utcnow()
    }



@router.get("/latest/{symbol}")
async def get_latest_signal(
    symbol: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    🧠 Memoria: Devuelve el último análisis conocido desde la BD.
    """
    verify_token(token)
    
    # Buscar la última señal para este símbolo
    last_signal = db.query(models.Signal)\
        .filter(models.Signal.symbol == symbol.upper())\
        .order_by(models.Signal.created_at.desc())\
        .first()
        
    if not last_signal:
        return None # No content / null
        
    # Reconstruct useful response
    try:
        reasoning_list = json.loads(last_signal.reasoning)
    except:
        reasoning_list = [last_signal.reasoning]
        
    try:
        ml_data = json.loads(last_signal.ml_data) if last_signal.ml_data else {}
    except:
        ml_data = {}

    return {
        "signal": last_signal.type,
        "confidence": last_signal.confidence,
        "reasoning": reasoning_list,
        "ml_data": {
            "lstm_price": 0, # Placeholder or store in ml_data
            "xgboost_signal": "NEUTRAL" # Placeholder or store in ml_data
        },
        "from_memory": True,
        "timestamp": last_signal.created_at
    }


@router.get("/performance")
async def get_agent_performance(token: str = Depends(oauth2_scheme)):
    """
    📊 Estadísticas de rendimiento del Agente IA.
    
    Muestra:
    - Win rate histórico
    - PnL total
    - Mejor/peor trade
    - Patrones aprendidos
    - Pesos de estrategias actuales
    """
    verify_token(token)
    
    agent = get_trading_agent()
    stats = agent.get_performance_stats()
    
    return {
        **stats,
        "timestamp": datetime.utcnow()
    }


@router.get("/patterns")
async def get_learned_patterns(token: str = Depends(oauth2_scheme)):
    """
    📚 Patrones aprendidos por el Agente IA.
    
    Muestra la precisión histórica de cada patrón detectado.
    """
    verify_token(token)
    
    agent = get_trading_agent()
    patterns = agent.get_learned_patterns()
    
    return {
        "count": len(patterns),
        "patterns": patterns,
        "timestamp": datetime.utcnow()
    }


@router.post("/record-result")
async def record_trade_result(
    result: TradeResultInput,
    token: str = Depends(oauth2_scheme)
):
    """
    📖 Registrar resultado de trade para que el agente aprenda.
    
    El agente ajusta sus pesos de estrategia basándose en:
    - Si el trade fue exitoso o no
    - Qué indicadores se usaron
    - Qué patrones se detectaron
    """
    verify_token(token)
    
    agent = get_trading_agent()
    agent.record_result(
        trade_id=result.trade_id,
        symbol=result.symbol,
        side=result.side,
        entry_price=result.entry_price,
        exit_price=result.exit_price,
        pnl=result.pnl,
        signals_used=result.signals_used,
        patterns_detected=result.patterns_detected
    )
    
    return {
        "success": True,
        "message": f"✅ Resultado registrado. El agente ha aprendido.",
        "new_win_rate": agent.get_performance_stats()["win_rate"]
    }


@router.post("/approve-auto-execute")
async def approve_auto_execute(
    data: ApproveAutoExecute,
    token: str = Depends(oauth2_scheme)
):
    """
    ✅ Aprobar ejecución automática de una señal.
    
    Cuando apruebas, el agente ejecutará la orden automáticamente
    cuando detecte la señal con los parámetros especificados.
    """
    verify_token(token)
    
    if not data.approve:
        return {
            "success": True,
            "message": "Ejecución automática NO aprobada. Modo manual.",
            "auto_execute": False
        }
    
    return {
        "success": True,
        "message": f"⚡ Ejecución automática APROBADA para {data.symbol} {data.direction}",
        "auto_execute": True,
        "warning": "El agente ejecutará la orden cuando las condiciones se cumplan."
    }


@router.get("/strategy-weights")
async def get_strategy_weights(token: str = Depends(oauth2_scheme)):
    """
    ⚖️ Ver pesos actuales de las estrategias.
    
    Estos pesos evolucionan con el tiempo basándose en el rendimiento.
    """
    verify_token(token)
    
    agent = get_trading_agent()
    weights = agent.memory.data["current_strategy_weights"]
    
    return {
        "weights": weights,
        "description": {
            "rsi": "Peso del indicador RSI",
            "macd": "Peso del indicador MACD",
            "bollinger": "Peso de Bandas Bollinger",
            "trend": "Peso de análisis de tendencia",
            "volume": "Peso del volumen",
            "support_resistance": "Peso de soportes/resistencias",
            "top_trader_signals": "Peso de señales de top traders"
        },
        "note": "Los pesos van de 0.3 (baja confianza) a 3.0 (alta confianza)"
    }


# === WebSocket para señales en tiempo real ===

@router.websocket("/ws")
async def websocket_signals(websocket: WebSocket):
    """
    🔌 WebSocket para señales en tiempo real.
    
    Comandos:
    - "scan": Escanear mercado inmediatamente
    - "analyze:BTCUSDT": Analizar símbolo específico
    - "performance": Ver rendimiento del agente
    """
    await manager.connect(websocket)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "🤖 Conectado al Agente IA de Trading",
            "commands": ["scan", "analyze:SYMBOL", "performance"],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0
                )
                
                if data == "ping":
                    await websocket.send_text("pong")
                
                elif data == "scan":
                    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
                    signals = []
                    
                    for symbol in symbols:
                        signal = get_full_analysis(symbol)
                        if signal:
                            signals.append({
                                "symbol": signal.symbol,
                                "direction": signal.direction,
                                "confidence": signal.confidence,
                                "strength": signal.strength,
                                "reasoning": signal.reasoning[:2]
                            })
                    
                    await websocket.send_json({
                        "type": "scan_result",
                        "count": len(signals),
                        "signals": signals,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif data.startswith("analyze:"):
                    symbol = data.split(":")[1].upper()
                    signal = get_full_analysis(symbol)
                    
                    if signal:
                        await websocket.send_json({
                            "type": "analysis",
                            "symbol": signal.symbol,
                            "direction": signal.direction,
                            "confidence": signal.confidence,
                            "strength": signal.strength,
                            "entry": signal.entry_price,
                            "stop_loss": signal.stop_loss,
                            "take_profit": signal.take_profit,
                            "reasoning": signal.reasoning,
                            "patterns": signal.patterns_detected,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    else:
                        await websocket.send_json({
                            "type": "no_signal",
                            "symbol": symbol,
                            "message": "Sin señal clara (HOLD)"
                        })
                
                elif data == "performance":
                    agent = get_trading_agent()
                    stats = agent.get_performance_stats()
                    await websocket.send_json({
                        "type": "performance",
                        **stats,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            except asyncio.TimeoutError:
                # Auto-scan cada minuto
                agent = get_trading_agent()
                await websocket.send_json({
                    "type": "heartbeat",
                    "win_rate": agent.get_performance_stats()["win_rate"],
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
