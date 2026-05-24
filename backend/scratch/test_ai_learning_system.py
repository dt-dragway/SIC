import os
import sys
import asyncio
from datetime import datetime, timedelta
from loguru import logger

# Agregar backend a la ruta de python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.binance.client import get_binance_client
from app.ml.llm_connector import get_llm_manager, OllamaProvider
from app.services.learning_engine import LearningEngine
from app.ml.post_trade_analyzer import get_post_trade_analyzer
from app.ml.trading_agent import get_trading_agent
from app.infrastructure.database.learning_models import AIProgress, AIAnalysis, PredictionResult

async def run_rigorous_ai_test():
    logger.info("🧪 Iniciando Prueba Rigurosa del Sistema de Aprendizaje IA & Gemma 2B...")
    
    # 1. Verificar Ollama y Gemma 2B
    logger.info("🔍 [PASO 1] Verificando conexión local con Ollama y modelo Gemma...")
    provider = OllamaProvider()
    if not provider.is_available():
        logger.error("❌ Ollama no responde en http://localhost:11434. Asegúrate de que el servicio esté corriendo.")
        return
        
    logger.info(f"✅ Ollama detectado. Modelo predeterminado: {provider.model}")
    
    # Probar inferencia en tiempo real
    prompt_prueba = (
        "ANÁLISIS TÉCNICO:\n"
        "Symbol: BTCUSDT\n"
        "Price: $67,500\n"
        "RSI: 22 (sobreventa extrema)\n"
        "MACD: alcista cruzando a positivo\n"
        "Sugerencia: BUY/SELL/HOLD? Da confianza % y justificación."
    )
    
    logger.info("🧠 Enviando consulta de prueba a Gemma:2b en Ollama (Primera carga, por favor espera)...")
    t_start = datetime.now()
    response = await provider.analyze(prompt_prueba)
    t_end = datetime.now()
    duration = (t_end - t_start).total_seconds()
    
    if not response:
        logger.error("❌ Gemma no devolvió respuesta. Revisa el log de Ollama.")
        return
        
    logger.success(f"⚡ Inferencia de Gemma completada exitosamente en {duration:.2f} segundos!")
    logger.info(f"📝 Respuesta de Gemma:\n----------------------\n{response}\n----------------------")

    # 2. Inicializar Motores y Base de Datos
    logger.info("⚙️ [PASO 2] Conectando a la base de datos PostgreSQL de SIC Ultra...")
    db = SessionLocal()
    learning_engine = LearningEngine(db)
    post_analyzer = get_post_trade_analyzer()
    
    # Obtener el progreso inicial de la IA
    initial_progress = learning_engine._get_or_create_progress()
    logger.info(
        f"📊 Progreso inicial de la IA:\n"
        f"   - Nivel: {initial_progress.level}\n"
        f"   - Puntos de Experiencia (XP): {initial_progress.experience_points}\n"
        f"   - Precisión (Accuracy): {initial_progress.accuracy:.1f}%\n"
        f"   - Análisis Totales: {initial_progress.total_analyses}"
    )

    # 3. Simular un Ciclo Completo de Aprendizaje por Refuerzo (RLMF)
    logger.info("🎯 [PASO 3] Iniciando Simulación de Aprendizaje por Refuerzo a partir de Market Feedback (RLMF)...")
    
    # A. Registrar un análisis del mercado de prueba
    logger.info("💾 Guardando el análisis de la IA en la base de datos...")
    analysis = learning_engine.record_analysis(
        user_id=1,
        symbol="BTCUSDT",
        query="Análisis técnico algorítmico",
        tools_used=["microstructure", "rsi_oscillator", "macd_trend"],
        recommendation="BUY",
        confidence=85.0,
        position_size=150.0,
        reasoning=[
            "Gemma 2B detectó sobreventa extrema (RSI 22)",
            "Divergencia alcista en MACD confirmada",
            "Soporte de liquidez institucional detectado en $67,200"
        ],
        market_data={"price": 67500.0, "rsi": 22.0}
    )
    
    # B. Registrar la predicción pendiente
    logger.info("🔮 Registrando la predicción asociada en la cola de aprendizaje...")
    prediction = learning_engine.record_prediction(
        analysis_id=analysis.id,
        predicted_direction="BUY",
        predicted_confidence=85.0,
        predicted_entry=67500.0
    )
    
    # C. Simular la ejecución de la orden con sus precios reales
    # Imaginemos que el trade fue exitoso y se cerró en positivo
    signal_price = 67500.0
    fill_price = 67520.0 # $20 de slippage
    exit_price = 69880.0
    pnl = 35.0  # +$35.0 USD (3.5% de ganancia)
    
    # Historial de precios durante el trade (para calcular MAE / MFE)
    price_history = [67520.0, 67410.0, 68100.0, 68900.0, 69500.0, 69880.0]
    
    logger.info("📈 [PASO 4] Generando Reporte de Desviaciones Post-Trade...")
    # Calcular excursiones y slippage en el analizador
    deviation_report = post_analyzer.analyze(
        trade_id=f"TEST_TRADE_{analysis.id}",
        symbol="BTCUSDT",
        direction="LONG",
        signal_price=signal_price,
        fill_price=fill_price,
        exit_price=exit_price,
        pnl=pnl,
        price_history_during_trade=price_history,
        signals_used=["rsi_oscillator", "macd_trend"],
        patterns_detected=["Bullish Hammer"],
        entry_time=datetime.utcnow() - timedelta(hours=2),
        exit_time=datetime.utcnow()
    )
    
    # D. Registrar el resultado en el Learning Engine (Otorga XP y recalcula accuracy)
    logger.info("🧠 [PASO 5] Retroalimentando al Learning Engine con los resultados del mercado real...")
    learning_engine.record_result(
        analysis_id=analysis.id,
        actual_direction="UP",
        actual_entry=fill_price,
        actual_exit=exit_price,
        actual_pnl=3.5 # +3.5%
    )
    
    # E. Aplicar los ajustes adaptativos de peso al modelo de IA en disco
    logger.info("⚙️ Aplicando ajustes de peso adaptativos al LearningEngine del Agente de Trading...")
    agent = get_trading_agent()
    post_analyzer.apply_adjustments(agent.learning)

    # 4. Mostrar el Progreso Final de la IA
    db.refresh(initial_progress)
    logger.success("🎉 ¡Prueba Completada Exitosamente!")
    logger.info(
        f"🏆 Resultados Finales del Aprendizaje IA:\n"
        f"   - Nivel IA actual: {initial_progress.level} (XP Total: {initial_progress.experience_points})\n"
        f"   - Precisión (Accuracy): {initial_progress.accuracy:.1f}%\n"
        f"   - Respuestas Correctas: {initial_progress.correct_predictions}\n"
        f"   - Respuestas Incorrectas: {initial_progress.incorrect_predictions}\n"
        f"   - Lección de Gemma integrada: {deviation_report.lesson_learned}"
    )
    
    db.close()

if __name__ == "__main__":
    asyncio.run(run_rigorous_ai_test())
