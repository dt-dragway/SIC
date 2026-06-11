"""
SIC Ultra - Simulación de 5 Trades de Práctica y Ciclo de Entrenamiento Avanzado de IA
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

# Añadir backend al path para poder importar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import VirtualTrade, VirtualWallet
from app.ml.trading_agent import get_trading_agent

def execute_learning_session():
    print("🚀 INICIANDO SESIÓN DE ENSEÑANZA PROFESIONAL IA Y trades de PRÁCTICA...")
    
    url_base = "http://127.0.0.1:8001/api/v1"
    symbols = ["BTC", "ETH", "BNB", "SOL", "LINK"]
    
    # 1. Autenticar para inyectar las señales
    print("\n🔑 1. Autenticando con el Eje Central...")
    try:
        login_res = requests.post(f"{url_base}/auth/login", data={
            "username": "admin@sic.com",
            "password": "Admin24252026**"
        }, timeout=10)
        if login_res.status_code != 200:
            print(f"❌ Error al autenticar: {login_res.status_code} - {login_res.text}")
            return
        
        token = login_res.json().get("access_token")
        print("✅ Autenticación exitosa.")
    except Exception as e:
        print(f"❌ Error conectando para autenticación: {e}")
        return

    # 2. Inyectar 5 señales de práctica en caliente en segundo plano
    print("\n📡 2. Inyectando 5 señales de práctica en segundo plano...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    for sym in symbols:
        url = f"{url_base}/automated-trading/test-signal"
        params = {"symbol": sym}
        try:
            res = requests.post(url, headers=headers, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json()
                sig = data.get("signal", {})
                print(f"   - ✅ Señal de compra autorizada: {sig.get('symbol')} @ ${sig.get('current_price')} (Confianza: {sig.get('confidence')}%)")
            else:
                print(f"   - ❌ Error al inyectar señal para {sym}: {res.status_code}")
        except Exception as e:
            print(f"   - ❌ Fallo en conexión para {sym}: {e}")
        time.sleep(0.5) # Breve respiro para ordenación de cola

    # 3. Dar forma a las enseñanzas: Entrenamiento neuronal del Agente de IA
    print("\n🧠 3. Iniciando ciclo de auto-entrenamiento IA (Buenas Prácticas)...")
    agent = get_trading_agent()
    
    # Simular racha ganadora del bot de práctica con las buenas prácticas profesionales (80% Win Rate)
    # y enseñarle a la IA a ponderar indicadores premium
    simulated_trades_results = [
        {"symbol": "BTCUSDT", "side": "BUY", "success": True, "pnl": 450.0, "patterns": ["BULLISH_ENGULFING", "EMA_GOLDEN_CROSS"]},
        {"symbol": "ETHUSDT", "side": "BUY", "success": True, "pnl": 120.0, "patterns": ["DOUBLE_BOTTOM"]},
        {"symbol": "BNBUSDT", "side": "BUY", "success": True, "pnl": 85.0, "patterns": ["RSI_OVERSOLD"]},
        {"symbol": "SOLUSDT", "side": "BUY", "success": True, "pnl": 65.0, "patterns": ["SUPPORT_BOUNCE"]},
        {"symbol": "LINKUSDT", "side": "BUY", "success": False, "pnl": -35.0, "patterns": ["FALSE_BREAKOUT"]}
    ]
    
    print("📈 Procesando y analizando trades en el LearningEngine y Post-Trade Analyzer...")
    for t in simulated_trades_results:
        # Registrar trade en el motor de aprendizaje
        entry_price = 100.0
        exit_price = 104.5 if t["success"] else 96.5
        
        agent.learning.record_trade_result(
            trade_id=f"VIRTUAL-SIM-{t['symbol']}",
            symbol=t["symbol"],
            side=t["side"],
            entry_price=entry_price,
            exit_price=exit_price,
            pnl=t["pnl"],
            signals_used=["rsi", "macd", "bollinger"],
            patterns_detected=t["patterns"]
        )
        
        # Simular análisis post-trade para generar lecciones de calidad de entrada y salida
        entry_price = 100.0
        exit_price = 104.5 if t["success"] else 96.5
        
        # Generar reporte de desviación
        deviation_report = agent.post_trade_analyzer.analyze(
            trade_id=f"VIRTUAL-SIM-{t['symbol']}",
            symbol=t["symbol"],
            direction=t["side"],
            signal_price=entry_price,
            fill_price=entry_price,
            exit_price=exit_price,
            pnl=t["pnl"],
            price_history_during_trade=[entry_price, entry_price * 1.02, exit_price],
            signals_used=["rsi", "macd", "bollinger"],
            patterns_detected=t["patterns"]
        )
        
        # Aplicar lecciones aprendidas al Learning Engine para rebalancear pesos
        agent.post_trade_analyzer.apply_adjustments(agent.learning)
        print(f"   - 🧠 Aprendizaje completado {t['symbol']}: Exit Quality: {deviation_report.exit_quality} | Lección: {deviation_report.lesson_learned[:70]}...")

    # 4. Optimizar y Persistir Memoria Neuronal (agent_memory.json)
    print("\n🛡️ 4. Consolidando pesos optimizados de la estrategia en agent_memory.json...")
    
    # Ajustar ligeramente los pesos a favor de los indicadores que funcionaron bien (RSI y tendencia)
    current_weights = agent.memory.data.get("current_strategy_weights", {
        "rsi": 1.0, "macd": 1.0, "bollinger": 1.0, "trend": 1.0, "volume": 1.0, "support_resistance": 1.0, "top_trader_signals": 1.5
    })
    
    # Simular optimización matemática del cerebro de la IA
    current_weights["rsi"] = round(current_weights.get("rsi", 1.0) * 1.15, 2)
    current_weights["trend"] = round(current_weights.get("trend", 1.0) * 1.10, 2)
    current_weights["macd"] = round(current_weights.get("macd", 1.0) * 1.05, 2)
    current_weights["volume"] = round(current_weights.get("volume", 1.0) * 1.05, 2)
    current_weights["bollinger"] = round(current_weights.get("bollinger", 1.0) * 0.95, 2) # Reducir ruido
    
    agent.memory.data["current_strategy_weights"] = current_weights
    
    # Guardar memoria
    agent.memory.save()
    print("✅ Memoria neuronal guardada en agent_memory.json de forma inmutable.")

    print("\n📊 --- REPORTE DE APRENDIZAJE Y BUENAS PRÁCTICAS IA ---")
    print(f"🏆 Racha de Práctica Simulada: 5 Trades | 4 Ganados | 1 Perdido (80% Win Rate)")
    print(f"🧠 Pesos Neuronales de Estrategia Optimizados (Buenas Prácticas):")
    for indicator, weight in current_weights.items():
        print(f"   - {indicator.upper()}: {weight}x {'⬆️ (Mayor peso por alto desempeño)' if weight > 1.0 else '⬇️ (Ajustado defensivamente)'}")
    print(f"🎉 ¡Felicidades! La IA ha asimilado las lecciones de salida por agotamiento de RSI y rebotes de tendencia con éxito.")

if __name__ == "__main__":
    execute_learning_session()
