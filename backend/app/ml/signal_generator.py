"""
SIC Ultra - Generador de Señales de Trading

Analiza el mercado con múltiples indicadores y genera señales.
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger

from app.ml.indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_atr, calculate_support_resistance, get_trend,
    calculate_sma, calculate_ema
)
from app.infrastructure.binance.client import get_binance_client


class SignalType(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    HOLD = "HOLD"


class SignalStrength(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"


class SignalGenerator:
    """
    Generador de señales de trading basado en análisis técnico.
    
    Utiliza múltiples indicadores para confirmar señales:
    - RSI (sobreventa/sobrecompra)
    - MACD (momentum)
    - Bollinger Bands (volatilidad)
    - Trend (tendencia general)
    """
    
    def __init__(self):
        self.binance = get_binance_client()
    
    def analyze(self, symbol: str, interval: str = "1h") -> Optional[Dict]:
        """
        Analizar un símbolo y generar señal de trading.
        
        Args:
            symbol: Par de trading (ej: BTCUSDT)
            interval: Timeframe (1h, 4h, 1d)
            
        Returns:
            Señal con tipo, fuerza, confianza y niveles
        """
        try:
            # Obtener datos históricos
            candles = self.binance.get_klines(symbol, interval, limit=100)
            
            if not candles or len(candles) < 50:
                logger.warning(f"Datos insuficientes para {symbol}")
                return None
            
            # Extraer precios
            closes = [c["close"] for c in candles]
            highs = [c["high"] for c in candles]
            lows = [c["low"] for c in candles]
            
            current_price = closes[-1]
            
            # Calcular indicadores
            rsi = calculate_rsi(closes, 14)
            macd = calculate_macd(closes)
            bollinger = calculate_bollinger_bands(closes, 20)
            atr = calculate_atr(highs, lows, closes, 14)
            support_resistance = calculate_support_resistance(closes, 20)
            trend = get_trend(closes, 10, 50)
            
            # Análisis de señales
            signals = []
            
            # === RSI Analysis ===
            if rsi:
                current_rsi = rsi[-1]
                if current_rsi < 30:
                    signals.append(("LONG", "RSI sobreventa", 2))
                elif current_rsi > 70:
                    signals.append(("SHORT", "RSI sobrecompra", 2))
                elif current_rsi < 40:
                    signals.append(("LONG", "RSI alcista", 1))
                elif current_rsi > 60:
                    signals.append(("SHORT", "RSI bajista", 1))
            
            # === MACD Analysis ===
            if macd["histogram"] and len(macd["histogram"]) >= 2:
                hist = macd["histogram"]
                if hist[-1] > 0 and hist[-2] <= 0:
                    signals.append(("LONG", "MACD cruce alcista", 2))
                elif hist[-1] < 0 and hist[-2] >= 0:
                    signals.append(("SHORT", "MACD cruce bajista", 2))
                elif hist[-1] > hist[-2] and hist[-1] > 0:
                    signals.append(("LONG", "MACD momentum positivo", 1))
                elif hist[-1] < hist[-2] and hist[-1] < 0:
                    signals.append(("SHORT", "MACD momentum negativo", 1))
            
            # === Bollinger Bands Analysis ===
            if bollinger["lower"] and bollinger["upper"]:
                lower = bollinger["lower"][-1]
                upper = bollinger["upper"][-1]
                
                if current_price <= lower:
                    signals.append(("LONG", "Precio en banda inferior", 2))
                elif current_price >= upper:
                    signals.append(("SHORT", "Precio en banda superior", 2))
            
            # === Trend Analysis ===
            if trend == "BULLISH":
                signals.append(("LONG", "Tendencia alcista", 1))
            elif trend == "BEARISH":
                signals.append(("SHORT", "Tendencia bajista", 1))
            
            # === Calcular señal final ===
            long_score = sum(s[2] for s in signals if s[0] == "LONG")
            short_score = sum(s[2] for s in signals if s[0] == "SHORT")
            
            # Determinar tipo de señal
            if long_score > short_score and long_score >= 3:
                signal_type = SignalType.LONG
                score = long_score
            elif short_score > long_score and short_score >= 3:
                signal_type = SignalType.SHORT
                score = short_score
            else:
                signal_type = SignalType.HOLD
                score = 0
            
            # Determinar fuerza
            if score >= 6:
                strength = SignalStrength.STRONG
            elif score >= 4:
                strength = SignalStrength.MODERATE
            else:
                strength = SignalStrength.WEAK
            
            # Calcular confianza (0-100%)
            max_possible = 8  # Máximo score teórico
            confidence = min((score / max_possible) * 100, 100)
            
            # Calcular niveles de entrada/salida
            current_atr = atr[-1] if atr else current_price * 0.02
            
            if signal_type == SignalType.LONG:
                entry = current_price
                stop_loss = current_price - (current_atr * 1.5)
                take_profit = current_price + (current_atr * 3)
            elif signal_type == SignalType.SHORT:
                entry = current_price
                stop_loss = current_price + (current_atr * 1.5)
                take_profit = current_price - (current_atr * 3)
            else:
                entry = current_price
                stop_loss = current_price
                take_profit = current_price
            
            # Risk/Reward ratio
            risk = abs(entry - stop_loss)
            reward = abs(take_profit - entry)
            risk_reward = reward / risk if risk > 0 else 0
            
            # Razonamiento
            reasons = [s[1] for s in signals if s[0] == signal_type.value]
            
            return {
                "symbol": symbol,
                "interval": interval,
                "type": signal_type.value,
                "strength": strength.value,
                "confidence": round(confidence, 1),
                "current_price": current_price,
                "entry_price": round(entry, 2),
                "stop_loss": round(stop_loss, 2),
                "take_profit": round(take_profit, 2),
                "risk_reward": round(risk_reward, 2),
                "indicators": {
                    "rsi": round(rsi[-1], 1) if rsi else None,
                    "macd_histogram": round(macd["histogram"][-1], 4) if macd["histogram"] else None,
                    "trend": trend,
                    "atr": round(current_atr, 2)
                },
                "reasoning": reasons,
                "support": round(support_resistance["support"], 2),
                "resistance": round(support_resistance["resistance"], 2),
                "timestamp": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=4)
            }
            
        except Exception as e:
            logger.error(f"Error analizando {symbol}: {e}")
            return None
    
    def scan_market(self, symbols: List[str] = None) -> List[Dict]:
        """
        Escanear múltiples símbolos y retornar solo señales activas.
        """
        if not symbols:
            symbols = [
                "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
                "XRPUSDT", "ADAUSDT", "DOTUSDT", "MATICUSDT"
            ]
        
        signals = []
        
        for symbol in symbols:
            signal = self.analyze(symbol)
            if signal and signal["type"] != "HOLD":
                signals.append(signal)
        
        # Ordenar por confianza
        signals.sort(key=lambda x: x["confidence"], reverse=True)
        
        return signals


# Singleton
_signal_generator: Optional[SignalGenerator] = None


def get_signal_generator() -> SignalGenerator:
    """Obtener generador de señales (singleton)"""
    global _signal_generator
    if _signal_generator is None:
        _signal_generator = SignalGenerator()
    return _signal_generator
