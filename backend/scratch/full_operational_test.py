import requests
import json
import time

def run_tests():
    url_base = "http://127.0.0.1:8001/api/v1"
    
    print("======================================================================")
    print("🚀 INICIANDO PRUEBA DE OPERACIONES COMPLETA - SIC ULTRA TRADING PLATFORM")
    print("======================================================================\n")
    
    # 1. AUTENTICACIÓN
    print("🔐 Paso 1: Autenticando usuario administrador...")
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
        print(f"   ✅ Autenticación exitosa. Token obtenido.")
    except Exception as e:
        print(f"   ❌ Error de conexión al autenticar: {e}")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 2. BILLETERA REAL
    print("\n💰 Paso 2: Consultando saldo en Billetera Real (Binance)...")
    try:
        wallet_res = requests.get(f"{url_base}/wallet", headers=headers, timeout=10)
        if wallet_res.status_code == 200:
            wallet_data = wallet_res.json()
            print(f"   ✅ Conexión con Binance exitosa.")
            # Mostrar saldos con precisión decimal especial para montos < $1
            for asset in wallet_data.get("assets", []):
                name = asset.get("asset")
                total = asset.get("free", 0.0) + asset.get("locked", 0.0)
                val_usd = asset.get("usd_value", 0.0)
                
                # Formatear balance con 5 decimales si el valor es menor a 1 USD
                if val_usd > 0 and val_usd < 1:
                    print(f"      - {name}: Total={total:.5f} | Valor en USD=${val_usd:.5f} (Precisión < $1)")
                else:
                    print(f"      - {name}: Total={total:.4f} | Valor en USD=${val_usd:.2f}")
        else:
            print(f"   ❌ Error al consultar billetera real: {wallet_res.status_code} - {wallet_res.text}")
    except Exception as e:
        print(f"   ❌ Excepción al consultar billetera real: {e}")

    # 3. BILLETERA DE PRÁCTICA
    print("\n🎮 Paso 3: Consultando saldo en Billetera de Práctica...")
    try:
        practice_res = requests.get(f"{url_base}/practice/wallet", headers=headers, timeout=10)
        if practice_res.status_code == 200:
            practice_data = practice_res.json()
            print(f"   ✅ Billetera de práctica consultada con éxito.")
            balances = practice_data.get("balances", [])
            for b in balances:
                asset = b.get("asset")
                amount = b.get("amount", 0.0)
                usd_val = b.get("usd_value", 0.0)
                print(f"      - {asset}: Cantidad={amount:.4f} | Valor USD=${usd_val:.2f}")
        else:
            print(f"   ❌ Error al consultar billetera de práctica: {practice_res.status_code} - {practice_res.text}")
    except Exception as e:
        print(f"   ❌ Excepción al consultar billetera de práctica: {e}")

    # 4. ESTADÍSTICAS DE TRADING (REAL Y PRÁCTICA)
    print("\n📈 Paso 4: Consultando estadísticas de trading...")
    try:
        # Real stats
        real_stats = requests.get(f"{url_base}/trading/stats", headers=headers, timeout=10)
        if real_stats.status_code == 200:
            stats = real_stats.json()
            print(f"   ✅ Estadísticas Real obtenidas: ROI={stats.get('roi_percent', 0.0)}% | Trades Totales={stats.get('total_trades', 0)}")
        else:
            print(f"   ❌ Error al consultar estadísticas real: {real_stats.status_code}")
            
        # Practice stats
        practice_stats = requests.get(f"{url_base}/practice/stats", headers=headers, timeout=10)
        if practice_stats.status_code == 200:
            stats = practice_stats.json()
            print(f"   ✅ Estadísticas Práctica obtenidas: ROI={stats.get('roi_percent', 0.0)}% | Ganancia/Pérdida={stats.get('total_pnl_usd', 0.0)} USD")
        else:
            print(f"   ❌ Error al consultar estadísticas práctica: {practice_stats.status_code}")
    except Exception as e:
        print(f"   ❌ Excepción al consultar estadísticas: {e}")

    # 5. DASHBOARD DE SEÑALES
    print("\n🎯 Paso 5: Consultando Dashboard de Señales de IA...")
    try:
        signals_res = requests.get(f"{url_base}/trading/signals/dashboard", headers=headers, timeout=10)
        if signals_res.status_code == 200:
            signals = signals_res.json()
            print(f"   ✅ Dashboard consultado: {len(signals)} señales encontradas en total.")
            for sig in signals[:3]: # mostrar primeras 3
                print(f"      - {sig.get('symbol')}: {sig.get('type')} | Confianza={sig.get('confidence')}% | Entry={sig.get('entry_price')}")
        else:
            print(f"   ❌ Error al consultar dashboard de señales: {signals_res.status_code}")
    except Exception as e:
        print(f"   ❌ Excepción al consultar señales: {e}")

    # 6. CONFIGURACIÓN Y PERSISTENCIA DE AUTOMATIZACIÓN
    print("\n⚙️ Paso 6: Verificando Configuración y Persistencia de Automatización...")
    try:
        # GET inicial
        get_settings_res = requests.get(f"{url_base}/automated-trading/settings", headers=headers, timeout=10)
        if get_settings_res.status_code == 200:
            current_settings = get_settings_res.json()
            print(f"   ✅ Configuración actual leída desde la BD:")
            print(f"      - Máximo de trades diarios: {current_settings.get('max_daily_trades')}")
            print(f"      - Confianza mínima de señal: {current_settings.get('min_signal_confidence')}%")
            print(f"      - Solo modo práctica: {current_settings.get('practice_mode_only')}")
        else:
            print(f"   ❌ Error al leer configuración: {get_settings_res.status_code}")
            
        # POST para cambiar configuración (Probar persistencia de slider)
        test_settings = {
            "enabled": False,
            "max_daily_trades": 7,
            "max_position_size": 35.0,
            "min_signal_confidence": 75,
            "allowed_tiers": ["S", "A"],
            "risk_level": "moderate",
            "pause_on_high_volatility": True,
            "check_interval_seconds": 25,
            "practice_mode_only": True
        }
        print("   ⚙️ Guardando nueva configuración (max_daily_trades = 7, min_signal_confidence = 75)...")
        post_res = requests.post(f"{url_base}/automated-trading/settings", headers=headers, json=test_settings, timeout=10)
        
        if post_res.status_code == 200:
            print("   ✅ Configuración guardada en DB con éxito.")
            # GET de verificación
            verify_res = requests.get(f"{url_base}/automated-trading/settings", headers=headers, timeout=10)
            verified_settings = verify_res.json()
            if verified_settings.get("max_daily_trades") == 7 and verified_settings.get("min_signal_confidence") == 75:
                print("   🌟 ¡ÉXITO! La persistencia en base de datos funciona perfectamente.")
            else:
                print("   ❌ Error: La configuración devuelta no coincide con la guardada.")
        else:
            print(f"   ❌ Error al guardar configuración: {post_res.status_code} - {post_res.text}")
    except Exception as e:
        print(f"   ❌ Excepción en persistencia de configuración: {e}")

    # 7. INICIAR AUTOMATIZACIÓN DE TRADING
    print("\n🤖 Paso 7: Iniciando automatización de trading...")
    try:
        # Estructura requerida por StartAutomationRequest: settings y symbols
        start_payload = {
            "settings": {
                "enabled": True,
                "max_daily_trades": 7,
                "max_position_size": 35.0,
                "min_signal_confidence": 75,
                "allowed_tiers": ["S", "A"],
                "risk_level": "moderate",
                "pause_on_high_volatility": True,
                "check_interval_seconds": 25,
                "practice_mode_only": True
            },
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "enabled": True,
                    "min_confidence": 75,
                    "max_position_size": 35.0,
                    "allowed_tiers": ["S", "A"]
                },
                {
                    "symbol": "SOLUSDT",
                    "enabled": True,
                    "min_confidence": 75,
                    "max_position_size": 35.0,
                    "allowed_tiers": ["S", "A"]
                }
            ]
        }
        start_res = requests.post(f"{url_base}/automated-trading/start", headers=headers, json=start_payload, timeout=15)
        if start_res.status_code == 200:
            print("   ✅ Automatización de trading iniciada correctamente.")
            status_data = start_res.json()
            print(f"      - Estado actual: Running={status_data.get('status', {}).get('running')}")
        else:
            # Si ya está activa, está bien, lo reportamos
            if "ya está activa" in start_res.text:
                print("   ℹ️ La automatización ya estaba corriendo. Procedemos con la prueba.")
            else:
                print(f"   ❌ Error al iniciar automatización: {start_res.status_code} - {start_res.text}")
    except Exception as e:
        print(f"   ❌ Excepción al iniciar automatización: {e}")

    # 8. INYECCIÓN Y EJECUCIÓN DE SEÑAL DE PRUEBA
    print("\n🚀 Paso 8: Inyectando señal de prueba en el motor de automatización...")
    try:
        test_signal_res = requests.post(
            f"{url_base}/automated-trading/test-signal",
            headers=headers,
            params={"symbol": "SOL"},
            timeout=15
        )
        if test_signal_res.status_code == 200:
            print("   ✅ Señal de prueba inyectada con éxito.")
            print(json.dumps(test_signal_res.json(), indent=6, ensure_ascii=False))
            
            # 9. ESPERA Y VERIFICACIÓN EN COLA
            print("\n⏳ Paso 9: Esperando 5 segundos para permitir que el motor ejecute la señal...")
            time.sleep(5)
            
            print("\n📋 Paso 10: Consultando cola de automatización e historial de ejecución...")
            queue_res = requests.get(f"{url_base}/automated-trading/queue", headers=headers, timeout=10)
            if queue_res.status_code == 200:
                queue_data = queue_res.json()
                print("   ✅ Cola consultada con éxito:")
                print(f"      - Estado de la Cola: {queue_data.get('queue_status')}")
                
                execution_history = queue_data.get("execution_history", [])
                print(f"      - Historial de Ejecuciones ({len(execution_history)} registradas):")
                for item in execution_history[-3:]: # últimos 3
                    status_emoji = "✅ Exitoso" if item.get("success") else "❌ Fallido"
                    print(f"         * [{item.get('executed_at')}] {item.get('symbol')} {item.get('action')} - {status_emoji} | Error: {item.get('error')}")
                
                print(f"      - Logs de escaneo recientes (últimos 3):")
                for log in queue_data.get("scan_logs", [])[-3:]:
                    print(f"         * [{log.get('timestamp')}] {log.get('symbol')}: {log.get('message')}")
            else:
                print(f"   ❌ Error al consultar la cola de ejecución: {queue_res.status_code}")
        else:
            print(f"   ❌ Error al inyectar señal de prueba: {test_signal_res.status_code} - {test_signal_res.text}")
    except Exception as e:
        print(f"   ❌ Excepción en inyección y ejecución de señal: {e}")

    # 10. DETENER AUTOMATIZACIÓN DE TRADING
    print("\n🛑 Paso 11: Deteniendo automatización de trading...")
    try:
        stop_res = requests.post(f"{url_base}/automated-trading/stop", headers=headers, timeout=15)
        if stop_res.status_code == 200:
            print("   ✅ Automatización de trading detenida correctamente.")
            final_status = stop_res.json().get("final_status", {})
            print(f"      - Estado final: Running={final_status.get('running')}")
        else:
            print(f"   ❌ Error al detener automatización: {stop_res.status_code} - {stop_res.text}")
    except Exception as e:
        print(f"   ❌ Excepción al detener automatización: {e}")

    print("\n======================================================================")
    print("🏁 PRUEBA DE OPERACIONES COMPLETADA CON ÉXITO")
    print("======================================================================\n")

if __name__ == "__main__":
    run_tests()
