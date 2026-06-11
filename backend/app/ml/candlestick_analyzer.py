"""
Analizador de Patrones de Velas (Candlestick Patterns)

Este módulo identifica patrones de velas profesionales en tiempo real
para generar señales de trading de alta precisión.

Patrones implementados:
- Hammer (Martillo)
- Shooting Star (Estrella Fugaz)
- Bullish/Bearish Engulfing (Envolvente Alcista/Bajista)
- Doji (Indecisión)
- Three White Soldiers / Three Black Crows
- Morning Star / Evening Star
- Y más...
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics
from loguru import logger


class PatternStrength(Enum):
    """Fuerza del patrón detectado"""
    WEAK = "DÉBIL"
    MODERATE = "MODERADA"
    STRONG = "FUERTE"
    VERY_STRONG = "MUY FUERTE"


@dataclass
class CandlestickPattern:
    """Patrón de vela identificado"""
    name: str  # Nombre técnico
    name_es: str  # Nombre en español
    direction: str  # "BULLISH" o "BEARISH"
    strength: float  # 0.0 - 1.0
    strength_label: PatternStrength
    timeframe: str  # "1m", "5m", "15m", "1h", "4h", "1d"
    description_es: str  # Explicación en español
    confidence: float  # Confianza del patrón (0-100)
    candle_index: int  # Índice de la vela donde se detectó
    
    # Datos para UI
    icon: str  # Emoji o símbolo
    color: str  # Color recomendado para UI


class CandlestickAnalyzer:
    """
    Analizador profesional de patrones de velas.
    
    Detecta patrones clásicos y avanzados en datos de velas,
    proporcionando señales claras para usuarios novatos.
    """
    
    def __init__(self, min_confidence: float = 60.0):
        """
        Args:
            min_confidence: Confianza mínima para reportar un patrón (default: 60%)
        """
        self.min_confidence = min_confidence
        logger.info(f"🕯️ Candlestick Analyzer inicializado (confianza mínima: {min_confidence}%)")
    
    def analyze(
        self, 
        candles: List[Dict], 
        timeframe: str = "1h"
    ) -> List[CandlestickPattern]:
        """
        Analizar velas y detectar patrones.
        
        Args:
            candles: Lista de velas con formato: 
                     [{"open": float, "high": float, "low": float, "close": float, "volume": float}]
            timeframe: Marco temporal ("1m", "5m", "15m", "1h", "4h", "1d")
        
        Returns:
            Lista de patrones detectados, ordenados por confianza (mayor a menor)
        """
        if len(candles) < 3:
            return []
        
        patterns = []
        
        # Analizar solo las últimas velas (más recientes)
        window_size = min(50, len(candles))
        recent_candles = candles[-window_size:]
        
        # Detectar patrones de 1 vela
        patterns.extend(self._detect_single_candle_patterns(recent_candles, timeframe))
        
        # Detectar patrones de 2 velas
        patterns.extend(self._detect_two_candle_patterns(recent_candles, timeframe))
        
        # Detectar patrones de 3 velas
        patterns.extend(self._detect_three_candle_patterns(recent_candles, timeframe))
        
        # Filtrar por confianza mínima
        patterns = [p for p in patterns if p.confidence >= self.min_confidence]
        
        # Ordenar por confianza (mayor primero)
        patterns.sort(key=lambda x: x.confidence, reverse=True)
        
        return patterns
    
    def _detect_single_candle_patterns(
        self, 
        candles: List[Dict], 
        timeframe: str
    ) -> List[CandlestickPattern]:
        """Detectar patrones de una sola vela"""
        patterns = []
        
        for i in range(len(candles)):
            candle = candles[i]
            
            # Doji - Indecisión del mercado
            if self._is_doji(candle):
                patterns.append(CandlestickPattern(
                    name="Doji",
                    name_es="Doji (Indecisión)",
                    direction="NEUTRAL",
                    strength=self._calculate_doji_strength(candle),
                    strength_label=self._get_strength_label(self._calculate_doji_strength(candle)),
                    timeframe=timeframe,
                    description_es="Indecisión en el mercado - precio de apertura y cierre muy similares. Posible cambio de tendencia.",
                    confidence=65.0,
                    candle_index=i,
                    icon="⚖️",
                    color="yellow"
                ))
            
            # Hammer - Patrón alcista
            if i > 0 and self._is_hammer(candle, candles[i-1]):
                strength = self._calculate_hammer_strength(candle, candles[:i])
                patterns.append(CandlestickPattern(
                    name="Hammer",
                    name_es="Martillo Alcista",
                    direction="BULLISH",
                    strength=strength,
                    strength_label=self._get_strength_label(strength),
                    timeframe=timeframe,
                    description_es="Martillo alcista detectado - reversión al alza probable. El precio fue rechazado a la baja y cerró cerca del máximo.",
                    confidence=70.0 + (strength * 15),  # 70-85%
                    candle_index=i,
                    icon="🔨",
                    color="green"
                ))
            
            # Shooting Star - Patrón bajista
            if i > 0 and self._is_shooting_star(candle, candles[i-1]):
                strength = self._calculate_shooting_star_strength(candle, candles[:i])
                patterns.append(CandlestickPattern(
                    name="Shooting Star",
                    name_es="Estrella Fugaz Bajista",
                    direction="BEARISH",
                    strength=strength,
                    strength_label=self._get_strength_label(strength),
                    timeframe=timeframe,
                    description_es="Estrella fugaz detectada - reversión a la baja probable. El precio fue rechazado al alza y cerró cerca del mínimo.",
                    confidence=70.0 + (strength * 15),  # 70-85%
                    candle_index=i,
                    icon="⭐",
                    color="red"
                ))
        
        return patterns
    
    def _detect_two_candle_patterns(
        self, 
        candles: List[Dict], 
        timeframe: str
    ) -> List[CandlestickPattern]:
        """Detectar patrones de dos velas"""
        patterns = []
        
        for i in range(1, len(candles)):
            prev_candle = candles[i-1]
            curr_candle = candles[i]
            
            # Bullish Engulfing - Envolvente alcista
            if self._is_bullish_engulfing(prev_candle, curr_candle):
                strength = self._calculate_engulfing_strength(prev_candle, curr_candle, candles[:i])
                patterns.append(CandlestickPattern(
                    name="Bullish Engulfing",
                    name_es="Envolvente Alcista",
                    direction="BULLISH",
                    strength=strength,
                    strength_label=self._get_strength_label(strength),
                    timeframe=timeframe,
                    description_es="Patrón envolvente alcista - la vela verde actual envuelve completamente la vela roja anterior. Fuerte señal de compra.",
                    confidence=75.0 + (strength * 20),  # 75-95%
                    candle_index=i,
                    icon="📈",
                    color="green"
                ))
            
            # Bearish Engulfing - Envolvente bajista
            if self._is_bearish_engulfing(prev_candle, curr_candle):
                strength = self._calculate_engulfing_strength(prev_candle, curr_candle, candles[:i])
                patterns.append(CandlestickPattern(
                    name="Bearish Engulfing",
                    name_es="Envolvente Bajista",
                    direction="BEARISH",
                    strength=strength,
                    strength_label=self._get_strength_label(strength),
                    timeframe=timeframe,
                    description_es="Patrón envolvente bajista - la vela roja actual envuelve completamente la vela verde anterior. Fuerte señal de venta.",
                    confidence=75.0 + (strength * 20),  # 75-95%
                    candle_index=i,
                    icon="📉",
                    color="red"
                ))
        
        return patterns
    
    def _detect_three_candle_patterns(
        self, 
        candles: List[Dict], 
        timeframe: str
    ) -> List[CandlestickPattern]:
        """Detectar patrones de tres velas"""
        patterns = []
        
        for i in range(2, len(candles)):
            c1 = candles[i-2]
            c2 = candles[i-1]
            c3 = candles[i]
            
            # Morning Star - Estrella de la mañana (alcista)
            if self._is_morning_star(c1, c2, c3):
                strength = self._calculate_star_strength(c1, c2, c3, candles[:i-2])
                patterns.append(CandlestickPattern(
                    name="Morning Star",
                    name_es="Estrella de la Mañana",
                    direction="BULLISH",
                    strength=strength,
                    strength_label=self._get_strength_label(strength),
                    timeframe=timeframe,
                    description_es="Patrón estrella de la mañana - reversión alcista confirmada después de tendencia bajista. Muy fuerte señal de compra.",
                    confidence=80.0 + (strength * 15),  # 80-95%
                    candle_index=i,
                    icon="🌅",
                    color="green"
                ))
            
            # Evening Star - Estrella de la tarde (bajista)
            if self._is_evening_star(c1, c2, c3):
                strength = self._calculate_star_strength(c1, c2, c3, candles[:i-2])
                patterns.append(CandlestickPattern(
                    name="Evening Star",
                    name_es="Estrella de la Tarde",
                    direction="BEARISH",
                    strength=strength,
                    strength_label=self._get_strength_label(strength),
                    timeframe=timeframe,
                    description_es="Patrón estrella de la tarde - reversión bajista confirmada después de tendencia alcista. Muy fuerte señal de venta.",
                    confidence=80.0 + (strength * 15),  # 80-95%
                    candle_index=i,
                    icon="🌆",
                    color="red"
                ))
            
            # Three White Soldiers - Tres soldados blancos (alcista)
            if self._is_three_white_soldiers(c1, c2, c3):
                patterns.append(CandlestickPattern(
                    name="Three White Soldiers",
                    name_es="Tres Soldados Blancos",
                    direction="BULLISH",
                    strength=0.85,
                    strength_label=PatternStrength.VERY_STRONG,
                    timeframe=timeframe,
                    description_es="Tres soldados blancos - tres velas verdes consecutivas ascendentes. Tendencia alcista muy fuerte confirmada.",
                    confidence=85.0,
                    candle_index=i,
                    icon="⬆️⬆️⬆️",
                    color="green"
                ))
            
            # Three Black Crows - Tres cuervos negros (bajista)
            if self._is_three_black_crows(c1, c2, c3):
                patterns.append(CandlestickPattern(
                    name="Three Black Crows",
                    name_es="Tres Cuervos Negros",
                    direction="BEARISH",
                    strength=0.85,
                    strength_label=PatternStrength.VERY_STRONG,
                    timeframe=timeframe,
                    description_es="Tres cuervos negros - tres velas rojas consecutivas descendentes. Tendencia bajista muy fuerte confirmada.",
                    confidence=85.0,
                    candle_index=i,
                    icon="⬇️⬇️⬇️",
                    color="red"
                ))
        
        return patterns
    
    # ==================== Pattern Detection Methods ====================
    
    def _is_doji(self, candle: Dict) -> bool:
        """Detectar Doji - apertura y cierre casi iguales"""
        body = abs(candle["close"] - candle["open"])
        full_range = candle["high"] - candle["low"]
        
        if full_range == 0:
            return False
        
        # Doji: cuerpo muy pequeño (< 5% del rango total)
        return (body / full_range) < 0.05
    
    def _is_hammer(self, candle: Dict, prev_candle: Dict) -> bool:
        """Detectar Hammer - cuerpo pequeño arriba, sombra larga abajo"""
        body = abs(candle["close"] - candle["open"])
        lower_shadow = min(candle["open"], candle["close"]) - candle["low"]
        upper_shadow = candle["high"] - max(candle["open"], candle["close"])
        
        # Hammer: sombra inferior >= 2x cuerpo, sombra superior pequeña
        return (
            lower_shadow >= 2 * body and
            upper_shadow < body * 0.3 and
            candle["close"] > candle["open"]  # Vela verde preferible
        )
    
    def _is_shooting_star(self, candle: Dict, prev_candle: Dict) -> bool:
        """Detectar Shooting Star - cuerpo pequeño abajo, sombra larga arriba"""
        body = abs(candle["close"] - candle["open"])
        lower_shadow = min(candle["open"], candle["close"]) - candle["low"]
        upper_shadow = candle["high"] - max(candle["open"], candle["close"])
        
        # Shooting Star: sombra superior >= 2x cuerpo, sombra inferior pequeña
        return (
            upper_shadow >= 2 * body and
            lower_shadow < body * 0.3 and
            candle["close"] < candle["open"]  # Vela roja preferible
        )
    
    def _is_bullish_engulfing(self, prev: Dict, curr: Dict) -> bool:
        """Detectar Bullish Engulfing - vela verde envuelve vela roja anterior"""
        prev_bearish = prev["close"] < prev["open"]
        curr_bullish = curr["close"] > curr["open"]
        
        # Vela actual debe envolver completamente la anterior
        return (
            prev_bearish and
            curr_bullish and
            curr["open"] < prev["close"] and
            curr["close"] > prev["open"]
        )
    
    def _is_bearish_engulfing(self, prev: Dict, curr: Dict) -> bool:
        """Detectar Bearish Engulfing - vela roja envuelve vela verde anterior"""
        prev_bullish = prev["close"] > prev["open"]
        curr_bearish = curr["close"] < curr["open"]
        
        # Vela actual debe envolver completamente la anterior
        return (
            prev_bullish and
            curr_bearish and
            curr["open"] > prev["close"] and
            curr["close"] < prev["open"]
        )
    
    def _is_morning_star(self, c1: Dict, c2: Dict, c3: Dict) -> bool:
        """Detectar Morning Star - reversión alcista de 3 velas"""
        c1_bearish = c1["close"] < c1["open"]
        c2_small = abs(c2["close"] - c2["open"]) < abs(c1["close"] - c1["open"]) * 0.3
        c3_bullish = c3["close"] > c3["open"]
        
        return (
            c1_bearish and
            c2_small and
            c3_bullish and
            c3["close"] > (c1["open"] + c1["close"]) / 2  # Vela 3 cierra en mitad superior de vela 1
        )
    
    def _is_evening_star(self, c1: Dict, c2: Dict, c3: Dict) -> bool:
        """Detectar Evening Star - reversión bajista de 3 velas"""
        c1_bullish = c1["close"] > c1["open"]
        c2_small = abs(c2["close"] - c2["open"]) < abs(c1["close"] - c1["open"]) * 0.3
        c3_bearish = c3["close"] < c3["open"]
        
        return (
            c1_bullish and
            c2_small and
            c3_bearish and
            c3["close"] < (c1["open"] + c1["close"]) / 2  # Vela 3 cierra en mitad inferior de vela 1
        )
    
    def _is_three_white_soldiers(self, c1: Dict, c2: Dict, c3: Dict) -> bool:
        """Detectar Three White Soldiers - tres velas alcistas consecutivas"""
        all_bullish = (
            c1["close"] > c1["open"] and
            c2["close"] > c2["open"] and
            c3["close"] > c3["open"]
        )
        
        ascending = c2["close"] > c1["close"] and c3["close"] > c2["close"]
        
        return all_bullish and ascending
    
    def _is_three_black_crows(self, c1: Dict, c2: Dict, c3: Dict) -> bool:
        """Detectar Three Black Crows - tres velas bajistas consecutivas"""
        all_bearish = (
            c1["close"] < c1["open"] and
            c2["close"] < c2["open"] and
            c3["close"] < c3["open"]
        )
        
        descending = c2["close"] < c1["close"] and c3["close"] < c2["close"]
        
        return all_bearish and descending
    
    # ==================== Strength Calculation Methods ====================
    
    def _calculate_doji_strength(self, candle: Dict) -> float:
        """Calcular fuerza del Doji"""
        body = abs(candle["close"] - candle["open"])
        full_range = candle["high"] - candle["low"]
        
        if full_range == 0:
            return 0.0
        
        # Más pequeño el cuerpo = más fuerte el Doji
        body_ratio = body / full_range
        return max(0.0, 1.0 - (body_ratio * 20))
    
    def _calculate_hammer_strength(self, candle: Dict, context: List[Dict]) -> float:
        """Calcular fuerza del Hammer considerando contexto"""
        lower_shadow = min(candle["open"], candle["close"]) - candle["low"]
        body = abs(candle["close"] - candle["open"])
        
        # Ratio sombra/cuerpo (más alto = más fuerte)
        if body == 0:
            shadow_ratio = 1.0
        else:
            shadow_ratio = min(lower_shadow / body / 3, 1.0)  # Normalizar a 1.0
        
        # Verificar si está en tendencia bajista previa (más fuerte)
        trend_bonus = 0.2 if self._is_downtrend(context) else 0.0
        
        return min(shadow_ratio + trend_bonus, 1.0)
    
    def _calculate_shooting_star_strength(self, candle: Dict, context: List[Dict]) -> float:
        """Calcular fuerza del Shooting Star"""
        upper_shadow = candle["high"] - max(candle["open"], candle["close"])
        body = abs(candle["close"] - candle["open"])
        
        if body == 0:
            shadow_ratio = 1.0
        else:
            shadow_ratio = min(upper_shadow / body / 3, 1.0)
        
        # Verificar si está en tendencia alcista previa (más fuerte)
        trend_bonus = 0.2 if self._is_uptrend(context) else 0.0
        
        return min(shadow_ratio + trend_bonus, 1.0)
    
    def _calculate_engulfing_strength(
        self, 
        prev: Dict, 
        curr: Dict, 
        context: List[Dict]
    ) -> float:
        """Calcular fuerza del patrón Engulfing"""
        prev_body = abs(prev["close"] - prev["open"])
        curr_body = abs(curr["close"] - curr["open"])
        
        # Ratio de tamaño (vela actual vs anterior)
        size_ratio = min(curr_body / prev_body / 2, 1.0) if prev_body > 0 else 0.5
        
        # Volumen (si está disponible)
        volume_bonus = 0.0
        if "volume" in curr and "volume" in prev:
            if curr["volume"] > prev["volume"]:
                volume_bonus = 0.2
        
        return min(size_ratio + volume_bonus, 1.0)
    
    def _calculate_star_strength(
        self, 
        c1: Dict, 
        c2: Dict, 
        c3: Dict, 
        context: List[Dict]
    ) -> float:
        """Calcular fuerza de Morning/Evening Star"""
        c1_body = abs(c1["close"] - c1["open"])
        c2_body = abs(c2["close"] - c2["open"])
        c3_body = abs(c3["close"] - c3["open"])
        
        # Vela intermedia debe ser muy pequeña
        small_middle = 1.0 - min(c2_body / c1_body, 1.0) if c1_body > 0 else 0.5
        
        # Vela final debe ser fuerte
        strong_final = min(c3_body / c1_body, 1.0) if c1_body > 0 else 0.5
        
        return (small_middle + strong_final) / 2
    
    # ==================== Helper Methods ====================
    
    def _is_uptrend(self, candles: List[Dict]) -> bool:
        """Verificar si hay tendencia alcista"""
        if len(candles) < 5:
            return False
        
        recent = candles[-5:]
        closes = [c["close"] for c in recent]
        
        # Simple: comparar primeras con últimas
        return closes[-1] > closes[0]
    
    def _is_downtrend(self, candles: List[Dict]) -> bool:
        """Verificar si hay tendencia bajista"""
        if len(candles) < 5:
            return False
        
        recent = candles[-5:]
        closes = [c["close"] for c in recent]
        
        return closes[-1] < closes[0]
    
    def _get_strength_label(self, strength: float) -> PatternStrength:
        """Convertir fuerza numérica a etiqueta"""
        if strength >= 0.85:
            return PatternStrength.VERY_STRONG
        elif strength >= 0.70:
            return PatternStrength.STRONG
        elif strength >= 0.50:
            return PatternStrength.MODERATE
        else:
            return PatternStrength.WEAK
    
    def get_summary(self, patterns: List[CandlestickPattern]) -> Dict:
        """
        Obtener resumen de patrones detectados.
        
        Returns:
            Dict con resumen: total, por dirección, por fuerza, etc.
        """
        if not patterns:
            return {
                "total": 0,
                "bullish": 0,
                "bearish": 0,
                "neutral": 0,
                "strongest_pattern": None,
                "dominant_direction": "NEUTRAL"
            }
        
        bullish = [p for p in patterns if p.direction == "BULLISH"]
        bearish = [p for p in patterns if p.direction == "BEARISH"]
        neutral = [p for p in patterns if p.direction == "NEUTRAL"]
        
        # Determinar dirección dominante
        if len(bullish) > len(bearish):
            dominant = "BULLISH"
        elif len(bearish) > len(bullish):
            dominant = "BEARISH"
        else:
            dominant = "NEUTRAL"
        
        return {
            "total": len(patterns),
            "bullish": len(bullish),
            "bearish": len(bearish),
            "neutral": len(neutral),
            "strongest_pattern": patterns[0].name_es if patterns else None,
            "dominant_direction": dominant,
            "avg_confidence": sum(p.confidence for p in patterns) / len(patterns)
        }
