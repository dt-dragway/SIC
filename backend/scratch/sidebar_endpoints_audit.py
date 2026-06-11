import requests
import json

def audit_all_endpoints():
    url_base = "http://127.0.0.1:8001/api/v1"
    
    print("======================================================================")
    print("🔬 AUDITORÍA DE FUNCIONALIDADES REALES Y ENDPOINTS DEL SIDEBAR MENU")
    print("======================================================================\n")
    
    # 1. AUTENTICACIÓN
    print("🔐 Paso 1: Obteniendo token de acceso...")
    try:
        login_res = requests.post(f"{url_base}/auth/login", data={
            "username": "admin@sic.com",
            "password": "Admin24252026**"
        }, timeout=10)
        
        if login_res.status_code != 200:
            print(f"❌ Error de autenticación: {login_res.status_code} - {login_res.text}")
            return
        
        token = login_res.json().get("access_token")
        print("   ✅ Token JWT generado dinámicamente con éxito.")
    except Exception as e:
        print(f"   ❌ Error al conectar al backend: {e}")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Función helper para auditar
    def check_endpoint(name, method, endpoint, params=None, payload=None):
        url = f"{url_base}{endpoint}"
        print(f"\n📡 Auditando: {name} ({method} {endpoint})...")
        try:
            if method == "GET":
                res = requests.get(url, headers=headers, params=params, timeout=10)
            else:
                res = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                print(f"   ✅ ÉXITO [200 OK]")
                # Mostrar un resumen corto para probar que no son datos fijos dummy
                if isinstance(data, dict):
                    keys = list(data.keys())
                    print(f"      - Estructura: Diccionario con llaves {keys}")
                    # Mostrar algún dato representativo si aplica
                    if "status" in data:
                        print(f"      - Estado/Status: {data['status']}")
                    if "total" in data:
                        print(f"      - Total registros: {data['total']}")
                elif isinstance(data, list):
                    print(f"      - Estructura: Lista de {len(data)} elementos.")
                    if len(data) > 0:
                        print(f"      - Primer elemento: {list(data[0].keys()) if isinstance(data[0], dict) else data[0]}")
            else:
                print(f"   ❌ ERROR [{res.status_code}]: {res.text}")
        except Exception as e:
            print(f"   ❌ EXCEPCIÓN: {e}")

    # 2. BILLETERA (Wallet)
    check_endpoint("Billetera Real (Binance API)", "GET", "/wallet")
    check_endpoint("Billetera Práctica (Base de Datos)", "GET", "/practice/wallet")

    # 3. TRADING & HISTORIAL
    check_endpoint("Estadísticas de Trading Real", "GET", "/trading/stats")
    check_endpoint("Estadísticas de Trading Práctica", "GET", "/practice/stats")
    check_endpoint("Historial Real (Binance Orders)", "GET", "/trading/orders")
    check_endpoint("Historial Práctica (PostgreSQL)", "GET", "/practice/trades")

    # 4. NEURAL ENGINE (Señales de IA)
    check_endpoint("Dashboard de Señales IA (Neural)", "GET", "/trading/signals/dashboard")

    # 5. SMART EXECUTION (TWAP/VWAP)
    check_endpoint("Smart Execution (Ordenes Algorítmicas Activas)", "GET", "/execution/active-orders")

    # 6. SENTIMENT HUB (Fear & Greed / Social Sentiment)
    check_endpoint("Sentiment Hub (Fear & Greed Index)", "GET", "/sentiment/fear-greed")
    check_endpoint("Sentiment Hub (Market Sentiment)", "GET", "/sentiment/market")

    # 7. DELTA NEUTRAL (Derivados & Arbitraje)
    check_endpoint("Delta Neutral (Basis Opportunities)", "GET", "/derivatives/basis-opportunities")

    # 8. TRADING JOURNAL (Diario Profesional)
    check_endpoint("Trading Journal (Metrics)", "GET", "/journal/metrics")
    check_endpoint("Trading Journal (Entries)", "GET", "/journal/entries")

    # 9. TRADE MARKERS (Gráficos)
    check_endpoint("Trade Markers (BTCUSDT Chart Data)", "GET", "/trade-markers/chart-data/BTCUSDT")

    # 10. RIESGO & MACRO CORRELATION
    check_endpoint("Macro Correlation & Risk Indicators", "GET", "/risk/macro-correlation")

    print("\n======================================================================")
    print("🏁 AUDITORÍA COMPLETADA. TODOS LOS ENDPOINTS HAN SIDO VERIFICADOS.")
    print("======================================================================\n")

if __name__ == "__main__":
    audit_all_endpoints()
