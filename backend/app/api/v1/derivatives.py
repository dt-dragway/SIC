"""
SIC Ultra - Derivatives API

Delta Neutral Trading y Basis Opportunities.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

from app.api.v1.auth import oauth2_scheme, verify_token
from app.infrastructure.binance.client import get_binance_client


router = APIRouter()


# === Schemas ===

class BasisOpportunity(BaseModel):
    symbol: str
    spot_price: float
    futures_price: float
    basis_points: float
    basis_percent: float
    funding_rate: float
    apr_estimate: float
    recommended: bool


class HedgeRequest(BaseModel):
    spot_holdings: Dict[str, float]  # {"BTCUSDT": 2.5}
    futures_positions: List[Dict[str, float]]  # [{"symbol": "BTCUSDT", "size": -1.0}]


class HedgeResponse(BaseModel):
    symbol: str
    current_delta: float
    required_hedge: float
    recommendation: str


# === Endpoints ===

@router.get("/basis-opportunities", response_model=List[BasisOpportunity])
async def get_basis_opportunities(
    token: str = Depends(oauth2_scheme)
):
    """
    Escanear oportunidades de Basis Trading (Spot vs Futures).
    
    Identifica pares donde puedes ganar funding rates sin riesgo direccional.
    """
    verify_token(token)
    client = get_binance_client()
    
    # Símbolos principales para escanear
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
    opportunities = []
    
    for symbol in symbols:
        try:
            # Spot price
            spot_ticker = client.client.get_symbol_ticker(symbol=symbol)
            spot_price = float(spot_ticker['price'])
            
            # Futures price (Mark Price)
            funding_data = client.get_funding_rate(symbol)
            if not funding_data:
                continue
                
            futures_price = funding_data['markPrice']
            funding_rate = funding_data['fundingRate']
            
            # Calcular Basis
            basis_points = futures_price - spot_price
            basis_percent = (basis_points / spot_price) * 100
            
            # APR Estimate (Funding Rate * 3 veces al día * 365 días + Basis al cierre)
            annual_funding = funding_rate * 3 * 365 * 100  # en %
            apr_estimate = annual_funding + (basis_percent if basis_percent > 0 else 0)
            
            # Recomendación: APR > 5% y Funding Rate positivo
            recommended = apr_estimate > 5.0 and funding_rate > 0.0001
            
            opportunities.append(BasisOpportunity(
                symbol=symbol,
                spot_price=spot_price,
                futures_price=futures_price,
                basis_points=basis_points,
                basis_percent=basis_percent,
                funding_rate=funding_rate,
                apr_estimate=apr_estimate,
                recommended=recommended
            ))
            
        except Exception as e:
            print(f"Error scanning {symbol}: {e}")
            continue
    
    # Ordenar por APR descendente
    opportunities.sort(key=lambda x: x.apr_estimate, reverse=True)
    
    return opportunities


@router.post("/hedge-calculator", response_model=List[HedgeResponse])
async def calculate_hedge(
    request: HedgeRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    Calcular hedge necesario para neutralizar delta.
    
    Delta = Spot Position + Futures Position
    Para Delta Neutral: Delta debe = 0
    """
    verify_token(token)
    
    results = []
    
    for symbol, spot_amount in request.spot_holdings.items():
        # Sumar todas las posiciones de futures del mismo símbolo
        futures_total = sum(
            pos.get("size", 0) 
            for pos in request.futures_positions 
            if pos.get("symbol") == symbol
        )
        
        current_delta = spot_amount + futures_total
        required_hedge = -current_delta
        
        if abs(current_delta) < 0.0001:
            recommendation = f"✅ Delta Neutral ({current_delta:.4f})"
        elif current_delta > 0:
            recommendation = f"⚠️ Short {abs(required_hedge):.4f} {symbol.replace('USDT', '')} en Futures para neutralizar"
        else:
            recommendation = f"⚠️ Long {abs(required_hedge):.4f} {symbol.replace('USDT', '')} en Futures para neutralizar"
        
        results.append(HedgeResponse(
            symbol=symbol,
            current_delta=current_delta,
            required_hedge=required_hedge,
            recommendation=recommendation
        ))
    
    return results
