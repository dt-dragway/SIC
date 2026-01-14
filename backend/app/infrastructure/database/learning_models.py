"""
SIC Ultra - AI Learning Models

Modelos de base de datos para sistema de aprendizaje de IA.
Permite que la IA evolucione y aprenda de sus predicciones.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.infrastructure.database.models import Base


class AIAnalysis(Base):
    """
    Registro de cada análisis realizado por la IA.
    Permite tracking de qué herramientas usó y qué recomendó.
    """
    __tablename__ = "ai_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    symbol = Column(String(20), nullable=False, index=True)
    query = Column(Text, nullable=True)  # Pregunta del usuario
    
    # Herramientas institucionales usadas
    tools_used = Column(JSON, nullable=False)  # ["microstructure", "risk", "onchain"]
    
    # Recomendación
    recommendation = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float, nullable=False)  # 0-100
    position_size = Column(Float, nullable=True)  # % del capital (Kelly)
    
    # Razonamiento
    reasoning = Column(JSON, nullable=True)  # Lista de razones
    
    # Datos del mercado en el momento
    market_data = Column(JSON, nullable=True)  # Precio, indicadores, etc
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    prediction = relationship("PredictionResult", back_populates="analysis", uselist=False)
    user = relationship("User", backref="ai_analyses")
    
    def __repr__(self):
        return f"<AIAnalysis {self.symbol} {self.recommendation} @ {self.confidence}%>"


class PredictionResult(Base):
    """
    Resultado real vs predicción.
    Fundamental para el aprendizaje: comparar lo que predijo vs lo que pasó.
    """
    __tablename__ = "prediction_results"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("ai_analyses.id"), unique=True, nullable=False)
    
    # Predicción
    predicted_direction = Column(String(10), nullable=False)  # BUY/SELL/HOLD
    predicted_confidence = Column(Float, nullable=False)
    predicted_entry = Column(Float, nullable=True)
    
    # Resultado real (NULL hasta que se cierre el trade)
    actual_direction = Column(String(10), nullable=True)  # UP/DOWN/SIDEWAYS
    actual_entry = Column(Float, nullable=True)
    actual_exit = Column(Float, nullable=True)
    actual_pnl = Column(Float, nullable=True)  # Profit/Loss en %
    
    # Evaluación
    was_correct = Column(Boolean, nullable=True)  # True si la predicción fue correcta
    error_margin = Column(Float, nullable=True)  # Diferencia entre predicho y real
    
    # Timestamps
    predicted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)  # Cuando se cerró el trade
    
    # Relationships
    analysis = relationship("AIAnalysis", back_populates="prediction")
    
    def __repr__(self):
        status = "✅" if self.was_correct else "❌" if self.was_correct is False else "⏳"
        return f"<PredictionResult {status} {self.predicted_direction} conf={self.predicted_confidence}%>"


class AIProgress(Base):
    """
    Stats globales de la IA.
    Sistema de progresión: XP, nivel, accuracy real.
    """
    __tablename__ = "ai_progress"
    
    id = Column(Integer, primary_key=True)
    
    # Progresión
    level = Column(Integer, default=1, nullable=False)
    experience_points = Column(Integer, default=0, nullable=False)
    
    # Métricas de performance
    total_analyses = Column(Integer, default=0, nullable=False)
    correct_predictions = Column(Integer, default=0, nullable=False)
    incorrect_predictions = Column(Integer, default=0, nullable=False)
    pending_predictions = Column(Integer, default=0, nullable=False)
    
    # Accuracy real (calculado)
    accuracy = Column(Float, default=0.0, nullable=False)  # %
    
    # Herramientas dominadas
    tools_mastered = Column(Integer, default=0, nullable=False)  # 0-6
    
    # Stats por herramienta (JSON)
    tool_performance = Column(JSON, nullable=True)  # {"microstructure": {"accuracy": 75}, ...}
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<AIProgress Lv.{self.level} XP:{self.experience_points} Acc:{self.accuracy}%>"
    
    @property
    def next_level_xp(self) -> int:
        """XP necesaria para siguiente nivel"""
        return (self.level + 1) * 1000
    
    @property
    def level_title(self) -> str:
        """Título según nivel"""
        if self.level < 5:
            return "Aprendiz"
        elif self.level < 10:
            return "Analista"
        elif self.level < 15:
            return "Trader Pro"
        elif self.level < 20:
            return "Experto Institucional"
        else:
            return "Maestro IA"
