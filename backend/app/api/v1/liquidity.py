from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.api.v1.auth import oauth2_scheme, verify_token
from app.services.liquidity_service import get_liquidity_service

router = APIRouter()

@router.get("/heatmap", response_model=List[Dict[str, Any]])
async def get_market_heatmap(
    token: str = Depends(oauth2_scheme)
):
    """
    Obtener datos del mapa de calor del mercado (Heatmap) por sectores.
    """
    verify_token(token)
    service = get_liquidity_service()
    return await service.get_market_heatmap()

@router.get("/sector-strength")
async def get_sector_strength(
    token: str = Depends(oauth2_scheme)
):
    """
    Analizar qué sectores están liderando el mercado (Dominancia).
    """
    verify_token(token)
    heatmap = await get_liquidity_service().get_market_heatmap()
    
    sectors = {}
    for item in heatmap:
        s = item["sector"]
        if s not in sectors:
            sectors[s] = {"total_change": 0, "count": 0, "volume": 0}
        sectors[s]["total_change"] += item["change_24h"]
        sectors[s]["count"] += 1
        sectors[s]["volume"] += item["volume_usd"]
        
    result = []
    for s, data in sectors.items():
        result.append({
            "sector": s,
            "avg_change": data["total_change"] / data["count"],
            "total_volume": data["volume"]
        })
        
    return sorted(result, key=lambda x: x["avg_change"], reverse=True)
