import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.binance.client import get_binance_client

async def test_wallets():
    print("📡 Conectando a Binance...")
    client = get_binance_client()
    
    if not client.is_connected():
        print("❌ Error: No conectado a Binance.")
        return
        
    print("\n💰 1. Billetera SPOT (Balances activos):")
    spot = client.get_balances(hide_zero=True)
    for b in spot:
        print(f"   Spot - {b['asset']}: {b['total']}")
        
    # Probar Billetera de Futuros (USD-M)
    print("\n🔮 2. Billetera FUTUROS (USD-M):")
    try:
        futures_bal = client.client.futures_account_balance()
        active_futures = [f for f in futures_bal if float(f.get("balance", 0)) > 0]
        print(f"   Encontrados {len(active_futures)} activos activos en Futuros:")
        for f in active_futures:
            print(f"   Futures - {f['asset']}: {f['balance']} (Libre = {f['withdrawAvailable']})")
    except Exception as e:
        print(f"   ❌ Error al consultar Futuros: {e}")
        
    # Probar Billetera de Fondos (Funding / P2P)
    print("\n💳 3. Billetera de FONDOS (Funding):")
    try:
        # GET /sapi/v1/asset/get-user-asset
        funding_bal = client.client.get_user_asset()
        active_funding = [f for f in funding_bal if float(f.get("free", 0)) + float(f.get("locked", 0)) > 0]
        print(f"   Encontrados {len(active_funding)} activos activos en Fondos:")
        for f in active_funding:
            total = float(f.get("free", 0)) + float(f.get("locked", 0))
            print(f"   Funding - {f['asset']}: {total} (Libre = {f['free']})")
    except Exception as e:
        print(f"   ❌ Error al consultar Fondos: {e}")

if __name__ == "__main__":
    asyncio.run(test_wallets())
