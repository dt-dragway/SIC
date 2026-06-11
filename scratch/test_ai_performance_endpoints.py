import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import User, AgentTrade
from datetime import datetime

def run_tests():
    print("=" * 70)
    print("🧪 INICIANDO VERIFICACIÓN DE NUEVOS ENDPOINTS DE RENDIMIENTO E IA")
    print("=" * 70)

    db = SessionLocal()
    try:
        # 1. Obtener primer usuario o crear uno de prueba si no existe
        user = db.query(User).first()
        if not user:
            print("⚠️ No hay usuarios en la base de datos para la prueba.")
            return

        print(f"👤 Usuario de prueba seleccionado: {user.email}")

        # 2. Asegurarse de que existan algunos trades en agent_trades para que no esté vacío
        # y poder auditar los cálculos matemáticos del P&L
        trades_count = db.query(AgentTrade).count()
        print(f"📊 Registros actuales en agent_trades: {trades_count}")

        if trades_count == 0:
            print("🆕 Inyectando registros de prueba persistentes en agent_trades...")
            test_trades = [
                AgentTrade(
                    trade_id="TEST_AI_001",
                    symbol="BTCUSDT",
                    side="BUY",
                    entry_price=64200.0,
                    exit_price=68450.0,
                    pnl=120.50,
                    signals_used='["top_trader_signals", "rsi"]',
                    patterns_detected='["Bullish Engulfing"]'
                ),
                AgentTrade(
                    trade_id="TEST_AI_002",
                    symbol="ETHUSDT",
                    side="SELL",
                    entry_price=3400.0,
                    exit_price=3480.0,
                    pnl=-25.30,
                    signals_used='["macd", "rsi"]',
                    patterns_detected='["Bearish Divergence"]'
                )
            ]
            for t in test_trades:
                db.add(t)
            db.commit()
            print("✅ 2 Registros inyectados con éxito.")
        
        # 3. Probar Endpoints usando TestClient
        client = TestClient(app)
        
        # Simular autenticación (obteniendo token)
        # Como es prueba interna, podemos mockear la dependencia o usar el usuario de prueba
        from app.api.v1.auth import get_current_user
        app.dependency_overrides[get_current_user] = lambda: user

        print("\n⚡ Paso 1: Consultando rendimiento acumulado y auditoría (/performance)...")
        res_perf = client.get("/api/v1/automated-trading/performance")
        
        if res_perf.status_code == 200:
            data = res_perf.json()
            print("✅ Endpoint /performance respondió exitosamente:")
            print(f"   - Trades Totales: {data.get('total_trades')}")
            print(f"   - Ganancia PNL Total: {data.get('total_pnl')} USD")
            print(f"   - Tasa de Acierto (Win Rate): {data.get('win_rate')}%")
            print(f"   - Mejor Trade: {data.get('best_trade')} USD")
            print(f"   - Peor Trade: {data.get('worst_trade')} USD")
            print(f"   - Promedio por Trade: {data.get('avg_trade')} USD")
            print(f"   - Cantidad de trades listados: {len(data.get('trades', []))}")
            if data.get('trades'):
                print(f"   - Muestra primer trade: {data['trades'][0]}")
        else:
            print(f"❌ Falló /performance con status {res_perf.status_code}: {res_perf.text}")

        print("\n⚡ Paso 2: Consultando escáner de Traders de Élite de Binance (/elite-traders)...")
        res_elite = client.get("/api/v1/automated-trading/elite-traders")
        
        if res_elite.status_code == 200:
            data = res_elite.json()
            print("✅ Endpoint /elite-traders respondió exitosamente:")
            print(f"   - Estado de la Consonancia de Mercado: {list(data.get('consensus', {}).keys())}")
            print(f"   - Cantidad de Traders de Élite monitoreados: {len(data.get('elite_traders', []))}")
            print(f"   - Neuronas Activas en el Mega Cerebro: {data.get('neurons_active_count')}")
            print(f"   - Pesos neuronales activos: {data.get('brain_learning_weights')}")
        else:
            print(f"❌ Falló /elite-traders con status {res_elite.status_code}: {res_elite.text}")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado durante el test: {e}")
    finally:
        db.close()
        app.dependency_overrides.clear()
        print("\n" + "=" * 70)
        print("🏁 VERIFICACIÓN COMPLETADA")
        print("=" * 70)

if __name__ == "__main__":
    run_tests()
