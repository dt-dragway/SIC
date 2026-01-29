"""
SIC Ultra - Generador de Señales Profesional con Multi-Timeframe Analysis

Sistema de trading de nivel profesional que analiza múltiples timeframes
para generar señales de alta confianza.

Estrategia MTF:
- 4h: Tendencia macro (dirección principal) - 40% peso
- 1h: Momentum y confirmación - 35% peso  
- 15m: Timing de entrada preciso - 25% peso

Regla de oro: Solo operar en la dirección de la tendencia de 4h.
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger

from app.ml.indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_atr, calculate_support_resistance, get_trend,
    calculate_stochastic_rsi, calculate_adx, detect_rsi_divergence,
    calculate_volume_profile, get_ema_alignment, calculate_fibonacci_levels
)
from app.ml.candle_patterns import detect_all_patterns
from app.infrastructure.binance.client import get_binance_client


class SignalTier(str, Enum):
    """Clasificación de calidad de señales"""
    S_TIER = "S"   # 85-100% - Señal premium
    A_TIER = "A"   # 70-84%  - Señal muy buena
    B_TIER = "B"   # 55-69%  - Señal aceptable
    C_TIER = "C"   # <55%    - No mostrar


class SignalType(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    HOLD = "HOLD"


class ProSignalGenerator:
    """
    Generador de señales profesional con Multi-Timeframe Analysis.
    
    Utiliza análisis en 3 timeframes para confirmar señales:
    - Tendencia macro (4h)
    - Momentum (1h)
    - Timing de entrada (15m)
    
    Además integra:
    - Patrones de velas japonesas
    - Divergencias RSI
    - Alineación de EMAs
    - ADX para fuerza de tendencia
    - Análisis de volumen
    """
    
    # Pesos de cada timeframe
    WEIGHT_4H = 0.40   # 40%
    WEIGHT_1H = 0.35   # 35%
    WEIGHT_15M = 0.25  # 25%
    
    # Umbral mínimo de R:R
    MIN_RISK_REWARD = 2.0
    
    def __init__(self):
        self.binance = get_binance_client()
    
    def _analyze_timeframe(self, symbol: str, interval: str) -> Dict:
        """
        Analizar un timeframe específico.
        
        Returns:
            Dict con dirección, score, indicadores y razones
        """
        try:
            # Obtener más velas para indicadores de largo plazo
            limit = 200 if interval == "4h" else 100
            candles = self.binance.get_klines(symbol, interval, limit=limit)
            
            if not candles or len(candles) < 50:
                return {"direction": "NEUTRAL", "score": 0, "indicators": {}, "reasons": []}
            
            # Extraer datos
            closes = [c["close"] for c in candles]
            highs = [c["high"] for c in candles]
            lows = [c["low"] for c in candles]
            volumes = [c.get("volume", 0) for c in candles]
            current_price = closes[-1]
            
            # === Calcular todos los indicadores ===
            rsi = calculate_rsi(closes, 14)
            macd = calculate_macd(closes)
            bollinger = calculate_bollinger_bands(closes, 20)
            atr = calculate_atr(highs, lows, closes, 14)
            stoch_rsi = calculate_stochastic_rsi(closes)
            adx_data = calculate_adx(highs, lows, closes)
            ema_alignment = get_ema_alignment(closes)
            volume_profile = calculate_volume_profile(volumes)
            patterns = detect_all_patterns(candles[-5:])  # Últimas 5 velas
            fibonacci = calculate_fibonacci_levels(closes)
            
            # Detectar divergencias RSI
            divergence = detect_rsi_divergence(closes, rsi) if rsi else {"type": None}
            
            # === Sistema de puntuación ===
            bullish_score = 0
            bearish_score = 0
            reasons = []
            
            # --- RSI Analysis ---
            if rsi and len(rsi) > 0:
                current_rsi = rsi[-1]
                if current_rsi < 30:
                    bullish_score += 3
                    reasons.append("RSI sobreventa extrema")
                elif current_rsi < 40:
                    bullish_score += 1.5
                    reasons.append("RSI zona alcista")
                elif current_rsi > 70:
                    bearish_score += 3
                    reasons.append("RSI sobrecompra extrema")
                elif current_rsi > 60:
                    bearish_score += 1.5
                    reasons.append("RSI zona bajista")
            
            # --- Divergencias RSI (muy poderosas) ---
            if divergence["type"] == "BULLISH_DIVERGENCE":
                bullish_score += 4
                reasons.append("🔥 Divergencia RSI alcista")
            elif divergence["type"] == "BEARISH_DIVERGENCE":
                bearish_score += 4
                reasons.append("🔥 Divergencia RSI bajista")
            
            # --- MACD Analysis ---
            if macd["histogram"] and len(macd["histogram"]) >= 2:
                hist = macd["histogram"]
                if hist[-1] > 0 and hist[-2] <= 0:
                    bullish_score += 2.5
                    reasons.append("MACD cruce alcista")
                elif hist[-1] < 0 and hist[-2] >= 0:
                    bearish_score += 2.5
                    reasons.append("MACD cruce bajista")
                elif hist[-1] > hist[-2] > 0:
                    bullish_score += 1
                    reasons.append("MACD momentum positivo")
                elif hist[-1] < hist[-2] < 0:
                    bearish_score += 1
                    reasons.append("MACD momentum negativo")
            
            # --- Stochastic RSI ---
            if stoch_rsi["k"] and stoch_rsi["d"]:
                k = stoch_rsi["k"][-1] if stoch_rsi["k"] else 50
                d = stoch_rsi["d"][-1] if stoch_rsi["d"] else 50
                
                if k < 20 and d < 20:
                    bullish_score += 2
                    reasons.append("StochRSI sobreventa")
                elif k > 80 and d > 80:
                    bearish_score += 2
                    reasons.append("StochRSI sobrecompra")
                elif k > d and k < 50:  # Cruce alcista desde abajo
                    bullish_score += 1
                elif k < d and k > 50:  # Cruce bajista desde arriba
                    bearish_score += 1
            
            # --- ADX (Fuerza de tendencia) ---
            if adx_data["adx"] and adx_data["plus_di"] and adx_data["minus_di"]:
                adx = adx_data["adx"][-1] if adx_data["adx"] else 0
                plus_di = adx_data["plus_di"][-1] if adx_data["plus_di"] else 0
                minus_di = adx_data["minus_di"][-1] if adx_data["minus_di"] else 0
                
                if adx > 25:  # Tendencia fuerte
                    if plus_di > minus_di:
                        bullish_score += 2
                        reasons.append(f"ADX fuerte alcista ({adx:.0f})")
                    else:
                        bearish_score += 2
                        reasons.append(f"ADX fuerte bajista ({adx:.0f})")
            
            # --- EMA Alignment ---
            if ema_alignment["alignment"] == "PERFECT_BULLISH":
                bullish_score += 3
                reasons.append("EMAs perfectamente alineadas ↑")
            elif ema_alignment["alignment"] == "BULLISH":
                bullish_score += 1.5
                reasons.append("EMAs mayormente alcistas")
            elif ema_alignment["alignment"] == "PERFECT_BEARISH":
                bearish_score += 3
                reasons.append("EMAs perfectamente alineadas ↓")
            elif ema_alignment["alignment"] == "BEARISH":
                bearish_score += 1.5
                reasons.append("EMAs mayormente bajistas")
            
            # --- Bollinger Bands ---
            if bollinger["lower"] and bollinger["upper"]:
                lower = bollinger["lower"][-1]
                upper = bollinger["upper"][-1]
                
                if current_price <= lower:
                    bullish_score += 2
                    reasons.append("Precio en banda inferior Bollinger")
                elif current_price >= upper:
                    bearish_score += 2
                    reasons.append("Precio en banda superior Bollinger")
            
            # --- Patrones de Velas ---
            if patterns["bullish_score"] > 0:
                bullish_score += patterns["bullish_score"]
                for p in patterns["patterns"]:
                    if p["direction"] == "BULLISH":
                        reasons.append(f"📊 {p['name']}")
            
            if patterns["bearish_score"] > 0:
                bearish_score += patterns["bearish_score"]
                for p in patterns["patterns"]:
                    if p["direction"] == "BEARISH":
                        reasons.append(f"📊 {p['name']}")
            
            # --- Volumen ---
            if volume_profile["is_high"] and volume_profile["trend"] == "INCREASING":
                # Volumen alto confirma la dirección
                if bullish_score > bearish_score:
                    bullish_score += 1
                    reasons.append("Volumen confirma movimiento")
                elif bearish_score > bullish_score:
                    bearish_score += 1
                    reasons.append("Volumen confirma movimiento")
            
            # === Determinar dirección ===
            if bullish_score > bearish_score and bullish_score >= 3:
                direction = "BULLISH"
                score = bullish_score
            elif bearish_score > bullish_score and bearish_score >= 3:
                direction = "BEARISH"
                score = bearish_score
            else:
                direction = "NEUTRAL"
                score = 0
            
            return {
                "direction": direction,
                "score": score,
                "bullish_score": bullish_score,
                "bearish_score": bearish_score,
                "indicators": {
                    "rsi": round(rsi[-1], 1) if rsi else None,
                    "macd": round(macd["histogram"][-1], 4) if macd["histogram"] else None,
                    "stoch_k": round(stoch_rsi["k"][-1], 1) if stoch_rsi["k"] else None,
                    "adx": round(adx_data["adx"][-1], 1) if adx_data["adx"] else None,
                    "ema_alignment": ema_alignment["alignment"],
                    "volume_ratio": volume_profile["ratio"],
                    "patterns": [p["name"] for p in patterns["patterns"]]
                },
                "reasons": reasons,
                "current_price": current_price,
                "atr": atr[-1] if atr else current_price * 0.02,
                "fibonacci": fibonacci
            }
            
        except Exception as e:
            logger.error(f"Error analizando {symbol} en {interval}: {e}")
            return {"direction": "NEUTRAL", "score": 0, "indicators": {}, "reasons": []}
    
    def analyze(self, symbol: str) -> Optional[Dict]:
        """
        Análisis Multi-Timeframe completo.
        
        Analiza en 4h → 1h → 15m para generar señales de alta confianza.
        Solo genera señal si los timeframes están alineados.
        """
        try:
            logger.info(f"🔬 Analizando {symbol} con MTF...")
            
            # Análisis en cada timeframe
            tf_4h = self._analyze_timeframe(symbol, "4h")
            tf_1h = self._analyze_timeframe(symbol, "1h")
            tf_15m = self._analyze_timeframe(symbol, "15m")
            
            # Verificar alineación de timeframes
            directions = [tf_4h["direction"], tf_1h["direction"], tf_15m["direction"]]
            
            # Contar alineación
            bullish_count = directions.count("BULLISH")
            bearish_count = directions.count("BEARISH")
            
            # Determinar señal final
            if bullish_count >= 2 and tf_4h["direction"] in ["BULLISH", "NEUTRAL"]:
                signal_type = SignalType.LONG
                aligned = bullish_count
            elif bearish_count >= 2 and tf_4h["direction"] in ["BEARISH", "NEUTRAL"]:
                signal_type = SignalType.SHORT
                aligned = bearish_count
            else:
                # Sin alineación clara
                return {
                    "symbol": symbol,
                    "type": "HOLD",
                    "tier": SignalTier.C_TIER.value,
                    "confidence": 0,
                    "reason": "Sin alineación de timeframes",
                    "timeframes": {
                        "4h": tf_4h["direction"],
                        "1h": tf_1h["direction"],
                        "15m": tf_15m["direction"]
                    }
                }
            
            # Calcular score ponderado
            weighted_score = (
                tf_4h["score"] * self.WEIGHT_4H +
                tf_1h["score"] * self.WEIGHT_1H +
                tf_15m["score"] * self.WEIGHT_15M
            )
            
            # Bonus por alineación perfecta
            if aligned == 3:
                weighted_score *= 1.25  # +25% bonus
            
            # Calcular confianza (0-100%)
            max_possible = 15  # Score máximo teórico
            confidence = min((weighted_score / max_possible) * 100, 100)
            
            # Determinar tier
            if confidence >= 85:
                tier = SignalTier.S_TIER
            elif confidence >= 70:
                tier = SignalTier.A_TIER
            elif confidence >= 55:
                tier = SignalTier.B_TIER
            else:
                tier = SignalTier.C_TIER
            
            # No mostrar señales de baja calidad
            if tier == SignalTier.C_TIER:
                return None
            
            # Usar datos del timeframe más preciso para entrada
            current_price = tf_15m["current_price"]
            atr = tf_1h["atr"]  # ATR de 1h para SL/TP
            
            # Calcular SL y TP con R:R mínimo de 2:1
            if signal_type == SignalType.LONG:
                stop_loss = current_price - (atr * 1.5)
                # Asegurar R:R >= 2:1
                risk = current_price - stop_loss
                take_profit = current_price + (risk * max(self.MIN_RISK_REWARD, 2.5))
            else:
                stop_loss = current_price + (atr * 1.5)
                risk = stop_loss - current_price
                take_profit = current_price - (risk * max(self.MIN_RISK_REWARD, 2.5))
            
            # Calcular R:R real
            risk_reward = abs(take_profit - current_price) / abs(current_price - stop_loss)
            
            # Combinar razones de todos los timeframes
            all_reasons = []
            for tf_name, tf_data in [("4h", tf_4h), ("1h", tf_1h), ("15m", tf_15m)]:
                for reason in tf_data.get("reasons", []):
                    if reason not in all_reasons:
                        all_reasons.append(f"[{tf_name}] {reason}")
            
            # Limitar a las 5 razones más importantes
            all_reasons = all_reasons[:5]
            
            return {
                "symbol": symbol,
                "type": signal_type.value,
                "tier": tier.value,
                "tier_emoji": "🔥" if tier == SignalTier.S_TIER else "⭐" if tier == SignalTier.A_TIER else "📈",
                "confidence": round(confidence, 1),
                "current_price": round(current_price, 2),
                "entry_price": round(current_price, 2),
                "stop_loss": round(stop_loss, 2),
                "take_profit": round(take_profit, 2),
                "risk_reward": round(risk_reward, 2),
                "timeframes": {
                    "4h": {
                        "direction": tf_4h["direction"],
                        "score": round(tf_4h["score"], 1),
                        "indicators": tf_4h["indicators"]
                    },
                    "1h": {
                        "direction": tf_1h["direction"],
                        "score": round(tf_1h["score"], 1),
                        "indicators": tf_1h["indicators"]
                    },
                    "15m": {
                        "direction": tf_15m["direction"],
                        "score": round(tf_15m["score"], 1),
                        "indicators": tf_15m["indicators"]
                    }
                },
                "alignment": aligned,
                "aligned_timeframes": f"{aligned}/3",
                "reasoning": all_reasons,
                "fibonacci": tf_1h.get("fibonacci", {}),
                "timestamp": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=2 if tier == SignalTier.S_TIER else 1)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis MTF de {symbol}: {e}")
            return None
    
    def scan_market(self, symbols: List[str] = None) -> List[Dict]:
        """
        Escanear múltiples símbolos y retornar solo señales de alta calidad.
        
        Solo retorna señales con tier B o superior.
        """
        if not symbols:
            symbols = [
                "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
                "XRPUSDT", "ADAUSDT", "DOTUSDT", "MATICUSDT"
            ]
        
        signals = []
        
        for symbol in symbols:
            signal = self.analyze(symbol)
            if signal and signal.get("type") != "HOLD":
                signals.append(signal)
        
        # Ordenar por tier y luego por confianza
        tier_order = {"S": 0, "A": 1, "B": 2}
        signals.sort(key=lambda x: (tier_order.get(x["tier"], 3), -x["confidence"]))
        
        return signals


# Mantener compatibilidad con el generador anterior
class SignalGenerator(ProSignalGenerator):
    """Alias para compatibilidad con código existente"""
    pass


# Singleton
_signal_generator: Optional[ProSignalGenerator] = None


def get_signal_generator() -> ProSignalGenerator:
    """Obtener generador de señales profesional (singleton)"""
    global _signal_generator
    if _signal_generator is None:
        _signal_generator = ProSignalGenerator()
    return _signal_generator
