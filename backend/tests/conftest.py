"""
SIC Ultra — Test Configuration & Fixtures
Chaos Engineering-grade test infrastructure.

ALL fixtures simulate real-world conditions:
- Network latency
- Partial data failures
- Market regime transitions
- Flash crashes

Standard: AAA (Arrange, Act, Assert) on every test.
"""

import pytest
import numpy as np
import random
import math
import sys
import os
from typing import List, Dict
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch
from dataclasses import dataclass

# Ensure app modules are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ====================================================================
# SYNTHETIC MARKET DATA GENERATORS
# ====================================================================

def generate_candles(
    n: int = 200,
    base_price: float = 50000,
    regime: str = "trending_up",
    volatility: float = 0.02,
    include_volume: bool = True
) -> List[Dict]:
    """
    Generate realistic OHLCV candles for testing.
    
    Regimes:
        trending_up: Persistent upward drift
        trending_down: Persistent downward drift
        mean_reverting: Oscillating around base
        flash_crash: Normal then sudden 20% drop
        low_volume: Normal price but extremely low volume
    """
    candles = []
    price = base_price
    
    for i in range(n):
        if regime == "trending_up":
            drift = abs(np.random.normal(0.001, volatility))
        elif regime == "trending_down":
            drift = -abs(np.random.normal(0.001, volatility))
        elif regime == "mean_reverting":
            drift = np.random.normal(0, volatility) * 0.5
            drift += (base_price - price) / base_price * 0.02
        elif regime == "flash_crash":
            if i == int(n * 0.7):
                drift = -0.20
            elif i > int(n * 0.7):
                drift = np.random.normal(0.005, volatility)
            else:
                drift = np.random.normal(0.001, volatility)
        elif regime == "low_volume":
            drift = np.random.normal(0, volatility * 0.3)
        else:
            drift = np.random.normal(0, volatility)
        
        price = price * (1 + drift)
        price = max(price, 1.0)
        
        high = price * (1 + abs(np.random.normal(0, volatility * 0.5)))
        low = price * (1 - abs(np.random.normal(0, volatility * 0.5)))
        open_price = price * (1 + np.random.normal(0, volatility * 0.2))
        
        vol = random.uniform(100, 1000) if include_volume else 0.0
        if regime == "low_volume":
            vol = random.uniform(0.01, 5.0)
        elif regime == "flash_crash" and i >= int(n * 0.7):
            vol = random.uniform(5000, 20000)
        
        candles.append({
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(price, 2),
            "volume": round(vol, 2),
            "timestamp": (datetime.utcnow() - timedelta(hours=n-i)).isoformat()
        })
    
    return candles


def generate_trade_history(
    n: int = 50,
    win_rate: float = 0.6,
    avg_win: float = 150,
    avg_loss: float = 100,
    include_timestamps: bool = True
) -> List[Dict]:
    """Generate synthetic trade history for testing."""
    trades = []
    for i in range(n):
        is_win = random.random() < win_rate
        pnl = random.uniform(50, avg_win * 2) if is_win else -random.uniform(50, avg_loss * 2)
        
        signals = random.sample(
            ["rsi", "macd", "bollinger", "trend", "top_trader_signals"],
            k=random.randint(1, 3)
        )
        patterns = random.sample(
            ["bullish_engulfing", "bearish_engulfing", "doji", "hammer", "rsi_divergence"],
            k=random.randint(0, 2)
        )
        
        trade = {
            "trade_id": f"TEST_{i:04d}",
            "symbol": random.choice(["BTCUSDT", "ETHUSDT", "SOLUSDT"]),
            "side": random.choice(["LONG", "SHORT"]),
            "entry_price": 50000 + random.uniform(-5000, 5000),
            "exit_price": 50000 + random.uniform(-5000, 5000),
            "pnl": round(pnl, 2),
            "signals_used": signals,
            "patterns_detected": patterns
        }
        
        if include_timestamps:
            trade["timestamp"] = (
                datetime.utcnow() - timedelta(hours=random.randint(1, 72))
            ).isoformat()
        
        trades.append(trade)
    
    return trades


def generate_indicators(candles: List[Dict]) -> Dict:
    """Generate realistic indicator data from candles."""
    from app.ml.indicators import (
        calculate_rsi, calculate_macd, calculate_bollinger_bands,
        calculate_atr, get_trend
    )
    
    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    
    return {
        "rsi": calculate_rsi(closes, 14),
        "macd": calculate_macd(closes, 12, 26, 9),
        "bollinger": calculate_bollinger_bands(closes, 20, 2.0),
        "atr": calculate_atr(highs, lows, closes, 14),
        "trend": get_trend(closes, 10, 50)
    }


# ====================================================================
# PYTEST FIXTURES
# ====================================================================

@pytest.fixture
def trending_candles():
    """200 candles with strong upward trend."""
    np.random.seed(42)
    return generate_candles(200, 50000, "trending_up", 0.015)


@pytest.fixture
def mean_reverting_candles():
    """200 candles oscillating around 50000."""
    np.random.seed(42)
    return generate_candles(200, 50000, "mean_reverting", 0.01)


@pytest.fixture
def flash_crash_candles():
    """200 candles with a 20% crash at candle 140."""
    np.random.seed(42)
    return generate_candles(200, 50000, "flash_crash", 0.015)


@pytest.fixture
def low_volume_candles():
    """200 candles with suspiciously low volume."""
    np.random.seed(42)
    return generate_candles(200, 50000, "low_volume", 0.01)


@pytest.fixture
def empty_candles():
    """Empty candle list — edge case."""
    return []


@pytest.fixture
def minimal_candles():
    """Only 10 candles — below minimum threshold."""
    np.random.seed(42)
    return generate_candles(10, 50000, "trending_up", 0.01)


@pytest.fixture
def trade_history_winning():
    """Trade history with 75% win rate."""
    random.seed(42)
    return generate_trade_history(100, win_rate=0.75, avg_win=200, avg_loss=80)


@pytest.fixture
def trade_history_losing():
    """Trade history with 30% win rate."""
    random.seed(42)
    return generate_trade_history(100, win_rate=0.30, avg_win=100, avg_loss=200)


@pytest.fixture
def trade_history_streak_losses():
    """8 consecutive losing trades — test anti-martingale."""
    return [
        {"trade_id": f"LOSS_{i}", "pnl": -random.uniform(50, 200),
         "symbol": "BTCUSDT", "side": "LONG",
         "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat()}
        for i in range(8)
    ]


@pytest.fixture
def mock_binance_none():
    """Binance API returning None for all calls."""
    mock = MagicMock()
    mock.get_price.return_value = None
    mock.get_klines.return_value = None
    mock.get_ticker.return_value = None
    return mock


@pytest.fixture
def mock_binance_slow():
    """Binance API with >5s latency simulation."""
    import asyncio
    
    async def slow_response(*args, **kwargs):
        await asyncio.sleep(5.5)
        return {"price": 50000}
    
    mock = MagicMock()
    mock.get_price = MagicMock(side_effect=lambda *a: 50000)
    mock.get_klines = AsyncMock(side_effect=slow_response)
    return mock
