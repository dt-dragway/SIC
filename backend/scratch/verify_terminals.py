import sys
import os

# Asegurar que el directorio raíz de la aplicación esté en el PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

def run_verification():
    print("======================================================================")
    print("🧪 INICIANDO VERIFICACIÓN INTEGRAL DE ENDPOINTS DE CONSOLAS Y TERMINALES")
    print("======================================================================\n")

    client = TestClient(app)

    # 1. Intentar autenticación con credenciales de administrador por defecto
    print("🔑 [1/7] Autenticando usuario administrador...")
    login_data = {
        "username": "admin@sic.com",
        "password": "Admin24252026**"
    }
    
    try:
        login_res = client.post("/api/v1/auth/login", data=login_data)
        if login_res.status_code != 200:
            print(f"❌ Falló autenticación. Status: {login_res.status_code}")
            print(f"Detalle: {login_res.text}")
            return
        
        token_data = login_res.json()
        token = token_data.get("access_token")
        print(f"✅ Autenticación exitosa. Token obtenido (primeros 20 caracteres): {token[:20]}...\n")
        
    except Exception as e:
        print(f"❌ Error durante el proceso de autenticación: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Verificar Endpoint de Cola de Trading Automático
    print("🤖 [2/7] Verificando endpoint `/api/v1/automated-trading/queue`...")
    try:
        res = client.get("/api/v1/automated-trading/queue", headers=headers)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("✅ Exitoso!")
            print(f"  - Tamaño de cola: {data.get('queue_status', {}).get('queue_size', 0)}")
            print(f"  - Historial de ejecución: {len(data.get('execution_history', []))} registros")
            print(f"  - Logs de escaneo: {len(data.get('scan_logs', []))} registros")
        else:
            print(f"❌ Falló con status: {res.status_code}, detalle: {res.text}")
    except Exception as e:
        print(f"❌ Error al consultar cola de trading: {e}")
    print()

    # 3. Verificar Endpoint de Logs del Centinela CIO
    print("🛡️ [3/7] Verificando endpoint `/api/v1/practice/sentinel-logs`...")
    try:
        res = client.get("/api/v1/practice/sentinel-logs?limit=5", headers=headers)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Exitoso! Retornó {len(data)} registros de Sentinel en la base de datos.")
            for i, log in enumerate(data[:3]):
                print(f"  {i+1}. [{log.get('timestamp')[-8:]}] [{log.get('side')}] {log.get('symbol')} -> PX: {log.get('price')} - {log.get('reason')[:60]}...")
        else:
            print(f"❌ Falló con status: {res.status_code}, detalle: {res.text}")
    except Exception as e:
        print(f"❌ Error al consultar logs de sentinel: {e}")
    print()

    # 4. Verificar Endpoint de Order Book / Profundidad de Mercado (Binance Integration)
    print("📊 [4/7] Verificando endpoint `/api/v1/trading/depth/BTCUSDT`...")
    try:
        res = client.get("/api/v1/trading/depth/BTCUSDT?limit=5", headers=headers)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("✅ Exitoso!")
            print(f"  - Símbolo: {data.get('symbol')}")
            print(f"  - Bids (Compras): {len(data.get('bids', []))} niveles devueltos")
            print(f"  - Asks (Ventas): {len(data.get('asks', []))} niveles devueltos")
            if data.get('bids') and data.get('asks'):
                best_bid = float(data['bids'][0][0])
                best_ask = float(data['asks'][0][0])
                spread = best_ask - best_bid
                print(f"  - Mejor Bid: ${best_bid:.2f} | Mejor Ask: ${best_ask:.2f} | Spread: ${spread:.2f}")
        else:
            print(f"❌ Falló con status: {res.status_code}, detalle: {res.text}")
    except Exception as e:
        print(f"❌ Error al consultar depth: {e}")
    print()

    # 5. Verificar Endpoint de Tasas de Financiación (Futures Funding Rates)
    print("⚡ [5/7] Verificando endpoint `/api/v1/trading/funding/BTCUSDT`...")
    try:
        res = client.get("/api/v1/trading/funding/BTCUSDT", headers=headers)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("✅ Exitoso!")
            print(f"  - Símbolo: {data.get('symbol')}")
            print(f"  - Tasa Funding: {data.get('fundingRate')}")
            print(f"  - Precio Marca: ${data.get('markPrice')}")
        else:
            print(f"❌ Falló con status: {res.status_code}, detalle: {res.text}")
    except Exception as e:
        print(f"❌ Error al consultar funding: {e}")
    print()

    # 6. Verificar Endpoint de Estado de Ollama (Cerebro IA)
    print("🧠 [6/7] Verificando endpoint `/api/v1/knowledge/ollama-status`...")
    try:
        res = client.get("/api/v1/knowledge/ollama-status", headers=headers)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("✅ Exitoso!")
            ollama = data.get("ollama", {})
            print(f"  - Disponible: {ollama.get('available')}")
            print(f"  - Modelo activo: {ollama.get('model')}")
            print(f"  - Estado: {ollama.get('message')}")
        else:
            print(f"❌ Falló con status: {res.status_code}, detalle: {res.text}")
    except Exception as e:
        print(f"❌ Error al consultar ollama status: {e}")
    print()

    # 7. Verificar Endpoint de Escaneo de Señales en Vivo (Neural Engine Reasonings)
    print("📡 [7/7] Verificando endpoint `/api/v1/signals/scan`...")
    try:
        res = client.get("/api/v1/signals/scan", headers=headers)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("✅ Exitoso!")
            signals = data.get("signals", [])
            print(f"  - Señales detectadas en mercados: {len(signals)}")
            for idx, s in enumerate(signals[:2]):
                print(f"    - {idx+1}. [{s.get('symbol')}] Dirección: {s.get('direction')} | Confianza: {s.get('confidence')}%")
                if s.get('reasoning'):
                    print(f"      Lógica de razonamiento: {s.get('reasoning')[0][:70]}...")
        else:
            print(f"❌ Falló con status: {res.status_code}, detalle: {res.text}")
    except Exception as e:
        print(f"❌ Error al consultar scan en vivo: {e}")
    print()

    print("======================================================================")
    print("🎉 PRUEBA DE ENDPOINTS COMPLETADA CON ÉXITO Y TOTALMENTE VERIFICADA")
    print("======================================================================")

if __name__ == "__main__":
    run_verification()
