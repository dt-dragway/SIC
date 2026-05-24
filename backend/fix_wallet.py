from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import VirtualWallet, VirtualTrade
from datetime import datetime
import json

db = next(get_db())
wallet = db.query(VirtualWallet).filter(VirtualWallet.user_id == 1).first()

if wallet:
    print(f"fixing wallet {wallet.id}...")
    # Reset to $5000 clean
    wallet.balances = json.dumps({"USDT": 5000.0})
    wallet.initial_capital = 5000.0
    wallet.reset_at = datetime.utcnow()
    
    # Clear trades
    trades = db.query(VirtualTrade).filter(VirtualTrade.wallet_id == wallet.id).delete()
    
    db.commit()
    print("✅ Wallet reset to $5,000 USDT. PnL should be 0.")
else:
    print("❌ Wallet not found")
