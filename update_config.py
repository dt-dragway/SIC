import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

try:
    engine = create_engine("postgresql://postgres:admin2425@localhost:5433/sic_db")
    Session = sessionmaker(bind=engine)
    db = Session()
    
    db.execute(text("""
        UPDATE automation_configs 
        SET min_signal_confidence = 50, 
            allowed_tiers = '["S", "A", "B", "C"]',
            spot_enabled = true,
            futures_enabled = true
        WHERE user_id = 1
    """))
    db.commit()
    print("✅ Config updated.")
except Exception as e:
    print("DB_ERROR:", e)
