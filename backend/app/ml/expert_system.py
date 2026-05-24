"""
SIC Ultra - Sistema de IA Local (Sin Costo)

Este módulo es la alternativa GRATUITA al usar LLMs de pago.
Usa técnicas de ML local para generar razonamiento inteligente.

Opciones gratuitas implementadas:
1. TensorFlow/Keras LSTM (ya incluido)
2. XGBoost Classifier (ya incluido)
3. Sistema experto basado en reglas (este archivo)
4. Ollama local (opcional, requiere instalación)
"""

from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger


class LocalExpertSystem:
    """
    Sistema experto local que simula razonamiento de IA.
    
    Usa reglas sofisticadas para generar análisis similar a un LLM,
    pero sin costo de API.
    
    El sistema combina:
    - Análisis técnico tradicional
    - Patrones aprendidos del historial
    - Lógica de gestión de riesgo
    """
    
    # === Reglas de Trading ===
    
    RULES = {
        # RSI Rules
        "rsi_oversold_extreme": {
            "condition": lambda ind: ind.get("rsi", 50) < 20,
            "signal": "BUY",
            "weight": 3.0,
            "reason": "RSI extremadamente sobrevendido (<20). Alta probabilidad de rebote."
        },
        "rsi_oversold": {
            "condition": lambda ind: 20 <= ind.get("rsi", 50) < 30,
            "signal": "BUY",
            "weight": 2.0,
            "reason": "RSI en zona de sobreventa. Posible reversión alcista."
        },
        "rsi_overbought_extreme": {
            "condition": lambda ind: ind.get("rsi", 50) > 80,
            "signal": "SELL",
            "weight": 3.0,
            "reason": "RSI extremadamente sobrecomprado (>80). Alta probabilidad de corrección."
        },
        "rsi_overbought": {
            "condition": lambda ind: 70 < ind.get("rsi", 50) <= 80,
            "signal": "SELL",
            "weight": 2.0,
            "reason": "RSI en zona de sobrecompra. Posible reversión bajista."
        },
        
        # MACD Rules
        "macd_bullish_cross": {
            "condition": lambda ind: ind.get("macd_cross") == "bullish",
            "signal": "BUY",
            "weight": 2.5,
            "reason": "Cruce alcista de MACD. Momentum positivo iniciando."
        },
        "macd_bearish_cross": {
            "condition": lambda ind: ind.get("macd_cross") == "bearish",
            "signal": "SELL",
            "weight": 2.5,
            "reason": "Cruce bajista de MACD. Momentum negativo iniciando."
        },
        "macd_strong_bullish": {
            "condition": lambda ind: ind.get("macd_hist", 0) > 0 and ind.get("macd_hist_prev", 0) > 0,
            "signal": "BUY",
            "weight": 1.5,
            "reason": "MACD positivo sostenido. Tendencia alcista confirmada."
        },
        "macd_strong_bearish": {
            "condition": lambda ind: ind.get("macd_hist", 0) < 0 and ind.get("macd_hist_prev", 0) < 0,
            "signal": "SELL",
            "weight": 1.5,
            "reason": "MACD negativo sostenido. Tendencia bajista confirmada."
        },
        
        # Trend Rules
        "uptrend_strong": {
            "condition": lambda ind: ind.get("trend") == "BULLISH" and ind.get("trend_strength", 0) > 0.7,
            "signal": "BUY",
            "weight": 2.0,
            "reason": "Tendencia alcista fuerte. Seguir la tendencia."
        },
        "downtrend_strong": {
            "condition": lambda ind: ind.get("trend") == "BEARISH" and ind.get("trend_strength", 0) > 0.7,
            "signal": "SELL",
            "weight": 2.0,
            "reason": "Tendencia bajista fuerte. Seguir la tendencia."
        },
        
        # Bollinger Rules
        "bb_lower_touch": {
            "condition": lambda ind: ind.get("bb_position") == "lower",
            "signal": "BUY",
            "weight": 2.0,
            "reason": "Precio tocando banda inferior de Bollinger. Posible rebote."
        },
        "bb_upper_touch": {
            "condition": lambda ind: ind.get("bb_position") == "upper",
            "signal": "SELL",
            "weight": 2.0,
            "reason": "Precio tocando banda superior de Bollinger. Posible corrección."
        },
        "bb_squeeze": {
            "condition": lambda ind: ind.get("bb_width", 1) < 0.03,
            "signal": "HOLD",
            "weight": 1.0,
            "reason": "Bandas de Bollinger muy apretadas. Breakout inminente, esperar dirección."
        },
        
        # Volume Rules
        "high_volume_up": {
            "condition": lambda ind: ind.get("volume_ratio", 1) > 2 and ind.get("price_change", 0) > 0,
            "signal": "BUY",
            "weight": 1.5,
            "reason": "Alto volumen con precio subiendo. Movimiento confirmado por volumen."
        },
        "high_volume_down": {
            "condition": lambda ind: ind.get("volume_ratio", 1) > 2 and ind.get("price_change", 0) < 0,
            "signal": "SELL",
            "weight": 1.5,
            "reason": "Alto volumen con precio bajando. Presión vendedora fuerte."
        },
        
        # Support/Resistance Rules
        "near_support": {
            "condition": lambda ind: ind.get("distance_to_support", 100) < 1,
            "signal": "BUY",
            "weight": 1.5,
            "reason": "Precio cerca de soporte. Posible rebote."
        },
        "near_resistance": {
            "condition": lambda ind: ind.get("distance_to_resistance", 100) < 1,
            "signal": "SELL",
            "weight": 1.5,
            "reason": "Precio cerca de resistencia. Posible rechazo."
        }
    }
    
    def __init__(self):
        self.history = []
        logger.info("🧠 Sistema Experto Local iniciado (Sin costo)")
    
    def analyze(self, indicators: Dict) -> Dict:
        """
        Analizar indicadores y generar señal con razonamiento.
        """
        buy_signals = []
        sell_signals = []
        hold_signals = []
        reasoning = []
        
        # Evaluar todas las reglas
        for rule_name, rule in self.RULES.items():
            try:
                if rule["condition"](indicators):
                    signal_type = rule["signal"]
                    weight = rule["weight"]
                    reason = rule["reason"]
                    
                    if signal_type == "BUY":
                        buy_signals.append({"rule": rule_name, "weight": weight, "reason": reason})
                    elif signal_type == "SELL":
                        sell_signals.append({"rule": rule_name, "weight": weight, "reason": reason})
                    else:
                        hold_signals.append({"rule": rule_name, "weight": weight, "reason": reason})
                    
                    reasoning.append(f"• {reason}")
            except:
                pass
        
        # Calcular scores
        buy_score = sum(s["weight"] for s in buy_signals)
        sell_score = sum(s["weight"] for s in sell_signals)
        
        # Determinar señal final
        min_threshold = 3.0  # Mínimo score para generar señal
        
        if buy_score > sell_score and buy_score >= min_threshold:
            final_signal = "BUY"
            final_score = buy_score
            active_rules = buy_signals
        elif sell_score > buy_score and sell_score >= min_threshold:
            final_signal = "SELL"
            final_score = sell_score
            active_rules = sell_signals
        else:
            final_signal = "HOLD"
            final_score = max(buy_score, sell_score)
            active_rules = hold_signals if hold_signals else []
            reasoning = ["No hay señal clara. Mantener posición y esperar confirmación."]
        
        # Calcular confianza (0-100)
        max_possible_score = 12  # Score máximo teórico
        confidence = min((final_score / max_possible_score) * 100, 100)
        
        # Determinar fuerza
        if confidence >= 75:
            strength = "STRONG"
        elif confidence >= 50:
            strength = "MODERATE"
        else:
            strength = "WEAK"
        
        return {
            "signal": final_signal,
            "confidence": round(confidence, 1),
            "strength": strength,
            "buy_score": round(buy_score, 2),
            "sell_score": round(sell_score, 2),
            "rules_triggered": len(active_rules),
            "reasoning": reasoning[:5],  # Top 5 razones
            "source": "LocalExpertSystem",
            "cost": "$0.00",
            "timestamp": datetime.utcnow()
        }
    
    def generate_market_analysis(
        self,
        symbol: str,
        current_price: float,
        indicators: Dict,
        patterns: List[str]
    ) -> str:
        """
        Generar análisis de mercado en texto (simula LLM).
        """
        analysis = self.analyze(indicators)
        
        # Construir texto de análisis
        text = f"""
📊 ANÁLISIS DE MERCADO - {symbol}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Precio actual: ${current_price:,.2f}

📈 INDICADORES:
• RSI: {indicators.get('rsi', 'N/A'):.1f} {'(Sobreventa)' if indicators.get('rsi', 50) < 30 else '(Sobrecompra)' if indicators.get('rsi', 50) > 70 else '(Neutral)'}
• MACD: {indicators.get('macd_hist', 'N/A'):.4f} {'📈' if indicators.get('macd_hist', 0) > 0 else '📉'}
• Tendencia: {indicators.get('trend', 'N/A')}
• ATR: {indicators.get('atr', 'N/A'):.2f}

🔍 PATRONES DETECTADOS:
{chr(10).join(['• ' + p for p in patterns]) if patterns else '• Ningún patrón claro'}

🎯 SEÑAL: {analysis['signal']}
💪 Fuerza: {analysis['strength']}
📊 Confianza: {analysis['confidence']}%

📝 RAZONAMIENTO:
{chr(10).join(analysis['reasoning'])}

⚠️ GESTIÓN DE RIESGO:
• Stop-loss sugerido: ${current_price * 0.97:,.2f} (-3%)
• Take-profit sugerido: ${current_price * 1.06:,.2f} (+6%)
• Ratio R:R: 1:2

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Generado por: Sistema Experto Local (Sin costo)
        """
        
        return text.strip()


# === Singleton ===

_expert_system: Optional[LocalExpertSystem] = None


def get_expert_system() -> LocalExpertSystem:
    """Obtener sistema experto local"""
    global _expert_system
    if _expert_system is None:
        _expert_system = LocalExpertSystem()
    return _expert_system
