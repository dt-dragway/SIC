"""
SIC Ultra — Edge Case Tests
What happens when the real world breaks your assumptions.

Tests: None responses, empty data, extreme values, negative prices.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ml.regime_detector import RegimeDetector, MarketRegime
from app.ml.signal_auditor import SignalAuditor
from app.ml.post_trade_analyzer import PostTradeAnalyzer
from app.ml.risk_engine import DynamicKellyEngine, FeeCalculator, PerformanceMetrics
from tests.conftest import generate_candles


class TestEdgeCasesRegimeDetector:
    """RegimeDetector must not crash on garbage input."""
    
    def setup_method(self):
        self.detector = RegimeDetector()
    
    def test_empty_candles(self):
        report = self.detector.detect([])
        assert report.regime == MarketRegime.TRANSITIONING
        assert report.confidence == 0.0
    
    def test_single_candle(self):
        candle = [{"open": 100, "high": 110, "low": 90, "close": 105, "volume": 50}]
        report = self.detector.detect(candle)
        assert report.regime == MarketRegime.TRANSITIONING
    
    def test_all_same_price(self):
        """Flat market — all candles identical."""
        candles = [
            {"open": 50000, "high": 50000, "low": 50000, "close": 50000, "volume": 100}
            for _ in range(200)
        ]
        report = self.detector.detect(candles)
        # Should not crash; regime should be mean-reverting or transitioning
        assert report.regime in (MarketRegime.MEAN_REVERTING, MarketRegime.TRANSITIONING)
    
    def test_zero_volume_candles(self):
        """All volumes zero — should not crash."""
        candles = [
            {"open": 50000 + i, "high": 50050 + i, "low": 49950 + i,
             "close": 50010 + i, "volume": 0}
            for i in range(200)
        ]
        report = self.detector.detect(candles)
        assert report.regime is not None
    
    def test_negative_prices_handled(self):
        """Negative prices (corrupted data) — should not crash."""
        candles = [
            {"open": -100, "high": -50, "low": -200, "close": -150, "volume": 100}
            for _ in range(200)
        ]
        # Should not raise, just give some result
        report = self.detector.detect(candles)
        assert report is not None


class TestEdgeCasesRiskEngine:
    """Risk engine must handle all edge cases without crashing."""
    
    def setup_method(self):
        self.kelly = DynamicKellyEngine()
    
    def test_negative_capital(self):
        result = self.kelly.calculate_position_size(-5000, 65, 150, 100, 80)
        assert result.position_size_usd >= 0
    
    def test_win_rate_over_100(self):
        """Invalid win rate should be clamped."""
        result = self.kelly.calculate_position_size(10000, 150, 150, 100, 80)
        assert result.position_size_usd >= 0
    
    def test_extreme_confidence(self):
        """0% and 100% confidence should not crash."""
        r0 = self.kelly.calculate_position_size(10000, 65, 150, 100, 0)
        r100 = self.kelly.calculate_position_size(10000, 65, 150, 100, 100)
        assert r0.position_size_usd >= 0
        assert r100.position_size_usd >= 0
    
    def test_fee_calculator_zero_price(self):
        """Zero entry price — division by zero guard."""
        result = FeeCalculator.adjust_targets(0, 0, 0)
        # Should not crash
        assert result is not None
    
    def test_sharpe_all_same_returns(self):
        """All identical returns → 0 std → handle gracefully."""
        metrics = PerformanceMetrics()
        sharpe = metrics.sharpe_ratio([0.01, 0.01, 0.01, 0.01])
        assert sharpe == 0.0  # Zero std → zero Sharpe
    
    def test_zscore_all_wins(self):
        """All wins → 0 losses → should return 0."""
        metrics = PerformanceMetrics()
        z = metrics.z_score_streaks([True] * 50)
        assert z == 0.0


class TestEdgeCasesPostTradeAnalyzer:
    """PostTradeAnalyzer must not crash on garbage trade data."""
    
    def setup_method(self):
        self.analyzer = PostTradeAnalyzer()
    
    def test_zero_prices(self):
        report = self.analyzer.analyze(
            trade_id="ZERO", symbol="BTCUSDT", direction="LONG",
            signal_price=0, fill_price=0, exit_price=0,
            pnl=0, price_history_during_trade=[],
            signals_used=[], patterns_detected=[]
        )
        assert report is not None
    
    def test_empty_price_history(self):
        report = self.analyzer.analyze(
            trade_id="EMPTY", symbol="ETHUSDT", direction="SHORT",
            signal_price=3000, fill_price=3000, exit_price=2900,
            pnl=100, price_history_during_trade=[],
            signals_used=["rsi"], patterns_detected=[]
        )
        assert report.mae_pct == 0.0
        assert report.mfe_pct == 0.0
    
    def test_parametric_adjustments_insufficient_data(self):
        """With <5 trades, should return 'insufficient'."""
        result = self.analyzer.get_parametric_adjustments()
        assert "Insuficientes" in result["status"]


class TestEdgeCasesSignalAuditor:
    """SignalAuditor must handle corrupted signals gracefully."""
    
    def setup_method(self):
        self.auditor = SignalAuditor()
    
    def test_empty_signal(self):
        import numpy as np
        np.random.seed(42)
        candles = generate_candles(200, 50000, "trending_up")
        from tests.conftest import generate_indicators
        indicators = generate_indicators(candles)
        
        signal = {}  # Empty signal
        report = self.auditor.preflight_check(signal, candles, indicators)
        assert report is not None
    
    def test_insufficient_candles(self):
        signal = {"direction": "LONG", "confidence": 80,
                  "entry_price": 50000, "stop_loss": 49000, "take_profit": 52000}
        report = self.auditor.preflight_check(signal, [], {})
        assert report.passed is False
        assert report.score == 0
