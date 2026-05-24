import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.auto_execution import AutoExecutionService

async def test_run():
    print("🚀 Iniciando prueba de AutoExecutionService...")
    service = AutoExecutionService()
    
    # 1. Verificar símbolos
    symbols = await service._get_automation_symbols()
    print(f"📊 Símbolos configurados para escaneo ({len(symbols)}): {symbols}")
    
    # 2. Ejecutar generación de señales para ver si escanea todos los símbolos
    print("🔍 Ejecutando generación de señales...")
    # Sobrescribimos temporalmente _get_automation_symbols para probar solo los primeros 3 y hacer la prueba más rápida
    async def temp_symbols():
        return ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    service._get_automation_symbols = temp_symbols
    
    await service._generate_new_signals()
    
    print("\n📋 Registros de Escaneo generados (scan_logs):")
    for log in service.scan_logs:
        print(f"[{log['timestamp']}] {log['symbol']}: {log['message']}")
        
    print("✅ Prueba completada con éxito.")

if __name__ == "__main__":
    asyncio.run(test_run())
