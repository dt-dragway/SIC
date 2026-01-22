"""
Generador de Explicaciones para Señales de Trading

Este módulo genera explicaciones claras en español y pasos de ejecución
para ayudar a usuarios novatos a entender y ejecutar señales de trading.
"""

from typing import List, Dict, Optional
from app.ml.candlestick_analyzer import CandlestickPattern


def generate_spanish_explanation(
    direction: str,
    symbol: str,
    candlestick_patterns: List[CandlestickPattern],
    indicators_summary: Dict[str, any],
    consensus: Optional[Dict]
) -> str:
    """
    Generar explicación en español clara para usuarios novatos.
    
    Args:
        direction: "LONG" o "SHORT"
        symbol: Símbolo de la criptomoneda
        candlestick_patterns: Patrones de velas detectados
        indicators_summary: Resumen de indicadores (RSI, MACD, etc.)
        consensus: Consenso de top traders
    
    Returns:
        Explicación en español clara y concisa
    """
    parts = []
    
    # Encabezado
    if direction == "LONG":
        parts.append(f"✅ SEÑAL DE COMPRA (LONG) para {symbol.replace('USDT', '')}")
    else:
        parts.append(f"⚠️ SEÑAL DE VENTA (SHORT) para {symbol.replace('USDT', '')}")
    
    parts.append("\n\n📊 Razones:")
    
    # Patrones de velas
    if candlestick_patterns:
        parts.append(f"\n• {len(candlestick_patterns)} patrón(es) de velas detectado(s):")
        for pattern in candlestick_patterns[:3]:  # Máximo 3 para no saturar
            parts.append(f"  - {pattern.name_es}: {pattern.description_es}")
    
    # Indicadores
    indicators_reasons = []
    if indicators_summary.get("rsi"):
        rsi_val = indicators_summary["rsi"]
        if rsi_val < 30:
            indicators_reasons.append(f"RSI en sobreventa ({rsi_val:.0f}) - presión compradora probable")
        elif rsi_val > 70:
            indicators_reasons.append(f"RSI en sobrecompra ({rsi_val:.0f}) - presión vendedora probable")
    
    if indicators_summary.get("macd_signal"):
        indicators_reasons.append(f"MACD señal {indicators_summary['macd_signal']}")
    
    if indicators_summary.get("trend"):
        trend_es = "alcista" if indicators_summary["trend"] == "BULLISH" else "bajista"
        indicators_reasons.append(f"Tendencia {trend_es} confirmada")
    
    if indicators_reasons:
        parts.append(f"\n• Indicadores técnicos:")
        for reason in indicators_reasons:
            parts.append(f"  - {reason}")
    
    # Consenso de traders
    if consensus:
        direction_es = "COMPRA" if consensus["direction"] == "LONG" else "VENTA"
        parts.append(f"\n• Top traders: {consensus['consensus']*100:.0f}% en {direction_es}")
    
    # Conclusión
    parts.append(f"\n\n💡 Conclusión:")
    if direction == "LONG":
        parts.append("El precio está en un buen momento para COMPRAR. Los indicadores sugieren una subida próxima.")
    else:
        parts.append("El precio está en un buen momento para VENDER. Los indicadores sugieren una bajada próxima.")
    
    return "".join(parts)


def generate_execution_steps(
    direction: str,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    risk_reward: float
) -> List[str]:
    """
    Generar pasos de ejecución para el usuario.
    
    Returns:
        Lista de pasos en español
    """
    action_es = "COMPRA (BUY/LONG)" if direction == "LONG" else "VENTA (SELL/SHORT)"
    
    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)
    
    steps = [
        f"1️⃣ Entrar en {action_es} al precio actual: ${entry_price:,.2f}",
        f"2️⃣ Colocar Stop Loss en: ${stop_loss:,.2f} (protege contra pérdidas de ${risk:,.2f})",
        f"3️⃣ Colocar Take Profit en: ${take_profit:,.2f} (ganancia objetivo: ${reward:,.2f})",
        f"4️⃣ Ratio Riesgo/Beneficio: 1:{risk_reward:.1f} (por cada $1 que arriesgas, puedes ganar ${risk_reward:.1f})"
    ]
    
    # Consejo adicional
    if direction == "LONG":
        steps.append("💡 Consejo: Si el precio baja al Stop Loss, la operación se cerrará automáticamente para limitar pérdidas.")
    else:
        steps.append("💡 Consejo: Si el precio sube al Stop Loss, la operación se cerrará automáticamente para limitar pérdidas.")
    
    return steps
