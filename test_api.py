import asyncio
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import AutomationConfig

db = SessionLocal()
config = db.query(AutomationConfig).filter(AutomationConfig.user_id == 1).first()
if config:
    print("CONFIG IN DB:")
    print("min_confidence:", config.min_signal_confidence)
    print("allowed_tiers:", config.allowed_tiers)
    print("enabled:", config.enabled)

