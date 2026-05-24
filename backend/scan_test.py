import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ml.signal_generator import get_signal_generator
import json

def test_professional_analysis():
    print("🚀 Iniciando Análisis Profesional de Mercado (Simulación MTF)...")
    generator = get_signal_generator()
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    
    for symbol in symbols:
        print(f"\n🔬 Analizando {symbol}...")
        signal = generator.analyze(symbol)
        
        if signal:
            print(f"✅ Señal Encontrada: {signal['type']}")
            print(f"   Tier: {signal['tier']} {signal['tier_emoji']}")
            print(f"   Confianza: {signal['confidence']}%")
            print(f"   Alineación MTF: {signal['aligned_timeframes']}")
            print(f"   Riesgo/Beneficio: {signal.get('risk_reward', 'N/A')}")
            print(f"   Entry: {signal.get('entry_price')}")
            print(f"   TP: {signal.get('take_profit')}")
            print(f"   SL: {signal.get('stop_loss')}")
            print("   Razones:")
            for reason in signal['reasoning']:
                print(f"    - {reason}")
        else:
            print(f"⏸️  {symbol}: Sin señal clara (HOLD/NEUTRAL)")

if __name__ == "__main__":
    test_professional_analysis()
