from fastapi import APIRouter, Depends
from typing import Dict, Any, Optional
from app.api.v1.auth import oauth2_scheme, verify_token
from app.services.sentiment_analysis import get_sentiment_service

router = APIRouter()

@router.get("/market", response_model=Dict[str, Any])
async def get_market_sentiment(
    symbol: str = "BTCUSDT",
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener el sentimiento del mercado y noticias relevantes.
    """
    verify_token(token)
    service = get_sentiment_service()
    clean_symbol = symbol.replace("USDT", "")
    return await service.get_market_sentiment(clean_symbol)

@router.get("/fear-greed", response_model=Dict[str, Any])
async def get_fear_greed_index(
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener el índice de Miedo y Codicia (Fear & Greed Index).
    """
    verify_token(token)
    # En producción llamaríamos a: https://api.alternative.me/fng/
    service = get_sentiment_service()
    data = await service.get_market_sentiment("BTC")
    return {
        "value": int(data["overall_score"]),
        "value_classification": data["label"],
        "timestamp": data["timestamp"]
    }
