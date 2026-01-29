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


# ============================================================
# INDICADORES PROFESIONALES AVANZADOS
# ============================================================

def calculate_stochastic_rsi(prices: List[float], rsi_period: int = 14, stoch_period: int = 14, k_smooth: int = 3, d_smooth: int = 3) -> Dict:
    """
    Stochastic RSI - Más sensible que RSI estándar para timing de entradas.
    
    - StochRSI > 80: Sobrecompra extrema
    - StochRSI < 20: Sobreventa extrema
    """
    rsi = calculate_rsi(prices, rsi_period)
    
    if len(rsi) < stoch_period:
        return {"k": [], "d": []}
    
    stoch_rsi = []
    for i in range(stoch_period - 1, len(rsi)):
        window = rsi[i - stoch_period + 1:i + 1]
        min_rsi = min(window)
        max_rsi = max(window)
        
        if max_rsi - min_rsi == 0:
            stoch_rsi.append(50)
        else:
            stoch_rsi.append(((rsi[i] - min_rsi) / (max_rsi - min_rsi)) * 100)
    
    # %K = SMA de StochRSI
    k_line = calculate_sma(stoch_rsi, k_smooth) if len(stoch_rsi) >= k_smooth else stoch_rsi
    
    # %D = SMA de %K
    d_line = calculate_sma(k_line, d_smooth) if len(k_line) >= d_smooth else k_line
    
    return {"k": k_line, "d": d_line}


def calculate_adx(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Dict:
    """
    ADX (Average Directional Index) - Mide la FUERZA de la tendencia.
    
    - ADX > 25: Tendencia fuerte (buena para seguir momentum)
    - ADX < 20: Mercado lateral (evitar trades de tendencia)
    - +DI > -DI: Tendencia alcista
    - -DI > +DI: Tendencia bajista
    """
    if len(highs) < period + 1:
        return {"adx": [], "plus_di": [], "minus_di": []}
    
    # Calcular +DM y -DM
    plus_dm = []
    minus_dm = []
    tr_list = []
    
    for i in range(1, len(highs)):
        high_diff = highs[i] - highs[i-1]
        low_diff = lows[i-1] - lows[i]
        
        # +DM
        if high_diff > low_diff and high_diff > 0:
            plus_dm.append(high_diff)
        else:
            plus_dm.append(0)
        
        # -DM
        if low_diff > high_diff and low_diff > 0:
            minus_dm.append(low_diff)
        else:
            minus_dm.append(0)
        
        # True Range
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        tr_list.append(tr)
    
    # Smooth con EMA
    atr = calculate_ema(tr_list, period)
    smooth_plus_dm = calculate_ema(plus_dm, period)
    smooth_minus_dm = calculate_ema(minus_dm, period)
    
    if not atr or not smooth_plus_dm or not smooth_minus_dm:
        return {"adx": [], "plus_di": [], "minus_di": []}
    
    # Calcular +DI y -DI
    min_len = min(len(atr), len(smooth_plus_dm), len(smooth_minus_dm))
    plus_di = []
    minus_di = []
    dx = []
    
    for i in range(min_len):
        if atr[i] != 0:
            pdi = (smooth_plus_dm[i] / atr[i]) * 100
            mdi = (smooth_minus_dm[i] / atr[i]) * 100
        else:
            pdi, mdi = 0, 0
        
        plus_di.append(pdi)
        minus_di.append(mdi)
        
        # DX
        if pdi + mdi != 0:
            dx.append(abs(pdi - mdi) / (pdi + mdi) * 100)
        else:
            dx.append(0)
    
    # ADX = EMA del DX
    adx = calculate_ema(dx, period) if len(dx) >= period else dx
    
    return {
        "adx": adx,
        "plus_di": plus_di,
        "minus_di": minus_di
    }


def detect_rsi_divergence(prices: List[float], rsi: List[float], lookback: int = 10) -> Dict:
    """
    Detectar divergencias RSI - Señales de reversión muy poderosas.
    
    - Divergencia Alcista: Precio hace lower low, RSI hace higher low → COMPRAR
    - Divergencia Bajista: Precio hace higher high, RSI hace lower high → VENDER
    """
    if len(prices) < lookback or len(rsi) < lookback:
        return {"bullish": False, "bearish": False, "type": None}
    
    # Alinear RSI con precios (RSI tiene menos elementos)
    offset = len(prices) - len(rsi)
    recent_prices = prices[-(lookback):]
    recent_rsi = rsi[-(lookback):]
    
    # Encontrar mínimos y máximos locales
    price_lows = []
    price_highs = []
    
    for i in range(1, len(recent_prices) - 1):
        if recent_prices[i] < recent_prices[i-1] and recent_prices[i] < recent_prices[i+1]:
            price_lows.append((i, recent_prices[i], recent_rsi[i] if i < len(recent_rsi) else 0))
        if recent_prices[i] > recent_prices[i-1] and recent_prices[i] > recent_prices[i+1]:
            price_highs.append((i, recent_prices[i], recent_rsi[i] if i < len(recent_rsi) else 0))
    
    # Detectar divergencia alcista (bullish)
    bullish_div = False
    if len(price_lows) >= 2:
        last_low = price_lows[-1]
        prev_low = price_lows[-2]
        # Precio hace lower low pero RSI hace higher low
        if last_low[1] < prev_low[1] and last_low[2] > prev_low[2]:
            bullish_div = True
    
    # Detectar divergencia bajista (bearish)
    bearish_div = False
    if len(price_highs) >= 2:
        last_high = price_highs[-1]
        prev_high = price_highs[-2]
        # Precio hace higher high pero RSI hace lower high
        if last_high[1] > prev_high[1] and last_high[2] < prev_high[2]:
            bearish_div = True
    
    div_type = None
    if bullish_div:
        div_type = "BULLISH_DIVERGENCE"
    elif bearish_div:
        div_type = "BEARISH_DIVERGENCE"
    
    return {
        "bullish": bullish_div,
        "bearish": bearish_div,
        "type": div_type
    }


def calculate_volume_profile(volumes: List[float], lookback: int = 20) -> Dict:
    """
    Análisis de volumen para confirmar movimientos.
    
    - Volumen creciente: Confirma la tendencia
    - Volumen decreciente: Tendencia débil
    - Volumen extremo: Posible reversión
    """
    if len(volumes) < lookback:
        return {"trend": "NEUTRAL", "ratio": 1.0, "is_high": False}
    
    recent = volumes[-lookback:]
    avg_volume = sum(recent) / len(recent)
    current_volume = volumes[-1]
    
    # Ratio actual vs promedio
    ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
    
    # Tendencia del volumen
    first_half = sum(recent[:lookback//2]) / (lookback//2)
    second_half = sum(recent[lookback//2:]) / (lookback//2)
    
    if second_half > first_half * 1.2:
        vol_trend = "INCREASING"
    elif second_half < first_half * 0.8:
        vol_trend = "DECREASING"
    else:
        vol_trend = "STABLE"
    
    return {
        "trend": vol_trend,
        "ratio": round(ratio, 2),
        "is_high": ratio > 1.5,  # Volumen 50% superior al promedio
        "is_extreme": ratio > 2.5,  # Posible climax
        "average": round(avg_volume, 2)
    }


def get_multi_ema(prices: List[float]) -> Dict:
    """
    Calcular múltiples EMAs usadas por traders profesionales.
    
    - EMA 9: Muy corto plazo (scalping)
    - EMA 21: Corto plazo
    - EMA 50: Medio plazo
    - EMA 200: Largo plazo (golden/death cross)
    """
    return {
        "ema_9": calculate_ema(prices, 9),
        "ema_21": calculate_ema(prices, 21),
        "ema_50": calculate_ema(prices, 50),
        "ema_200": calculate_ema(prices, 200) if len(prices) >= 200 else []
    }


def get_ema_alignment(prices: List[float]) -> Dict:
    """
    Verificar alineación de EMAs para confirmar tendencia fuerte.
    
    - Perfect Bullish: 9 > 21 > 50 > 200 (todos alineados hacia arriba)
    - Perfect Bearish: 9 < 21 < 50 < 200 (todos alineados hacia abajo)
    """
    emas = get_multi_ema(prices)
    
    if not emas["ema_9"] or not emas["ema_21"] or not emas["ema_50"]:
        return {"alignment": "NEUTRAL", "score": 0, "description": "Datos insuficientes"}
    
    e9 = emas["ema_9"][-1]
    e21 = emas["ema_21"][-1]
    e50 = emas["ema_50"][-1]
    e200 = emas["ema_200"][-1] if emas["ema_200"] else e50  # Usar EMA 50 si no hay 200
    
    current = prices[-1]
    
    # Calcular score de alineación
    score = 0
    if current > e9:
        score += 1
    if e9 > e21:
        score += 1
    if e21 > e50:
        score += 1
    if e50 > e200:
        score += 1
    
    # Invertir para bearish
    bearish_score = 4 - score
    
    if score == 4:
        alignment = "PERFECT_BULLISH"
        desc = "Todas las EMAs alineadas alcistas (9 > 21 > 50 > 200)"
    elif score >= 3:
        alignment = "BULLISH"
        desc = "Mayoría de EMAs alcistas"
    elif bearish_score == 4:
        alignment = "PERFECT_BEARISH"
        desc = "Todas las EMAs alineadas bajistas (9 < 21 < 50 < 200)"
    elif bearish_score >= 3:
        alignment = "BEARISH"
        desc = "Mayoría de EMAs bajistas"
    else:
        alignment = "MIXED"
        desc = "EMAs mezcladas, sin tendencia clara"
    
    return {
        "alignment": alignment,
        "score": score,
        "bearish_score": bearish_score,
        "description": desc,
        "values": {
            "ema_9": round(e9, 2),
            "ema_21": round(e21, 2),
            "ema_50": round(e50, 2),
            "ema_200": round(e200, 2)
        }
    }


def calculate_fibonacci_levels(prices: List[float], lookback: int = 50) -> Dict:
    """
    Calcular niveles de Fibonacci para encontrar zonas de entrada/salida.
    
    Niveles clave: 23.6%, 38.2%, 50%, 61.8%, 78.6%
    """
    if len(prices) < lookback:
        return {"levels": {}, "trend": "NEUTRAL"}
    
    recent = prices[-lookback:]
    high = max(recent)
    low = min(recent)
    diff = high - low
    
    # Determinar tendencia para calcular retrocesos
    if prices[-1] > prices[-lookback]:
        # Tendencia alcista: retrocesos desde el máximo
        trend = "BULLISH"
        levels = {
            "0.0": round(high, 2),
            "0.236": round(high - (diff * 0.236), 2),
            "0.382": round(high - (diff * 0.382), 2),
            "0.5": round(high - (diff * 0.5), 2),
            "0.618": round(high - (diff * 0.618), 2),
            "0.786": round(high - (diff * 0.786), 2),
            "1.0": round(low, 2)
        }
    else:
        # Tendencia bajista: retrocesos desde el mínimo
        trend = "BEARISH"
        levels = {
            "0.0": round(low, 2),
            "0.236": round(low + (diff * 0.236), 2),
            "0.382": round(low + (diff * 0.382), 2),
            "0.5": round(low + (diff * 0.5), 2),
            "0.618": round(low + (diff * 0.618), 2),
            "0.786": round(low + (diff * 0.786), 2),
            "1.0": round(high, 2)
        }
    
    # Encontrar nivel más cercano al precio actual
    current = prices[-1]
    closest_level = min(levels.items(), key=lambda x: abs(x[1] - current))
    
    return {
        "levels": levels,
        "trend": trend,
        "high": round(high, 2),
        "low": round(low, 2),
        "current": round(current, 2),
        "closest_level": closest_level[0],
        "closest_price": closest_level[1]
    }

