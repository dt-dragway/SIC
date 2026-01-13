"""
SIC Ultra - Modelos SQLAlchemy

Modelos de base de datos para PostgreSQL.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime


Base = declarative_base()


class User(Base):
    """Modelo de usuario"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # 2FA
    totp_secret = Column(String(32), nullable=True)
    has_2fa = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user")
    virtual_wallet = relationship("VirtualWallet", back_populates="user", uselist=False)
    alerts = relationship("Alert", back_populates="user")


class TrustedDevice(Base):
    """Dispositivos confiables que no requieren 2FA por 30 días"""
    __tablename__ = "trusted_devices"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(String(64), unique=True, nullable=False)
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # 30 días


class Transaction(Base):
    """Transacciones reales de trading"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    symbol = Column(String(20), nullable=False)  # BTCUSDT
    side = Column(String(10), nullable=False)  # BUY, SELL
    type = Column(String(20), nullable=False)  # MARKET, LIMIT
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    order_id = Column(String(50), nullable=True)  # ID de Binance
    status = Column(String(20), default="PENDING")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")


class VirtualWallet(Base):
    """Wallet virtual para modo práctica"""
    __tablename__ = "virtual_wallets"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    initial_capital = Column(Float, default=100.0)
    balances = Column(Text, default='{"USDT": 100.0}')  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow)
    reset_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="virtual_wallet")
    trades = relationship("VirtualTrade", back_populates="wallet")


class VirtualTrade(Base):
    """Trades virtuales en modo práctica"""
    __tablename__ = "virtual_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("virtual_wallets.id"), nullable=False)
    
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    type = Column(String(20), default="MARKET") # MARKET, LIMIT
    strategy = Column(String(50), default="MANUAL") # MANUAL, AI_SIGNAL
    reason = Column(Text, nullable=True) # Contexto o razón del trade
    
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    pnl = Column(Float, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    wallet = relationship("VirtualWallet", back_populates="trades")


class Signal(Base):
    """Señales de trading generadas por el agente IA"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    
    symbol = Column(String(20), nullable=False)
    type = Column(String(10), nullable=False)  # LONG, SHORT, HOLD
    strength = Column(String(20), nullable=False)  # STRONG, MODERATE, WEAK
    confidence = Column(Float, nullable=False)  # 0-100
    
    entry_price = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    risk_reward = Column(Float, nullable=False)
    
    reasoning = Column(Text) # JSON list of reasons
    ml_data = Column(Text) # JSON storage for LSTM/XGBoost metrics
    raw_response = Column(Text) # Store full LLM response for future training
    
    # Resultado
    result = Column(String(20), nullable=True)  # WIN, LOSS, PENDING
    actual_pnl = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=True)


class Alert(Base):
    """Alertas personalizadas del usuario"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    type = Column(String(50), nullable=False)  # PRICE, P2P, SIGNAL
    symbol = Column(String(20))
    condition = Column(String(20))  # ABOVE, BELOW
    target_value = Column(Float)
    
    is_active = Column(Boolean, default=True)
    triggered_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="alerts")


class P2PRate(Base):
    """Historial de tasas P2P VES"""
    __tablename__ = "p2p_rates"
    
    id = Column(Integer, primary_key=True)
    
    avg_buy_price = Column(Float, nullable=False)
    avg_sell_price = Column(Float, nullable=False)
    best_buy_price = Column(Float, nullable=False)
    best_sell_price = Column(Float, nullable=False)
    spread_percent = Column(Float, nullable=False)
    
    offers_count = Column(Integer)
    volume = Column(Float, nullable=True)
    
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
