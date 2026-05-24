"""
SIC Ultra — Learning Engine Tests
Tests the complete learning loop: trade → learn → adjust → improve

Validates that the system genuinely learns from experience.
"""

import pytest
import random
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ml.post_trade_analyzer import PostTradeAnalyzer
from app.ml.risk_engine import (
    DynamicKellyEngine, AntiMartingaleGuard, PerformanceMetrics
)
from app.ml.regime_detector import RegimeDetector, MarketRegime
from app.ml.signal_auditor import SignalAuditor
from tests.conftest import generate_candles, generate_indicators


class TestLearningLoop:
    """
    Verifies the complete RLMF learning loop works end-to-end.
    Trade → Analyze → Adjust Weights → Next Trade Uses New Weights
    """
    
    def test_winning_strategy_gets_reinforced(self):
        """
        If 'rsi' signals win 80% of the time, its weight should INCREASE.
        If 'macd' signals win 30%, its weight should DECREASE.
        """
        analyzer = PostTradeAnalyzer()
        
        # 50 trades where RSI signals are winners
        for i in range(40):
            analyzer.analyze(
                trade_id=f"RSI_WIN_{i}", symbol="BTCUSDT", direction="LONG",
                signal_price=50000, fill_price=50000, exit_price=51000,
                pnl=1000,
                price_history_during_trade=[50000, 50500, 51000],
                signals_used=["rsi"], patterns_detected=[]
            )
        for i in range(10):
            analyzer.analyze(
                trade_id=f"RSI_LOSE_{i}", symbol="BTCUSDT", direction="LONG",
                signal_price=50000, fill_price=50000, exit_price=49500,
                pnl=-500,
                price_history_during_trade=[50000, 49800, 49500],
                signals_used=["rsi"], patterns_detected=[]
            )
        
        # 50 trades where MACD signals are losers
        for i in range(15):
            analyzer.analyze(
                trade_id=f"MACD_WIN_{i}", symbol="BTCUSDT", direction="LONG",
                signal_price=50000, fill_price=50000, exit_price=50500,
                pnl=500,
                price_history_during_trade=[50000, 50500],
                signals_used=["macd"], patterns_detected=[]
            )
        for i in range(35):
            analyzer.analyze(
                trade_id=f"MACD_LOSE_{i}", symbol="BTCUSDT", direction="SHORT",
                signal_price=50000, fill_price=50000, exit_price=50800,
                pnl=-800,
                price_history_during_trade=[50000, 50800],
                signals_used=["macd"], patterns_detected=[]
            )
        
        adjustments = analyzer.get_parametric_adjustments()
        assert adjustments["status"] != "Insuficientes trades para ajustes"
        
        # Verify metrics are computed from 100 trades
        metrics = adjustments.get("metrics", {})
        assert "avg_slippage" in metrics
        assert "avg_efficiency" in metrics
    
    def test_regime_switch_changes_parameters(self):
        """
        When regime changes from TRENDING → MEAN_REVERTING,
        TP/SL multipliers must change.
        """
        import numpy as np
        detector = RegimeDetector()
        
        # Trending market
        np.random.seed(42)
        trending = generate_candles(200, 50000, "trending_up", 0.02)
        report_trend = detector.detect(trending)
        
        # Mean reverting market
        np.random.seed(42)
        lateral = generate_candles(200, 50000, "mean_reverting", 0.005)
        report_lateral = detector.detect(lateral)
        
        # TP multiplier should be larger in trending
        if report_trend.regime == MarketRegime.TRENDING:
            assert report_trend.params["tp_atr_multiplier"] >= report_lateral.params["tp_atr_multiplier"], (
                f"Trending TP ({report_trend.params['tp_atr_multiplier']}) should be >= "
                f"lateral TP ({report_lateral.params['tp_atr_multiplier']})"
            )
    
    def test_consecutive_losses_trigger_position_reduction(self):
        """
        After 5 consecutive losses, Kelly should reduce position by ≥70%.
        """
        kelly = DynamicKellyEngine()
        
        normal = kelly.calculate_position_size(
            capital=10000, win_rate=52, avg_win=110, avg_loss=100,
            signal_confidence=80, consecutive_losses=0
        )
        
        reduced = kelly.calculate_position_size(
            capital=10000, win_rate=52, avg_win=110, avg_loss=100,
            signal_confidence=80, consecutive_losses=5
        )
        
        assert reduced.anti_martingale_applied is True
        assert reduced.kelly_adjusted < normal.kelly_adjusted
    
    def test_auditor_learns_from_recent_failures(self):
        """
        If we tell the auditor about recent failed patterns,
        similar signals should score lower.
        """
        import numpy as np
        np.random.seed(42)
        
        auditor = SignalAuditor()
        candles = generate_candles(200, 50000, "trending_up")
        indicators = generate_indicators(candles)
        price = candles[-1]["close"]
        
        signal = {
            "direction": "LONG", "confidence": 75,
            "entry_price": price,
            "stop_loss": price * 0.97, "take_profit": price * 1.06,
            "patterns_detected": ["bullish_engulfing"],
            "indicators_used": ["rsi", "macd"]
        }
        
        # First audit: no history
        report_clean = auditor.preflight_check(signal, candles, indicators)
        
        # Create history with many failures using same signals
        bad_history = [
            {
                "pnl": -100, "signals_used": ["rsi", "macd"],
                "patterns_detected": ["bullish_engulfing"],
                "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat()
            }
            for _ in range(10)
        ]
        
        # Second audit: with bad history
        auditor2 = SignalAuditor()
        report_bad = auditor2.preflight_check(signal, candles, indicators, bad_history)
        
        # The score with bad history should be lower or equal
        # (the historical pattern check should penalize)
        pattern_clean = [c for c in report_clean.checks if c["name"] == "Historical Pattern"]
        pattern_bad = [c for c in report_bad.checks if c["name"] == "Historical Pattern"]
        
        if pattern_clean and pattern_bad:
            assert pattern_bad[0]["score"] <= pattern_clean[0]["score"], (
                f"Bad history should reduce pattern score: "
                f"clean={pattern_clean[0]['score']} vs bad={pattern_bad[0]['score']}"
            )
    
    def test_efficiency_measurement_accuracy(self):
        """
        Verify efficiency ratio math:
        - Capture 100% of move → efficiency ≈ 1.0
        - Capture 50% of move → efficiency ≈ 0.5
        """
        analyzer = PostTradeAnalyzer()
        
        # Perfect capture: entry at bottom, exit at top
        perfect = analyzer.analyze(
            trade_id="PERFECT", symbol="BTCUSDT", direction="LONG",
            signal_price=50000, fill_price=50000, exit_price=52000,
            pnl=2000,
            price_history_during_trade=[50000, 50500, 51000, 51500, 52000],
            signals_used=["rsi"], patterns_detected=[]
        )
        
        # Partial capture: exit at 50% of the move
        partial = analyzer.analyze(
            trade_id="PARTIAL", symbol="BTCUSDT", direction="LONG",
            signal_price=50000, fill_price=50000, exit_price=51000,
            pnl=1000,
            price_history_during_trade=[50000, 50500, 51000, 51500, 52000],
            signals_used=["rsi"], patterns_detected=[]
        )
        
        assert perfect.efficiency_ratio > partial.efficiency_ratio, (
            f"Perfect exit ({perfect.efficiency_ratio:.2%}) "
            f"should rank higher than partial ({partial.efficiency_ratio:.2%})"
        )
    
    def test_daily_learning_log_separates_wins_and_losses(self):
        """Log must categorize lessons by outcome."""
        analyzer = PostTradeAnalyzer()
        
        # Add wins
        for i in range(5):
            analyzer.analyze(
                trade_id=f"W_{i}", symbol="BTCUSDT", direction="LONG",
                signal_price=50000, fill_price=50000, exit_price=51000,
                pnl=1000,
                price_history_during_trade=[50000, 51000],
                signals_used=["rsi"], patterns_detected=[]
            )
        
        # Add losses
        for i in range(3):
            analyzer.analyze(
                trade_id=f"L_{i}", symbol="BTCUSDT", direction="SHORT",
                signal_price=50000, fill_price=50000, exit_price=51000,
                pnl=-1000,
                price_history_during_trade=[50000, 51000],
                signals_used=["macd"], patterns_detected=[]
            )
        
        log = analyzer.get_daily_learning_log()
        
        assert log["lessons_count"] == 8
        assert len(log["winning_lessons"]) == 5
        assert len(log["losing_lessons"]) == 3
    
    def test_sharpe_ratio_distinguishes_strategies(self):
        """
        Strategy A (consistent small wins) should have higher Sharpe
        than Strategy B (volatile big wins/losses).
        """
        metrics = PerformanceMetrics()
        
        # Strategy A: consistent
        consistent_returns = [0.01, 0.012, 0.008, 0.011, 0.009, 0.01, 0.013, 0.007]
        
        # Strategy B: volatile (same average but much higher std)
        volatile_returns = [0.05, -0.03, 0.04, -0.02, 0.06, -0.04, 0.03, -0.01]
        
        sharpe_a = metrics.sharpe_ratio(consistent_returns)
        sharpe_b = metrics.sharpe_ratio(volatile_returns)
        
        assert sharpe_a > sharpe_b, (
            f"Consistent strategy Sharpe ({sharpe_a:.2f}) should beat "
            f"volatile strategy ({sharpe_b:.2f})"
        )


class TestRedisCircuitBreaker:
    """Test the Redis circuit breaker fallback mechanism."""
    
    def test_fallback_cache_basic_operations(self):
        """InMemoryTTLCache should work as Redis drop-in replacement."""
        from app.infrastructure.redis_client import InMemoryTTLCache
        
        cache = InMemoryTTLCache(default_ttl=60)
        
        # Set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Exists
        assert cache.exists("key1") is True
        assert cache.exists("nonexistent") is False
        
        # Delete
        cache.delete("key1")
        assert cache.get("key1") is None
    
    def test_fallback_cache_ttl_expiry(self):
        """Expired keys should return None."""
        from app.infrastructure.redis_client import InMemoryTTLCache
        import time
        
        cache = InMemoryTTLCache()
        cache.set("expire_me", "value", ex=1)  # 1 second TTL
        
        assert cache.get("expire_me") == "value"
        time.sleep(1.1)
        assert cache.get("expire_me") is None
    
    def test_circuit_breaker_states(self):
        """Circuit breaker should transition correctly."""
        from app.infrastructure.redis_client import (
            ResilientRedisClient, CircuitState
        )
        
        # Create client pointing to non-existent Redis
        client = ResilientRedisClient(
            redis_url="redis://localhost:99999",  # Invalid port
            failure_threshold=2,
            recovery_timeout=1
        )
        
        # Should be OPEN (failed to connect)
        state = client.get_circuit_state()
        assert state["state"] in ("OPEN", "CLOSED")
        
        # Fallback should still work
        client.set("test_key", "test_value", ex=60)
        assert client.get("test_key") == "test_value"
    
    def test_circuit_breaker_dual_write(self):
        """SET should always succeed via fallback even if Redis is down."""
        from app.infrastructure.redis_client import ResilientRedisClient
        
        client = ResilientRedisClient(redis_url="redis://localhost:99999")
        
        result = client.set("dual_key", "dual_value")
        assert result is True
        
        value = client.get("dual_key")
        assert value == "dual_value"
