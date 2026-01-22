"""
SIC Ultra - Indicadores Técnicos

Cálculo de indicadores técnicos para análisis de mercado.
"""

import numpy as np
from typing import List, Dict, Optional
from datetime import datetime


def calculate_sma(prices: List[float], period: int) -> List[float]:
    """
    Simple Moving Average (Media Móvil Simple)
    """
    if len(prices) < period:
        return []
    
    sma = []
    for i in range(period - 1, len(prices)):
        avg = sum(prices[i - period + 1:i + 1]) / period
        sma.append(avg)
    
    return sma


def calculate_ema(prices: List[float], period: int) -> List[float]:
    """
    Exponential Moving Average (Media Móvil Exponencial)
    """
    if len(prices) < period:
        return []
    
    multiplier = 2 / (period + 1)
    ema = [sum(prices[:period]) / period]  # Primera EMA = SMA
    
    for price in prices[period:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    
    return ema


def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """
    Relative Strength Index (Índice de Fuerza Relativa)
    
    - RSI > 70: Sobrecompra (posible venta)
    - RSI < 30: Sobreventa (posible compra)
    """
    if len(prices) < period + 1:
        return []
    
    # Calcular cambios
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    # Separar ganancias y pérdidas
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    # Calcular promedios iniciales
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    rsi = []
    
    # Calcular RSI
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))
    
    return rsi


def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """
    MACD (Moving Average Convergence Divergence)
    
    Returns:
        - macd_line: EMA rápida - EMA lenta
        - signal_line: EMA del MACD
        - histogram: Diferencia entre MACD y Signal
    """
    if len(prices) < slow:
        return {"macd_line": [], "signal_line": [], "histogram": []}
    
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    # Alinear longitudes
    diff = len(ema_fast) - len(ema_slow)
    ema_fast = ema_fast[diff:]
    
    # MACD Line
    macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
    
    # Signal Line
    signal_line = calculate_ema(macd_line, signal)
    
    # Histogram
    diff = len(macd_line) - len(signal_line)
    macd_aligned = macd_line[diff:]
    histogram = [m - s for m, s in zip(macd_aligned, signal_line)]
    
    return {
        "macd_line": macd_line,
        "signal_line": signal_line,
        "histogram": histogram
    }


def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict:
    """
    Bandas de Bollinger
    
    - Precio cerca de banda superior: posible sobrecompra
    - Precio cerca de banda inferior: posible sobreventa
    """
    if len(prices) < period:
        return {"upper": [], "middle": [], "lower": []}
    
    middle = calculate_sma(prices, period)
    
    upper = []
    lower = []
    
    for i in range(period - 1, len(prices)):
        window = prices[i - period + 1:i + 1]
        std = np.std(window)
        idx = i - period + 1
        upper.append(middle[idx] + (std_dev * std))
        lower.append(middle[idx] - (std_dev * std))
    
    return {
        "upper": upper,
        "middle": middle,
        "lower": lower
    }


def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
    """
    Average True Range (Rango Verdadero Promedio)
    
    Mide la volatilidad del mercado. Útil para calcular stop-loss.
    """
    if len(highs) < period + 1:
        return []
    
    true_ranges = []
    
    for i in range(1, len(highs)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        true_ranges.append(tr)
    
    # ATR = EMA del True Range
    atr = calculate_ema(true_ranges, period)
    
    return atr


def calculate_support_resistance(prices: List[float], window: int = 20) -> Dict:
    """
    Calcular niveles de soporte y resistencia
    """
    if len(prices) < window:
        return {"support": None, "resistance": None}
    
    recent = prices[-window:]
    
    return {
        "support": min(recent),
        "resistance": max(recent),
        "current": prices[-1],
        "distance_to_support": ((prices[-1] - min(recent)) / prices[-1]) * 100,
        "distance_to_resistance": ((max(recent) - prices[-1]) / prices[-1]) * 100
    }


def get_trend(prices: List[float], short_period: int = 10, long_period: int = 50) -> str:
    """
    Detectar tendencia basada en cruces de medias móviles
    
    Returns: "BULLISH", "BEARISH", o "NEUTRAL"
    """
    if len(prices) < long_period:
        return "NEUTRAL"
    
    sma_short = calculate_sma(prices, short_period)
    sma_long = calculate_sma(prices, long_period)
    
    if not sma_short or not sma_long:
        return "NEUTRAL"
    
    # Comparar últimas medias
    diff = len(sma_short) - len(sma_long)
    sma_short = sma_short[diff:]
    
    if sma_short[-1] > sma_long[-1]:
        return "BULLISH"
    elif sma_short[-1] < sma_long[-1]:
        return "BEARISH"
    else:
        return "NEUTRAL"


def calculate_indicators(candles: List[Dict]) -> Dict:
    """
    Calcular todos los indicadores técnicos para una lista de velas.
    
    Args:
        candles: Lista de velas con formato:
                [{"open": float, "high": float, "low": float, "close": float, "volume": float}]
    
    Returns:
        Dict con todos los indicadores calculados
    """
    if not candles or len(candles) < 50:
        return {}
    
    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    
    return {
        "rsi": calculate_rsi(closes, 14),
        "macd": calculate_macd(closes, 12, 26, 9),
        "bollinger": calculate_bollinger_bands(closes, 20, 2.0),
        "atr": calculate_atr(highs, lows, closes, 14),
        "trend": get_trend(closes, 10, 50),
        "support_resistance": calculate_support_resistance(closes, 20)
    }
