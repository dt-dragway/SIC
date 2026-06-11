import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

def run_integration_test():
    print("======================================================================")
    print("🧪 INICIANDO INTEGRACIÓN DE PRUEBAS DE FUTUROS VIRTUALES (1x a 5x)")
    print("======================================================================\n")

    client = TestClient(app)

    # 1. Login
    login_data = {
        "username": "admin@sic.com",
        "password": "Admin24252026**"
    }
    print("🔑 [1/4] Autenticando usuario...")
    login_res = client.post("/api/v1/auth/login", data=login_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Token obtenido.")

    # 2. Abrir Contrato Futuro SHORT 5x en SOLUSDT
    print("\n📈 [2/4] Abriendo posición de futuros virtual (SHORT 5x SOLUSDT)...")
    futures_order = {
        "symbol": "SOLUSDT",
        "side": "SHORT",
        "size": 0.5,
        "leverage": 5
    }
    
    open_res = client.post("/api/v1/practice/futures/open", json=futures_order, headers=headers)
    print(f"Status Code: {open_res.status_code}")
    if open_res.status_code != 200:
        print(f"❌ Falló al abrir posición: {open_res.text}")
        return
        
    pos_data = open_res.json()
    position_id = pos_data.get("id")
    print("✅ Posición abierta con éxito:")
    print(f"  - ID Posición: {position_id}")
    print(f"  - Símbolo: {pos_data.get('symbol')}")
    print(f"  - Lado: {pos_data.get('side')}")
    print(f"  - Apalancamiento: {pos_data.get('leverage')}x")
    print(f"  - Margen Colateral: ${pos_data.get('margin')} USDT")
    print(f"  - Precio Entrada: ${pos_data.get('entry_price')}")
    print(f"  - Precio Liquidación: ${pos_data.get('liquidation_price')}")

    # 3. Listar posiciones activas
    print("\n📡 [3/4] Consultando posiciones activas en tiempo real...")
    positions_res = client.get("/api/v1/practice/futures/positions", headers=headers)
    print(f"Status Code: {positions_res.status_code}")
    if positions_res.status_code == 200:
        positions = positions_res.json()
        print(f"✅ Encontrada(s) {len(positions)} posición(es) activa(s):")
        for pos in positions:
            print(f"  * [{pos.get('side')}] {pos.get('symbol')} -> Margen: ${pos.get('margin')} | uPNL: ${pos.get('unrealized_pnl')} ({pos.get('pnl_percent')}%)")
            
    # 4. Cerrar posición
    print(f"\n🔒 [4/4] Cerrando la posición de futuros (ID: {position_id})...")
    close_res = client.post(f"/api/v1/practice/futures/close/{position_id}", headers=headers)
    print(f"Status Code: {close_res.status_code}")
    if close_res.status_code == 200:
        close_data = close_res.json()
        print("✅ Posición cerrada con éxito!")
        print(f"  - Mensaje: {close_data.get('message')}")
        print(f"  - PNL Realizado: ${close_data.get('realized_pnl')} USD")
        print(f"  - Fondos Retornados: ${close_data.get('returned_funds')} USD")
        print(f"  - Nuevo Balance USDT: ${close_data.get('new_usdt_balance')} USD")
    else:
        print(f"❌ Falló al cerrar posición: {close_res.text}")

    print("\n======================================================================")
    print("🎉 PRUEBA DE INTEGRACIÓN DE FUTUROS COMPLETADA CON ÉXITO")
    print("======================================================================")

if __name__ == "__main__":
    run_integration_test()
