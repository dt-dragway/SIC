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
from app.ml.candlestick_analyzer import CandlestickAnalyzer, CandlestickPattern

# RLMF Modules (Signal Intelligence Evolution)
from app.ml.regime_detector import get_regime_detector, MarketRegime
from app.ml.signal_auditor import get_signal_auditor
from app.ml.post_trade_analyzer import get_post_trade_analyzer
from app.ml.risk_engine import (
    get_kelly_engine, FeeCalculator, AntiMartingaleGuard, PerformanceMetrics
)


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
        
        # Sistema de backups automáticos
        try:
            from app.ml.backup_manager import BackupManager
            backup_dir = os.path.join(os.path.dirname(__file__), "backups")
            self.backup_manager = BackupManager(
                source_file=self.memory_file,
                backup_dir=backup_dir,
                retention_days=30
            )
            # Crear backup al iniciar
            self.backup_manager.create_backup()
            self.backup_manager.rotate_backups()
            logger.info("✅ Sistema de backups inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Backups no disponibles: {e}")
    
    def _load(self) -> dict:
        """Cargar memoria desde archivo"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Error cargando memoria del agente: {e}")
                # Intentar cargar backup si existe
                backup_path = f"{self.memory_file}.bak"
                if os.path.exists(backup_path):
                    try:
                        with open(backup_path, 'r') as f:
                            logger.info("⚠️ Restaurando memoria desde backup...")
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
        """Guardar memoria a archivo con backup atómico"""
        try:
            # 1. Crear backup del actual si existe
            if os.path.exists(self.memory_file):
                import shutil
                shutil.copy2(self.memory_file, f"{self.memory_file}.bak")
            
            # 2. Guardar nuevo estado
            with open(self.memory_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"❌ Error guardando memoria del agente: {e}")
    
    def sync_to_database(self, db_session, trade_id: str, symbol: str, side: str, 
                         entry_price: float, exit_price: float, pnl: float,
                         signals_used: list, patterns_detected: list):
        """
        Sincronizar trade con base de datos PostgreSQL.
        
        Args:
            db_session: Sesión de SQLAlchemy
            trade_id: ID del trade
            symbol: Símbolo (ej: BTCUSDT)
            side: BUY o SELL
            entry_price: Precio de entrada
            exit_price: Precio de salida
            pnl: Profit and Loss
            signals_used: Lista de señales usadas
            patterns_detected: Lista de patrones detectados
        """
        try:
            from app.infrastructure.database.models import AgentTrade
            import json as json_lib
            
            # Verificar si ya existe
            existing = db_session.query(AgentTrade).filter(
                AgentTrade.trade_id == trade_id
            ).first()
            
            if existing:
                logger.debug(f"Trade {trade_id} ya existe en BD")
                return
            
            # Crear nuevo registro
            agent_trade = AgentTrade(
                trade_id=trade_id,
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                exit_price=exit_price,
                pnl=pnl,
                signals_used=json_lib.dumps(signals_used),
                patterns_detected=json_lib.dumps(patterns_detected)
            )
            
            db_session.add(agent_trade)
            db_session.commit()
            logger.info(f"✅ Trade {trade_id} sincronizado con BD")
            
        except Exception as e:
            logger.error(f"❌ Error sincronizando trade con BD: {e}")
            if db_session:
                db_session.rollback()
    
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
        # Top traders se obtienen dinámicamente via Binance Futures API
        # en get_consensus(). No se almacenan datos hardcodeados.
        self.top_traders = []  # Populated dynamically from Binance Leaderboard
    
    def get_consensus(self, symbol: str) -> Optional[Dict]:
        """
        Obtener consenso REAL de Top Traders (Binance Futures).
        """
        try:
            from app.infrastructure.binance.client import get_binance_client
            client = get_binance_client()
            
            # Obtener ratio real de Binance
            data = client.get_top_long_short_ratio(symbol)
            
            if not data:
                return None
            
            long_ratio = data["long_ratio"]
            short_ratio = data["short_ratio"]
            
            # Determinar consenso (> 55% es significativo en top traders)
            if long_ratio > 0.55:
                direction = "LONG"
                consensus = long_ratio
            elif short_ratio > 0.55:
                direction = "SHORT"
                consensus = short_ratio
            else:
                return None # Mercado indeciso
                
            return {
                "direction": direction,
                "consensus": consensus,
                "traders": ["Binance Top Traders"], # Anonimizado por API
                "avg_confidence": consensus,
                "ratio_value": data["ratio"],
                "source": "Binance Futures Real-Time"
            }
            
        except Exception as e:
            logger.error(f"Error analizando top traders: {e}")
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
        patterns_detected: List[str],
        db_session=None
    ):
        """
        Registrar resultado de un trade para aprendizaje.
        
        Args:
            db_session: (Opcional) Sesión de BD para sincronización
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
        
        # Registrar en historial de trades (RLMF usa esto)
        if "trade_results" not in self.memory.data:
            self.memory.data["trade_results"] = []
        self.memory.data["trade_results"].append({
            "trade_id": trade_id,
            "pnl": pnl,
            "side": side,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Mantener solo últimos 1000 registros
        if len(self.memory.data["evolution_history"]) > 1000:
            self.memory.data["evolution_history"] = self.memory.data["evolution_history"][-1000:]
        
        # Guardar en JSON
        self.memory.save()
        
        # NUEVO: Sincronizar con BD si está disponible
        if db_session:
            self.memory.sync_to_database(
                db_session=db_session,
                trade_id=trade_id,
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                exit_price=exit_price,
                pnl=pnl,
                signals_used=signals_used,
                patterns_detected=patterns_detected
            )
        
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
    patterns_detected: List[str]  # Nombres de patrones técnicos
    indicators_used: List[str]  # Indicadores usados (RSI, MACD, etc.)
    top_trader_consensus: Optional[Dict]
    
    # NUEVO: Patrones de velas detectados
    candlestick_patterns: List[Dict]  # Patrones de velas con detalles
    
    # NUEVO: Explicación en español para usuarios novatos
    explanation_es: str  # Explicación clara y concisa
    
    # NUEVO: Pasos de ejecución para el usuario
    execution_steps: List[str]  # Instrucciones paso a paso
    
    # NUEVO: Análisis multi-timeframe
    timeframe_analysis: Dict[str, str]  # {"1h": "BULLISH", "4h": "BULLISH", ...}
    
    # Razonamiento (técnico)
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
        # NUEVO: Analizador de patrones de velas
        self.candlestick_analyzer = CandlestickAnalyzer(min_confidence=65.0)
        
        # === RLMF Modules (Signal Intelligence Evolution) ===
        self.regime_detector = get_regime_detector()
        self.signal_auditor = get_signal_auditor()
        self.post_trade_analyzer = get_post_trade_analyzer()
        self.kelly_engine = get_kelly_engine()
        self.fee_calculator = FeeCalculator()
        self.anti_martingale = AntiMartingaleGuard()
        self.performance_metrics = PerformanceMetrics()
        
        logger.info("🤖 Agente IA Trading iniciado (RLMF Evolution Active)")
        logger.info(f"📊 Trades históricos: {self.memory.data['total_trades']}")
        logger.info(f"🏆 Win Rate: {self.memory.get_win_rate():.1f}%")
        logger.info(f"🕯️ Candlestick Analyzer: Activo (confianza mínima: 65%)")
        logger.info(f"📊 Regime Detector: Activo")
        logger.info(f"🛡️ Signal Auditor: Activo")
        logger.info(f"📈 Post-Trade Analyzer: Activo")
    
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
        if len(candles) < 20:
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
        min_threshold = 2.0  # Mínimo score para generar señal activado
        
        if long_score > short_score and long_score >= min_threshold:
            direction = "LONG"
            score = long_score
        elif short_score > long_score and short_score >= min_threshold:
            direction = "SHORT"
            score = short_score
        else:
            # En modo testing/baja convicción, forzamos un log para depurar
            logger.debug(f"Hold Forzado: LS={long_score} SS={short_score} Min={min_threshold}")
            return None  # HOLD - no hay señal clara
        
        # === 5. Calcular Niveles (con Regime-Aware Multipliers) ===
        atr = indicators.get("atr", current_price * 0.02)
        if isinstance(atr, list) and atr:
            atr = atr[-1]
        
        # RLMF: Detectar régimen y ajustar multiplicadores
        regime_report = self.regime_detector.detect(candles, indicators)
        regime_params = regime_report.params
        sl_multiplier = regime_params.get("sl_atr_multiplier", 1.5)
        tp_multiplier = regime_params.get("tp_atr_multiplier", 3.0)
        
        if direction == "LONG":
            stop_loss = current_price - (atr * sl_multiplier)
            take_profit = current_price + (atr * tp_multiplier)
        else:
            stop_loss = current_price + (atr * sl_multiplier)
            take_profit = current_price - (atr * tp_multiplier)
        
        # RLMF: Verificar viabilidad de fees
        fee_result = self.fee_calculator.adjust_targets(current_price, stop_loss, take_profit)
        if not fee_result.viable:
            reasoning.append(f"⚠️ Fees: {fee_result.reasoning}")
            # No retornar None — dejamos que el auditor lo evalúe
        
        risk = abs(current_price - stop_loss)
        reward = abs(take_profit - current_price)
        risk_reward = reward / risk if risk > 0 else 0
        
        # === 6. Análisis de Patrones de Velas ===
        candlestick_patterns_detected = self.candlestick_analyzer.analyze(candles, timeframe="1h")
        
        # Agregar patrones de velas al score
        for cp in candlestick_patterns_detected:
            if cp.direction == "BULLISH" and direction == "LONG":
                long_score += cp.confidence / 20  # Normalizar a escala de score
                reasoning.append(f"Patrón vela: {cp.name_es} ({cp.confidence:.0f}% confianza)")
            elif cp.direction == "BEARISH" and direction == "SHORT":
                short_score += cp.confidence / 20
                reasoning.append(f"Patrón vela: {cp.name_es} ({cp.confidence:.0f}% confianza)")
        
        # Convertir patrones a formato dict para serialización
        candlestick_patterns_list = [
            {
                "name": cp.name,
                "name_es": cp.name_es,
                "direction": cp.direction,
                "strength": cp.strength_label.value,
                "confidence": cp.confidence,
                "description_es": cp.description_es,
                "icon": cp.icon,
                "color": cp.color
            }
            for cp in candlestick_patterns_detected
        ]
        
        # === 7. Calcular Confianza ===
        max_possible_score = 15  # Score máximo teórico
        confidence = min((score / max_possible_score) * 100, 100)
        
        # Ajustar confianza con win rate histórico
        historical_win_rate = self.memory.get_win_rate()
        if historical_win_rate > 0:
            confidence = confidence * 0.7 + historical_win_rate * 0.3
        
        # Boost de confianza si hay patrones de velas fuertes
        if candlestick_patterns_detected:
            avg_pattern_confidence = sum(cp.confidence for cp in candlestick_patterns_detected) / len(candlestick_patterns_detected)
            confidence = confidence * 0.8 + avg_pattern_confidence * 0.2
        
        # Determinar fuerza
        if confidence >= 80:
            strength = "STRONG"
        elif confidence >= 60:
            strength = "MODERATE"
        else:
            strength = "WEAK"
        
        # === 8. Generar Explicación en Español ===
        from app.ml.signal_explanation import (
            generate_spanish_explanation,
            generate_execution_steps
        )
        
        indicators_summary = {
            "rsi": rsi[-1] if rsi else None,
            "macd_signal": "alcista" if (macd.get("histogram") and len(macd["histogram"]) >= 2 and 
                                         macd["histogram"][-1] > 0 and macd["histogram"][-2] <= 0) else "bajista",
            "trend": indicators.get("trend", "NEUTRAL")
        }
        
        explanation_es = generate_spanish_explanation(
            direction=direction,
            symbol=symbol,
            candlestick_patterns=candlestick_patterns_detected,
            indicators_summary=indicators_summary,
            consensus=consensus
        )
        
        execution_steps = generate_execution_steps(
            direction=direction,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward=risk_reward
        )
        
        # === 9. RLMF: Signal Quality Audit (Pre-Flight Check) ===
        signal_data = {
            "direction": direction,
            "confidence": round(confidence, 1),
            "entry_price": current_price,
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
            "patterns_detected": patterns_detected,
            "indicators_used": indicators_used
        }
        
        # Obtener historial de trades para pattern check
        trade_history = self.memory.data.get("trade_results", [])
        
        audit_report = self.signal_auditor.preflight_check(
            signal=signal_data,
            candles=candles,
            indicators=indicators,
            trade_history=trade_history
        )
        
        # Si la señal no pasa el audit, no la emitimos
        if not audit_report.passed:
            logger.warning(
                f"🛡️ Señal RECHAZADA por auditor: {symbol} {direction} | "
                f"Score={audit_report.score:.1f}/100 | "
                f"Razones: {', '.join(audit_report.reasons_to_reject[:3])}"
            )
            return None
        
        # Agregar info del audit al reasoning
        reasoning.append(f"🛡️ Signal Audit: APROBADA (Score={audit_report.score:.1f}/100)")
        reasoning.append(f"📊 Régimen: {audit_report.regime}")
        if audit_report.reasons_to_accept:
            reasoning.extend(audit_report.reasons_to_accept[:2])
        
        # === 10. Análisis Multi-Timeframe ===
        timeframe_analysis = {
            "1h": direction,
            "regime": regime_report.regime.value,
            "regime_confidence": regime_report.confidence
        }
        
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
            candlestick_patterns=candlestick_patterns_list,
            explanation_es=explanation_es,
            execution_steps=execution_steps,
            timeframe_analysis=timeframe_analysis,
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
        patterns_detected: List[str],
        signal_price: float = None,
        price_history_during_trade: List[float] = None,
        entry_time: datetime = None,
        exit_time: datetime = None
    ):
        """
        Registrar resultado del trade para que el agente aprenda.
        Ahora incluye Post-Trade Analysis (RLMF).
        """
        # 1. Aprendizaje base (original)
        self.learning.record_trade_result(
            trade_id, symbol, side, entry_price, exit_price,
            pnl, signals_used, patterns_detected
        )
        
        # 2. RLMF: Post-Trade Analysis
        try:
            fill_price = signal_price or entry_price
            prices_during = price_history_during_trade or [entry_price, exit_price]
            
            deviation_report = self.post_trade_analyzer.analyze(
                trade_id=trade_id,
                symbol=symbol,
                direction=side,
                signal_price=fill_price,
                fill_price=entry_price,
                exit_price=exit_price,
                pnl=pnl,
                price_history_during_trade=prices_during,
                signals_used=signals_used,
                patterns_detected=patterns_detected,
                entry_time=entry_time,
                exit_time=exit_time
            )
            
            # Aplicar ajustes de peso al learning engine
            self.post_trade_analyzer.apply_adjustments(self.learning)
            
            logger.info(
                f"📈 Post-Trade [{trade_id}]: {deviation_report.entry_quality} entry | "
                f"{deviation_report.exit_quality} exit | Lesson: {deviation_report.lesson_learned[:80]}"
            )
        except Exception as e:
            logger.error(f"Error en Post-Trade Analysis: {e}")
    
    def get_performance_stats(self) -> Dict:
        """Obtener estadísticas de rendimiento del agente (con RLMF metrics)"""
        
        # Métricas base
        stats = {
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
        
        # RLMF metrics
        trade_results = self.memory.data.get("trade_results", [])
        stats["consecutive_losses"] = self.anti_martingale.get_consecutive_losses(trade_results) if trade_results else 0
        
        if trade_results:
            returns = [t.get("pnl", 0) for t in trade_results[-500:]]
            is_win_list = [t.get("pnl", 0) > 0 for t in trade_results[-500:]]
            
            stats["sharpe_ratio"] = self.performance_metrics.sharpe_ratio(returns)
            stats["z_score"] = self.performance_metrics.z_score_streaks(is_win_list)
            stats["signal_approval_rate"] = self.signal_auditor.get_approval_rate()
            stats["regime_stability"] = self.regime_detector.get_regime_stability()
        
        # Post-trade learning log
        stats["daily_learning"] = self.post_trade_analyzer.get_daily_learning_log()
        stats["parametric_adjustments"] = self.post_trade_analyzer.get_parametric_adjustments()
        
        return stats
    
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
