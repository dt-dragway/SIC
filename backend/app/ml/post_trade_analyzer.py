"""
SIC Ultra - Post Trade Analyzer (RLMF Module)

Análisis post-trade que genera un Reporte de Desviación por cada operación cerrada.
Implementa el feedback loop de "Reinforcement Learning from Market Feedback".

Cada trade cerrado se convierte en datos de entrenamiento inmediato:
- Slippage del entry
- MAE/MFE (Maximum Adverse/Favorable Excursion)
- Efficiency Ratio
- Ajuste de pesos del modelo

PRINCIPIO: "Cada error del mercado real es una lección que ningún backtest puede dar."
"""

import math
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from loguru import logger


@dataclass
class DeviationReport:
    """Reporte de desviación de un trade completado."""
    trade_id: str
    symbol: str
    direction: str
    
    # Desviaciones medidas
    slippage_pct: float        # (fill_price - signal_price) / signal_price
    mae_pct: float             # Maximum Adverse Excursion (% contra nosotros)
    mfe_pct: float             # Maximum Favorable Excursion (% a favor)
    efficiency_ratio: float    # actual_pnl / mfe (¿capturamos el máximo?)
    
    # Duración
    hold_duration_minutes: float
    
    # Diagnóstico
    entry_quality: str         # EXCELLENT, GOOD, POOR, TERRIBLE
    exit_quality: str          # EXCELLENT, GOOD, POOR, TERRIBLE
    
    # Ajustes recomendados
    weight_adjustments: Dict[str, float]  # indicador → nuevo peso sugerido
    parameter_adjustments: Dict[str, float]  # parámetro → nuevo valor sugerido
    
    # Aprendizaje
    lesson_learned: str        # Descripción del insight
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


class PostTradeAnalyzer:
    """
    Analizador post-trade para aprendizaje adaptativo.
    
    Por cada trade cerrado:
    1. Mide desviaciones (slippage, MAE, MFE)
    2. Evalúa calidad de entry/exit
    3. Genera ajustes de peso para el LearningEngine
    4. Acumula insights para el log diario de aprendizaje
    """
    
    # Thresholds de calidad
    SLIPPAGE_THRESHOLDS = {
        "EXCELLENT": 0.001,  # < 0.1%
        "GOOD": 0.003,       # < 0.3%
        "POOR": 0.005,       # < 0.5%
        "TERRIBLE": 1.0      # >= 0.5%
    }
    
    def __init__(self):
        self._deviation_history: List[DeviationReport] = []
        self._daily_lessons: List[Dict] = []
        self._weight_adjustments_queue: List[Dict] = []
        logger.info("📈 Post-Trade Analyzer inicializado")
    
    def analyze(
        self,
        trade_id: str,
        symbol: str,
        direction: str,
        signal_price: float,
        fill_price: float,
        exit_price: float,
        pnl: float,
        price_history_during_trade: List[float],
        signals_used: List[str],
        patterns_detected: List[str],
        entry_time: Optional[datetime] = None,
        exit_time: Optional[datetime] = None
    ) -> DeviationReport:
        """
        Analizar un trade completado y generar reporte de desviación.
        
        Args:
            signal_price: Precio al que la IA generó la señal
            fill_price: Precio real de ejecución
            exit_price: Precio de cierre
            pnl: Profit/Loss en USD
            price_history_during_trade: Lista de precios durante la vida del trade
            signals_used: Indicadores usados en la señal
            patterns_detected: Patrones que se detectaron
        """
        # === 1. Slippage ===
        slippage_pct = abs(fill_price - signal_price) / signal_price if signal_price > 0 else 0
        
        # === 2. MAE / MFE ===
        mae_pct, mfe_pct = self._calculate_excursions(
            fill_price, price_history_during_trade, direction
        )
        
        # === 3. Efficiency Ratio ===
        actual_pnl_pct = abs(pnl / fill_price) if fill_price > 0 else 0
        efficiency_ratio = (actual_pnl_pct / mfe_pct) if mfe_pct > 0 else 0
        if pnl < 0:
            efficiency_ratio = -efficiency_ratio  # Negativo si perdimos
        
        # === 4. Duración ===
        hold_duration = 0.0
        if entry_time and exit_time:
            hold_duration = (exit_time - entry_time).total_seconds() / 60
        
        # === 5. Calidad de Entry ===
        entry_quality = self._rate_quality(slippage_pct, self.SLIPPAGE_THRESHOLDS)
        
        # === 6. Calidad de Exit ===
        exit_quality = self._rate_exit_quality(efficiency_ratio, pnl > 0)
        
        # === 7. Ajustes de Peso ===
        weight_adjustments = self._calculate_weight_adjustments(
            slippage_pct, mae_pct, mfe_pct, efficiency_ratio,
            signals_used, pnl > 0
        )
        
        # === 8. Ajustes de Parámetros ===
        parameter_adjustments = self._calculate_param_adjustments(
            mae_pct, mfe_pct, efficiency_ratio, direction
        )
        
        # === 9. Lección Aprendida ===
        lesson = self._generate_lesson(
            symbol, direction, slippage_pct, mae_pct, mfe_pct,
            efficiency_ratio, pnl, entry_quality, exit_quality
        )
        
        report = DeviationReport(
            trade_id=trade_id,
            symbol=symbol,
            direction=direction,
            slippage_pct=round(slippage_pct, 6),
            mae_pct=round(mae_pct, 6),
            mfe_pct=round(mfe_pct, 6),
            efficiency_ratio=round(efficiency_ratio, 4),
            hold_duration_minutes=round(hold_duration, 1),
            entry_quality=entry_quality,
            exit_quality=exit_quality,
            weight_adjustments=weight_adjustments,
            parameter_adjustments=parameter_adjustments,
            lesson_learned=lesson
        )
        
        # Almacenar
        self._deviation_history.append(report)
        if len(self._deviation_history) > 500:
            self._deviation_history = self._deviation_history[-500:]
        
        self._daily_lessons.append({
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": symbol,
            "lesson": lesson,
            "pnl": pnl
        })
        
        # Queue weight adjustments for LearningEngine
        self._weight_adjustments_queue.append(weight_adjustments)
        
        logger.info(
            f"📈 Post-Trade [{trade_id}]: {entry_quality} entry | {exit_quality} exit | "
            f"Slippage={slippage_pct:.3%} | MAE={mae_pct:.3%} | "
            f"MFE={mfe_pct:.3%} | Efficiency={efficiency_ratio:.1%}"
        )
        
        return report
    
    def apply_adjustments(self, learning_engine) -> Dict:
        """
        Aplica los ajustes acumulados al LearningEngine.
        Debe llamarse después de record_trade_result().
        
        Returns:
            Resumen de ajustes aplicados
        """
        if not self._weight_adjustments_queue:
            return {"applied": 0}
        
        applied = 0
        for adjustments in self._weight_adjustments_queue:
            for strategy, adjustment in adjustments.items():
                # Aplicar ajuste incremental
                current_weight = learning_engine.get_strategy_confidence(strategy)
                new_weight = max(0.3, min(3.0, current_weight + adjustment))
                
                # Actualizar en memory
                if strategy in learning_engine.memory.data["current_strategy_weights"]:
                    learning_engine.memory.data["current_strategy_weights"][strategy] = new_weight
                    applied += 1
        
        if applied > 0:
            learning_engine.memory.save()
            logger.info(f"⚙️ {applied} ajustes de peso aplicados desde Post-Trade Analyzer")
        
        self._weight_adjustments_queue.clear()
        return {"applied": applied}
    
    def get_daily_learning_log(self) -> Dict:
        """
        Genera el log diario de aprendizaje.
        "Qué aprendió el sistema hoy del entorno real que no estaba en los libros."
        """
        now = datetime.utcnow()
        today_lessons = [
            l for l in self._daily_lessons
            if (now - datetime.fromisoformat(l["timestamp"])) < timedelta(hours=24)
        ]
        
        if not today_lessons:
            return {
                "date": now.strftime("%Y-%m-%d"),
                "lessons_count": 0,
                "lessons": [],
                "summary": "Sin trades hoy → Sin aprendizaje nuevo"
            }
        
        # Agrupar por resultado
        wins = [l for l in today_lessons if l["pnl"] > 0]
        losses = [l for l in today_lessons if l["pnl"] <= 0]
        
        summary_parts = []
        if wins:
            summary_parts.append(f"✅ {len(wins)} trades ganadores")
        if losses:
            summary_parts.append(f"❌ {len(losses)} trades perdedores")
        
        # Métricas de desviación del día
        today_reports = self._deviation_history[-len(today_lessons):]
        if today_reports:
            avg_slippage = sum(r.slippage_pct for r in today_reports) / len(today_reports)
            avg_efficiency = sum(r.efficiency_ratio for r in today_reports) / len(today_reports)
            avg_mae = sum(r.mae_pct for r in today_reports) / len(today_reports)
            
            summary_parts.append(f"Slippage promedio: {avg_slippage:.3%}")
            summary_parts.append(f"Efficiency promedio: {avg_efficiency:.1%}")
            summary_parts.append(f"MAE promedio: {avg_mae:.3%}")
        
        return {
            "date": now.strftime("%Y-%m-%d"),
            "lessons_count": len(today_lessons),
            "lessons": [l["lesson"] for l in today_lessons],
            "summary": " | ".join(summary_parts),
            "winning_lessons": [l["lesson"] for l in wins],
            "losing_lessons": [l["lesson"] for l in losses]
        }
    
    def get_parametric_adjustments(self) -> Dict:
        """
        Lista de ajustes paramétricos para mejorar la ejecución mañana.
        """
        if len(self._deviation_history) < 5:
            return {"status": "Insuficientes trades para ajustes", "adjustments": []}
        
        recent = self._deviation_history[-50:]
        
        adjustments = []
        
        # Analizar slippage promedio
        avg_slippage = sum(r.slippage_pct for r in recent) / len(recent)
        if avg_slippage > 0.003:
            adjustments.append({
                "parameter": "execution_method",
                "current": "market_order",
                "suggested": "limit_order_with_timeout",
                "reason": f"Slippage promedio {avg_slippage:.3%} > 0.3% → Usar limit orders"
            })
        
        # Analizar MAE promedio
        avg_mae = sum(r.mae_pct for r in recent) / len(recent)
        if avg_mae > 0.02:
            adjustments.append({
                "parameter": "sl_atr_multiplier",
                "current": 1.5,
                "suggested": 2.0,
                "reason": f"MAE promedio {avg_mae:.3%} >> SL → Ampliar SL para evitar wicks"
            })
        
        # Analizar efficiency promedio
        avg_efficiency = sum(r.efficiency_ratio for r in recent) / len(recent)
        if 0 < avg_efficiency < 0.4:
            adjustments.append({
                "parameter": "tp_atr_multiplier",
                "current": 3.0,
                "suggested": 2.0,
                "reason": f"Efficiency {avg_efficiency:.1%} < 40% → Reducir TP para capturar más profit"
            })
        
        # Analizar calidad de entries
        poor_entries = sum(1 for r in recent if r.entry_quality in ("POOR", "TERRIBLE"))
        if poor_entries / len(recent) > 0.3:
            adjustments.append({
                "parameter": "min_signal_confidence",
                "current": 60,
                "suggested": 75,
                "reason": f"{poor_entries}/{len(recent)} entries de baja calidad → Subir threshold"
            })
        
        return {
            "status": f"Basado en últimos {len(recent)} trades",
            "adjustments": adjustments,
            "metrics": {
                "avg_slippage": round(avg_slippage, 5),
                "avg_mae": round(avg_mae, 5),
                "avg_efficiency": round(avg_efficiency, 4),
                "poor_entry_rate": round(poor_entries / len(recent), 3)
            }
        }
    
    # === Métodos Internos ===
    
    def _calculate_excursions(
        self, entry_price: float, prices: List[float], direction: str
    ) -> tuple:
        """Calcula MAE y MFE."""
        if not prices or entry_price <= 0:
            return 0.0, 0.0
        
        if direction == "LONG":
            min_price = min(prices)
            max_price = max(prices)
            mae = (entry_price - min_price) / entry_price  # Cuánto bajó
            mfe = (max_price - entry_price) / entry_price  # Cuánto subió
        else:  # SHORT
            max_price = max(prices)
            min_price = min(prices)
            mae = (max_price - entry_price) / entry_price  # Cuánto subió (contra nosotros)
            mfe = (entry_price - min_price) / entry_price  # Cuánto bajó (a nuestro favor)
        
        return max(0, mae), max(0, mfe)
    
    def _rate_quality(self, value: float, thresholds: Dict) -> str:
        """Clasificar calidad basándose en thresholds."""
        for quality, threshold in thresholds.items():
            if value < threshold:
                return quality
        return "TERRIBLE"
    
    def _rate_exit_quality(self, efficiency: float, is_winner: bool) -> str:
        """Clasificar calidad del exit."""
        if not is_winner:
            if efficiency > -0.5:
                return "GOOD"  # Perdimos poco vs MFE
            return "POOR"
        
        if efficiency > 0.7:
            return "EXCELLENT"
        elif efficiency > 0.4:
            return "GOOD"
        elif efficiency > 0.2:
            return "POOR"
        return "TERRIBLE"
    
    def _calculate_weight_adjustments(
        self, slippage: float, mae: float, mfe: float,
        efficiency: float, signals_used: List[str], is_winner: bool
    ) -> Dict[str, float]:
        """
        Calcular ajustes de peso para cada indicador usado.
        
        Winners → increase weight slightly
        Losers con high MAE → decrease entry timing weight
        Low efficiency → adjust exit parameters
        """
        adjustments = {}
        
        for signal in signals_used:
            adj = 0.0
            
            if is_winner:
                # Ganar → reforzar ligeramente el indicador
                adj += 0.02
                if efficiency > 0.6:
                    adj += 0.01  # Bonus por buena efficiency
            else:
                # Perder → penalizar ligeramente
                adj -= 0.02
                if mae > 0.03:
                    adj -= 0.02  # Penalty extra por alto MAE
            
            # Slippage alto afecta entry timing
            if slippage > 0.003:
                adj -= 0.01
            
            adjustments[signal] = round(adj, 4)
        
        return adjustments
    
    def _calculate_param_adjustments(
        self, mae: float, mfe: float, efficiency: float, direction: str
    ) -> Dict[str, float]:
        """Calcular ajustes de parámetros del sistema."""
        adjustments = {}
        
        # Si MAE es consistentemente alto, necesitamos SL más amplio o mejor timing
        if mae > 0.02:
            adjustments["sl_buffer_increase"] = round(mae * 0.5, 4)
        
        # Si efficiency es baja, el TP está demasiado lejos
        if 0 < efficiency < 0.3:
            adjustments["tp_reduction_factor"] = 0.8
        
        # Si MFE es alto pero efficiency baja → estamos cerrando mal
        if mfe > 0.03 and efficiency < 0.4:
            adjustments["use_trailing_stop"] = 1.0
        
        return adjustments
    
    def _generate_lesson(
        self, symbol: str, direction: str, slippage: float,
        mae: float, mfe: float, efficiency: float,
        pnl: float, entry_quality: str, exit_quality: str
    ) -> str:
        """Genera una lección en lenguaje natural."""
        parts = []
        
        result = "GANADOR" if pnl > 0 else "PERDEDOR"
        parts.append(f"[{symbol} {direction} {result}]")
        
        if slippage > 0.003:
            parts.append(f"Entry con alto slippage ({slippage:.3%}) → considerar limit orders")
        
        if mae > 0.02 and pnl > 0:
            parts.append(
                f"Sufrió {mae:.3%} de drawdown antes de ganar → "
                f"SL casi activado, mejorar timing de entrada"
            )
        
        if mae > 0.02 and pnl < 0:
            parts.append(
                f"MAE de {mae:.3%} muestra que la entrada fue contra el flujo del mercado"
            )
        
        if mfe > 0.03 and efficiency < 0.3:
            parts.append(
                f"El precio fue {mfe:.3%} a favor pero solo capturamos {efficiency:.0%} → "
                f"considerar trailing stop"
            )
        
        if efficiency > 0.7 and pnl > 0:
            parts.append("Excelente captura de movimiento → mantener estrategia actual")
        
        if not parts[1:]:
            parts.append("Trade normal sin desviaciones significativas")
        
        return " | ".join(parts)


# === Singleton ===
_post_trade_analyzer: Optional[PostTradeAnalyzer] = None


def get_post_trade_analyzer() -> PostTradeAnalyzer:
    global _post_trade_analyzer
    if _post_trade_analyzer is None:
        _post_trade_analyzer = PostTradeAnalyzer()
    return _post_trade_analyzer
