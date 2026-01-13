"""
SIC Ultra - On-Chain Analysis API

Whale Tracking y análisis de flujos blockchain.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.api.v1.auth import oauth2_scheme, verify_token
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import WhaleAlert


router = APIRouter()


# === Schemas ===

class WhaleAlertResponse(BaseModel):
    id: int
    blockchain: str
    amount: float
    amount_usd: float
    from_label: Optional[str]
    to_label: Optional[str]
    flow_type: str
    sentiment: str
    timestamp: datetime


class WhaleAlertSummary(BaseModel):
    total_alerts: int
    total_volume_usd: float
    exchange_inflows: int
    exchange_outflows: int
    whale_to_whale: int
    bullish_signals: int
    bearish_signals: int


# === Endpoints ===

@router.get("/whale-feed", response_model=List[WhaleAlertResponse])
async def get_whale_feed(
    blockchain: str = "BTC",
    limit: int = 50,
    hours: int = 24,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Feed en vivo de Whale Alerts.
    
    Retorna movimientos grandes detectados en las últimas X horas.
    """
    verify_token(token)
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    alerts = db.query(WhaleAlert)\
        .filter(WhaleAlert.blockchain == blockchain.upper())\
        .filter(WhaleAlert.timestamp >= cutoff_time)\
        .order_by(WhaleAlert.timestamp.desc())\
        .limit(limit)\
        .all()
    
    return [
        WhaleAlertResponse(
            id=a.id,
            blockchain=a.blockchain,
            amount=a.amount,
            amount_usd=a.amount_usd,
            from_label=a.from_label,
            to_label=a.to_label,
            flow_type=a.flow_type,
            sentiment=a.sentiment,
            timestamp=a.timestamp
        ) for a in alerts
    ]


@router.get("/whale-summary", response_model=WhaleAlertSummary)
async def get_whale_summary(
    blockchain: str = "BTC",
    hours: int = 24,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Resumen de actividad de ballenas.
    """
    verify_token(token)
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    alerts = db.query(WhaleAlert)\
        .filter(WhaleAlert.blockchain == blockchain.upper())\
        .filter(WhaleAlert.timestamp >= cutoff_time)\
        .all()
    
    total_volume = sum(a.amount_usd for a in alerts)
    inflows = len([a for a in alerts if a.flow_type == "exchange_inflow"])
    outflows = len([a for a in alerts if a.flow_type == "exchange_outflow"])
    whale_moves = len([a for a in alerts if a.flow_type == "whale_to_whale"])
    
    bullish = len([a for a in alerts if a.sentiment == "bullish"])
    bearish = len([a for a in alerts if a.sentiment == "bearish"])
    
    return WhaleAlertSummary(
        total_alerts=len(alerts),
        total_volume_usd=total_volume,
        exchange_inflows=inflows,
        exchange_outflows=outflows,
        whale_to_whale=whale_moves,
        bullish_signals=bullish,
        bearish_signals=bearish
    )


@router.post("/simulate-whale")
async def simulate_whale_alert(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    🧪 Simular una whale alert para testing.
    SOLO para desarrollo - en producción conectaríamos a Whale Alert API real.
    """
    verify_token(token)
    
    import random
    
    flow_types = ["exchange_inflow", "exchange_outflow", "whale_to_whale"]
    flow = random.choice(flow_types)
    
    # Lógica de sentimiento
    if flow == "exchange_outflow":
        sentiment = "bullish"  # Salida de exchanges = acumulación
    elif flow == "exchange_inflow":
        sentiment = "bearish"  # Entrada a exchanges = presión de venta
    else:
        sentiment = "neutral"
    
    whale = WhaleAlert(
        blockchain="BTC",
        tx_hash=f"0x{''.join(random.choices('0123456789abcdef', k=64))}",
        amount=random.uniform(50, 500),
        amount_usd=random.uniform(1_000_000, 10_000_000),
        from_address="0xABC...123",
        to_address="0xDEF...456",
        from_label="Whale Wallet" if flow != "exchange_inflow" else "Binance Cold",
        to_label="Binance Cold" if flow == "exchange_inflow" else "Unknown Wallet",
        flow_type=flow,
        sentiment=sentiment,
        timestamp=datetime.utcnow()
    )
    
    db.add(whale)
    db.commit()
    db.refresh(whale)
    
    return {
        "message": f"✅ Whale alert simulada: {flow}",
        "alert": {
            "amount_usd": whale.amount_usd,
            "flow_type": whale.flow_type,
            "sentiment": whale.sentiment
        }
    }
