"""
SIC Ultra - AI Institutional Analysis API

Endpoint para análisis comprehensivo usando IA institucional.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

from app.api.v1.auth import oauth2_scheme, verify_token
from app.services.ai_agent import institutional_agent


router = APIRouter()


# === Schemas ===

class AnalysisRequest(BaseModel):
    symbol: str
    query: str
    context: Optional[Dict] = None  # Balance, posiciones, historial


class AnalysisResponse(BaseModel):
    symbol: str
    query: str
    tools_used: list
    recommendation: Dict
    data: Dict
    timestamp: str


# === Endpoints ===

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_comprehensive(
    request: AnalysisRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    Análisis comprehensivo institucional usando IA.
    
    La IA decide automáticamente qué herramientas usar según el contexto:
    - Microstructure (Order Book, Funding Rate)
    - On-Chain (Whale Alerts)
    - Derivatives (Basis Trading, Delta Neutral)
    - DeFi (IL Calculator)
    - Risk Management (Kelly Criterion)
    - Automation (Backtesting)
    
    Ejemplo:
        Query: "¿Debería comprar BTC?"
        -> IA usa: microstructure + onchain + risk
        -> Retorna: Recomendación BUY/SELL/HOLD con confianza
    """
    verify_token(token)
    
    try:
        result = await institutional_agent.analyze_comprehensive(
            symbol=request.symbol,
            user_query=request.query,
            token=token,
            context=request.context
        )
        
        return AnalysisResponse(**result)
        
    except Exception as e:
        raise HTTPException(500, f"Error en análisis IA: {str(e)}")


@router.get("/tools", tags=["AI"])
async def list_available_tools(token: str = Depends(oauth2_scheme)):
    """Lista todas las herramientas institucionales disponibles"""
    verify_token(token)
    
    return {
        "tools": institutional_agent.available_tools,
        "categories": list(institutional_agent.available_tools.keys())
    }
