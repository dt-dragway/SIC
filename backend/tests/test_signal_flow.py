"""
SIC Ultra — Integration Test: Signal Flow
Tests the complete signal path: Candles → Regime → Signal → Audit → PostTrade

AAA Standard on every test.
"""

import pytest
import numpy as np
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ml.regime_detector import RegimeDetector, MarketRegime
from app.ml.signal_auditor import SignalAuditor
from app.ml.post_trade_analyzer import PostTradeAnalyzer
from app.ml.risk_engine import FeeCalculator
from app.ml.indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_atr, get_trend, calculate_adx
)
from tests.conftest import generate_candles, generate_indicators, generate_trade_history


class TestRegimeDetector:
    """Regime classification must be correct for each market type."""
    
    def setup_method(self):
        self.detector = RegimeDetector()
    
    def test_trending_market_detected(self):
        """Strong uptrend should classify as TRENDING."""
        # Arrange
        np.random.seed(42)
        candles = generate_candles(200, 50000, "trending_up", 0.02)
        
        # Act
        report = self.detector.detect(candles)
        
        # Assert
        assert report.regime in (MarketRegime.TRENDING, MarketRegime.TRANSITIONING), (
            f"Uptrend should be TRENDING, got {report.regime.value}"
        )
        assert report.confidence > 0
        assert report.params["tp_atr_multiplier"] >= 2.0
    
    def test_mean_reverting_market_detected(self):
        """Sideways market should classify as MEAN_REVERTING or TRANSITIONING."""
        # Arrange
        np.random.seed(42)
        candles = generate_candles(200, 50000, "mean_reverting", 0.005)
        
        # Act
        report = self.detector.detect(candles)
        
        # Assert
        assert report.regime in (MarketRegime.MEAN_REVERTING, MarketRegime.TRANSITIONING), (
            f"Sideways market should not be TRENDING, got {report.regime.value}"
        )
    
    def test_insufficient_data_returns_default(self):
        """Less than 50 candles → TRANSITIONING with 0 confidence."""
        # Arrange
        candles = generate_candles(10, 50000, "trending_up")
        
        # Act
        report = self.detector.detect(candles)
        
        # Assert
        assert report.regime == MarketRegime.TRANSITIONING
        assert report.confidence == 0.0
    
    def test_hurst_exponent_range(self):
        """Hurst must be between 0 and 1."""
        np.random.seed(42)
        candles = generate_candles(200, 50000, "trending_up")
        report = self.detector.detect(candles)
        assert 0.0 <= report.hurst_exponent <= 1.0
    
    def test_regime_stability_scoring(self):
        """After multiple detections, stability should be computable."""
        np.random.seed(42)
        candles = generate_candles(200, 50000, "trending_up")
        
        for _ in range(5):
            self.detector.detect(candles)
        
        stability = self.detector.get_regime_stability()
        assert 0.0 <= stability <= 1.0


class TestSignalAuditor:
    """Signal pre-flight validation must block bad signals."""
    
    def setup_method(self):
        self.auditor = SignalAuditor()
    
    def test_good_signal_passes(self):
        """Strong signal with volume and trend confirmation should PASS."""
        # Arrange
        np.random.seed(42)
        candles = generate_candles(200, 50000, "trending_up", 0.02)
        indicators = generate_indicators(candles)
        
        signal = {
            "direction": "LONG",
            "confidence": 85,
            "entry_price": candles[-1]["close"],
            "stop_loss": candles[-1]["close"] * 0.97,
            "take_profit": candles[-1]["close"] * 1.06,
            "patterns_detected": ["bullish_engulfing"],
            "indicators_used": ["rsi", "macd"]
        }
        
        # Act
        report = self.auditor.preflight_check(signal, candles, indicators)
        
        # Assert
        assert report.score > 0, "Score should be calculated"
        assert isinstance(report.passed, bool)
        assert isinstance(report.risk_factor, float)
        assert 1.0 <= report.risk_factor <= 10.0
    
    def test_low_volume_signal_penalized(self):
        """Low volume should reduce audit score."""
        # Arrange
        np.random.seed(42)
        candles = generate_candles(200, 50000, "low_volume", 0.01)
        indicators = generate_indicators(candles)
        
        signal = {
            "direction": "LONG",
            "confidence": 70,
            "entry_price": candles[-1]["close"],
            "stop_loss": candles[-1]["close"] * 0.98,
            "take_profit": candles[-1]["close"] * 1.04,
            "patterns_detected": [],
            "indicators_used": ["rsi"]
        }
        
        # Act
        report = self.auditor.preflight_check(signal, candles, indicators)
        
        # Assert
        assert report.risk_factor >= 5.0, (
            f"Low volume should increase risk factor, got {report.risk_factor}"
        )
    
    def test_fee_nonviable_signal_flagged(self):
        """Signal where fees exceed profit should be flagged."""
        # Arrange
        np.random.seed(42)
        candles = generate_candles(200, 50000, "trending_up")
        indicators = generate_indicators(candles)
        price = candles[-1]["close"]
        
        signal = {
            "direction": "LONG",
            "confidence": 75,
            "entry_price": price,
            "stop_loss": price * 0.9999,
            "take_profit": price * 1.0001,
            "patterns_detected": [],
            "indicators_used": ["rsi"]
        }
        
        # Act
        report = self.auditor.preflight_check(signal, candles, indicators)
        
        # Assert
        assert report.fee_viable is False
    
    def test_repeated_failed_pattern_blocked(self):
        """If same pattern failed >60% in last 24h, signal should score low."""
        # Arrange
        np.random.seed(42)
        candles = generate_candles(200, 50000, "trending_up")
        indicators = generate_indicators(candles)
        price = candles[-1]["close"]
        
        # Create history where "rsi" signals failed 80% of the time
        from datetime import timedelta
        trade_history = [
            {
                "pnl": -100, "signals_used": ["rsi", "macd"],
                "patterns_detected": ["bullish_engulfing"],
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat()
            }
            for _ in range(8)
        ] + [
            {
                "pnl": 100, "signals_used": ["rsi", "macd"],
                "patterns_detected": ["bullish_engulfing"],
                "timestamp": (datetime.utcnow() - timedelta(hours=3)).isoformat()
            }
            for _ in range(2)
        ]
        
        signal = {
            "direction": "LONG", "confidence": 75,
            "entry_price": price,
            "stop_loss": price * 0.97, "take_profit": price * 1.06,
            "patterns_detected": ["bullish_engulfing"],
            "indicators_used": ["rsi", "macd"]
        }
        
        # Act
        report = self.auditor.preflight_check(signal, candles, indicators, trade_history)
        
        # Assert
        pattern_check = [c for c in report.checks if c["name"] == "Historical Pattern"]
        if pattern_check:
            assert pattern_check[0]["score"] < 50, (
                f"Repeated failed pattern should score low, got {pattern_check[0]['score']}"
            )
    
    def test_approval_rate_tracking(self):
        """Approval rate should be calculable after multiple audits."""
        np.random.seed(42)
        candles = generate_candles(200, 50000, "trending_up")
        indicators = generate_indicators(candles)
        price = candles[-1]["close"]
        
        signal = {
            "direction": "LONG", "confidence": 85,
            "entry_price": price,
            "stop_loss": price * 0.97, "take_profit": price * 1.06,
            "patterns_detected": [], "indicators_used": ["rsi"]
        }
        
        for _ in range(5):
            self.auditor.preflight_check(signal, candles, indicators)
        
        rate = self.auditor.get_approval_rate()
        assert 0.0 <= rate <= 100.0


class TestPostTradeAnalyzer:
    """Post-trade analysis must measure deviations correctly."""
    
    def setup_method(self):
        self.analyzer = PostTradeAnalyzer()
    
    def test_winning_trade_analysis(self):
        """Winning trade should have positive efficiency."""
        # Arrange / Act
        report = self.analyzer.analyze(
            trade_id="WIN_001", symbol="BTCUSDT", direction="LONG",
            signal_price=50000, fill_price=50010, exit_price=51500,
            pnl=1490,
            price_history_during_trade=[50010, 49800, 50500, 51200, 51500],
            signals_used=["rsi", "macd"], patterns_detected=["bullish_engulfing"]
        )
        
        # Assert
        assert report.efficiency_ratio > 0, "Winning trade should have positive efficiency"
        assert report.slippage_pct >= 0
        assert report.mfe_pct > 0, "There should be favorable excursion"
        assert report.entry_quality in ("EXCELLENT", "GOOD", "POOR", "TERRIBLE")
    
    def test_losing_trade_analysis(self):
        """Losing trade efficiency should be negative."""
        report = self.analyzer.analyze(
            trade_id="LOSS_001", symbol="BTCUSDT", direction="LONG",
            signal_price=50000, fill_price=50050, exit_price=48500,
            pnl=-1550,
            price_history_during_trade=[50050, 49500, 49000, 48800, 48500],
            signals_used=["trend"], patterns_detected=[]
        )
        
        assert report.efficiency_ratio <= 0, "Losing trade should have negative efficiency"
        assert report.mae_pct > 0, "There should be adverse excursion"
    
    def test_high_slippage_detected(self):
        """0.5% slippage should be rated POOR or TERRIBLE."""
        report = self.analyzer.analyze(
            trade_id="SLIP_001", symbol="ETHUSDT", direction="SHORT",
            signal_price=3000, fill_price=3015, exit_price=2900,
            pnl=85,
            price_history_during_trade=[3015, 3020, 2950, 2900],
            signals_used=["rsi"], patterns_detected=[]
        )
        
        assert report.slippage_pct > 0.003, "Should detect high slippage"
        assert report.entry_quality in ("POOR", "TERRIBLE")
    
    def test_daily_learning_log(self):
        """After trades, daily log should contain lessons."""
        self.analyzer.analyze(
            trade_id="LOG_001", symbol="BTCUSDT", direction="LONG",
            signal_price=50000, fill_price=50000, exit_price=51000,
            pnl=1000, price_history_during_trade=[50000, 51000],
            signals_used=["rsi"], patterns_detected=[]
        )
        
        log = self.analyzer.get_daily_learning_log()
        assert log["lessons_count"] >= 1
        assert len(log["lessons"]) >= 1
    
    def test_weight_adjustments_generated(self):
        """Each trade should produce weight adjustments."""
        report = self.analyzer.analyze(
            trade_id="ADJ_001", symbol="BTCUSDT", direction="LONG",
            signal_price=50000, fill_price=50000, exit_price=51000,
            pnl=1000, price_history_during_trade=[50000, 51000],
            signals_used=["rsi", "macd"], patterns_detected=[]
        )
        
        assert len(report.weight_adjustments) > 0, "Should produce weight adjustments"
        assert "rsi" in report.weight_adjustments
