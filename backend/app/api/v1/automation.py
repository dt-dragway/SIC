"""
SIC Ultra - Automation & Backtesting API

Motor de backtesting con datos históricos reales.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import numpy as np

from app.api.v1.auth import oauth2_scheme, verify_token
from app.infrastructure.binance.client import get_binance_client


router = APIRouter()


# === Schemas ===

class BacktestRequest(BaseModel):
    symbol: str
    strategy: str  # "SIMPLE_MA_CROSS", "RSI_MEAN_REVERSION"
    parameters: Dict[str, float]
    start_date: str  # "2024-01-01"
    end_date: str


class Trade(BaseModel):
    timestamp: str
    type: str  # "BUY" or "SELL"
    price: float
    pnl: Optional[float] = None


class BacktestResult(BaseModel):
    symbol: str
    strategy: str
    total_trades: int
    win_rate: float
    total_pnl: float
    sharpe_ratio: float
    max_drawdown: float
    trades: List[Trade]


# === Backtesting Engine ===

def simple_ma_cross_strategy(prices: List[float], fast_ma: int, slow_ma: int) -> List[str]:
    """
    Estrategia de cruce de medias móviles.
    Retorna señales: ["HOLD", "BUY", "SELL", ...]
    """
    signals = ["HOLD"] * len(prices)
    
    if len(prices) < slow_ma:
        return signals
    
    # Calcular MAs
    fast_mas = []
    slow_mas = []
    
    for i in range(len(prices)):
        if i >= fast_ma - 1:
            fast_mas.append(np.mean(prices[i - fast_ma + 1:i + 1]))
        else:
            fast_mas.append(None)
            
        if i >= slow_ma - 1:
            slow_mas.append(np.mean(prices[i - slow_ma + 1:i + 1]))
        else:
            slow_mas.append(None)
    
    # Generar señales
    for i in range(1, len(prices)):
        if fast_mas[i] is None or slow_mas[i] is None:
            continue
            
        # Cruce alcista
        if fast_mas[i - 1] <= slow_mas[i - 1] and fast_mas[i] > slow_mas[i]:
            signals[i] = "BUY"
        # Cruce bajista
        elif fast_mas[i - 1] >= slow_mas[i - 1] and fast_mas[i] < slow_mas[i]:
            signals[i] = "SELL"
    
    return signals


def rsi_mean_reversion_strategy(prices: List[float], rsi_period: int, oversold: float, overbought: float) -> List[str]:
    """
    Estrategia de reversión a la media con RSI.
    Compra en oversold, vende en overbought.
    """
    signals = ["HOLD"] * len(prices)
    
    if len(prices) < rsi_period + 1:
        return signals
    
    # Calcular RSI
    rsi_values = [None] * len(prices)
    
    for i in range(rsi_period, len(prices)):
        gains = []
        losses = []
        
        for j in range(i - rsi_period + 1, i + 1):
            change = prices[j] - prices[j - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            rsi_values[i] = 100
        else:
            rs = avg_gain / avg_loss
            rsi_values[i] = 100 - (100 / (1 + rs))
    
    # Generar señales
    for i in range(len(prices)):
        if rsi_values[i] is None:
            continue
            
        if rsi_values[i] < oversold:
            signals[i] = "BUY"
        elif rsi_values[i] > overbought:
            signals[i] = "SELL"
    
    return signals


# === Endpoints ===

@router.post("/backtest", response_model=BacktestResult)
async def run_backtest(
    request: BacktestRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    Ejecutar backtest con datos históricos de Binance.
    """
    verify_token(token)
    client = get_binance_client()
    
    # Fetch historical data (klines)
    start_ts = int(datetime.strptime(request.start_date, "%Y-%m-%d").timestamp() * 1000)
    end_ts = int(datetime.strptime(request.end_date, "%Y-%m-%d").timestamp() * 1000)
    
    klines = client.client.get_historical_klines(
        request.symbol,
        "1d",  # Daily candles
        start_ts,
        end_ts
    )
    
    # Extract close prices
    prices = [float(k[4]) for k in klines]  # Close price is index 4
    timestamps = [datetime.fromtimestamp(k[0] / 1000).isoformat() for k in klines]
    
    # Apply strategy
    if request.strategy == "SIMPLE_MA_CROSS":
        fast_ma = int(request.parameters.get("fast_ma", 9))
        slow_ma = int(request.parameters.get("slow_ma", 21))
        signals = simple_ma_cross_strategy(prices, fast_ma, slow_ma)
    elif request.strategy == "RSI_MEAN_REVERSION":
        rsi_period = int(request.parameters.get("rsi_period", 14))
        oversold = request.parameters.get("oversold", 30)
        overbought = request.parameters.get("overbought", 70)
        signals = rsi_mean_reversion_strategy(prices, rsi_period, oversold, overbought)
    else:
        return BacktestResult(
            symbol=request.symbol,
            strategy=request.strategy,
            total_trades=0,
            win_rate=0,
            total_pnl=0,
            sharpe_ratio=0,
            max_drawdown=0,
            trades=[]
        )
    
    # Simulate trades
    trades = []
    position = None
    entry_price = None
    wins = 0
    losses = 0
    pnl_history = [0]
    
    for i, signal in enumerate(signals):
        if signal == "BUY" and position is None:
            position = "LONG"
            entry_price = prices[i]
            trades.append(Trade(
                timestamp=timestamps[i],
                type="BUY",
                price=prices[i],
                pnl=None
            ))
        elif signal == "SELL" and position == "LONG":
            pnl = prices[i] - entry_price
            pnl_history.append(pnl_history[-1] + pnl)
            
            if pnl > 0:
                wins += 1
            else:
                losses += 1
                
            trades.append(Trade(
                timestamp=timestamps[i],
                type="SELL",
                price=prices[i],
                pnl=pnl
            ))
            position = None
    
    # Calculate metrics
    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    total_pnl = pnl_history[-1]
    
    # Sharpe Ratio (simplified)
    if len(pnl_history) > 1:
        returns = np.diff(pnl_history)
        sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
    else:
        sharpe_ratio = 0
    
    # Max Drawdown
    peak = pnl_history[0]
    max_dd = 0
    for pnl in pnl_history:
        if pnl > peak:
            peak = pnl
        dd = peak - pnl
        if dd > max_dd:
            max_dd = dd
    
    return BacktestResult(
        symbol=request.symbol,
        strategy=request.strategy,
        total_trades=total_trades,
        win_rate=win_rate,
        total_pnl=total_pnl,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_dd,
        trades=trades
    )
