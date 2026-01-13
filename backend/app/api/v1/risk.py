"""
SIC Ultra - Risk Management API

Kelly Criterion y análisis de correlación.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict

from app.api.v1.auth import oauth2_scheme, verify_token


router = APIRouter()


# === Schemas ===

class KellyRequest(BaseModel):
    win_rate: float  # 0-100
    avg_win: float  # Dollar amount
    avg_loss: float  # Dollar amount


class KellyResponse(BaseModel):
    kelly_percent: float
    recommended_position: float  # % of capital
    risk_reward_ratio: float
    recommendation: str


class CorrelationData(BaseModel):
    asset_pairs: Dict[str, float]  # {"BTC-SPX": 0.65, ...}
    interpretation: str


# === Endpoints ===

@router.post("/kelly-criterion", response_model=KellyResponse)
async def calculate_kelly(
    request: KellyRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    Kelly Criterion: Calcular tamaño óptimo de posición.
    
    Fórmula: f* = (p * b - q) / b
    Donde:
    - p = probabilidad de ganar (win rate)
    - q = probabilidad de perder (1 - p)
    - b = ratio win/loss
    """
    verify_token(token)
    
    # Convertir win rate a decimal
    p = request.win_rate / 100
    q = 1 - p
    
    # Risk/Reward ratio
    if request.avg_loss == 0:
        return KellyResponse(
            kelly_percent=0,
            recommended_position=0,
            risk_reward_ratio=0,
            recommendation="⚠️ Error: Avg Loss no puede ser 0"
        )
    
    b = request.avg_win / request.avg_loss if request.avg_loss > 0 else 0
    
    # Kelly Criterion
    kelly = (p * b - q) / b if b > 0 else 0
    kelly_percent = kelly * 100
    
    # Recomendación conservadora: usar 25%-50% del Full Kelly
    recommended = kelly_percent * 0.5  # Half Kelly (más conservador)
    
    # Interpretación
    if kelly_percent <= 0:
        recommendation = "🚫 Estrategia negativa. NO operar con este sistema."
    elif recommended < 5:
        recommendation = "⚠️ Kelly muy bajo. Sistema marginal, operar con extrema precaución."
    elif recommended <= 15:
        recommendation = f"✅ Usar {recommended:.1f}% del capital por trade (Half Kelly conservador)"
    else:
        recommendation = f"⚠️ Kelly alto ({kelly_percent:.1f}%). Recomendado: max 15% por precaución"
        recommended = min(recommended, 15)
    
    return KellyResponse(
        kelly_percent=kelly_percent,
        recommended_position=recommended,
        risk_reward_ratio=b,
        recommendation=recommendation
    )


@router.get("/macro-correlation", response_model=CorrelationData)
async def get_macro_correlation(
    token: str = Depends(oauth2_scheme)
):
    """
    Correlaciones macro (simuladas).
    
    En producción:
    - Fetch real correlation data de APIs financieras
    - Calcular correlación entre BTC y S&P500, Gold, DXY, etc
    """
    verify_token(token)
    
    # SIMULACIÓN - En producción usarías datos reales
    correlations = {
        "BTC-SPX": 0.65,  # BTC vs S&P500 (equity risk-on)
        "BTC-GOLD": 0.42,  # BTC vs Gold (safe haven)
        "BTC-DXY": -0.58,  # BTC vs US Dollar Index (inverse)
        "BTC-VIX": -0.35,  # BTC vs VIX (fear index)
        "ETH-BTC": 0.88,  # ETH sigue a BTC
        "ALTS-BTC": 0.72  # Altcoins correlacionan con BTC
    }
    
    interpretation = """
📊 **Interpretación:**
- **BTC-SPX (0.65)**: Alta correlación con equities. BTC actúa como risk-on asset.
- **BTC-DXY (-0.58)**: Correlación negativa con USD. Dólar fuerte = BTC débil.
- **ETH-BTC (0.88)**: ETH muy correlacionado, movimientos similares.

💡 **Estrategia**: Cuando stocks caen, espera caída en BTC. Diversifica fuera de crypto.
    """
    
    return CorrelationData(
        asset_pairs=correlations,
        interpretation=interpretation.strip()
    )
