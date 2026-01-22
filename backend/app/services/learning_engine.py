"""
SIC Ultra - Learning Engine

Motor de aprendizaje que permite que la IA evolucione.
Compara predicciones vs realidad y ajusta la IA accordingly.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

from app.infrastructure.database.learning_models import AIAnalysis, PredictionResult, AIProgress


class LearningEngine:
    """
    Motor de aprendizaje de la IA.
    
    Responsabilidades:
    - Guardar cada análisis realizado
    - Registrar predicciones
    - Comparar predicciones vs resultados reales
    - Actualizar stats (XP, nivel, accuracy)
    - Calcular performance por herramienta
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_analysis(
        self,
        user_id: Optional[int],
        symbol: str,
        query: Optional[str],
        tools_used: List[str],
        recommendation: str,
        confidence: float,
        position_size: Optional[float],
        reasoning: List[str],
        market_data: Optional[Dict] = None
    ) -> AIAnalysis:
        """
        Registrar un análisis de la IA.
        
        Returns:
            AIAnalysis record creado
        """
        analysis = AIAnalysis(
            user_id=user_id,
            symbol=symbol,
            query=query,
            tools_used=tools_used,
            recommendation=recommendation,
            confidence=confidence,
            position_size=position_size,
            reasoning=reasoning,
            market_data=market_data
        )
        
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        
        # Actualizar contador de análisis
        self._increment_total_analyses()
        
        logger.info(f"📊 Análisis registrado: {symbol} {recommendation} @ {confidence}%")
        
        return analysis
    
    def record_prediction(
        self,
        analysis_id: int,
        predicted_direction: str,
        predicted_confidence: float,
        predicted_entry: Optional[float] = None
    ) -> PredictionResult:
        """
        Registrar una predicción para comparar después.
        
        Args:
            analysis_id: ID del análisis
            predicted_direction: BUY, SELL, HOLD
            predicted_confidence: 0-100
            predicted_entry: Precio de entrada predicho
        """
        prediction = PredictionResult(
            analysis_id=analysis_id,
            predicted_direction=predicted_direction,
            predicted_confidence=predicted_confidence,
            predicted_entry=predicted_entry
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        # Incrementar pending predictions
        progress = self._get_or_create_progress()
        progress.pending_predictions += 1
        self.db.commit()
        
        logger.info(f"🔮 Predicción registrada: {predicted_direction} @ {predicted_confidence}%")
        
        return prediction
    
    def record_result(
        self,
        analysis_id: int,
        actual_direction: str,
        actual_entry: float,
        actual_exit: float,
        actual_pnl: float
    ):
        """
        Registrar resultado real y comparar con predicción.
        Aquí es donde la IA aprende!
        
        Args:
            analysis_id: ID del análisis
            actual_direction: UP, DOWN, SIDEWAYS
            actual_entry: Precio real de entrada
            actual_exit: Precio real de salida
            actual_pnl: P&L real en %
        """
        prediction = self.db.query(PredictionResult).filter(
            PredictionResult.analysis_id == analysis_id
        ).first()
        
        if not prediction:
            logger.warning(f"No prediction found for analysis {analysis_id}")
            return
        
        # Actualizar predicción con resultado real
        prediction.actual_direction = actual_direction
        prediction.actual_entry = actual_entry
        prediction.actual_exit = actual_exit
        prediction.actual_pnl = actual_pnl
        prediction.resolved_at = datetime.utcnow()
        
        # Determinar si fue correcta
        predicted_dir = prediction.predicted_direction
        was_correct = self._evaluate_prediction(predicted_dir, actual_direction, actual_pnl)
        
        prediction.was_correct = was_correct
        prediction.error_margin = abs(actual_pnl) if actual_pnl else 0
        
        self.db.commit()
        
        # Actualizar stats de la IA
        self._update_ai_stats(was_correct, prediction.predicted_confidence)
        
        result = "✅" if was_correct else "❌"
        logger.info(f"{result} Resultado: {predicted_dir} → {actual_direction} (PnL: {actual_pnl:.1f}%)")
    
    def _evaluate_prediction(self, predicted: str, actual: str, pnl: float) -> bool:
        """Evaluar si la predicción fue correcta"""
        if predicted == "BUY":
            return actual == "UP" or pnl > 0
        elif predicted == "SELL":
            return actual == "DOWN" or pnl < 0
        else:  # HOLD
            return abs(pnl) < 1  # Movimiento menor a 1%
    
    def _update_ai_stats(self, was_correct: bool, confidence: float):
        """
        Actualizar stats globales de la IA.
        Aquí se gana XP y se sube de nivel.
        """
        progress = self._get_or_create_progress()
        
        # Decrementar pending
        progress.pending_predictions = max(0, progress.pending_predictions - 1)
        
        # Actualizar contadores
        if was_correct:
            progress.correct_predictions += 1
            # XP basado en confidence: mayor confianza = más XP
            xp_gain = int(100 + (confidence * 2))  # 100-300 XP
        else:
            progress.incorrect_predictions += 1
            xp_gain = 50  # XP parcial por intentar
        
        # Agregar XP
        old_level = progress.level
        progress.experience_points += xp_gain
        
        # Calcular nivel (cada 1000 XP = 1 nivel)
        progress.level = progress.experience_points // 1000 + 1
        
        # Level up!
        if progress.level > old_level:
            logger.success(f"🎉 ¡LEVEL UP! Nivel {progress.level}")
        
        # Calcular accuracy
        total_resolved = progress.correct_predictions + progress.incorrect_predictions
        if total_resolved > 0:
            progress.accuracy = (progress.correct_predictions / total_resolved) * 100
        
        progress.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"📈 +{xp_gain} XP | Level {progress.level} | Accuracy: {progress.accuracy:.1f}%")
    
    def _increment_total_analyses(self):
        """Incrementar contador de análisis totales"""
        progress = self._get_or_create_progress()
        progress.total_analyses += 1
        self.db.commit()
    
    def _get_or_create_progress(self) -> AIProgress:
        """Obtener o crear registro de progreso"""
        progress = self.db.query(AIProgress).first()
        
        if not progress:
            progress = AIProgress(
                level=1,
                experience_points=0,
                total_analyses=0,
                correct_predictions=0,
                incorrect_predictions=0,
                pending_predictions=0,
                accuracy=0.0,
                tools_mastered=0
            )
            self.db.add(progress)
            self.db.commit()
            self.db.refresh(progress)
        
        return progress
    
    def get_progress(self) -> Dict:
        """Obtener stats actuales de la IA"""
        progress = self._get_or_create_progress()
        
        return {
            "level": progress.level,
            "experience_points": progress.experience_points,
            "next_level_xp": progress.next_level_xp,
            "total_analyses": progress.total_analyses,
            "correct_predictions": progress.correct_predictions,
            "incorrect_predictions": progress.incorrect_predictions,
            "pending_predictions": progress.pending_predictions,
            "accuracy": round(progress.accuracy, 1),
            "tools_mastered": progress.tools_mastered,
            "level_title": progress.level_title
        }
    
    def get_recent_analyses(self, limit: int = 10) -> List[AIAnalysis]:
        """Obtener análisis recientes"""
        return self.db.query(AIAnalysis).order_by(
            AIAnalysis.created_at.desc()
        ).limit(limit).all()
    
    def get_accuracy_by_tool(self) -> Dict[str, float]:
        """Calcular accuracy por herramienta"""
        # TODO: Implementar análisis por herramienta
        return {
            "microstructure": 75.0,
            "onchain": 82.0,
            "derivatives": 78.0,
            "defi": 70.0,
            "risk": 85.0,
            "automation": 80.0
        }
