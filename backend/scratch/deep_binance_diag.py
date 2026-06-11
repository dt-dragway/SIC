"""
Diagnóstico PROFUNDO de Binance - Sin capas intermedias de SIC
Llama directo a la librería python-binance y a la API REST raw.
"""
import sys
import os
import time
import hmac
import hashlib
import urllib.parse
import requests

# Cargar keys directamente desde .env (sin pydantic ni cache)
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", ".env")
    env_path = os.path.abspath(env_path)
    keys = {}
    print(f"📂 Leyendo .env desde: {env_path}")
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                keys[k.strip()] = v.strip()
    return keys

env = load_env()
API_KEY    = env.get("BINANCE_API_KEY", "")
API_SECRET = env.get("BINANCE_API_SECRET", "")
PROXY      = env.get("BINANCE_PROXY", "")

# Configuración de proxies para requests
PROXIES = {"http": PROXY, "https": PROXY} if PROXY else None

print(f"\n{'='*60}")
print(f"🔑 API Key  (primeros/últimos 6): {API_KEY[:6]}...{API_KEY[-6:]}")
print(f"🔑 API Secret (primeros/últimos 6): {API_SECRET[:6]}...{API_SECRET[-6:]}")
print(f"📏 Longitud API Key: {len(API_KEY)} chars")
print(f"📏 Longitud API Secret: {len(API_SECRET)} chars")
if PROXY:
    print(f"🛡️  Proxy Configurado: {PROXY}")
else:
    print(f"🌐 Sin Proxy Configurado (Conexión Directa)")
print(f"{'='*60}\n")

BASE_URL = "https://api.binance.com"

def signed_request(method, endpoint, params=None):
    """Realiza una llamada firmada a Binance REST API directamente."""
    params = params or {}
    params["timestamp"] = int(time.time() * 1000)
    query = urllib.parse.urlencode(params)
    signature = hmac.new(
        API_SECRET.encode("utf-8"),
        query.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    url = f"{BASE_URL}{endpoint}?{query}&signature={signature}"
    headers = {"X-MBX-APIKEY": API_KEY}
    if method == "GET":
        return requests.get(url, headers=headers, timeout=10, proxies=PROXIES)
    elif method == "POST":
        return requests.post(url, headers=headers, timeout=10, proxies=PROXIES)

# ── TEST 0: Verificar IP de Salida Real ───────────────────────────────────────
print("🌐 TEST 0: Verificando IP de salida...")
try:
    ip = requests.get("https://api.ipify.org", timeout=5, proxies=PROXIES).text
    print(f"   IP de salida detectada: {ip} {'(A través de Proxy)' if PROXY else '(Conexión Directa)'}")
except Exception as e:
    print(f"   ❌ Error al consultar la IP: {e}")

# ── TEST 1: Ping (no requiere firma) ──────────────────────────────────────────
print("\n⏱️  TEST 1: Ping público a Binance...")
try:
    r = requests.get(f"{BASE_URL}/api/v3/ping", timeout=10, proxies=PROXIES)
    print(f"   Status: {r.status_code} -> {'✅ OK' if r.status_code == 200 else '❌ FAIL'}")
except Exception as e:
    print(f"   ❌ Error en Ping: {e}")

# ── TEST 2: Server Time (no requiere firma) ────────────────────────────────────
print("\n⏱️  TEST 2: Server Time de Binance...")
try:
    r = requests.get(f"{BASE_URL}/api/v3/time", timeout=10, proxies=PROXIES)
    binance_time = r.json().get("serverTime", 0)
    local_time = int(time.time() * 1000)
    diff_ms = abs(binance_time - local_time)
    print(f"   Binance time: {binance_time}")
    print(f"   Local time:   {local_time}")
    print(f"   Diferencia:   {diff_ms} ms -> {'✅ OK (< 1000ms)' if diff_ms < 1000 else '⚠️  ALTO (>1000ms, puede causar -1021)'}")
except Exception as e:
    print(f"   ❌ Error obteniendo Server Time: {e}")

# ── TEST 3: Account Info con firma HMAC directa ───────────────────────────────
print("\n🔐 TEST 3: /api/v3/account (signed) - LLAMADA DIRECTA sin wrappers...")
try:
    r = signed_request("GET", "/api/v3/account")
    print(f"   HTTP Status: {r.status_code}")
    data = r.json()
    if r.status_code == 200:
        perms = data.get("permissions", [])
        can_trade = data.get("canTrade", False)
        balances = [b for b in data.get("balances", []) if float(b["free"]) > 0 or float(b["locked"]) > 0]
        print(f"   ✅ ¡ÉXITO! Cuenta autenticada correctamente.")
        print(f"   🔑 Permisos: {perms}")
        print(f"   📊 canTrade: {can_trade}")
        print(f"   💰 Activos con balance > 0: {len(balances)}")
        for b in balances[:10]:
            print(f"       {b['asset']}: libre={b['free']} | bloqueado={b['locked']}")
    else:
        code = data.get("code")
        msg  = data.get("msg")
        print(f"   ❌ Error: code={code} | msg={msg}")
        if code == -2015:
            print("\n   📋 DIAGNÓSTICO -2015:")
            print("      • La IP del servidor/proxy NO está autorizada en la API Key de Binance, O")
            print("      • La API Key/Secret tiene algún carácter incorrecto, O")
            print("      • Los permisos de la API Key no incluyen 'Enable Reading'.")
            print(f"\n   ➡️  La IP detectada ({ip}) DEBE estar en la lista de permitidas en la consola de Binance.")
        elif code == -1021:
            print("      • Desincronización de tiempo - ajusta el reloj del servidor.")
except Exception as e:
    print(f"   ❌ Error en llamada autenticada: {e}")

# ── TEST 4: Test Order (sin costo, solo valida firma+permisos) ────────────────
print("\n🧪 TEST 4: POST /api/v3/order/test (Test Order) - sin costo real...")
try:
    r = signed_request("POST", "/api/v3/order/test", {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "quantity": 0.001
    })
    print(f"   HTTP Status: {r.status_code}")
    data = r.json()
    if r.status_code == 200:
        print("   ✅ ¡Test Order ACEPTADA! La API Key tiene permisos de Spot Trading.")
    else:
        print(f"   ❌ Error: {data}")
except Exception as e:
    print(f"   ❌ Error en Test Order: {e}")

print(f"\n{'='*60}")
print("Diagnóstico completado.")
print(f"{'='*60}")

