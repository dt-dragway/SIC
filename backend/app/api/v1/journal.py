from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.api.v1.auth import oauth2_scheme, verify_token
from app.infrastructure.database.session import get_db
from app.services.journal_service import JournalService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class JournalCreate(BaseModel):
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float] = None
    pnl: float = 0.0
    mood: str = "CALM"
    strategy: str = "MANUAL"
    notes: str = ""
    lessons: str = ""
    rating: int = 3

@router.get("/entries")
async def get_entries(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user_data = verify_token(token)
    return JournalService.get_entries(db, user_data["sub"])

@router.post("/entries")
async def create_entry(
    entry_data: JournalCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    return JournalService.create_entry(db, user_data["user_id"], entry_data.dict())

@router.get("/metrics")
async def get_metrics(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user_data = verify_token(token)
    if not user_data:
         raise HTTPException(status_code=401, detail="Invalid token")
    return JournalService.get_performance_metrics(db, user_data["user_id"])

@router.post("/analyze")
async def analyze_journal(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Genera un reporte de inteligencia artificial sobre el desempeño del trader.
    """
    from loguru import logger
    logger.info("📡 Endpoint /analyze hittet!")
    logger.info("Step 1: Importing service")
    from app.services.journal_analyst import journal_analyst
    logger.info("Step 2: Verifying token")
    user_data = verify_token(token)
    logger.info(f"Step 3: User Data: {user_data}")
    user_id = user_data.get("user_id")
    if not user_id:
        # Fallback for old tokens or different structure
        logger.warning(f"⚠️ user_id missing in token, using id=1 as fallback. Sub: {user_data.get('sub')}")
        user_id = 1
        
    result = await journal_analyst.analyze_performance_async(db, user_id)
    logger.info(f"Step 4: Result: {result}")
    return result
