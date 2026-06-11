import sys
import os
sys.path.append(os.getcwd())

from app.ml.trading_agent import TradingAgentAI
from app.infrastructure.database.session import get_db

print("--- AI SYNCHRONIZATION TEST ---")

# 1. Load Agent
agent = TradingAgentAI()
initial_pnl = agent.memory.data.get("total_pnl", 0)
initial_trades = agent.memory.data.get("total_trades", 0)

print(f"1. Initial State:")
print(f"   - PnL: ${initial_pnl}")
print(f"   - Trades: {initial_trades}")

# 2. Simulate Learning Event (A winning trade)
print("\n2. Simulating Trade 'VERIFY_SYNC_001' (+$10.00 Profit)...")
try:
    agent.record_result(
        trade_id="VERIFY_SYNC_001",
        symbol="BTCUSDT",
        side="LONG",
        entry_price=95000.0,
        exit_price=96000.0,  # +$1000 price diff * 0.01 qty = $10 
        pnl=10.0,
        signals_used=["RSI_OVERSOLD", "MACD_CROSS"],
        patterns_detected=["BULLISH_ENGULFING"]
    )
    print("   -> Trade Recorded Successfully.")
except Exception as e:
    print(f"   -> ERROR recording trade: {e}")
    sys.exit(1)

# 3. Verify Immediate Update
updated_pnl = agent.memory.data.get("total_pnl", 0)
updated_trades = agent.memory.data.get("total_trades", 0)

print(f"\n3. Immediate State Check:")
print(f"   - PnL: ${updated_pnl} (Expected: ${initial_pnl + 10})")
print(f"   - Trades: {updated_trades} (Expected: {initial_trades + 1})")

if updated_pnl == initial_pnl + 10:
    print("\n✅ SUCCESS: Memory updated instantly in-process.")
else:
    print("\n❌ FAILURE: Memory did not update correctly.")

# 4. Verify Persistence (Reload Agent)
print("\n4. Verifying Persistence (Reloading Agent from Disk)...")
agent_new = TradingAgentAI()
persisted_pnl = agent_new.memory.data.get("total_pnl", 0)

if persisted_pnl == updated_pnl:
    print(f"   - Persisted PnL: ${persisted_pnl}")
    print("✅ SUCCESS: Data persisted to disk json.")
else:
    print(f"   - Persisted PnL: ${persisted_pnl} (Expected: ${updated_pnl})")
    print("❌ FAILURE: Data did not persist to disk.")
