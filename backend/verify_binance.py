
import sys
import os

# Get absolute path to backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.config import settings
from app.infrastructure.binance.client import BinanceClient
from loguru import logger

def verify_binance():
    print(f"Checking Binance Configuration...")
    print(f"API Key configured: {'YES' if settings.binance_api_key else 'NO'}")
    print(f"API Secret configured: {'YES' if settings.binance_api_secret else 'NO'}")
    print(f"Testnet Mode: {settings.binance_testnet}")

    if not settings.binance_api_key or not settings.binance_api_secret:
        print("❌ CRITICAL: Binance API Keys are missing in .env")
        return

    try:
        client = BinanceClient()
        if client.is_connected():
            print("✅ SUCCESS: Connected to Binance API")
            
            # Try to fetch account info
            info = client.get_account_info()
            if info:
                print("✅ Account Info Retrieved")
                # print(f"Permissions: {info.get('permissions')}")
                
                # Check balances (first 5 non-zero)
                balances = client.get_balances(hide_zero=True)
                print(f"Found {len(balances)} assets with balance > 0")
                for b in balances[:5]:
                    print(f" - {b['asset']}: {b['total']}")
            else:
                 print("⚠️ WARNING: Connected but failed to get account info (Check API Key permissions)")

        else:
             print("❌ ERROR: Connection failed (is_connected returned False)")
             
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    verify_binance()
