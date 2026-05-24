import requests
import json

def trigger():
    url_base = "http://127.0.0.1:8001/api/v1"
    
    # 1. Log in to get fresh token
    print("🔑 Autenticando...")
    try:
        login_res = requests.post(f"{url_base}/auth/login", data={
            "username": "admin@sic.com",
            "password": "Admin24252026**"
        }, timeout=10)
        if login_res.status_code != 200:
            print(f"❌ Error al autenticar: {login_res.status_code} - {login_res.text}")
            return
        
        token_data = login_res.json()
        token = token_data.get("access_token")
        print("✅ Autenticado con éxito.")
    except Exception as e:
        print(f"❌ Error de conexión al autenticar: {e}")
        return

    # 2. Trigger test signal
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"{url_base}/automated-trading/test-signal"
    params = {
        "symbol": "SOL"
    }
    
    print("🚀 Enviando petición HTTP POST a /test-signal...")
    try:
        response = requests.post(url, headers=headers, params=params, timeout=15)
        print(f"Status Code: {response.status_code}")
        print("Response Content:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error al enviar la petición de señal: {e}")

if __name__ == "__main__":
    trigger()
