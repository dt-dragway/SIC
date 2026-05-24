"""
SIC Ultra — Risk Engine Unit Tests
AAA Standard: Arrange → Act → Assert

Tests Kelly Criterion, Sharpe Ratio, Z-Score, Anti-Martingale, Fee Calculator.
"""

import pytest
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ml.risk_engine import (
    DynamicKellyEngine, AntiMartingaleGuard, FeeCalculator, PerformanceMetrics
)


class TestDynamicKellyEngine:
    """Unit tests for Kelly Criterion position sizing."""
    
    def setup_method(self):
        self.kelly = DynamicKellyEngine()
    
    # --- Happy Path ---
    
    def test_kelly_profitable_strategy(self):
        """A strategy with 65% win rate and 1.5:1 W/L should produce positive Kelly."""
        # Arrange
        capital = 10000
        win_rate = 65
        avg_win = 150
        avg_loss = 100
        confidence = 80
        
        # Act
        result = self.kelly.calculate_position_size(
            capital, win_rate, avg_win, avg_loss, confidence
        )
        
        # Assert
        assert result.position_size_usd > 0, "Profitable strategy should have positive position"
        assert result.kelly_raw > 0, "Kelly raw should be positive for profitable strategy"
        assert result.fraction_of_capital <= 0.02, "Should never exceed 2% risk"
        assert result.fraction_of_capital > 0, "Should allocate something"
    
    def test_kelly_losing_strategy_returns_zero(self):
        """A strategy with 30% win rate and 0.5:1 W/L should return 0."""
        # Arrange
        capital = 10000
        win_rate = 30
        avg_win = 50
        avg_loss = 100
        confidence = 80
        
        # Act
        result = self.kelly.calculate_position_size(
            capital, win_rate, avg_win, avg_loss, confidence
        )
        
        # Assert
        assert result.position_size_usd == 0.0, "Losing strategy should NOT allocate capital"
        assert result.kelly_raw <= 0, "Kelly should be negative for losing strategy"
        assert "NO OPERAR" in result.reasoning
    
    def test_kelly_half_kelly_applied(self):
        """Half-Kelly should always be less than full Kelly."""
        # Arrange
        capital = 100000
        win_rate = 70
        avg_win = 200
        avg_loss = 100
        confidence = 100  # Max confidence
        
        # Act
        result = self.kelly.calculate_position_size(
            capital, win_rate, avg_win, avg_loss, confidence
        )
        
        # Assert
        assert result.kelly_adjusted <= result.kelly_raw, "Adjusted should be ≤ raw Kelly"
        assert result.kelly_adjusted > 0, "Should be positive for profitable strategy"
    
    def test_kelly_max_risk_cap(self):
        """Position should NEVER exceed max_risk_pct regardless of Kelly."""
        # Arrange — Extremely profitable strategy
        capital = 100000
        win_rate = 95
        avg_win = 500
        avg_loss = 50
        confidence = 100
        max_risk = 0.02
        
        # Act
        result = self.kelly.calculate_position_size(
            capital, win_rate, avg_win, avg_loss, confidence, max_risk_pct=max_risk
        )
        
        # Assert
        assert result.fraction_of_capital <= max_risk, (
            f"Fraction {result.fraction_of_capital} exceeds max {max_risk}"
        )
        assert result.position_size_usd <= capital * max_risk
    
    def test_kelly_confidence_scales_position(self):
        """Higher confidence → larger position."""
        # Arrange — use low win_rate so Kelly stays below 2% cap
        capital = 10000
        win_rate = 52
        avg_win = 110
        avg_loss = 100
        
        # Act
        low_conf = self.kelly.calculate_position_size(capital, win_rate, avg_win, avg_loss, 30)
        high_conf = self.kelly.calculate_position_size(capital, win_rate, avg_win, avg_loss, 90)
        
        # Assert
        assert high_conf.position_size_usd >= low_conf.position_size_usd, (
            "High confidence should produce larger or equal position than low confidence"
        )
    
    # --- Anti-Martingale Integration ---
    
    def test_kelly_reduces_after_2_losses(self):
        """Position must shrink after 2 consecutive losses."""
        # Arrange — use low win_rate so Kelly stays below 2% cap
        capital = 10000
        params = dict(win_rate=52, avg_win=110, avg_loss=100, signal_confidence=80)
        
        # Act
        normal = self.kelly.calculate_position_size(capital, **params, consecutive_losses=0)
        after_2 = self.kelly.calculate_position_size(capital, **params, consecutive_losses=2)
        
        # Assert
        assert after_2.kelly_adjusted < normal.kelly_adjusted, (
            "2 losses must reduce kelly_adjusted value"
        )
        assert after_2.anti_martingale_applied is True
    
    def test_kelly_severe_reduction_after_5_losses(self):
        """5+ losses → kelly_adjusted drops significantly."""
        # Arrange — use low win_rate so Kelly stays below 2% cap
        capital = 10000
        params = dict(win_rate=52, avg_win=110, avg_loss=100, signal_confidence=80)
        
        # Act
        normal = self.kelly.calculate_position_size(capital, **params, consecutive_losses=0)
        after_5 = self.kelly.calculate_position_size(capital, **params, consecutive_losses=5)
        
        # Assert — kelly_adjusted must drop drastically
        if normal.kelly_adjusted > 0 and after_5.kelly_adjusted > 0:
            ratio = after_5.kelly_adjusted / normal.kelly_adjusted
            assert ratio < 0.3, f"After 5 losses, kelly_adjusted should be <30% of normal, got {ratio:.2%}"
        assert after_5.anti_martingale_applied is True
    
    # --- Edge Cases ---
    
    def test_kelly_zero_capital(self):
        """Zero capital → zero position."""
        result = self.kelly.calculate_position_size(0, 65, 150, 100, 80)
        assert result.position_size_usd >= 0
    
    def test_kelly_zero_avg_loss(self):
        """Zero avg_loss → conservative fallback."""
        result = self.kelly.calculate_position_size(10000, 65, 150, 0, 80)
        assert result.position_size_usd >= 0  # Should not crash
    
    def test_kelly_zero_avg_win(self):
        """Zero avg_win → conservative fallback."""
        result = self.kelly.calculate_position_size(10000, 65, 0, 100, 80)
        assert result.position_size_usd >= 0


class TestAntiMartingaleGuard:
    """Tests for the Martingale detection and prevention system."""
    
    def test_consecutive_losses_count(self):
        # Arrange
        trades = [{"pnl": 100}, {"pnl": -50}, {"pnl": -30}, {"pnl": -20}]
        
        # Act
        losses = AntiMartingaleGuard.get_consecutive_losses(trades)
        
        # Assert
        assert losses == 3
    
    def test_consecutive_losses_after_win(self):
        # Arrange
        trades = [{"pnl": -50}, {"pnl": -30}, {"pnl": 100}, {"pnl": -20}]
        
        # Act
        losses = AntiMartingaleGuard.get_consecutive_losses(trades)
        
        # Assert
        assert losses == 1, "Should only count from the end"
    
    def test_no_losses(self):
        trades = [{"pnl": 100}, {"pnl": 50}, {"pnl": 200}]
        assert AntiMartingaleGuard.get_consecutive_losses(trades) == 0
    
    def test_empty_history(self):
        assert AntiMartingaleGuard.get_consecutive_losses([]) == 0
    
    def test_martingale_detection_blocks(self):
        """Increasing size after losses MUST be detected."""
        assert AntiMartingaleGuard.is_martingale_attempt(200, 100, 3) is True
    
    def test_martingale_allows_decrease(self):
        """Decreasing size after losses is OK."""
        assert AntiMartingaleGuard.is_martingale_attempt(50, 100, 3) is False
    
    def test_size_reduction_tiers(self):
        """Verify correct reduction multipliers for each tier."""
        _, mult_2 = AntiMartingaleGuard.should_reduce_size(2)
        _, mult_3 = AntiMartingaleGuard.should_reduce_size(3)
        _, mult_5 = AntiMartingaleGuard.should_reduce_size(5)
        
        assert mult_2 == 0.5, "2 losses → 50%"
        assert mult_3 == 0.25, "3 losses → 25%"
        assert mult_5 == 0.1, "5 losses → 10%"


class TestFeeCalculator:
    """Tests for fee-adjusted target validation."""
    
    def test_viable_trade(self):
        """BTC trade with 2% TP should be viable."""
        # Arrange / Act
        result = FeeCalculator.adjust_targets(50000, 49000, 52000)
        
        # Assert
        assert result.viable is True
        assert result.net_profit_pct > 0
        assert result.risk_reward >= 1.0
    
    def test_tiny_trade_not_viable(self):
        """0.1% TP with 0.2% fees → NOT viable."""
        # Arrange / Act
        result = FeeCalculator.adjust_targets(50000, 49950, 50050)
        
        # Assert
        assert result.viable is False, "Tiny TP should be rejected — fees exceed profit"
    
    def test_short_trade_viable(self):
        """Short trade with adequate distance."""
        result = FeeCalculator.adjust_targets(50000, 51000, 48000)
        assert result.viable is True
        assert result.net_profit_pct > 0
    
    def test_fees_deducted_correctly(self):
        """Total fees should be 2 × fee_rate."""
        result = FeeCalculator.adjust_targets(50000, 49000, 52000, fee_rate=0.001)
        assert result.total_fees_pct == pytest.approx(0.002, abs=0.0001)
    
    def test_custom_fee_rate(self):
        """Custom fee rate should be applied."""
        low_fee = FeeCalculator.adjust_targets(50000, 49000, 52000, fee_rate=0.0005)
        high_fee = FeeCalculator.adjust_targets(50000, 49000, 52000, fee_rate=0.002)
        assert low_fee.net_profit_pct > high_fee.net_profit_pct


class TestPerformanceMetrics:
    """Tests for Sharpe Ratio, Z-Score, Profit Factor, Expectancy."""
    
    def setup_method(self):
        self.metrics = PerformanceMetrics()
    
    def test_sharpe_positive_returns(self):
        """Consistently positive returns → positive Sharpe."""
        returns = [0.02, 0.015, 0.01, 0.025, 0.018, 0.02, 0.012, 0.022]
        sharpe = self.metrics.sharpe_ratio(returns)
        assert sharpe > 0, f"Positive returns should produce positive Sharpe, got {sharpe}"
    
    def test_sharpe_negative_returns(self):
        """Consistently negative returns → negative Sharpe."""
        returns = [-0.02, -0.015, -0.01, -0.025, -0.018, -0.02]
        sharpe = self.metrics.sharpe_ratio(returns)
        assert sharpe < 0, f"Negative returns should produce negative Sharpe, got {sharpe}"
    
    def test_sharpe_insufficient_data(self):
        """Less than 2 returns → 0."""
        assert self.metrics.sharpe_ratio([0.01]) == 0.0
        assert self.metrics.sharpe_ratio([]) == 0.0
    
    def test_zscore_random_trades(self):
        """Truly random results should have |Z| close to 0."""
        import random
        random.seed(42)
        results = [random.random() > 0.5 for _ in range(1000)]
        z = self.metrics.z_score_streaks(results)
        assert abs(z) < 3.0, f"Random trades Z-Score should be near 0, got {z}"
    
    def test_zscore_perfect_alternating(self):
        """Perfect WLWLWL pattern → |Z| high (anti-persistent)."""
        results = [i % 2 == 0 for i in range(100)]
        z = self.metrics.z_score_streaks(results)
        assert abs(z) > 1.5, f"Perfect alternating should have high |Z|, got {z}"
    
    def test_zscore_insufficient_data(self):
        assert self.metrics.z_score_streaks([True, False]) == 0.0
    
    def test_profit_factor(self):
        assert self.metrics.profit_factor(1000, 500) == 2.0
        assert self.metrics.profit_factor(500, 1000) == 0.5
        assert self.metrics.profit_factor(100, 0) == float('inf')
    
    def test_expectancy_profitable(self):
        """60% win rate with 2:1 W/L → positive expectancy."""
        exp = self.metrics.expectancy(60, 200, 100)
        assert exp > 0, f"Should be profitable, got {exp}"
    
    def test_expectancy_losing(self):
        """30% win rate with 1:2 W/L → negative expectancy."""
        exp = self.metrics.expectancy(30, 50, 100)
        assert exp < 0, f"Should be losing, got {exp}"
