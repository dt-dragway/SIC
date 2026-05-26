import sys
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
try:
    engine = create_engine("postgresql://postgres:admin2425@localhost:5433/sic_db")
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # Check trades today
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    result = db.execute("SELECT symbol, side, status, amount, created_at FROM trades WHERE created_at >= :today ORDER BY created_at DESC", {"today": today})
    trades = result.fetchall()
    
    print(f"TRADES_TODAY={len(trades)}")
    for t in trades:
        print(f" - {t.created_at}: {t.side} {t.amount} {t.symbol} ({t.status})")
        
    # Also check if it's scanning
    print("---")
except Exception as e:
    print("DB_ERROR:", e)
