import json
import redis
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import VirtualWallet

# Limpiar balances y forzar 20 USD en BD
db = SessionLocal()
wallets = db.query(VirtualWallet).all()
for w in wallets:
    w.balances = json.dumps({"USDT": 20.0})
    w.initial_capital = 20.0
db.commit()
db.close()

# Limpiar caché Redis si existe
try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.flushdb()
    print("✅ Caché de Redis limpiada con éxito.")
except Exception as e:
    print(f"⚠️ Error limpiando Redis (puede que no esté en uso): {e}")

