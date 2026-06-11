"""
SIC Ultra - Detector de Patrones de Velas Japonesas

Detecta patrones de velas profesionales para confirmar señales de trading.
Cada patrón tiene un score de fuerza y dirección.
"""

from typing import Dict, List, Optional
from loguru import logger


def analyze_candle(candle: Dict) -> Dict:
    """
    Analizar propiedades de una vela individual.
    """
    open_price = candle["open"]
    close = candle["close"]
    high = candle["high"]
    low = candle["low"]
    
    body = abs(close - open_price)
    upper_shadow = high - max(close, open_price)
    lower_shadow = min(close, open_price) - low
    total_range = high - low
    
    is_bullish = close > open_price
    
    # Ratios importantes
    body_ratio = body / total_range if total_range > 0 else 0
    upper_ratio = upper_shadow / total_range if total_range > 0 else 0
    lower_ratio = lower_shadow / total_range if total_range > 0 else 0
    
    return {
        "open": open_price,
        "close": close,
        "high": high,
        "low": low,
        "body": body,
        "upper_shadow": upper_shadow,
        "lower_shadow": lower_shadow,
        "total_range": total_range,
        "is_bullish": is_bullish,
        "body_ratio": body_ratio,
        "upper_ratio": upper_ratio,
        "lower_ratio": lower_ratio
    }


def is_doji(candle: Dict, threshold: float = 0.1) -> bool:
    """
    Doji: Cuerpo muy pequeño, señal de indecisión.
    
    Interpretación:
    - En tendencia alcista: posible reversión bajista
    - En tendencia bajista: posible reversión alcista
    """
    c = analyze_candle(candle)
    return c["body_ratio"] < threshold


def is_hammer(candle: Dict, prev_candle: Dict = None) -> bool:
    """
    Hammer (Martillo): Cola inferior larga, cuerpo pequeño arriba.
    
    Señal ALCISTA fuerte cuando aparece en tendencia bajista.
    La cola inferior debe ser al menos 2x el cuerpo.
    """
    c = analyze_candle(candle)
    
    # Cuerpo pequeño, sombra inferior larga, sombra superior mínima
    has_small_body = c["body_ratio"] < 0.35
    has_long_lower = c["lower_ratio"] > 0.55
    has_small_upper = c["upper_ratio"] < 0.15
    
    return has_small_body and has_long_lower and has_small_upper


def is_inverted_hammer(candle: Dict) -> bool:
    """
    Inverted Hammer: Cola superior larga, cuerpo pequeño abajo.
    
    Señal alcista cuando aparece en tendencia bajista.
    """
    c = analyze_candle(candle)
    
    has_small_body = c["body_ratio"] < 0.35
    has_long_upper = c["upper_ratio"] > 0.55
    has_small_lower = c["lower_ratio"] < 0.15
    
    return has_small_body and has_long_upper and has_small_lower


def is_shooting_star(candle: Dict) -> bool:
    """
    Shooting Star: Igual que inverted hammer pero en tendencia alcista.
    
    Señal BAJISTA cuando aparece en tendencia alcista.
    """
    c = analyze_candle(candle)
    
    has_small_body = c["body_ratio"] < 0.35
    has_long_upper = c["upper_ratio"] > 0.55
    has_small_lower = c["lower_ratio"] < 0.15
    is_bearish = not c["is_bullish"]
    
    return has_small_body and has_long_upper and has_small_lower and is_bearish


def is_hanging_man(candle: Dict) -> bool:
    """
    Hanging Man: Martillo en tendencia alcista (señal bajista).
    """
    c = analyze_candle(candle)
    
    has_small_body = c["body_ratio"] < 0.35
    has_long_lower = c["lower_ratio"] > 0.55
    has_small_upper = c["upper_ratio"] < 0.15
    is_bearish = not c["is_bullish"]
    
    return has_small_body and has_long_lower and has_small_upper and is_bearish


def is_bullish_engulfing(candles: List[Dict]) -> bool:
    """
    Bullish Engulfing: Vela alcista que envuelve completamente la anterior.
    
    Señal ALCISTA muy fuerte. La vela verde debe abrir por debajo y
    cerrar por encima de la vela roja anterior.
    """
    if len(candles) < 2:
        return False
    
    prev = analyze_candle(candles[-2])
    curr = analyze_candle(candles[-1])
    
    # La anterior debe ser bajista, la actual alcista
    prev_bearish = not prev["is_bullish"]
    curr_bullish = curr["is_bullish"]
    
    # La actual envuelve a la anterior
    engulfs = curr["open"] <= prev["close"] and curr["close"] >= prev["open"]
    
    # El cuerpo actual es significativamente más grande
    bigger_body = curr["body"] > prev["body"] * 1.2
    
    return prev_bearish and curr_bullish and engulfs and bigger_body


def is_bearish_engulfing(candles: List[Dict]) -> bool:
    """
    Bearish Engulfing: Vela bajista que envuelve completamente la anterior.
    
    Señal BAJISTA muy fuerte.
    """
    if len(candles) < 2:
        return False
    
    prev = analyze_candle(candles[-2])
    curr = analyze_candle(candles[-1])
    
    prev_bullish = prev["is_bullish"]
    curr_bearish = not curr["is_bullish"]
    
    engulfs = curr["open"] >= prev["close"] and curr["close"] <= prev["open"]
    bigger_body = curr["body"] > prev["body"] * 1.2
    
    return prev_bullish and curr_bearish and engulfs and bigger_body


def is_morning_star(candles: List[Dict]) -> bool:
    """
    Morning Star (Estrella de la Mañana): Patrón de 3 velas alcista.
    
    1. Vela bajista grande
    2. Vela pequeña (doji o spinning top) con gap
    3. Vela alcista grande que cierra en la mitad superior de la primera
    
    Señal ALCISTA muy fuerte.
    """
    if len(candles) < 3:
        return False
    
    first = analyze_candle(candles[-3])
    second = analyze_candle(candles[-2])
    third = analyze_candle(candles[-1])
    
    # Primera: bajista con cuerpo grande
    first_is_bearish = not first["is_bullish"] and first["body_ratio"] > 0.5
    
    # Segunda: cuerpo pequeño (indecisión)
    second_is_small = second["body_ratio"] < 0.3
    
    # Tercera: alcista con cuerpo grande, cierra por encima del 50% de la primera
    third_is_bullish = third["is_bullish"] and third["body_ratio"] > 0.5
    first_midpoint = (first["open"] + first["close"]) / 2
    closes_above_mid = third["close"] > first_midpoint
    
    return first_is_bearish and second_is_small and third_is_bullish and closes_above_mid


def is_evening_star(candles: List[Dict]) -> bool:
    """
    Evening Star (Estrella del Atardecer): Patrón de 3 velas bajista.
    
    Opuesto al Morning Star. Señal BAJISTA muy fuerte.
    """
    if len(candles) < 3:
        return False
    
    first = analyze_candle(candles[-3])
    second = analyze_candle(candles[-2])
    third = analyze_candle(candles[-1])
    
    first_is_bullish = first["is_bullish"] and first["body_ratio"] > 0.5
    second_is_small = second["body_ratio"] < 0.3
    third_is_bearish = not third["is_bullish"] and third["body_ratio"] > 0.5
    first_midpoint = (first["open"] + first["close"]) / 2
    closes_below_mid = third["close"] < first_midpoint
    
    return first_is_bullish and second_is_small and third_is_bearish and closes_below_mid


def is_three_white_soldiers(candles: List[Dict]) -> bool:
    """
    Three White Soldiers: 3 velas alcistas consecutivas grandes.
    
    Cada vela abre dentro del cuerpo anterior y cierra por encima.
    Señal ALCISTA muy fuerte de continuación.
    """
    if len(candles) < 3:
        return False
    
    first = analyze_candle(candles[-3])
    second = analyze_candle(candles[-2])
    third = analyze_candle(candles[-1])
    
    # Todas alcistas con cuerpos significativos
    all_bullish = first["is_bullish"] and second["is_bullish"] and third["is_bullish"]
    all_big = first["body_ratio"] > 0.5 and second["body_ratio"] > 0.5 and third["body_ratio"] > 0.5
    
    # Cada una cierra más alto
    ascending = first["close"] < second["close"] < third["close"]
    
    # Sombras superiores pequeñas (fuerza compradora)
    small_wicks = first["upper_ratio"] < 0.2 and second["upper_ratio"] < 0.2 and third["upper_ratio"] < 0.2
    
    return all_bullish and all_big and ascending and small_wicks


def is_three_black_crows(candles: List[Dict]) -> bool:
    """
    Three Black Crows: 3 velas bajistas consecutivas grandes.
    
    Señal BAJISTA muy fuerte.
    """
    if len(candles) < 3:
        return False
    
    first = analyze_candle(candles[-3])
    second = analyze_candle(candles[-2])
    third = analyze_candle(candles[-1])
    
    all_bearish = not first["is_bullish"] and not second["is_bullish"] and not third["is_bullish"]
    all_big = first["body_ratio"] > 0.5 and second["body_ratio"] > 0.5 and third["body_ratio"] > 0.5
    descending = first["close"] > second["close"] > third["close"]
    small_wicks = first["lower_ratio"] < 0.2 and second["lower_ratio"] < 0.2 and third["lower_ratio"] < 0.2
    
    return all_bearish and all_big and descending and small_wicks


def is_marubozu(candle: Dict) -> Dict:
    """
    Marubozu: Vela sin sombras (o muy pequeñas). Indica dominio total.
    
    - Bullish Marubozu: Compradores dominan completamente
    - Bearish Marubozu: Vendedores dominan completamente
    """
    c = analyze_candle(candle)
    
    almost_no_wicks = c["upper_ratio"] < 0.05 and c["lower_ratio"] < 0.05
    big_body = c["body_ratio"] > 0.9
    
    if almost_no_wicks and big_body:
        return {
            "is_marubozu": True,
            "direction": "BULLISH" if c["is_bullish"] else "BEARISH"
        }
    
    return {"is_marubozu": False, "direction": None}


def detect_all_patterns(candles: List[Dict]) -> Dict:
    """
    Detectar todos los patrones de velas en las últimas velas.
    
    Returns:
        Dict con patrones detectados, su dirección y score
    """
    if len(candles) < 3:
        return {"patterns": [], "bullish_score": 0, "bearish_score": 0}
    
    patterns = []
    bullish_score = 0
    bearish_score = 0
    
    last_candle = candles[-1]
    
    # === Patrones de 1 vela ===
    if is_doji(last_candle):
        patterns.append({
            "name": "Doji",
            "direction": "NEUTRAL",
            "strength": 1,
            "description": "Indecisión en el mercado"
        })
    
    if is_hammer(last_candle):
        patterns.append({
            "name": "Hammer",
            "direction": "BULLISH",
            "strength": 2,
            "description": "Posible reversión alcista"
        })
        bullish_score += 2
    
    if is_inverted_hammer(last_candle):
        patterns.append({
            "name": "Inverted Hammer",
            "direction": "BULLISH",
            "strength": 1.5,
            "description": "Posible reversión alcista (requiere confirmación)"
        })
        bullish_score += 1.5
    
    if is_shooting_star(last_candle):
        patterns.append({
            "name": "Shooting Star",
            "direction": "BEARISH",
            "strength": 2,
            "description": "Posible reversión bajista"
        })
        bearish_score += 2
    
    if is_hanging_man(last_candle):
        patterns.append({
            "name": "Hanging Man",
            "direction": "BEARISH",
            "strength": 1.5,
            "description": "Advertencia bajista"
        })
        bearish_score += 1.5
    
    marubozu = is_marubozu(last_candle)
    if marubozu["is_marubozu"]:
        patterns.append({
            "name": f"{marubozu['direction']} Marubozu",
            "direction": marubozu['direction'],
            "strength": 2.5,
            "description": "Dominio total del lado comprador/vendedor"
        })
        if marubozu['direction'] == "BULLISH":
            bullish_score += 2.5
        else:
            bearish_score += 2.5
    
    # === Patrones de 2 velas ===
    if is_bullish_engulfing(candles):
        patterns.append({
            "name": "Bullish Engulfing",
            "direction": "BULLISH",
            "strength": 3,
            "description": "Fuerte señal de reversión alcista"
        })
        bullish_score += 3
    
    if is_bearish_engulfing(candles):
        patterns.append({
            "name": "Bearish Engulfing",
            "direction": "BEARISH",
            "strength": 3,
            "description": "Fuerte señal de reversión bajista"
        })
        bearish_score += 3
    
    # === Patrones de 3 velas ===
    if is_morning_star(candles):
        patterns.append({
            "name": "Morning Star",
            "direction": "BULLISH",
            "strength": 4,
            "description": "Señal de reversión alcista muy fuerte"
        })
        bullish_score += 4
    
    if is_evening_star(candles):
        patterns.append({
            "name": "Evening Star",
            "direction": "BEARISH",
            "strength": 4,
            "description": "Señal de reversión bajista muy fuerte"
        })
        bearish_score += 4
    
    if is_three_white_soldiers(candles):
        patterns.append({
            "name": "Three White Soldiers",
            "direction": "BULLISH",
            "strength": 4,
            "description": "Fuerte continuación alcista"
        })
        bullish_score += 4
    
    if is_three_black_crows(candles):
        patterns.append({
            "name": "Three Black Crows",
            "direction": "BEARISH",
            "strength": 4,
            "description": "Fuerte continuación bajista"
        })
        bearish_score += 4
    
    # Determinar dirección predominante
    if bullish_score > bearish_score and bullish_score >= 2:
        overall = "BULLISH"
    elif bearish_score > bullish_score and bearish_score >= 2:
        overall = "BEARISH"
    else:
        overall = "NEUTRAL"
    
    return {
        "patterns": patterns,
        "bullish_score": bullish_score,
        "bearish_score": bearish_score,
        "overall_direction": overall,
        "pattern_count": len(patterns)
    }
