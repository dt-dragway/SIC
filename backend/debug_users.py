from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import User, VirtualWallet
from sqlalchemy.orm import Session

db = next(get_db())
users = db.query(User).all()

print(f"Found {len(users)} users")
for u in users:
    print(f"User ID: {u.id}, Email: {u.email}, Name: {u.name}")
    wallet = db.query(VirtualWallet).filter(VirtualWallet.user_id == u.id).first()
    if wallet:
        print(f"  -> Has Wallet ID: {wallet.id}")
    else:
        print("  -> No Wallet")
