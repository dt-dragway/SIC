"""
SIC Ultra - Risk Engine (RLMF Module)

Motor de gestión de riesgo dinámico que incluye:
- Dynamic Kelly Criterion para position sizing
- Anti-Martingale Guard contra rachas de pérdidas
- Fee Calculator para ajustar targets por comisiones
- Sharpe Ratio y Z-Score para evaluación de performance

REGLA DE ORO: Nunca aumentar riesgo para compensar pérdidas.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger


@dataclass
class PositionSizeResult:
    """Resultado del cálculo de tamaño de posición."""
    position_size_usd: float
    fraction_of_capital: float
    kelly_raw: float
    kelly_adjusted: float
    anti_martingale_applied: bool
    reasoning: str


@dataclass 
class FeeAdjustedTargets:
    """Targets ajustados por comisiones."""
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    total_fees_pct: float
    net_profit_pct: float  # Profit real after fees
    viable: bool  # False si fees > profit potencial
    reasoning: str


class DynamicKellyEngine:
    """
    Position sizing dinámico basado en Kelly Criterion.
    
    Usa Half-Kelly por conservadurismo institucional,
    ajustado por la confianza de la señal del agente.
    """
    
    def calculate_position_size(
        self,
        capital: float,
        win_rate: float,           # % del AgentMemory (0-100)
        avg_win: float,            # PnL promedio de ganadores (USD)
        avg_loss: float,           # PnL promedio de perdedores (USD, valor positivo)
        signal_confidence: float,  # 0-100 del agente
        max_risk_pct: float = 0.02,  # 2% max por trade
        consecutive_losses: int = 0
    ) -> PositionSizeResult:
        """
        Calcula el tamaño óptimo de posición.
        
        Fórmula Kelly: f* = (b*p - q) / b
        donde b = avg_win/avg_loss, p = win_rate, q = 1-p
        
        Aplicamos Half-Kelly y ajustamos por confianza de señal.
        """
        # Protección: si no hay datos suficientes, ir ultra-conservador
        if avg_loss <= 0 or avg_win <= 0 or capital <= 0:
            conservative_size = max(0, capital * max_risk_pct * 0.25)
            return PositionSizeResult(
                position_size_usd=round(conservative_size, 2),
                fraction_of_capital=round(max_risk_pct * 0.25, 4),
                kelly_raw=0.0,
                kelly_adjusted=0.0,
                anti_martingale_applied=False,
                reasoning="Datos insuficientes → tamaño ultra-conservador (0.5% capital)"
            )
        
        # Kelly Criterion
        b = avg_win / avg_loss  # Win/Loss ratio
        p = min(win_rate / 100, 0.99)  # Probabilidad de ganar (capped)
        q = 1 - p
        
        kelly_raw = (b * p - q) / b
        
        # Si Kelly es negativo → la estrategia pierde dinero, no operar
        if kelly_raw <= 0:
            return PositionSizeResult(
                position_size_usd=0.0,
                fraction_of_capital=0.0,
                kelly_raw=round(kelly_raw, 4),
                kelly_adjusted=0.0,
                anti_martingale_applied=False,
                reasoning=f"Kelly NEGATIVO ({kelly_raw:.4f}) → Estrategia no rentable, NO OPERAR"
            )
        
        # Half-Kelly para conservadurismo
        half_kelly = kelly_raw / 2
        
        # Ajustar por confianza de señal
        confidence_modifier = max(signal_confidence / 100, 0.1)
        adjusted_kelly = half_kelly * confidence_modifier
        
        # Anti-Martingale: reducir tras pérdidas consecutivas
        anti_martingale_applied = False
        if consecutive_losses >= 3:
            adjusted_kelly *= 0.25  # 75% reducción absoluta del capital permitido
            max_risk_pct *= 0.25    # También reducir el techo máximo!
            anti_martingale_applied = True
        elif consecutive_losses >= 2:
            adjusted_kelly *= 0.50  # 50% reducción absoluta
            max_risk_pct *= 0.50
            anti_martingale_applied = True
        
        # Clamp: NUNCA más del max_risk_pct dinámico ajustado
        final_fraction = max(0.001, min(adjusted_kelly, max_risk_pct))
        position_size = capital * final_fraction
        
        reasoning_parts = [
            f"Kelly raw={kelly_raw:.4f}",
            f"Half-Kelly={half_kelly:.4f}",
            f"Confidence modifier={confidence_modifier:.2f}",
        ]
        if anti_martingale_applied:
            reasoning_parts.append(
                f"Anti-Martingale: {consecutive_losses} pérdidas → reducción aplicada"
            )
        reasoning_parts.append(f"Final: {final_fraction:.4f} del capital = ${position_size:.2f}")
        
        return PositionSizeResult(
            position_size_usd=round(position_size, 2),
            fraction_of_capital=round(final_fraction, 4),
            kelly_raw=round(kelly_raw, 4),
            kelly_adjusted=round(adjusted_kelly, 4),
            anti_martingale_applied=anti_martingale_applied,
            reasoning=" | ".join(reasoning_parts)
        )


class AntiMartingaleGuard:
    """
    Protección contra el instinto de aumentar riesgo tras pérdidas.
    
    REGLA ABSOLUTA: Tras pérdidas consecutivas, REDUCIR posición.
    NUNCA aumentar para "recuperar".
    """
    
    @staticmethod
    def get_consecutive_losses(trade_history: List[Dict]) -> int:
        """Cuenta pérdidas consecutivas recientes."""
        if not trade_history:
            return 0
        
        count = 0
        for trade in reversed(trade_history):
            if trade.get("pnl", 0) < 0:
                count += 1
            else:
                break
        return count
    
    @staticmethod
    def get_consecutive_wins(trade_history: List[Dict]) -> int:
        """Cuenta victorias consecutivas recientes."""
        if not trade_history:
            return 0
        
        count = 0
        for trade in reversed(trade_history):
            if trade.get("pnl", 0) > 0:
                count += 1
            else:
                break
        return count
    
    @staticmethod
    def should_reduce_size(consecutive_losses: int) -> Tuple[bool, float]:
        """
        Determina si debe reducirse el tamaño de posición.
        
        Returns:
            (should_reduce, multiplier)
        """
        if consecutive_losses >= 5:
            return True, 0.1   # Solo 10% del tamaño estándar
        elif consecutive_losses >= 3:
            return True, 0.25  # 25% del tamaño estándar
        elif consecutive_losses >= 2:
            return True, 0.5   # 50% del tamaño estándar
        return False, 1.0
    
    @staticmethod
    def is_martingale_attempt(
        current_size: float,
        previous_size: float,
        consecutive_losses: int
    ) -> bool:
        """Detecta si se está intentando hacer Martingala."""
        if consecutive_losses >= 2 and current_size > previous_size:
            logger.warning(
                f"🚨 MARTINGALE DETECTADA: Intentando {current_size} > {previous_size} "
                f"tras {consecutive_losses} pérdidas. BLOQUEADO."
            )
            return True
        return False


class FeeCalculator:
    """
    Calcula el impacto de comisiones en los targets de trading.
    
    Binance Fee Tiers:
    - Maker: 0.10% (limit orders)
    - Taker: 0.10% (market orders)
    - Con BNB: 0.075% descuento
    """
    
    DEFAULT_FEE_RATE = 0.001  # 0.1% per side (maker/taker default)
    
    @classmethod
    def adjust_targets(
        cls,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        fee_rate: float = None
    ) -> FeeAdjustedTargets:
        """
        Ajusta TP/SL para compensar comisiones de trading.
        
        Total cost = entry_fee + exit_fee = 2 * fee_rate
        """
        if fee_rate is None:
            fee_rate = cls.DEFAULT_FEE_RATE
        
        # Guard: zero entry price
        if entry_price <= 0:
            return FeeAdjustedTargets(
                entry_price=entry_price, stop_loss=stop_loss,
                take_profit=take_profit, risk_reward=0,
                total_fees_pct=0, net_profit_pct=0,
                viable=False, reasoning="❌ Entry price es 0 o negativo"
            )
        
        total_fees_pct = fee_rate * 2  # Entry + Exit
        
        # Calcular distancias
        is_long = take_profit > entry_price
        
        if is_long:
            raw_profit_pct = (take_profit - entry_price) / entry_price
            raw_risk_pct = (entry_price - stop_loss) / entry_price
        else:
            raw_profit_pct = (entry_price - take_profit) / entry_price
            raw_risk_pct = (stop_loss - entry_price) / entry_price
        
        # Profit neto después de fees
        net_profit_pct = raw_profit_pct - total_fees_pct
        
        # Risk/Reward ajustado
        effective_risk = raw_risk_pct + total_fees_pct  
        risk_reward = net_profit_pct / effective_risk if effective_risk > 0 else 0
        
        # ¿Es viable? El net profit debe ser positivo y el R:R > 1.5
        viable = net_profit_pct > 0 and risk_reward >= 1.0
        
        reasoning_parts = []
        if not viable:
            if net_profit_pct <= 0:
                reasoning_parts.append(
                    f"❌ Fees ({total_fees_pct:.3%}) superan profit ({raw_profit_pct:.3%})"
                )
            elif risk_reward < 1.0:
                reasoning_parts.append(
                    f"❌ R:R ajustado ({risk_reward:.2f}) < 1.0 mínimo"
                )
        else:
            reasoning_parts.append(
                f"✅ R:R ajustado={risk_reward:.2f} | Net profit={net_profit_pct:.3%}"
            )
        
        return FeeAdjustedTargets(
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward=round(risk_reward, 2),
            total_fees_pct=round(total_fees_pct, 4),
            net_profit_pct=round(net_profit_pct, 4),
            viable=viable,
            reasoning=" | ".join(reasoning_parts)
        )


class PerformanceMetrics:
    """
    Cálculos de métricas institucionales de performance.
    """
    
    @staticmethod
    def sharpe_ratio(
        returns: List[float],
        risk_free_rate: float = 0.05,
        periods_per_year: int = 252
    ) -> float:
        """
        Sharpe Ratio anualizado.
        
        sharpe = (mean_return - risk_free_rate/periods) / std_return * sqrt(periods)
        """
        if len(returns) < 2:
            return 0.0
        
        import numpy as np
        arr = np.array(returns)
        mean_return = np.mean(arr)
        std_return = np.std(arr, ddof=1)
        
        if std_return == 0:
            return 0.0
        
        daily_rf = risk_free_rate / periods_per_year
        sharpe = (mean_return - daily_rf) / std_return * math.sqrt(periods_per_year)
        
        return round(sharpe, 4)
    
    @staticmethod
    def z_score_streaks(trade_results: List[bool]) -> float:
        """
        Z-Score de rachas para determinar si los resultados son aleatorios.
        
        |Z| > 1.96: Los resultados NO son aleatorios (95% confidence)
        |Z| < 1.96: Los resultados podrían ser aleatorios
        
        Z positivo: Rachas menos de lo esperado (sistema de reversión a media)
        Z negativo: Rachas más de lo esperado (sistema de tendencia)
        """
        if len(trade_results) < 10:
            return 0.0
        
        n = len(trade_results)
        wins = sum(trade_results)
        losses = n - wins
        
        if wins == 0 or losses == 0:
            return 0.0
        
        # Contar rachas (runs)
        runs = 1
        for i in range(1, n):
            if trade_results[i] != trade_results[i - 1]:
                runs += 1
        
        # Expected runs
        expected_runs = (2 * wins * losses) / n + 1
        
        # Standard deviation of runs
        numerator = 2 * wins * losses * (2 * wins * losses - n)
        denominator = n * n * (n - 1)
        
        if denominator == 0 or numerator / denominator < 0:
            return 0.0
        
        std_runs = math.sqrt(numerator / denominator)
        
        if std_runs == 0:
            return 0.0
        
        z = (runs - expected_runs) / std_runs
        return round(z, 4)
    
    @staticmethod
    def profit_factor(wins_total: float, losses_total: float) -> float:
        """Profit Factor = Total Wins / Total Losses."""
        if losses_total == 0:
            return float('inf') if wins_total > 0 else 0.0
        return round(abs(wins_total / losses_total), 4)
    
    @staticmethod
    def expectancy(win_rate: float, avg_win: float, avg_loss: float) -> float:
        """
        Expectancy = (win_rate * avg_win) - ((1-win_rate) * avg_loss)
        
        Positivo = sistema rentable a largo plazo
        Negativo = sistema perdedor
        """
        p = win_rate / 100
        return round(p * avg_win - (1 - p) * avg_loss, 4)


# === Singleton ===
_kelly_engine: Optional[DynamicKellyEngine] = None
_fee_calculator: Optional[FeeCalculator] = None


def get_kelly_engine() -> DynamicKellyEngine:
    global _kelly_engine
    if _kelly_engine is None:
        _kelly_engine = DynamicKellyEngine()
    return _kelly_engine


def get_fee_calculator() -> FeeCalculator:
    global _fee_calculator
    if _fee_calculator is None:
        _fee_calculator = FeeCalculator()
    return _fee_calculator
