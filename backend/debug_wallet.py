from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import VirtualWallet, VirtualTrade
from sqlalchemy.orm import Session
import json

db = next(get_db())
wallets = db.query(VirtualWallet).all()

print(f"Found {len(wallets)} wallets")
for w in wallets:
    print(f"Wallet ID: {w.id}, User: {w.user_id}")
    print(f"Initial Capital: {w.initial_capital}")
    print(f"Balances: {w.balances}")
    trades_count = db.query(VirtualTrade).filter(VirtualTrade.wallet_id == w.id).count()
    print(f"Trades Count: {trades_count}")
    print("-" * 30)
