"""
SIC Ultra — RLMF Stress Test
Injects 1000 trades to verify PostTradeAnalyzer REALLY adjusts weights.

PURPOSE: Prove the feedback loop is NOT cosmetic.
If weights don't change after 1000 trades, the RLMF is broken.
"""

import pytest
import random
import sys
import os
from copy import deepcopy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ml.post_trade_analyzer import PostTradeAnalyzer
from app.ml.risk_engine import PerformanceMetrics


class TestRLMFStress:
    """Stress test: 1000 trade injections."""
    
    def test_1000_trades_adjust_weights(self):
        """
        CRITICAL TEST: After 1000 trades, the PostTradeAnalyzer
        must produce non-zero weight adjustments for the strategies used.
        
        If this test fails, the RLMF learning loop is cosmetic.
        """
        # Arrange
        analyzer = PostTradeAnalyzer()
        signals_pool = ["rsi", "macd", "bollinger", "trend", "top_trader_signals"]
        
        total_adjustments = {}
        
        # Act — Inject 1000 trades with realistic parameters
        for i in range(1000):
            is_winner = random.random() < 0.55  # Slight edge
            pnl = random.uniform(50, 300) if is_winner else -random.uniform(50, 250)
            
            slippage_factor = random.uniform(0.0001, 0.01)
            entry_price = 50000
            signal_price = entry_price * (1 - slippage_factor)
            fill_price = entry_price
            exit_price = entry_price + pnl if pnl > 0 else entry_price + pnl
            
            # Generate realistic price history during trade
            prices = [fill_price]
            for _ in range(random.randint(5, 20)):
                prices.append(prices[-1] * (1 + random.uniform(-0.005, 0.005)))
            prices.append(exit_price)
            
            signals_used = random.sample(signals_pool, k=random.randint(1, 3))
            
            report = analyzer.analyze(
                trade_id=f"STRESS_{i:04d}",
                symbol=random.choice(["BTCUSDT", "ETHUSDT", "SOLUSDT"]),
                direction=random.choice(["LONG", "SHORT"]),
                signal_price=signal_price,
                fill_price=fill_price,
                exit_price=exit_price,
                pnl=pnl,
                price_history_during_trade=prices,
                signals_used=signals_used,
                patterns_detected=[]
            )
            
            # Accumulate weight adjustments
            for strategy, adj in report.weight_adjustments.items():
                total_adjustments[strategy] = total_adjustments.get(strategy, 0) + adj
        
        # Assert — Weights MUST have changed
        assert len(total_adjustments) > 0, (
            "After 1000 trades, there should be weight adjustments"
        )
        
        # At least some strategies should have meaningful cumulative adjustments
        significant_changes = {
            k: v for k, v in total_adjustments.items() if abs(v) > 0.5
        }
        assert len(significant_changes) > 0, (
            f"After 1000 trades, at least some strategies should have significant "
            f"cumulative adjustments (>0.5). Got: {total_adjustments}"
        )
    
    def test_slippage_distribution_realistic(self):
        """After many trades, slippage stats should be calculable."""
        # Arrange
        analyzer = PostTradeAnalyzer()
        
        # Act — 200 trades
        for i in range(200):
            slippage = random.uniform(0.0001, 0.005)
            entry = 50000
            report = analyzer.analyze(
                trade_id=f"SLIP_{i:04d}", symbol="BTCUSDT", direction="LONG",
                signal_price=entry, fill_price=entry * (1 + slippage),
                exit_price=entry * 1.02, pnl=1000,
                price_history_during_trade=[entry * (1 + slippage), entry * 1.02],
                signals_used=["rsi"], patterns_detected=[]
            )
        
        # Assert
        adjustments = analyzer.get_parametric_adjustments()
        assert adjustments["status"] != "Insuficientes trades para ajustes"
        assert "metrics" in adjustments
        assert adjustments["metrics"]["avg_slippage"] > 0
    
    def test_losing_streak_increases_risk_awareness(self):
        """10 consecutive losses should trigger parameter adjustment suggestions."""
        # Arrange
        analyzer = PostTradeAnalyzer()
        
        # Act — 10 losses then check
        for i in range(10):
            analyzer.analyze(
                trade_id=f"LSTREAK_{i}", symbol="BTCUSDT", direction="LONG",
                signal_price=50000, fill_price=50050,
                exit_price=48000, pnl=-2050,
                price_history_during_trade=[50050, 49000, 48500, 48000],
                signals_used=["macd", "rsi"], patterns_detected=[]
            )
        
        # Assert — Daily log should show pattern
        log = analyzer.get_daily_learning_log()
        assert log["lessons_count"] >= 10
        assert len(log["losing_lessons"]) >= 10
    
    def test_efficiency_improves_with_better_exits(self):
        """Perfect exits (close at MFE) should show high efficiency."""
        analyzer = PostTradeAnalyzer()
        
        # Trade where we capture ALL the move
        report = analyzer.analyze(
            trade_id="PERFECT", symbol="BTCUSDT", direction="LONG",
            signal_price=50000, fill_price=50000, exit_price=52000,
            pnl=2000,
            price_history_during_trade=[50000, 50500, 51000, 51500, 52000],
            signals_used=["rsi"], patterns_detected=[]
        )
        
        assert report.efficiency_ratio > 0.8, (
            f"Perfect exit should have >80% efficiency, got {report.efficiency_ratio:.2%}"
        )
    
    def test_sharpe_and_zscore_after_bulk(self):
        """After bulk trades, Sharpe and Z-Score must be computable."""
        metrics = PerformanceMetrics()
        
        random.seed(42)
        returns = [random.uniform(-0.03, 0.04) for _ in range(500)]
        
        sharpe = metrics.sharpe_ratio(returns)
        assert isinstance(sharpe, float)
        
        is_win = [r > 0 for r in returns]
        z = metrics.z_score_streaks(is_win)
        assert isinstance(z, float)
