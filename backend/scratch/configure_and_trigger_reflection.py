import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import AutomationConfig, VirtualWallet
from app.ml.evolution_agent import get_evolution_agent

def configure_and_reflect():
    db = SessionLocal()
    try:
        # 1. Buscar o crear configuración para el usuario #1
        config = db.query(AutomationConfig).filter(AutomationConfig.user_id == 1).first()
        if not config:
            print("⚙️ Creando AutomationConfig por defecto...")
            config = AutomationConfig(
                user_id=1,
                enabled=True,
                spot_enabled=True,
                futures_enabled=True,
                practice_mode_only=True,
                max_daily_trades=10,
                max_position_size=50.0,
                min_signal_confidence=70,
                risk_level="moderate"
            )
            db.add(config)
        else:
            print("⚙️ Sincronizando e incrementando defensas de automatización...")
            config.enabled = True
            config.spot_enabled = True
            config.futures_enabled = True
            config.practice_mode_only = True
            config.min_signal_confidence = 70
            config.max_position_size = 50.0
            config.risk_level = "moderate"
        
        # Incrementar fondos de la wallet de simulación a $500 USDT libres para buscar la meta de $1000 USD
        wallet = db.query(VirtualWallet).filter(VirtualWallet.user_id == 1).first()
        if wallet:
            import json as json_lib
            balances = json_lib.loads(wallet.balances) if wallet.balances else {}
            balances["USDT"] = 500.0 # Asegurar suficiente colateral para contratos simultáneos
            wallet.balances = json_lib.dumps(balances)
            print(f"💰 Balance de USDT en wallet de simulación recargado a ${balances['USDT']} USDT libres.")
        
        db.commit()
        print("✅ Configuración de Automatización DUAL (Spot + Futuros) guardada y activa en DB.")

        # 2. Gatillar ciclo de Auto-Reflexión y Mutaciones en caliente
        print("\n🧠 Disparando ciclo de Auto-Reflexión y Mutaciones de la IA (Smart Reflection)...")
        evo_agent = get_evolution_agent()
        mutation_result = evo_agent.perform_macro_mutations(db, user_id=1)
        
        print("\n🧬 [INFORME DE EVOLUCIÓN IA DE SIC]")
        print(f"   Status: {mutation_result.get('status')}")
        print(f"   Cambio de Parámetros: {mutation_result.get('message')}")
        if mutation_result.get("config"):
            print("   Configuración Actualizada:")
            for k, v in mutation_result["config"].items():
                print(f"    - {k}: {v}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error configurando IA: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    configure_and_reflect()
