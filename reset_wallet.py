import json
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import VirtualWallet, AutomationConfig

db = SessionLocal()
try:
    # Resetear todas las billeteras de práctica a 20 USDT
    wallets = db.query(VirtualWallet).all()
    for w in wallets:
        w.balances = json.dumps({"USDT": 20.0})
        w.initial_capital = 20.0
        
    # Ajustar configuración de automatización
    configs = db.query(AutomationConfig).all()
    for c in configs:
        c.max_position_size = 11.0
        
    db.commit()
    print("✅ Billeteras reseteadas a 20 USDT.")
except Exception as e:
    db.rollback()
    print("❌ Error:", e)
finally:
    db.close()
