import sys
import os
import asyncio
import json

# Ensure we can import 'app' package
sys.path.append(os.getcwd())

from app.api.v1.signals import get_full_analysis
from app.ml.signal_generator import get_signal_generator

def debug_signal():
    print("--- DEBUGGING SIGNALS (BACKEND CONTEXT) ---\n")
    
    # 1. Test Raw Generator
    print("1. Testing ProSignalGenerator.analyze('ETHUSDT')...")
    gen = get_signal_generator()
    try:
        raw_signal = gen.analyze("ETHUSDT")
        print(f"RAW RESULT TYPE: {type(raw_signal)}")
        if raw_signal:
            print(json.dumps(raw_signal, indent=2, default=str))
        else:
            print("Raw signal is None")
    except Exception as e:
        print(f"Generator Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n------------------------------------------------\n")

    # 2. Test Wrapper via signals.py
    print("2. Testing get_full_analysis('BTCUSDT')...")
    try:
        wrapper = get_full_analysis("BTCUSDT")
        if wrapper:
            print(f"Wrapper Symbol: {wrapper.symbol}")
            print(f"Wrapper Direction: {wrapper.direction}")
            print(f"Wrapper Confidence: {wrapper.confidence}")
            print(f"Wrapper Entry: {wrapper.entry_price}")
        else:
            print("Wrapper returned None (HOLD)")
    except Exception as e:
        print(f"Wrapper Error: {e}")

if __name__ == "__main__":
    debug_signal()
