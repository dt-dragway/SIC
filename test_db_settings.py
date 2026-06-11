from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import AutomationConfig
from app.api.v1.automated_trading import AutomationSettings

db = SessionLocal()
config = db.query(AutomationConfig).filter(AutomationConfig.user_id == 1).first()

try:
    settings = AutomationSettings(
        enabled=config.enabled,
        max_daily_trades=config.max_daily_trades,
        max_position_size=config.max_position_size,
        min_signal_confidence=config.min_signal_confidence,
        allowed_tiers=config.allowed_tiers or ["S", "A"],
        risk_level=config.risk_level,
        pause_on_high_volatility=config.pause_on_high_volatility,
        check_interval_seconds=config.check_interval_seconds,
        practice_mode_only=config.practice_mode_only,
        spot_enabled=config.spot_enabled,
        futures_enabled=config.futures_enabled
    )
    print("ÉXITO AL PARSEAR:", settings.model_dump())
except Exception as e:
    print("ERROR AL PARSEAR PYDANTIC:", str(e))

