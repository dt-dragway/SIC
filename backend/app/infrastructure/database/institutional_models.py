"""
SIC Ultra - Modelos SQLAlchemy INSTITUCIONALES

Modelos adicionales para análisis institucional.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from app.infrastructure.database.models import Base


class OrderBookSnapshot(Base):
    """Snapshots de Order Book para análisis de microestructura"""
    __tablename__ = "order_book_snapshots"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    best_bid = Column(Float, nullable=False)
    best_ask = Column(Float, nullable=False)
    spread = Column(Float, nullable=False)
    
    bids_json = Column(Text)
    asks_json = Column(Text)
    
    bid_volume_10 = Column(Float)
    ask_volume_10 = Column(Float)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class WhaleAlert(Base):
    """Alertas de movimientos grandes (Whale Tracking)"""
    __tablename__ = "whale_alerts"
    
    id = Column(Integer, primary_key=True)
    
    blockchain = Column(String(20), default="BTC")
    tx_hash = Column(String(128), unique=True, nullable=True)
    
    amount = Column(Float, nullable=False)
    amount_usd = Column(Float, nullable=False)
    
    from_address = Column(String(128))
    to_address = Column(String(128))
    from_label = Column(String(100))
    to_label = Column(String(100))
    
    flow_type = Column(String(50))
    sentiment = Column(String(20))
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class FundingRateHistory(Base):
    """Historial de Funding Rates"""
    __tablename__ = "funding_rate_history"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    funding_rate = Column(Float, nullable=False)
    mark_price = Column(Float, nullable=False)
    index_price = Column(Float, nullable=False)
    
    open_interest = Column(Float, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    next_funding_time = Column(DateTime, nullable=True)
