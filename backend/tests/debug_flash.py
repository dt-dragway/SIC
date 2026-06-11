import sys
import asyncio
from app.ml.trading_agent import get_trading_agent

def run_test():
    agent = get_trading_agent()
    
    # Simular velas de consolidación
    base_price = 50000
    candles = []
    for i in range(50):
        c = {"open": base_price, "close": base_price + (i % 2) * 50, "high": base_price + 100, "low": base_price - 100, "volume": 100}
        candles.append(c)
        
    indicators = {
        "rsi": [25] * 50,  # Sobreventa fuerte (<30)
        "macd": {"histogram": [-10, -5, 0, 5, 10]}, # Cruce alcista
        "bollinger": {"lower": [49000]*50, "upper": [51000]*50, "middle": [50000]*50},
        "trend": "BULLISH",
        "atr": [500] * 50
    }
    
    print("Iniciando analyze...")
    signal = agent.analyze("BTCUSDT", candles, indicators)
    print(f"Resultado final: {signal}")

if __name__ == '__main__':
    run_test()
