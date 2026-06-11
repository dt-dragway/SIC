import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

def test_endpoints():
    client = TestClient(app)
    
    # 1. Obtener token de acceso para admin@sic.com
    print("🔑 Autenticando con el usuario administrador...")
    login_res = client.post("/api/v1/auth/login", data={
        "username": "admin@sic.com",
        "password": "Admin24252026**"
    })
    
    if login_res.status_code != 200:
        print(f"❌ Error al autenticar: {login_res.status_code} - {login_res.text}")
        return
        
    token_data = login_res.json()
    token = token_data.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Autenticación exitosa.")
    
    # 2. Llamar a /api/v1/trading/stats (Modo Real Stats)
    print("\n📡 Consultando /api/v1/trading/stats (Estadísticas Reales)...")
    stats_res = client.get("/api/v1/trading/stats", headers=headers)
    print(f"   Status Code: {stats_res.status_code}")
    print(f"   Response Body: {stats_res.text}")
    
    # 3. Llamar a /api/v1/wallet (Modo Real Wallet)
    print("\n📡 Consultando /api/v1/wallet (Wallet Real)...")
    wallet_res = client.get("/api/v1/wallet", headers=headers)
    print(f"   Status Code: {wallet_res.status_code}")
    print(f"   Response Body: {wallet_res.text}")
    
    # 4. Llamar a /api/v1/practice/stats (Modo Práctica Stats)
    print("\n📡 Consultando /api/v1/practice/stats (Estadísticas Práctica)...")
    pstats_res = client.get("/api/v1/practice/stats", headers=headers)
    print(f"   Status Code: {pstats_res.status_code}")
    print(f"   Response Body: {pstats_res.text}")

if __name__ == "__main__":
    test_endpoints()
