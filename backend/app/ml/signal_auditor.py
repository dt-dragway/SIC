"""
SIC Ultra - Signal Auditor (RLMF Module)

Validación Pre-Vuelo para señales de trading.
Cada señal pasa por un gate de calidad multi-capa antes de ser aprobada.

FILOSOFÍA: Es mejor perder una oportunidad que ejecutar una señal basura.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from loguru import logger

from app.ml.indicators import calculate_volume_profile, calculate_adx
from app.ml.regime_detector import get_regime_detector, MarketRegime
from app.ml.risk_engine import FeeCalculator


@dataclass
class SignalQualityReport:
    """Reporte de calidad de una señal."""
    score: float  # 0-100
    risk_factor: float  # 0-10 (10 = riesgo máximo)
    passed: bool  # Gate pass/fail
    regime: str  # Régimen de mercado actual
    checks: List[Dict]  # Detalle de cada check
    reasons_to_reject: List[str]
    reasons_to_accept: List[str]
    fee_viable: bool  # ¿Los targets cubren las comisiones?
    timestamp: datetime = field(default_factory=datetime.utcnow)


class SignalAuditor:
    """
    Auditor de calidad de señales.
    
    Capas de validación:
    1. Volume Validation — ¿El volumen es real o wash trading?
    2. Trend Strength — ¿ADX confirma la señal?
    3. Regime Alignment — ¿La señal es coherente con el régimen actual?
    4. Historical Pattern Check — ¿Este patrón falló recientemente?
    5. Fee Viability — ¿Los targets cubren comisiones?
    6. Macro Absorption — ¿El Order Flow ya absorbió la noticia?
    """
    
    # Threshold mínimo para aprobar señal
    MIN_SCORE = 60
    
    # Pesos de cada check
    WEIGHTS = {
        "volume_check": 20,
        "trend_strength": 20,
        "regime_alignment": 20,
        "historical_pattern": 20,
        "fee_viability": 10,
        "volume_confirmation": 10
    }
    
    def __init__(self):
        self.regime_detector = get_regime_detector()
        self.fee_calculator = FeeCalculator()
        self._audit_history: List[Dict] = []
        logger.info("🛡️ Signal Auditor inicializado")
    
    def preflight_check(
        self,
        signal: Dict,
        candles: List[Dict],
        indicators: Dict,
        trade_history: List[Dict] = None
    ) -> SignalQualityReport:
        """
        Validación pre-vuelo completa de una señal.
        
        Args:
            signal: Señal generada por TradingAgentAI (dict con direction, confidence, etc.)
            candles: Velas OHLCV recientes
            indicators: Indicadores pre-calculados
            trade_history: Historial de trades del AgentMemory
        
        Returns:
            SignalQualityReport con score y pass/fail
        """
        checks = []
        reject_reasons = []
        accept_reasons = []
        total_score = 0.0
        risk_factor = 5.0  # Base neutral
        
        direction = signal.get("direction", "HOLD")
        confidence = signal.get("confidence", 0)
        entry_price = signal.get("entry_price", 0)
        stop_loss = signal.get("stop_loss", 0)
        take_profit = signal.get("take_profit", 0)
        
        if len(candles) < 50:
            return SignalQualityReport(
                score=0, risk_factor=10, passed=False,
                regime="UNKNOWN", checks=[], 
                reasons_to_reject=["Datos insuficientes (< 50 velas)"],
                reasons_to_accept=[], fee_viable=False
            )
        
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        volumes = [c.get("volume", 0) for c in candles]
        
        # === CHECK 1: Volume Validation ===
        vol_score, vol_detail = self._check_volume(volumes, direction)
        checks.append({"name": "Volume Validation", "score": vol_score, "detail": vol_detail})
        total_score += vol_score * (self.WEIGHTS["volume_check"] / 100)
        
        if vol_score < 30:
            reject_reasons.append(f"Volumen sospechoso: {vol_detail}")
            risk_factor += 1.5
        elif vol_score > 70:
            accept_reasons.append(f"Volumen saludable: {vol_detail}")
            risk_factor -= 0.5
        
        # === CHECK 2: Trend Strength (ADX) ===
        adx_score, adx_detail = self._check_trend_strength(highs, lows, closes, direction)
        checks.append({"name": "Trend Strength", "score": adx_score, "detail": adx_detail})
        total_score += adx_score * (self.WEIGHTS["trend_strength"] / 100)
        
        if adx_score > 70:
            accept_reasons.append(f"Tendencia fuerte confirma señal: {adx_detail}")
        elif adx_score < 30:
            reject_reasons.append(f"Tendencia débil contradice señal: {adx_detail}")
            risk_factor += 1.0
        
        # === CHECK 3: Regime Alignment ===
        regime_report = self.regime_detector.detect(candles, indicators)
        regime_score, regime_detail = self._check_regime_alignment(
            direction, confidence, regime_report
        )
        checks.append({"name": "Regime Alignment", "score": regime_score, "detail": regime_detail})
        total_score += regime_score * (self.WEIGHTS["regime_alignment"] / 100)
        
        if regime_score < 40:
            reject_reasons.append(f"Señal no alineada con régimen: {regime_detail}")
            risk_factor += 1.5
        else:
            accept_reasons.append(f"Régimen compatible: {regime_detail}")
        
        # === CHECK 4: Historical Pattern Check ===
        hist_score, hist_detail = self._check_historical_patterns(
            direction, signal.get("patterns_detected", []),
            signal.get("indicators_used", []),
            trade_history or []
        )
        checks.append({"name": "Historical Pattern", "score": hist_score, "detail": hist_detail})
        total_score += hist_score * (self.WEIGHTS["historical_pattern"] / 100)
        
        if hist_score < 30:
            reject_reasons.append(f"Patrón repetido con fallos recientes: {hist_detail}")
            risk_factor += 2.0
        
        # === CHECK 5: Fee Viability ===
        fee_result = self.fee_calculator.adjust_targets(entry_price, stop_loss, take_profit)
        fee_score = 100 if fee_result.viable else 0
        checks.append({
            "name": "Fee Viability",
            "score": fee_score,
            "detail": fee_result.reasoning
        })
        total_score += fee_score * (self.WEIGHTS["fee_viability"] / 100)
        
        if not fee_result.viable:
            reject_reasons.append(f"Targets no cubren comisiones: {fee_result.reasoning}")
            risk_factor += 1.0
        
        # === CHECK 6: Volume Confirmation ===
        vol_confirm_score, vol_confirm_detail = self._check_volume_confirmation(
            volumes, closes, direction
        )
        checks.append({
            "name": "Volume Confirmation",
            "score": vol_confirm_score,
            "detail": vol_confirm_detail
        })
        total_score += vol_confirm_score * (self.WEIGHTS["volume_confirmation"] / 100)
        
        # === RESULTADO FINAL ===
        risk_factor = max(1.0, min(10.0, risk_factor))
        passed = total_score >= self.MIN_SCORE and len(reject_reasons) < 3
        
        # Override: si hay volatility compression, pasar con precaución
        if regime_report.volatility_compression and not passed:
            accept_reasons.append("⚠️ Volatility compression → breakout posible, permitido con precaución")
            # No override pass automáticamente, solo lo nota
        
        report = SignalQualityReport(
            score=round(total_score, 1),
            risk_factor=round(risk_factor, 1),
            passed=passed,
            regime=regime_report.regime.value,
            checks=checks,
            reasons_to_reject=reject_reasons,
            reasons_to_accept=accept_reasons,
            fee_viable=fee_result.viable
        )
        
        # Log
        status = "✅ APROBADA" if passed else "❌ RECHAZADA"
        logger.info(
            f"🛡️ Signal Audit {status}: Score={total_score:.1f}/100 | "
            f"Risk={risk_factor:.1f}/10 | Regime={regime_report.regime.value}"
        )
        
        # Guardar en historial
        self._audit_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "direction": direction,
            "score": total_score,
            "passed": passed,
            "regime": regime_report.regime.value
        })
        if len(self._audit_history) > 500:
            self._audit_history = self._audit_history[-500:]
        
        return report
    
    def _check_volume(self, volumes: List[float], direction: str) -> tuple:
        """Check 1: ¿El volumen es real o hay wash trading?"""
        if not volumes or len(volumes) < 20:
            return 50, "Datos de volumen insuficientes"
        
        vol_profile = calculate_volume_profile(volumes, lookback=20)
        
        score = 50  # Base
        details = []
        
        # Volumen actual vs promedio
        ratio = vol_profile.get("ratio", 1.0)
        
        if ratio < 0.3:
            # Volumen extremadamente bajo → posible mercado ilíquido
            score = 20
            details.append(f"Volumen {ratio:.1f}x del promedio (muy bajo, posible iliquidez)")
        elif ratio > 5.0:
            # Volumen extremo → posible wash trading o evento
            score = 35
            details.append(f"Volumen {ratio:.1f}x del promedio (extremo, posible manipulación)")
        elif 0.8 <= ratio <= 2.5:
            # Rango saludable
            score = 85
            details.append(f"Volumen {ratio:.1f}x del promedio (saludable)")
        else:
            score = 60
            details.append(f"Volumen {ratio:.1f}x del promedio (aceptable)")
        
        # Volume trend
        vol_trend = vol_profile.get("trend", "STABLE")
        if vol_trend == "INCREASING" and direction in ("LONG", "SHORT"):
            score = min(100, score + 10)
            details.append("Volumen creciente confirma señal")
        elif vol_trend == "DECREASING":
            score = max(0, score - 15)
            details.append("Volumen decreciente debilita señal")
        
        return score, " | ".join(details)
    
    def _check_trend_strength(
        self, highs: List[float], lows: List[float], 
        closes: List[float], direction: str
    ) -> tuple:
        """Check 2: ¿ADX confirma fuerza de tendencia?"""
        adx_data = calculate_adx(highs, lows, closes, period=14)
        
        if not adx_data["adx"]:
            return 50, "ADX no calculable"
        
        adx = adx_data["adx"][-1]
        plus_di = adx_data["plus_di"][-1] if adx_data["plus_di"] else 0
        minus_di = adx_data["minus_di"][-1] if adx_data["minus_di"] else 0
        
        score = 50
        details = []
        
        # Señal LONG requiere +DI > -DI con ADX fuerte
        if direction == "LONG":
            if adx > 25 and plus_di > minus_di:
                score = 90
                details.append(f"ADX={adx:.0f} (+DI > -DI) → Tendencia alcista fuerte")
            elif adx > 25 and plus_di < minus_di:
                score = 20
                details.append(f"ADX={adx:.0f} pero -DI domina → Contra-tendencia")
            elif adx < 20:
                score = 40
                details.append(f"ADX={adx:.0f} → Sin tendencia clara")
            else:
                score = 55
                details.append(f"ADX={adx:.0f} → Tendencia moderada")
        
        elif direction == "SHORT":
            if adx > 25 and minus_di > plus_di:
                score = 90
                details.append(f"ADX={adx:.0f} (-DI > +DI) → Tendencia bajista fuerte")
            elif adx > 25 and minus_di < plus_di:
                score = 20
                details.append(f"ADX={adx:.0f} pero +DI domina → Contra-tendencia")
            elif adx < 20:
                score = 40
                details.append(f"ADX={adx:.0f} → Sin tendencia clara")
            else:
                score = 55
                details.append(f"ADX={adx:.0f} → Tendencia moderada")
        
        return score, " | ".join(details)
    
    def _check_regime_alignment(
        self, direction: str, confidence: float, regime_report
    ) -> tuple:
        """Check 3: ¿La señal es coherente con el régimen actual?"""
        regime = regime_report.regime
        params = regime_report.params
        
        score = 50
        details = []
        
        signal_filter = params.get("signal_filter", "all")
        min_conf = params.get("min_confidence", 60)
        
        # Verificar que la confianza pasa el threshold del régimen
        if confidence < min_conf:
            score = 25
            details.append(
                f"Confianza {confidence:.0f}% < mínimo {min_conf}% para régimen {regime.value}"
            )
            return score, " | ".join(details)
        
        # Verificar alineación de tipo de señal con régimen
        if regime == MarketRegime.TRENDING:
            # En trending, preferimos señales de momentum (LONG en bull, SHORT en bear)
            score = 80
            details.append(f"Régimen TRENDING → Señales de momentum permitidas")
        
        elif regime == MarketRegime.MEAN_REVERTING:
            # En mean-reverting, solo reversión (RSI extremos, BB touches)
            score = 70
            details.append(f"Régimen MEAN_REVERTING → Señales de reversión evaluadas")
        
        elif regime == MarketRegime.TRANSITIONING:
            # Transición → alta exigencia
            score = 50
            details.append(f"Régimen TRANSITIONING → Precaución extra aplicada")
        
        # Bonus si volatility compression y la señal es fuerte
        if regime_report.volatility_compression and confidence > 75:
            score = min(100, score + 15)
            details.append("Volatility compression + señal fuerte → breakout play")
        
        return score, " | ".join(details)
    
    def _check_historical_patterns(
        self, direction: str, patterns: List[str],
        indicators_used: List[str], trade_history: List[Dict]
    ) -> tuple:
        """Check 4: ¿Este patrón falló recientemente?"""
        if not trade_history:
            return 60, "Sin historial → Score neutral"
        
        # Filtrar últimas 24h
        now = datetime.utcnow()
        recent_trades = []
        for t in trade_history:
            ts = t.get("timestamp")
            if ts:
                try:
                    if isinstance(ts, str):
                        trade_time = datetime.fromisoformat(ts)
                    else:
                        trade_time = ts
                    if (now - trade_time) < timedelta(hours=24):
                        recent_trades.append(t)
                except (ValueError, TypeError):
                    continue
        
        if not recent_trades:
            return 65, "Sin trades en últimas 24h → Score ligeramente positivo"
        
        # Buscar patrones similares que fallaron
        similar_failures = 0
        similar_total = 0
        
        for trade in recent_trades:
            trade_patterns = trade.get("patterns_detected", [])
            trade_signals = trade.get("signals_used", [])
            
            # Calcular overlap de patrones
            pattern_overlap = len(set(patterns) & set(trade_patterns))
            signal_overlap = len(set(indicators_used) & set(trade_signals))
            
            if pattern_overlap > 0 or signal_overlap >= 2:
                similar_total += 1
                if trade.get("pnl", 0) < 0:
                    similar_failures += 1
        
        if similar_total == 0:
            return 70, "Sin patrones similares recientes → Pass"
        
        failure_rate = similar_failures / similar_total
        
        if failure_rate > 0.6:
            score = 15
            detail = (
                f"⚠️ Patrón similar falló {similar_failures}/{similar_total} veces ({failure_rate:.0%}) "
                f"en últimas 24h → BLOQUEO recomendado"
            )
        elif failure_rate > 0.4:
            score = 40
            detail = f"Patrón parcialmente fallido ({failure_rate:.0%} fail rate) → Precaución"
        else:
            score = 80
            detail = f"Patrón con buen historial ({1-failure_rate:.0%} éxito) → Confiable"
        
        return score, detail
    
    def _check_volume_confirmation(
        self, volumes: List[float], closes: List[float], direction: str
    ) -> tuple:
        """Check 6: ¿El volumen confirma la dirección del movimiento?"""
        if len(volumes) < 5 or len(closes) < 5:
            return 50, "Insuficientes datos para volume confirmation"
        
        # Últimas 5 velas: ¿el volumen crece en la dirección de la señal?
        price_changes = [closes[i] - closes[i-1] for i in range(-4, 0)]
        vol_changes = volumes[-4:]
        
        confirming = 0
        total = len(price_changes)
        
        for pc, vol in zip(price_changes, vol_changes):
            if direction == "LONG" and pc > 0 and vol > sum(volumes[-20:]) / 20:
                confirming += 1
            elif direction == "SHORT" and pc < 0 and vol > sum(volumes[-20:]) / 20:
                confirming += 1
        
        ratio = confirming / total if total > 0 else 0
        
        if ratio > 0.6:
            return 85, f"Volumen confirma dirección ({confirming}/{total} velas)"
        elif ratio > 0.3:
            return 55, f"Volumen parcialmente confirma ({confirming}/{total} velas)"
        else:
            return 30, f"Volumen NO confirma dirección ({confirming}/{total} velas)"
    
    def get_approval_rate(self) -> float:
        """Porcentaje de señales aprobadas."""
        if not self._audit_history:
            return 0.0
        approved = sum(1 for a in self._audit_history if a["passed"])
        return round((approved / len(self._audit_history)) * 100, 1)


# === Singleton ===
_signal_auditor: Optional[SignalAuditor] = None


def get_signal_auditor() -> SignalAuditor:
    global _signal_auditor
    if _signal_auditor is None:
        _signal_auditor = SignalAuditor()
    return _signal_auditor
