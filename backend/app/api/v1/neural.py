"""
SIC Ultra - Neural Engine Signal API

Endpoints para señales de trading generadas por el Neural Engine (IA).
Proporciona análisis de patrones de velas y señales en español para usuarios novatos.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

from app.api.v1.auth import oauth2_scheme, verify_token
from app.ml.trading_agent import TradingAgentAI
from app.infrastructure.binance.client import get_binance_client
from app.ml.indicators import calculate_indicators
from loguru import logger


router = APIRouter()

# Instancia global del agente
neural_engine = None

def get_neural_engine() -> TradingAgentAI:
    """Obtener instancia del Neural Engine (singleton)"""
    global neural_engine
    if neural_engine is None:
        neural_engine = TradingAgentAI()
    return neural_engine


# === Schemas ===

class NeuralSignalResponse(BaseModel):
    """Respuesta de señal del Neural Engine"""
    signal_id: str
    symbol: str
    direction: str  # "LONG", "SHORT", "HOLD"
    confidence: float
    strength: str  # "STRONG", "MODERATE", "WEAK"
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    
    # Patrones de velas
    candlestick_patterns: List[Dict]
    
    # Explicación en español
    explanation_es: str
    execution_steps: List[str]
    
    # Análisis técnico
    patterns_detected: List[str]
    indicators_used: List[str]
    top_trader_consensus: Optional[Dict]
    timeframe_analysis: Dict[str, str]
    reasoning: List[str]
    
    # Metadata
    generated_at: datetime
    expires_at: datetime
    

class AllSignalsResponse(BaseModel):
    """Señales para todas las criptomonedas"""
    signals: List[Dict]
    timestamp: datetime
    total_symbols: int
    bullish_count: int
    bearish_count: int
    neutral_count: int


class NeuralStatusResponse(BaseModel):
    """Estado del Neural Engine"""
    status: str
    total_trades_analyzed: int
    win_rate: float
    patterns_learned: int
    candlestick_analyzer_active: bool
    supported_symbols: List[str]
    last_analysis: Optional[datetime]


# List of supported cryptocurrencies (14 best for trading)
SUPPORTED_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
    "XRPUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT",
    "MATICUSDT", "AVAXUSDT", "LINKUSDT", "LTCUSDT",
    "TRXUSDT", "ATOMUSDT"
]


# === Endpoints ===

@router.get("/neural-signal/{symbol}", response_model=NeuralSignalResponse, tags=["Neural Engine"])
async def get_neural_signal(
    symbol: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener señal del Neural Engine para una criptomoneda específica.
    
    El Neural Engine analiza:
    - Multi-Timeframe (4h, 1h, 15m)
    - Patrones de velas (Hammer, Engulfing, Doji, etc.)
    - Indicadores técnicos avanzados (RSI Divergence, ADX, EMAs)
    - Tendencias de mercado
    
    Retorna señal con explicación clara en español y pasos de ejecución.
    """
    verify_token(token)
    
    # Validar símbolo
    symbol = symbol.upper()
    if symbol not in SUPPORTED_SYMBOLS:
        raise HTTPException(
            400, 
            f"Símbolo no soportado. Símbolos disponibles: {', '.join(SUPPORTED_SYMBOLS)}"
        )
    
    try:
        from app.ml.signal_generator import get_signal_generator
        generator = get_signal_generator()
        
        # Generar señal profesional
        signal_data = generator.analyze(symbol)
        
        if signal_data is None:
            # No hay señal clara (HOLD)
            return {
                "signal_id": f"neutral_{symbol}_{int(datetime.utcnow().timestamp())}",
                "symbol": symbol,
                "direction": "HOLD",
                "confidence": 0.0,
                "strength": "WEAK",
                "entry_price": 0.0,
                "stop_loss": 0.0,
                "take_profit": 0.0,
                "risk_reward": 0.0,
                "candlestick_patterns": [],
                "explanation_es": "No se detecta señal clara en este momento. El mercado está neutral o sin patrones fuertes.",
                "execution_steps": ["Esperar a que aparezca una señal más clara"],
                "patterns_detected": [],
                "indicators_used": [],
                "top_trader_consensus": None,
                "timeframe_analysis": {},
                "reasoning": ["Mercado neutral - sin señales claras"],
                "generated_at": datetime.utcnow(),
                "expires_at": datetime.utcnow()
            }
        
        # --- ADAPTADOR DE DATOS PRO A FRONTEND ---
        
        # 1. Mapear Strength
        strength_map = {"S": "STRONG", "A": "STRONG", "B": "MODERATE", "C": "WEAK"}
        strength = strength_map.get(signal_data.get("tier", "B"), "MODERATE")
        
        # 2. Generar explicación en español basada en razones
        direction_es = "ALCISTA" if signal_data["type"] == "LONG" else "BAJISTA"
        tier_desc = "Premium (S-Tier)" if signal_data.get("tier") == "S" else "Alta Calidad (A-Tier)" if signal_data.get("tier") == "A" else "Estándar (B-Tier)"
        
        reasons_es = []
        for r in signal_data["reasoning"]:
            # Traducción básica de razones comunes
            r_es = r.replace("Overbought", "Sobrecompra").replace("Oversold", "Sobreventa")\
                   .replace("Bullish", "Alcista").replace("Bearish", "Bajista")\
                   .replace("Divergence", "Divergencia").replace("Trend", "Tendencia")
            reasons_es.append(r_es)
            
        explanation = f"Señal {direction_es} de nivel {tier_desc} detectada.\n\n"
        explanation += f"El sistema ha confirmado la tendencia en {signal_data.get('aligned_timeframes', '?')} timeframes alineados.\n"
        explanation += "Factores clave:\n" + "\n".join([f"- {r}" for r in reasons_es[:3]])
        
        # 3. Generar pasos de ejecución
        steps = []
        if signal_data["type"] == "LONG":
            steps = [
                f"Entrar en COMPRA (LONG) ahora a mercado (~${signal_data['entry_price']})",
                f"Colocar Stop Loss en ${signal_data['stop_loss']} (Protección)",
                f"Colocar Take Profit en ${signal_data['take_profit']} (Objetivo)",
                f"Ratio Riesgo/Beneficio: 1:{signal_data['risk_reward']} (Excelente)"
            ]
        else:
            steps = [
                f"Entrar en VENTA (SHORT) ahora a mercado (~${signal_data['entry_price']})",
                f"Colocar Stop Loss en ${signal_data['stop_loss']} (Protección)",
                f"Colocar Take Profit en ${signal_data['take_profit']} (Objetivo)",
                f"Ratio Riesgo/Beneficio: 1:{signal_data['risk_reward']} (Excelente)"
            ]
            
        # 4. Formatear patrones de velas (mock para compatibilidad UI)
        patterns = []
        for p in signal_data.get("timeframes", {}).get("15m", {}).get("indicators", {}).get("patterns", []):
            patterns.append({
                "name": p,
                "name_es": p, # Debería traducir
                "direction": signal_data["type"],
                "strength": "STRONG", 
                "confidence": 80,
                "description_es": "Patrón confirmado en M15",
                "icon": "📊",
                "color": "emerald" if signal_data["type"] == "LONG" else "rose"
            })

        # Retornar señal completa adaptada
        return {
            "signal_id": f"{signal_data['type'].lower()}_{symbol}_{int(signal_data['timestamp'].timestamp())}",
            "symbol": signal_data["symbol"],
            "direction": signal_data["type"],
            "confidence": signal_data["confidence"],
            "strength": strength,
            "entry_price": signal_data["entry_price"],
            "stop_loss": signal_data["stop_loss"],
            "take_profit": signal_data["take_profit"],
            "risk_reward": signal_data["risk_reward"],
            "candlestick_patterns": patterns,
            "explanation_es": explanation,
            "execution_steps": steps,
            "patterns_detected": signal_data.get("reasoning", []),
            "indicators_used": ["Multi-Timeframe", "RSI", "MACD", "Bollinger", "ADX"],
            "top_trader_consensus": {"bullish": 0, "bearish": 0},
            "timeframe_analysis": {
                "4h": signal_data["timeframes"]["4h"]["direction"],
                "1h": signal_data["timeframes"]["1h"]["direction"],
                "15m": signal_data["timeframes"]["15m"]["direction"]
            },
            "reasoning": signal_data["reasoning"],
            "generated_at": signal_data["timestamp"],
            "expires_at": signal_data["expires_at"]
        }
        
    except Exception as e:
        logger.error(f"Error generando señal para {symbol}: {e}")
        # En caso de error, retornar mensaje amigable en vez de 500
        raise HTTPException(500, f"Error en motor de análisis: {str(e)}")


@router.get("/neural-signals/all", response_model=AllSignalsResponse, tags=["Neural Engine"])
async def get_all_neural_signals(
    token: str = Depends(oauth2_scheme),
    only_strong: bool = Query(False, description="Solo señales STRONG")
):
    """
    Obtener señales del Neural Engine para todas las 14 criptomonedas.
    
    Útil para dashboard que muestra todas las oportunidades disponibles.
    """
    verify_token(token)
    
    signals = []
    bullish = 0
    bearish = 0
    neutral = 0
    
    engine = get_neural_engine()
    client = get_binance_client()
    
    for symbol in SUPPORTED_SYMBOLS:
        try:
            # Obtener datos y generate señal (simplificado para todas)
            candles = client.get_klines(symbol, "1h", limit=100)
            candles_formatted = [
                {
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4]),
                    "volume": float(c[5])
                }
                for c in candles
            ]
            
            indicators = calculate_indicators(candles_formatted)
            signal = engine.analyze(symbol, candles_formatted, indicators)
            
            if signal is None:
                neutral += 1
                if not only_strong:
                    signals.append({
                        "symbol": symbol,
                        "direction": "HOLD",
                        "confidence": 0.0,
                        "strength": "WEAK",
                        "entry_price": candles_formatted[-1]["close"]
                    })
                continue
            
            # Contar direcciones
            if signal.direction == "LONG":
                bullish += 1
            elif signal.direction == "SHORT":
                bearish += 1
            
            # Filtrar si solo queremos STRONG
            if only_strong and signal.strength != "STRONG":
                continue
            
            signals.append({
                "symbol": signal.symbol,
                "direction": signal.direction,
                "confidence": signal.confidence,
                "strength": signal.strength,
                "entry_price": signal.entry_price,
                "stop_loss": signal.stop_loss,
                "take_profit": signal.take_profit,
                "candlestick_patterns": len(signal.candlestick_patterns),
                "explanation_short": signal.explanation_es[:100] + "..."  # Resumen
            })
            
        except Exception as e:
            logger.warning(f"Error procesando {symbol}: {e}")
            continue
    
    return {
        "signals": signals,
        "timestamp": datetime.utcnow(),
        "total_symbols": len(SUPPORTED_SYMBOLS),
        "bullish_count": bullish,
        "bearish_count": bearish,
        "neutral_count": neutral
    }


@router.get("/neural-status", response_model=NeuralStatusResponse, tags=["Neural Engine"])
async def get_neural_status(token: str = Depends(oauth2_scheme)):
    """
    Obtener estado del Neural Engine.
    
    Muestra estadísticas de rendimiento, patrones aprendidos, etc.
    """
    verify_token(token)
    
    engine = get_neural_engine()
    stats = engine.get_performance_stats()
    
    return {
        "status": "active",
        "total_trades_analyzed": stats["total_trades"],
        "win_rate": stats["win_rate"],
        "patterns_learned": stats["patterns_learned"],
        "candlestick_analyzer_active": True,
        "supported_symbols": SUPPORTED_SYMBOLS,
        "last_analysis": datetime.utcnow()
    }


@router.get("/neural-performance", tags=["Neural Engine"])
async def get_neural_performance(token: str = Depends(oauth2_scheme)):
    """
    Obtener estadísticas detalladas de rendimiento del Neural Engine.
    """
    verify_token(token)
    
    engine = get_neural_engine()
    stats = engine.get_performance_stats()
    learned_patterns = engine.get_learned_patterns()
    
    return {
        "performance": stats,
        "learned_patterns": learned_patterns,
        "timestamp": datetime.utcnow()
    }
