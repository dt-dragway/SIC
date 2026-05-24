"""
API Endpoints para Learning System
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.auth import oauth2_scheme, verify_token
from app.services.learning_engine import LearningEngine
from app.infrastructure.database.session import get_db

router = APIRouter()


class RecordResultRequest(BaseModel):
    """Registrar resultado real de un trade"""
    analysis_id: int
    actual_direction: str  # UP, DOWN, SIDEWAYS
    actual_entry: float
    actual_exit: float
    actual_pnl: float  # % profit/loss


@router.get("/progress")
async def get_ai_progress(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Obtener progreso REAL de la IA.
    Reemplaza datos hardcodeados con stats reales de aprendizaje.
    """
    verify_token(token)
    
    learning = LearningEngine(db)
    progress = learning.get_progress()
    
    return progress


@router.post("/record-result")
async def record_trade_result(
    request: RecordResultRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Registrar resultado real de un trade (FEEDBACK LOOP).
    Esto permite que la IA aprenda comparando predicción vs realidad.
    
    Ejemplo:
        IA predijo BUY con 85% confidence
        → Usuario compró
        → Precio subió 5%
        → POST /ai/record-result con actual_direction="UP", actual_pnl=5.0
        → IA gana XP y mejora accuracy
    """
    verify_token(token)
    
    try:
        learning = LearningEngine(db)
        learning.record_result(
            analysis_id=request.analysis_id,
            actual_direction=request.actual_direction,
            actual_entry=request.actual_entry,
            actual_exit=request.actual_exit,
            actual_pnl=request.actual_pnl
        )
        
        # Obtener stats actualizados
        progress = learning.get_progress()
        
        return {
            "success": True,
            "message": "Resultado registrado. IA aprendió de esta predicción.",
            "updated_progress": progress
        }
    except Exception as e:
        raise HTTPException(500, f"Error registrando resultado: {str(e)}")


@router.get("/recent-analyses")
async def get_recent_analyses(
    limit: int = 10,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Obtener análisis recientes de la IA"""
    verify_token(token)
    
    learning = LearningEngine(db)
    analyses = learning.get_recent_analyses(limit)
    
    return {
        "analyses": [
            {
                "id": a.id,
                "symbol": a.symbol,
                "recommendation": a.recommendation,
                "confidence": a.confidence,
                "tools_used": a.tools_used,
                "created_at": a.created_at.isoformat()
            }
            for a in analyses
        ]
    }
