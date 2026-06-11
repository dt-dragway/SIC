import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.binance.client import get_binance_client
from app.config import settings

def test_real_wallet():
    print("🔑 Cargando configuraciones de Binance...")
    print(f"   Testnet: {settings.binance_testnet}")
    print(f"   API Key: {settings.binance_api_key[:10]}...{settings.binance_api_key[-10:] if settings.binance_api_key else ''}")
    
    print("\n📡 Conectando a Binance...")
    client = get_binance_client()
    
    connected = client.is_connected()
    print(f"   Conectado: {connected}")
    
    if connected:
        print("\n💰 Obteniendo balances reales...")
        balances = client.get_balances(hide_zero=True)
        print(f"   Número de activos con balance > 0: {len(balances)}")
        for b in balances:
            print(f"    - {b['asset']}: Total = {b['total']} (Libre = {b['free']}, Bloqueado = {b['locked']})")
            
        print("\n📈 Calculando valor total de la cartera en USD...")
        total_usd = client.get_wallet_value_usd()
        print(f"   💵 Valor total estimado: ${total_usd:.4f} USD")
    else:
        print("❌ Error: No se pudo establecer conexión con Binance. Verifica las API keys y la red.")

if __name__ == "__main__":
    test_real_wallet()
