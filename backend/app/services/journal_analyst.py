from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.infrastructure.database.models import JournalEntry
from app.ml.llm_connector import get_llm_manager
from loguru import logger
import json
import re

class JournalAnalyst:
    def __init__(self):
        self.llm = get_llm_manager()

    def analyze_performance(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Analiza el historial de trades del usuario usando IA para encontrar patrones,
        fortalezas y debilidades.
        """
        # 1. Obtener últimos 20 trades
        entries = db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id
        ).order_by(JournalEntry.created_at.desc()).limit(20).all()

        if not entries:
            return {
                "strengths": ["No hay suficientes datos"],
                "weaknesses": ["Registra más trades para análisis"],
                "psychology": "Neutro",
                "actionable_tip": "Comienza a operar y registrar tus resultados."
            }

        # 2. Formatear datos para el LLM
        trades_text = self._format_trades(entries)

        # 3. Construir Prompt
        prompt = f"""
        Actúa como un Coach de Trading Institucional de alto nivel.
        Analiza los siguientes últimos {len(entries)} trades de mi diario:

        {trades_text}

        Tu tarea es identificar patrones ocultos en mi comportamiento y resultados.
        
        Responde ESTRICTAMENTE en formato JSON con esta estructura (sin markdown, solo JSON válido):
        {{
            "strengths": ["punto fuerte 1", "punto fuerte 2"],
            "weaknesses": ["fuga de capital 1", "error mental 2"],
            "psychology": "Evaluación breve de mi estado emocional (basado en 'mood' y notas)",
            "actionable_tip": "Un consejo concreto y accionable para mejorar esta semana"
        }}
        """

        # 4. Enviar a LLM
        try:
            # Usamos un proveedor directamente si el manager lo permite o el método analyze genérico
            # El LLMManager actual tiene analyze_market, pero necesitamos uno genérico.
            # Vamos a usar el active_provider directamente si es posible, o añadir un método raw_analyze al manager.
            # Al revisar LLMManager, los proveedores tienen .analyze(prompt).
            # Accedemos al proveedor activo.
            
            if not self.llm.is_available:
                return {
                    "strengths": ["IA no disponible"],
                    "weaknesses": ["Verifica configuración de LLM"],
                    "psychology": "N/A",
                    "actionable_tip": "Contacta soporte."
                }

            response_text = "Simulando respuesta si no es async..." 
            # Nota: LLMManager.analyze_market es async, pero los providers tienen analyze async.
            # Necesitamos llamar async. Este método debería ser async.
            
            # ESPERA: Este método debe ser async para llamar al LLM
            return {
                "error": "Debe ser llamado con await" 
            } 
        except Exception as e:
            logger.error(f"Error en JournalAnalyst: {e}")
            return {
                "strengths": [],
                "weaknesses": ["Error analizando datos"],
                "psychology": "N/A",
                "actionable_tip": "Intenta más tarde."
            }

    async def analyze_performance_async(self, db: Session, user_id: int) -> Dict[str, Any]:
        try:
            logger.info(f"🧠 JournalAnalyst start for user {user_id}")
            entries = db.query(JournalEntry).filter(
                JournalEntry.user_id == user_id
            ).order_by(JournalEntry.created_at.desc()).limit(20).all()

            if len(entries) < 3:
                 return {
                    "strengths": ["Faltan datos"],
                    "weaknesses": ["Se requieren mínimo 3 trades"],
                    "psychology": "N/A",
                    "actionable_tip": "Registra al menos 3 operaciones para recibir análisis."
                }

            trades_text = self._format_trades(entries)
            
            prompt = f"""
            Actúa como un Coach de Trading Institucional. Analiza estos trades del usuario:
            
            {trades_text}
            
            Identifica patrones de éxito y fracaso. Presta atención al 'Mood' y 'Notes'.
            
            Responde SOLO con un JSON válido (sin bloques de código ```json):
            {{
                "strengths": ["breve punto 1", "breve punto 2"],
                "weaknesses": ["breve punto 1", "breve punto 2"],
                "psychology": "Resumen del estado mental detectado",
                "actionable_tip": "Consejo directo de 1 frase"
            }}
            """
            
            # Check availability
            if not self.llm.is_available:
                logger.warning("⚠️ LLM no disponible, retornando respuesta simulada.")
                return self._get_mock_response()
                 
            # Acceder al proveedor activo de forma segura
            response = await self.llm._active_provider.analyze(prompt)
            
            if not response:
                logger.warning("⚠️ LLM retornó vacío, retornando respuesta simulada.")
                return self._get_mock_response()
                
            return self._parse_json(response)
            
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR en JournalAnalyst: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._get_mock_response(error_msg=str(e))

    def _get_mock_response(self, error_msg: str = "") -> Dict[str, Any]:
        """Respuesta simulada para cuando falla la IA o no hay keys"""
        tip = "Configura las API Keys de DeepSeek o OpenAI para análisis real."
        if error_msg:
            tip += f" (Error: {error_msg})"
            
        return {
            "strengths": ["Gestión de riesgo consistente (Simulado)", "Buena selección de activos (Simulado)"],
            "weaknesses": ["Falta paciencia en entradas (Simulado)", "Sobreoperar en rangos (Simulado)"],
            "psychology": "Ansiedad detectada en días de pérdidas. (Simulado)",
            "actionable_tip": tip
        }

    def _format_trades(self, entries: List[JournalEntry]) -> str:
        lines = []
        for e in entries:
            result = "WIN" if e.pnl > 0 else "LOSS"
            lines.append(f"- {e.symbol} ({e.side}): {result} (${e.pnl}). Mood: {e.mood}. Strategy: {e.strategy}. Notes: {e.notes}")
        return "\n".join(lines)

    def _parse_json(self, text: str) -> Dict[str, Any]:
        try:
            # Limpiar markdown si existe
            clean_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except json.JSONDecodeError:
            logger.warning(f"Fallo al parsear JSON de IA: {text}")
            return {
                "strengths": ["Análisis generado (formato raw)"],
                "weaknesses": [],
                "psychology": "Ver raw output",
                "actionable_tip": text[:200] + "..."
            }

# Singleton
journal_analyst = JournalAnalyst()
