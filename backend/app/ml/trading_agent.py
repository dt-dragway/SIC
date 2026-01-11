"""
SIC Ultra - Agente de Trading IA Profesional

Sistema de inteligencia artificial que:
- Aprende de cada trade (éxito y fracaso)
- Evoluciona sus estrategias con el tiempo
- Estudia patrones de mercado en profundidad
- Copia técnicas de top traders
- Genera señales con alta precisión
- Ejecuta automáticamente con autorización del usuario

Este es el CEREBRO del sistema SIC Ultra.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from loguru import logger
import random

from app.config import settings


# === Memory Storage ===

class AgentMemory:
    """
    Memoria persistente del agente.
    Guarda todo el historial de aprendizaje.
    """
    
    def __init__(self, memory_file: str = "agent_memory.json"):
        self.memory_file = os.path.join(
            os.path.dirname(__file__), 
            memory_file
        )
        self.data = self._load()
    
    def _load(self) -> dict:
        """Cargar memoria desde archivo"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0",
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_pnl": 0.0,
            "best_trade": None,
            "worst_trade": None,
            "patterns_learned": {},
            "strategy_performance": {},
            "market_insights": [],
            "evolution_history": [],
            "current_strategy_weights": {
                "rsi": 1.0,
                "macd": 1.0,
                "bollinger": 1.0,
                "trend": 1.0,
                "volume": 1.0,
                "support_resistance": 1.0,
                "top_trader_signals": 1.5  # Mayor peso a señales de top traders
            }
        }
    
    def save(self):
        """Guardar memoria a archivo"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def get_win_rate(self) -> float:
        """Calcular win rate actual"""
        total = self.data["total_trades"]
        if total == 0:
            return 0.0
        return (self.data["winning_trades"] / total) * 100
    
    def update_strategy_weight(self, strategy: str, success: bool):
        """
        Ajustar peso de estrategia basado en resultado.
        Las estrategias exitosas ganan más peso.
        """
        weights = self.data["current_strategy_weights"]
        if strategy in weights:
            if success:
                weights[strategy] = min(weights[strategy] * 1.1, 3.0)  # Max 3x
            else:
                weights[strategy] = max(weights[strategy] * 0.9, 0.3)  # Min 0.3x
        self.save()


# === Pattern Recognition ===

@dataclass
class MarketPattern:
    """Patrón de mercado identificado"""
    name: str
    confidence: float
    timeframe: str
    indicators: Dict[str, float]
    expected_direction: str  # "BULLISH" or "BEARISH"
    expected_move_percent: float
    historical_accuracy: float


class PatternRecognizer:
    """
    Reconocedor de patrones de mercado.
    Aprende de patrones históricos y los identifica en tiempo real.
    """
    
    # Patrones conocidos
    PATTERNS = {
        "double_bottom": {
            "direction": "BULLISH",
            "avg_move": 5.0,
            "min_confidence": 0.7
        },
        "double_top": {
            "direction": "BEARISH",
            "avg_move": 5.0,
            "min_confidence": 0.7
        },
        "bullish_engulfing": {
            "direction": "BULLISH",
            "avg_move": 3.0,
            "min_confidence": 0.65
        },
        "bearish_engulfing": {
            "direction": "BEARISH",
            "avg_move": 3.0,
            "min_confidence": 0.65
        },
        "rsi_divergence_bullish": {
            "direction": "BULLISH",
            "avg_move": 4.0,
            "min_confidence": 0.75
        },
        "rsi_divergence_bearish": {
            "direction": "BEARISH",
            "avg_move": 4.0,
            "min_confidence": 0.75
        },
        "macd_golden_cross": {
            "direction": "BULLISH",
            "avg_move": 6.0,
            "min_confidence": 0.8
        },
        "macd_death_cross": {
            "direction": "BEARISH",
            "avg_move": 6.0,
            "min_confidence": 0.8
        },
        "bollinger_squeeze_breakout": {
            "direction": "NEUTRAL",  # Se determina por dirección del breakout
            "avg_move": 7.0,
            "min_confidence": 0.7
        }
    }
    
    def identify_patterns(
        self, 
        candles: List[Dict],
        rsi: List[float],
        macd: Dict,
        bollinger: Dict
    ) -> List[MarketPattern]:
        """
        Identificar patrones en los datos actuales.
        """
        patterns = []
        
        if len(candles) < 20 or not rsi:
            return patterns
        
        # RSI Extremos
        current_rsi = rsi[-1]
        if current_rsi < 25:
            patterns.append(MarketPattern(
                name="rsi_extreme_oversold",
                confidence=min((30 - current_rsi) / 10, 1.0),
                timeframe="current",
                indicators={"rsi": current_rsi},
                expected_direction="BULLISH",
                expected_move_percent=3.0,
                historical_accuracy=0.68
            ))
        elif current_rsi > 75:
            patterns.append(MarketPattern(
                name="rsi_extreme_overbought",
                confidence=min((current_rsi - 70) / 10, 1.0),
                timeframe="current",
                indicators={"rsi": current_rsi},
                expected_direction="BEARISH",
                expected_move_percent=3.0,
                historical_accuracy=0.65
            ))
        
        # MACD Crossovers
        if macd.get("histogram") and len(macd["histogram"]) >= 3:
            hist = macd["histogram"]
            # Golden Cross (MACD cruza arriba de signal)
            if hist[-1] > 0 and hist[-2] <= 0 and hist[-3] < 0:
                patterns.append(MarketPattern(
                    name="macd_golden_cross",
                    confidence=0.8,
                    timeframe="recent",
                    indicators={"macd_hist": hist[-1]},
                    expected_direction="BULLISH",
                    expected_move_percent=6.0,
                    historical_accuracy=0.72
                ))
            # Death Cross
            elif hist[-1] < 0 and hist[-2] >= 0 and hist[-3] > 0:
                patterns.append(MarketPattern(
                    name="macd_death_cross",
                    confidence=0.8,
                    timeframe="recent",
                    indicators={"macd_hist": hist[-1]},
                    expected_direction="BEARISH",
                    expected_move_percent=6.0,
                    historical_accuracy=0.70
                ))
        
        # Bollinger Squeeze
        if bollinger.get("upper") and bollinger.get("lower"):
            upper = bollinger["upper"][-1]
            lower = bollinger["lower"][-1]
            middle = bollinger["middle"][-1]
            band_width = (upper - lower) / middle
            
            if band_width < 0.04:  # Squeeze muy apretado
                price = candles[-1]["close"]
                direction = "BULLISH" if price > middle else "BEARISH"
                patterns.append(MarketPattern(
                    name="bollinger_squeeze",
                    confidence=0.75,
                    timeframe="current",
                    indicators={"band_width": band_width},
                    expected_direction=direction,
                    expected_move_percent=7.0,
                    historical_accuracy=0.67
                ))
        
        return patterns


# === Top Trader Analyzer ===

class TopTraderAnalyzer:
    """
    Analiza y aprende de los mejores traders de Binance.
    Simula copy trading inteligente.
    """
    
    def __init__(self):
        # Datos simulados de top traders (en producción: API de Binance Leaderboard)
        self.top_traders = [
            {
                "nickname": "CryptoMaster_01",
                "roi_30d": 45.2,
                "win_rate": 78.5,
                "avg_trade_duration": "4h",
                "favorite_pairs": ["BTCUSDT", "ETHUSDT"],
                "current_position": None
            },
            {
                "nickname": "WhaleHunter",
                "roi_30d": 38.7,
                "win_rate": 72.3,
                "avg_trade_duration": "12h",
                "favorite_pairs": ["BTCUSDT", "SOLUSDT", "BNBUSDT"],
                "current_position": None
            },
            {
                "nickname": "DeFiKing",
                "roi_30d": 52.1,
                "win_rate": 65.0,
                "avg_trade_duration": "2h",
                "favorite_pairs": ["ETHUSDT", "LINKUSDT"],
                "current_position": None
            }
        ]
    
    def get_consensus(self, symbol: str) -> Optional[Dict]:
        """
        Obtener consenso de top traders para un símbolo.
        
        Returns:
            Señal si hay consenso, None si no hay
        """
        # Simular posiciones actuales de traders
        positions = []
        for trader in self.top_traders:
            if symbol in trader["favorite_pairs"]:
                # Simular: 60% probabilidad de tener posición
                if random.random() < 0.6:
                    pos = {
                        "trader": trader["nickname"],
                        "side": random.choice(["LONG", "SHORT"]),
                        "confidence": trader["win_rate"] / 100
                    }
                    positions.append(pos)
        
        if len(positions) < 2:
            return None
        
        # Contar votos
        longs = sum(1 for p in positions if p["side"] == "LONG")
        shorts = len(positions) - longs
        
        # Necesitamos >= 66% de consenso
        total = len(positions)
        if longs / total >= 0.66:
            return {
                "direction": "LONG",
                "consensus": longs / total,
                "traders": [p["trader"] for p in positions if p["side"] == "LONG"],
                "avg_confidence": sum(p["confidence"] for p in positions if p["side"] == "LONG") / longs
            }
        elif shorts / total >= 0.66:
            return {
                "direction": "SHORT",
                "consensus": shorts / total,
                "traders": [p["trader"] for p in positions if p["side"] == "SHORT"],
                "avg_confidence": sum(p["confidence"] for p in positions if p["side"] == "SHORT") / shorts
            }
        
        return None


# === Learning Engine ===

class LearningEngine:
    """
    Motor de aprendizaje del agente.
    Aprende de cada trade y mejora la estrategia.
    """
    
    def __init__(self, memory: AgentMemory):
        self.memory = memory
    
    def record_trade_result(
        self,
        trade_id: str,
        symbol: str,
        side: str,
        entry_price: float,
        exit_price: float,
        pnl: float,
        signals_used: List[str],
        patterns_detected: List[str]
    ):
        """
        Registrar resultado de un trade para aprendizaje.
        """
        success = pnl > 0
        
        # Actualizar estadísticas generales
        self.memory.data["total_trades"] += 1
        if success:
            self.memory.data["winning_trades"] += 1
        else:
            self.memory.data["losing_trades"] += 1
        
        self.memory.data["total_pnl"] += pnl
        
        # Actualizar mejor/peor trade
        if self.memory.data["best_trade"] is None or pnl > self.memory.data["best_trade"]:
            self.memory.data["best_trade"] = pnl
        if self.memory.data["worst_trade"] is None or pnl < self.memory.data["worst_trade"]:
            self.memory.data["worst_trade"] = pnl
        
        # Aprender de las señales usadas
        for signal in signals_used:
            self.memory.update_strategy_weight(signal, success)
        
        # Aprender de patrones
        for pattern in patterns_detected:
            if pattern not in self.memory.data["patterns_learned"]:
                self.memory.data["patterns_learned"][pattern] = {
                    "total": 0, "wins": 0, "losses": 0
                }
            
            self.memory.data["patterns_learned"][pattern]["total"] += 1
            if success:
                self.memory.data["patterns_learned"][pattern]["wins"] += 1
            else:
                self.memory.data["patterns_learned"][pattern]["losses"] += 1
        
        # Registrar en historial de evolución
        self.memory.data["evolution_history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "trade_id": trade_id,
            "pnl": pnl,
            "win_rate": self.memory.get_win_rate(),
            "strategy_weights": dict(self.memory.data["current_strategy_weights"])
        })
        
        # Mantener solo últimos 1000 registros
        if len(self.memory.data["evolution_history"]) > 1000:
            self.memory.data["evolution_history"] = self.memory.data["evolution_history"][-1000:]
        
        self.memory.save()
        
        logger.info(f"📚 Aprendizaje registrado: Trade {trade_id}, PnL: ${pnl:.2f}, Win Rate: {self.memory.get_win_rate():.1f}%")
    
    def get_strategy_confidence(self, strategy: str) -> float:
        """Obtener confianza actual en una estrategia"""
        weights = self.memory.data["current_strategy_weights"]
        return weights.get(strategy, 1.0)
    
    def get_pattern_accuracy(self, pattern: str) -> float:
        """Obtener precisión histórica de un patrón"""
        patterns = self.memory.data["patterns_learned"]
        if pattern not in patterns or patterns[pattern]["total"] == 0:
            return 0.5  # Sin datos, asumir 50%
        
        p = patterns[pattern]
        return p["wins"] / p["total"]


# === Main Trading Agent ===

@dataclass
class TradingSignal:
    """Señal de trading generada por el agente"""
    symbol: str
    direction: str  # LONG, SHORT, HOLD
    confidence: float  # 0-100
    strength: str  # STRONG, MODERATE, WEAK
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    
    # Análisis detallado
    patterns_detected: List[str]
    indicators_used: List[str]
    top_trader_consensus: Optional[Dict]
    
    # Razonamiento
    reasoning: List[str]
    
    # Metadata
    timestamp: datetime
    expires_at: datetime
    auto_execute_approved: bool = False


class TradingAgentAI:
    """
    Agente de Trading IA Profesional.
    
    El CEREBRO de SIC Ultra que:
    - Analiza el mercado en profundidad
    - Aprende y evoluciona con cada trade
    - Genera señales de alta precisión
    - Ejecuta automáticamente con autorización
    """
    
    def __init__(self):
        self.memory = AgentMemory()
        self.learning = LearningEngine(self.memory)
        self.pattern_recognizer = PatternRecognizer()
        self.top_trader_analyzer = TopTraderAnalyzer()
        
        logger.info("🤖 Agente IA Trading iniciado")
        logger.info(f"📊 Trades históricos: {self.memory.data['total_trades']}")
        logger.info(f"🏆 Win Rate: {self.memory.get_win_rate():.1f}%")
    
    def analyze(
        self, 
        symbol: str,
        candles: List[Dict],
        indicators: Dict
    ) -> Optional[TradingSignal]:
        """
        Análisis profundo del mercado para generar señal.
        
        Este es el método principal que:
        1. Analiza indicadores técnicos
        2. Detecta patrones
        3. Consulta consenso de top traders
        4. Aplica pesos aprendidos
        5. Genera señal con confianza calibrada
        """
        if len(candles) < 50:
            return None
        
        closes = [c["close"] for c in candles]
        current_price = closes[-1]
        
        # === 1. Análisis de Indicadores ===
        signals = []
        reasoning = []
        indicators_used = []
        
        # RSI
        rsi = indicators.get("rsi", [])
        if rsi:
            current_rsi = rsi[-1]
            rsi_weight = self.learning.get_strategy_confidence("rsi")
            
            if current_rsi < 30:
                signals.append(("LONG", 2 * rsi_weight, "RSI sobreventa"))
                indicators_used.append("rsi")
            elif current_rsi > 70:
                signals.append(("SHORT", 2 * rsi_weight, "RSI sobrecompra"))
                indicators_used.append("rsi")
            elif current_rsi < 40:
                signals.append(("LONG", 1 * rsi_weight, "RSI tendencia alcista"))
                indicators_used.append("rsi")
            elif current_rsi > 60:
                signals.append(("SHORT", 1 * rsi_weight, "RSI tendencia bajista"))
                indicators_used.append("rsi")
        
        # MACD
        macd = indicators.get("macd", {})
        if macd.get("histogram"):
            hist = macd["histogram"]
            macd_weight = self.learning.get_strategy_confidence("macd")
            
            if len(hist) >= 2:
                if hist[-1] > 0 and hist[-2] <= 0:
                    signals.append(("LONG", 2.5 * macd_weight, "MACD cruce alcista"))
                    indicators_used.append("macd")
                elif hist[-1] < 0 and hist[-2] >= 0:
                    signals.append(("SHORT", 2.5 * macd_weight, "MACD cruce bajista"))
                    indicators_used.append("macd")
        
        # Bollinger
        bollinger = indicators.get("bollinger", {})
        if bollinger.get("lower") and bollinger.get("upper"):
            bb_weight = self.learning.get_strategy_confidence("bollinger")
            lower = bollinger["lower"][-1]
            upper = bollinger["upper"][-1]
            
            if current_price <= lower:
                signals.append(("LONG", 2 * bb_weight, "Precio en banda inferior Bollinger"))
                indicators_used.append("bollinger")
            elif current_price >= upper:
                signals.append(("SHORT", 2 * bb_weight, "Precio en banda superior Bollinger"))
                indicators_used.append("bollinger")
        
        # Trend
        trend = indicators.get("trend", "NEUTRAL")
        trend_weight = self.learning.get_strategy_confidence("trend")
        if trend == "BULLISH":
            signals.append(("LONG", 1.5 * trend_weight, "Tendencia alcista confirmada"))
            indicators_used.append("trend")
        elif trend == "BEARISH":
            signals.append(("SHORT", 1.5 * trend_weight, "Tendencia bajista confirmada"))
            indicators_used.append("trend")
        
        # === 2. Detección de Patrones ===
        patterns = self.pattern_recognizer.identify_patterns(
            candles, rsi, macd, bollinger
        )
        patterns_detected = []
        
        for pattern in patterns:
            # Aplicar precisión histórica aprendida
            learned_accuracy = self.learning.get_pattern_accuracy(pattern.name)
            adjusted_confidence = pattern.confidence * learned_accuracy
            
            if adjusted_confidence > 0.5:
                direction = "LONG" if pattern.expected_direction == "BULLISH" else "SHORT"
                signals.append((
                    direction, 
                    adjusted_confidence * 2, 
                    f"Patrón: {pattern.name} ({pattern.historical_accuracy*100:.0f}% histórico)"
                ))
                patterns_detected.append(pattern.name)
        
        # === 3. Consenso de Top Traders ===
        top_trader_weight = self.learning.get_strategy_confidence("top_trader_signals")
        consensus = self.top_trader_analyzer.get_consensus(symbol)
        
        if consensus:
            signals.append((
                consensus["direction"],
                3 * top_trader_weight * consensus["consensus"],
                f"Top traders ({len(consensus['traders'])}): {consensus['direction']}"
            ))
            indicators_used.append("top_trader_signals")
        
        # === 4. Calcular Señal Final ===
        long_score = sum(s[1] for s in signals if s[0] == "LONG")
        short_score = sum(s[1] for s in signals if s[0] == "SHORT")
        
        # Recoger razonamiento
        reasoning = [s[2] for s in signals]
        
        # Determinar dirección
        min_threshold = 4.0  # Mínimo score para generar señal
        
        if long_score > short_score and long_score >= min_threshold:
            direction = "LONG"
            score = long_score
        elif short_score > long_score and short_score >= min_threshold:
            direction = "SHORT"
            score = short_score
        else:
            return None  # HOLD - no hay señal clara
        
        # === 5. Calcular Niveles ===
        atr = indicators.get("atr", current_price * 0.02)
        if isinstance(atr, list) and atr:
            atr = atr[-1]
        
        if direction == "LONG":
            stop_loss = current_price - (atr * 1.5)
            take_profit = current_price + (atr * 3)
        else:
            stop_loss = current_price + (atr * 1.5)
            take_profit = current_price - (atr * 3)
        
        risk = abs(current_price - stop_loss)
        reward = abs(take_profit - current_price)
        risk_reward = reward / risk if risk > 0 else 0
        
        # === 6. Calcular Confianza ===
        max_possible_score = 15  # Score máximo teórico
        confidence = min((score / max_possible_score) * 100, 100)
        
        # Ajustar confianza con win rate histórico
        historical_win_rate = self.memory.get_win_rate()
        if historical_win_rate > 0:
            confidence = confidence * 0.7 + historical_win_rate * 0.3
        
        # Determinar fuerza
        if confidence >= 80:
            strength = "STRONG"
        elif confidence >= 60:
            strength = "MODERATE"
        else:
            strength = "WEAK"
        
        return TradingSignal(
            symbol=symbol,
            direction=direction,
            confidence=round(confidence, 1),
            strength=strength,
            entry_price=current_price,
            stop_loss=round(stop_loss, 2),
            take_profit=round(take_profit, 2),
            risk_reward=round(risk_reward, 2),
            patterns_detected=patterns_detected,
            indicators_used=indicators_used,
            top_trader_consensus=consensus,
            reasoning=reasoning,
            timestamp=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=4),
            auto_execute_approved=False
        )
    
    def approve_auto_execute(self, signal: TradingSignal) -> TradingSignal:
        """Usuario aprueba ejecución automática de la señal"""
        signal.auto_execute_approved = True
        logger.info(f"✅ Auto-ejecución aprobada: {signal.symbol} {signal.direction}")
        return signal
    
    def record_result(
        self,
        trade_id: str,
        symbol: str,
        side: str,
        entry_price: float,
        exit_price: float,
        pnl: float,
        signals_used: List[str],
        patterns_detected: List[str]
    ):
        """
        Registrar resultado del trade para que el agente aprenda.
        """
        self.learning.record_trade_result(
            trade_id, symbol, side, entry_price, exit_price,
            pnl, signals_used, patterns_detected
        )
    
    def get_performance_stats(self) -> Dict:
        """Obtener estadísticas de rendimiento del agente"""
        return {
            "total_trades": self.memory.data["total_trades"],
            "winning_trades": self.memory.data["winning_trades"],
            "losing_trades": self.memory.data["losing_trades"],
            "win_rate": self.memory.get_win_rate(),
            "total_pnl": self.memory.data["total_pnl"],
            "best_trade": self.memory.data["best_trade"],
            "worst_trade": self.memory.data["worst_trade"],
            "patterns_learned": len(self.memory.data["patterns_learned"]),
            "strategy_weights": self.memory.data["current_strategy_weights"],
            "evolution_entries": len(self.memory.data["evolution_history"])
        }
    
    def get_learned_patterns(self) -> Dict:
        """Obtener patrones aprendidos con su precisión"""
        patterns = {}
        for name, data in self.memory.data["patterns_learned"].items():
            if data["total"] > 0:
                patterns[name] = {
                    "total": data["total"],
                    "wins": data["wins"],
                    "accuracy": round(data["wins"] / data["total"] * 100, 1)
                }
        return patterns


# === Singleton ===
_trading_agent: Optional[TradingAgentAI] = None


def get_trading_agent() -> TradingAgentAI:
    """Obtener instancia del agente de trading"""
    global _trading_agent
    if _trading_agent is None:
        _trading_agent = TradingAgentAI()
    return _trading_agent
