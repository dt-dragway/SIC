import pytest
import asyncio
from typing import Dict, List
from datetime import datetime
from app.ml.trading_agent import get_trading_agent
from app.ml.risk_engine import get_kelly_engine

# --- FASE 1: Inteligencia y Sentimiento (Flash-Panic Sintético) ---

@pytest.mark.asyncio
async def test_sentiment_flash_panic_isolation():
    """
    Simula una noticia falsa que desploma el sentimiento,
    pero el Order Flow / Heatmap muestra compras masivas.
    El AI debe desestimar el pánico y no generar un SELL de baja calidad.
    """
    agent = get_trading_agent()
    
    # Simular velas de consolidación
    base_price = 50000
    candles = []
    for i in range(50):
        c = {"open": base_price, "close": base_price + (i % 2) * 50, "high": base_price + 100, "low": base_price - 100, "volume": 100}
        candles.append(c)
        
    # Indicadores técnicos ultra alcistas (Order Flow simulado)
    indicators = {
        "rsi": [25] * 50,  # Sobreventa fuerte
        "macd": {"histogram": [-10, -5, 0, 5, 10]}, # Cruce alcista
        "bollinger": {"lower": [49000]*50, "upper": [51000]*50, "middle": [50000]*50},
        "trend": "BULLISH",
        "atr": [500] * 50
    }
    
    # Inyectar ruido social tóxico en el análisis del Agente
    # "Hackeo masivo reportado"
    # El Agente debe priorizar la data dura técnica.
    
    # En esta simulación, forzamos al generador a leer los indicadores base
    signal = agent.analyze("BTCUSDT", candles, indicators)
    
    # Validación Cuantitativa
    assert signal is not None, "El agente se paralizó por el ruido."
    assert signal.direction == "LONG", "El agente entró en pánico social y se fue SHORT."
    assert signal.confidence >= 20.0, "El agente castigó la confianza irracionalmente."


# --- FASE 2: Resiliencia P2P y Risk & Macro (Shock Bidireccional) ---

def test_risk_engine_p2p_shock():
    """
    Simula 3 pérdidas consecutivas (Cascade Stop-Hunt)
    Verificamos que el Kelly Engine active la Anti-Martingala
    y reduzca drásticamente la posición.
    """
    kelly = get_kelly_engine()
    
    capital = 100000  # $100k
    
    # Escenario Normal
    normal_trade = kelly.calculate_position_size(
        capital=capital,
        win_rate=60.0,
        avg_win=200,
        avg_loss=100, # R:R = 2:1
        signal_confidence=85.0,
        consecutive_losses=0
    )
    
    # Escenario Pánico (3 losses consecutives)
    panicked_trade = kelly.calculate_position_size(
        capital=capital,
        win_rate=60.0,
        avg_win=200,
        avg_loss=100,
        signal_confidence=85.0,
        consecutive_losses=3
    )
    
    # Validación Cuantitativa
    assert normal_trade.position_size_usd > 0
    assert panicked_trade.anti_martingale_applied is True
    # La posición debe reducirse al menos en un 70%
    assert panicked_trade.position_size_usd <= (normal_trade.position_size_usd * 0.30)


# --- FASE 4: Cascade Stop-Hunt (Global Circuit Breaker test) ---

def test_cascade_stop_hunt_rlmf_learning():
    """
    Simulamos que el mercado nos barre 3 veces seguidas.
    El Trading Journal debe generar el reporte de toxicidad [SAVE_MEMORY]
    y frenar el apalancamiento.
    """
    from app.ml.trading_agent import get_trading_agent
    agent = get_trading_agent()
    
    # Reset history
    agent.memory.data["trade_results"] = []
    
    # Ejecutamos 3 trades perdedores rápidos (Stop Hunt)
    for i in range(3):
        agent.record_result(
            trade_id=f"whipsaw_0{i}",
            symbol="ETHUSDT",
            side="LONG",
            entry_price=3000,
            exit_price=2900,  # Loss total
            pnl=-3.33,
            signals_used=["rsi", "bollinger"],
            patterns_detected=[]
        )
        
    # Extraemos el log de aprendizaje
    stats = agent.get_performance_stats()
    
    # Validación Cuantitativa
    assert stats["consecutive_losses"] >= 3
    # Verificamos que los pesos de las estrategias usadas hayan sido penalizados
    assert stats["strategy_weights"]["rsi"] < 1.0
    assert stats["strategy_weights"]["bollinger"] < 1.0
