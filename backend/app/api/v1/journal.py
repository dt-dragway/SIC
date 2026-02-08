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
    return JournalService.create_entry(db, user_data["sub"], entry_data.dict())

@router.get("/metrics")
async def get_metrics(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user_data = verify_token(token)
    return JournalService.get_performance_metrics(db, user_data["sub"])
