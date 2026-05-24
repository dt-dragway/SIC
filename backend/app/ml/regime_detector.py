"""
SIC Ultra - Regime Detector (RLMF Module)

Sensor de Cambio de Régimen que identifica si el mercado está en:
- TRENDING: ADX > 25 + Hurst > 0.55 → Usar señales de momentum
- MEAN_REVERTING: ADX < 20 + Hurst < 0.45 → Usar señales de reversión
- TRANSITIONING: Entre ambos → Aumentar threshold de confianza

Este módulo ajusta dinámicamente los parámetros de señal del agente IA.
"""

import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from app.ml.indicators import calculate_adx, calculate_atr, calculate_bollinger_bands


class MarketRegime(str, Enum):
    TRENDING = "TRENDING"
    MEAN_REVERTING = "MEAN_REVERTING"
    TRANSITIONING = "TRANSITIONING"


@dataclass
class RegimeReport:
    """Reporte de régimen de mercado actual."""
    regime: MarketRegime
    adx_value: float
    hurst_exponent: float
    volatility_compression: bool  # Bollinger Squeeze detectado
    confidence: float  # 0-100
    params: Dict[str, float]  # Parámetros ajustados (TP/SL multipliers)
    reasoning: List[str]


class RegimeDetector:
    """
    Sensor de cambio de régimen de mercado.
    
    Combina:
    1. ADX (Average Directional Index) para fuerza de tendencia
    2. Hurst Exponent simplificado para persistencia/reversión
    3. Bollinger Width para detección de compresión de volatilidad
    """
    
    # Parámetros por régimen
    REGIME_PARAMS = {
        MarketRegime.TRENDING: {
            "tp_atr_multiplier": 3.0,     # TP más lejano en tendencias
            "sl_atr_multiplier": 1.5,     # SL estándar
            "min_confidence": 60,          # Threshold bajo (momentum fuerte)
            "signal_filter": "momentum",   # Solo señales de momentum
            "max_position_pct": 0.02,      # 2% max
        },
        MarketRegime.MEAN_REVERTING: {
            "tp_atr_multiplier": 1.5,     # TP corto (capturar reversión rápida)
            "sl_atr_multiplier": 1.0,     # SL ajustado
            "min_confidence": 70,          # Más exigente
            "signal_filter": "reversal",   # Solo señales de reversión
            "max_position_pct": 0.015,     # 1.5% max (más conservador)
        },
        MarketRegime.TRANSITIONING: {
            "tp_atr_multiplier": 2.0,     # TP medio
            "sl_atr_multiplier": 1.2,     # SL medio
            "min_confidence": 80,          # Muy exigente (alta incertidumbre)
            "signal_filter": "all",        # Todo pasa, pero con threshold alto
            "max_position_pct": 0.01,      # 1% max (ultra conservador)
        }
    }
    
    def __init__(self):
        self._previous_regime: Optional[MarketRegime] = None
        self._regime_history: List[Dict] = []
        logger.info("📊 Regime Detector inicializado")
    
    def detect(
        self,
        candles: List[Dict],
        indicators: Optional[Dict] = None
    ) -> RegimeReport:
        """
        Detectar el régimen de mercado actual.
        
        Args:
            candles: Lista de velas OHLCV
            indicators: Indicadores pre-calculados (opcional)
        
        Returns:
            RegimeReport con régimen detectado y parámetros ajustados
        """
        if len(candles) < 50:
            return self._default_report("Datos insuficientes (< 50 velas)")
        
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        
        reasoning = []
        
        # === 1. ADX Analysis ===
        adx_data = calculate_adx(highs, lows, closes, period=14)
        adx_value = adx_data["adx"][-1] if adx_data["adx"] else 20.0
        plus_di = adx_data["plus_di"][-1] if adx_data["plus_di"] else 0
        minus_di = adx_data["minus_di"][-1] if adx_data["minus_di"] else 0
        
        if adx_value > 25:
            adx_signal = MarketRegime.TRENDING
            di_direction = "BULLISH" if plus_di > minus_di else "BEARISH"
            reasoning.append(f"ADX={adx_value:.1f} (>25) → Tendencia {di_direction} fuerte")
        elif adx_value < 20:
            adx_signal = MarketRegime.MEAN_REVERTING
            reasoning.append(f"ADX={adx_value:.1f} (<20) → Mercado lateral/mean-reverting")
        else:
            adx_signal = MarketRegime.TRANSITIONING
            reasoning.append(f"ADX={adx_value:.1f} (20-25) → Zona de transición")
        
        # === 2. Hurst Exponent (simplified R/S method) ===
        hurst = self._calculate_hurst(closes)
        
        if hurst > 0.55:
            hurst_signal = MarketRegime.TRENDING
            reasoning.append(f"Hurst={hurst:.3f} (>0.55) → Serie persistente (trending)")
        elif hurst < 0.45:
            hurst_signal = MarketRegime.MEAN_REVERTING
            reasoning.append(f"Hurst={hurst:.3f} (<0.45) → Serie anti-persistente (mean-reverting)")
        else:
            hurst_signal = MarketRegime.TRANSITIONING
            reasoning.append(f"Hurst={hurst:.3f} (0.45-0.55) → Random walk / indeciso")
        
        # === 3. Volatility Compression (Bollinger Squeeze) ===
        bb = calculate_bollinger_bands(closes, 20, 2.0)
        volatility_compression = False
        
        if bb["upper"] and bb["lower"] and bb["middle"]:
            bb_width = (bb["upper"][-1] - bb["lower"][-1]) / bb["middle"][-1]
            # Comparar con width promedio de las últimas 20 lecturas
            if len(bb["upper"]) >= 20 and len(bb["lower"]) >= 20:
                recent_widths = [
                    (bb["upper"][-(i+1)] - bb["lower"][-(i+1)]) / bb["middle"][-(i+1)]
                    for i in range(min(20, len(bb["upper"])))
                ]
                avg_width = sum(recent_widths) / len(recent_widths)
                
                if bb_width < avg_width * 0.6:
                    volatility_compression = True
                    reasoning.append(
                        f"⚠️ Bollinger Squeeze detectado (width={bb_width:.4f} vs avg={avg_width:.4f}) "
                        f"→ Breakout inminente"
                    )
        
        # === 4. Determinar régimen final (voting ponderado) ===
        regime = self._resolve_regime(adx_signal, hurst_signal, volatility_compression)
        
        # Confianza basada en acuerdo entre señales
        if adx_signal == hurst_signal:
            confidence = 85.0
            reasoning.append("✅ ADX y Hurst coinciden → Alta confianza en régimen")
        else:
            confidence = 55.0
            reasoning.append("⚠️ ADX y Hurst no coinciden → Confianza reducida")
        
        if volatility_compression:
            confidence = min(confidence, 60.0)
            reasoning.append("Compresión de volatilidad reduce confianza del régimen actual")
        
        # === 5. Detectar cambio de régimen ===
        if self._previous_regime and self._previous_regime != regime:
            reasoning.append(
                f"🔄 CAMBIO DE RÉGIMEN: {self._previous_regime.value} → {regime.value}"
            )
            logger.warning(f"🔄 Regime change: {self._previous_regime.value} → {regime.value}")
        
        self._previous_regime = regime
        
        # Guardar historial
        self._regime_history.append({
            "regime": regime.value,
            "adx": adx_value,
            "hurst": hurst,
            "compression": volatility_compression,
            "confidence": confidence
        })
        if len(self._regime_history) > 500:
            self._regime_history = self._regime_history[-500:]
        
        params = self.REGIME_PARAMS[regime].copy()
        
        report = RegimeReport(
            regime=regime,
            adx_value=round(adx_value, 2),
            hurst_exponent=round(hurst, 4),
            volatility_compression=volatility_compression,
            confidence=round(confidence, 1),
            params=params,
            reasoning=reasoning
        )
        
        logger.info(
            f"📊 Régimen: {regime.value} | ADX={adx_value:.1f} | "
            f"Hurst={hurst:.3f} | Conf={confidence:.0f}%"
        )
        
        return report
    
    def _calculate_hurst(self, prices: List[float], max_lag: int = 20) -> float:
        """
        Hurst Exponent simplificado via R/S (Rescaled Range) analysis.
        
        H > 0.5: Persistent (trending)
        H = 0.5: Random walk
        H < 0.5: Anti-persistent (mean-reverting)
        """
        if len(prices) < max_lag * 2:
            return 0.5  # Fallback: random walk
        
        try:
            ts = np.array(prices)
            lags = range(2, max_lag + 1)
            rs_values = []
            
            for lag in lags:
                # Dividir serie en sub-series
                n_subseries = len(ts) // lag
                rs_list = []
                
                for i in range(n_subseries):
                    subseries = ts[i * lag:(i + 1) * lag]
                    mean_val = np.mean(subseries)
                    deviations = subseries - mean_val
                    cumulative = np.cumsum(deviations)
                    
                    r = np.max(cumulative) - np.min(cumulative)
                    s = np.std(subseries, ddof=1) if np.std(subseries, ddof=1) > 0 else 1e-10
                    
                    rs_list.append(r / s)
                
                rs_values.append(np.mean(rs_list))
            
            # Regresión log-log para obtener H
            log_lags = np.log(list(lags))
            log_rs = np.log(rs_values)
            
            # Regresión lineal simple
            n = len(log_lags)
            sum_x = np.sum(log_lags)
            sum_y = np.sum(log_rs)
            sum_xy = np.sum(log_lags * log_rs)
            sum_x2 = np.sum(log_lags ** 2)
            
            hurst = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            
            # Clamp entre 0 y 1
            return max(0.0, min(1.0, hurst))
            
        except Exception as e:
            logger.error(f"Error calculando Hurst Exponent: {e}")
            return 0.5
    
    def _resolve_regime(
        self,
        adx_signal: MarketRegime,
        hurst_signal: MarketRegime,
        compression: bool
    ) -> MarketRegime:
        """Resolver régimen final con voting ponderado."""
        if compression:
            # Si hay compresión, siempre transitioning (breakout inminente)
            return MarketRegime.TRANSITIONING
        
        if adx_signal == hurst_signal:
            return adx_signal
        
        # ADX tiene más peso (60%) porque es más reactivo
        # Si uno dice TRANSITIONING y otro algo definido, usar el definido
        if adx_signal == MarketRegime.TRANSITIONING:
            return hurst_signal
        if hurst_signal == MarketRegime.TRANSITIONING:
            return adx_signal
        
        # Conflicto real (uno trending, otro mean-reverting) → transitioning
        return MarketRegime.TRANSITIONING
    
    def _default_report(self, reason: str) -> RegimeReport:
        """Reporte por defecto cuando no hay datos suficientes."""
        return RegimeReport(
            regime=MarketRegime.TRANSITIONING,
            adx_value=0.0,
            hurst_exponent=0.5,
            volatility_compression=False,
            confidence=0.0,
            params=self.REGIME_PARAMS[MarketRegime.TRANSITIONING].copy(),
            reasoning=[reason]
        )
    
    def get_regime_stability(self, lookback: int = 20) -> float:
        """
        Calcula qué tan estable ha sido el régimen recientemente.
        1.0 = mismo régimen en todos los lookback periodos
        0.0 = cambio constante
        """
        if len(self._regime_history) < 2:
            return 0.5
        
        recent = self._regime_history[-lookback:]
        if not recent:
            return 0.5
        
        current = recent[-1]["regime"]
        same_count = sum(1 for r in recent if r["regime"] == current)
        return same_count / len(recent)


# === Singleton ===
_regime_detector: Optional[RegimeDetector] = None


def get_regime_detector() -> RegimeDetector:
    global _regime_detector
    if _regime_detector is None:
        _regime_detector = RegimeDetector()
    return _regime_detector
