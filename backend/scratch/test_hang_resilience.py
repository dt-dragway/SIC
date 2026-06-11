import asyncio
import sys
import os
from typing import Dict, List, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.auto_execution import AutoExecutionService

# Mock LLM Manager que simula un cuelgue/hang en el modelo de IA
class MockHangingLLMManager:
    async def analyze_market(
        self,
        symbol: str,
        current_price: float,
        indicators: Dict,
        patterns: List[str],
        recent_signals: List[Dict]
    ) -> Optional[Dict]:
        print(f"   [MockLLM] Recibida solicitud para {symbol}. Simulando retraso prolongado de 15 segundos...")
        await asyncio.sleep(15.0)  # Duerme 15 segundos (mayor que el timeout de 10s)
        return {"signal": "BUY", "confidence": 85, "reasoning": "Señal mock tras retraso"}

async def test_hang_resilience():
    print("\n🚨 Probando resiliencia ante cuelgues del LLM (Opción B)...")
    service = AutoExecutionService()
    
    # 1. Mockear la obtención del LLM Manager para inyectar nuestro MockHangingLLMManager
    import app.ml.llm_connector as llm_connector
    llm_connector.get_llm_manager = lambda: MockHangingLLMManager()
    
    # 2. Mockear el generador de señales para que devuelva una señal técnica de COMPRA activa
    # de modo que intente validar con el LLM
    class MockSignalGenerator:
        def analyze(self, symbol: str) -> Optional[Dict]:
            print(f"   [MockGen] Generando señal técnica ficticia BUY para {symbol}...")
            return {
                "symbol": symbol,
                "type": "BUY",
                "confidence": 75,
                "current_price": 50000.0,
                "timeframes": {
                    "1h": {
                        "indicators": {"rsi": 35, "macd": 1.2}
                    }
                },
                "reasoning": ["📊 Ruptura de soporte", "RSI en sobreventa"]
            }
            
    import app.ml.signal_generator as sig_generator
    sig_generator.get_signal_generator = lambda: MockSignalGenerator()
    
    # 3. Limitar símbolos a BTCUSDT y ETHUSDT
    async def temp_symbols():
        return ['BTCUSDT', 'ETHUSDT']
    service._get_automation_symbols = temp_symbols
    
    # 4. Registrar tiempo inicial y ejecutar
    start_time = asyncio.get_event_loop().time()
    await service._generate_new_signals()
    end_time = asyncio.get_event_loop().time()
    
    elapsed = end_time - start_time
    print(f"\n⏱️ Tiempo total transcurrido: {elapsed:.2f} segundos")
    
    print("\n📋 Registros de Escaneo generados (scan_logs):")
    for log in service.scan_logs:
        print(f"[{log['timestamp']}] {log['symbol']}: {log['message']}")
        
    # Verificar que el timeout funcionó:
    # Cada llamada LLM debe durar 10 segundos debido al timeout, por lo que para 2 símbolos debe tomar aproximadamente 20 segundos
    # en lugar de 30 segundos, y en scan_logs debe figurar el log de timeout.
    timeout_logs = [log for log in service.scan_logs if "Timeout de IA" in log['message']]
    if len(timeout_logs) > 0 and elapsed < 25.0:
        print("\n🎉 ¡ÉXITO! La Opción B funciona perfectamente. La IA se colgó pero el escáner la descartó tras 10 segundos y continuó con la siguiente moneda.")
    else:
        print("\n❌ FALLO: El escáner se quedó colgado o no manejó el timeout correctamente.")

if __name__ == "__main__":
    asyncio.run(test_hang_resilience())
