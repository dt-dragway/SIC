import sys
import os
from dotenv import load_dotenv

# Cargar env desde donde sea que estemos
load_dotenv("../.env")
load_dotenv(".env")

try:
    from binance.client import Client
except ImportError:
    print("Error: python-binance no instalado en este entorno")
    sys.exit(1)

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
testnet = os.getenv("BINANCE_TESTNET", "False").lower() == "true"

print(f"--- DIAGNOSTICO DE CONEXION ---")
print(f"Testnet activado: {testnet}")
print(f"API Key detectada: {'SI' if api_key and len(api_key) > 5 else 'NO/INVALIDA'}")

if not api_key or "INGRESA" in api_key:
    print("ERROR: API Key no configurada correctamente.")
    sys.exit(1)

try:
    print("Intentando conectar a Binance...")
    client = Client(api_key, api_secret, testnet=testnet)
    client.ping()
    print("✅ PING EXITOSO: Conexión establecida con servidores de Binance.")
    
    print("Consultando saldo...")
    info = client.get_account()
    if info:
        print("✅ AUTENTICACION EXITOSA: Credenciales válidas.")
        balances = [b for b in info['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
        print(f"Activos encontrados con saldo: {len(balances)}")
        for b in balances[:5]: # Mostrar max 5
            print(f"- {b['asset']}: {b['free']}")
    else:
        print("❌ FALLO: No se pudo obtener información de la cuenta.")

except Exception as e:
    print(f"❌ ERROR CRITICO: {str(e)}")
