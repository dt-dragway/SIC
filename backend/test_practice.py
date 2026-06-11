"""
Test manual del practice endpoint
"""
import sys
sys.path.append('.')

from app.infrastructure.database.session import SessionLocal
from app.api.v1.practice import get_or_create_wallet

db = SessionLocal()

# Crear wallet para user_id = 1
wallet = get_or_create_wallet(db, user_id=1)
print(f"✅ Wallet creada: User {wallet.user_id}, Balance: ${wallet.total_usd:.2f}")
print(f"   Balances: {wallet.balances}")

db.close()
