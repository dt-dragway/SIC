#!/usr/bin/env python
import os
import sys
import json
from datetime import datetime

# Añadir directorio raíz al PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import VirtualWallet, VirtualTrade, AutomationConfig
from app.ml.evolution_agent import get_evolution_agent
from app.ml.trading_agent import get_trading_agent
from loguru import logger

def test_evolution_loop():
    logger.info("🧪 INICIANDO TEST DE AUTO-REFLEXIÓN Y MUTACIÓN DEFENSIVA IA...")
    db = SessionLocal()
    evo_agent = get_evolution_agent()
    agent = get_trading_agent()
    
    # IDs de prueba
    user_id = 1
    
    try:
        # 1. Obtener billetera
        wallet = db.query(VirtualWallet).filter(VirtualWallet.user_id == user_id).first()
        if not wallet:
            logger.error("❌ Error: No se encontró la billetera del usuario 1.")
            return
            
        # 2. Obtener config de automatización inicial
        config = db.query(AutomationConfig).filter(AutomationConfig.user_id == user_id).first()
        if not config:
            logger.info("⚙️ Creando configuración por defecto...")
            config = AutomationConfig(
                user_id=user_id,
                min_signal_confidence=70,
                max_position_size=50.0,
                risk_level="moderate"
            )
            db.add(config)
            db.commit()
            db.refresh(config)
            
        logger.info(f"📋 Configuración Inicial en DB:")
        logger.info(f"   - Confianza Mínima: {config.min_signal_confidence}%")
        logger.info(f"   - Tamaño de Posición: ${config.max_position_size} USD")
        logger.info(f"   - Nivel de Riesgo: {config.risk_level}")
        
        # Guardar valores para restaurar al final
        orig_confidence = config.min_signal_confidence
        orig_position_size = config.max_position_size
        orig_risk_level = config.risk_level
        
        # 3. Insertar 3 trades ficticios PERDEDORES para simular racha negativa
        logger.info("📉 Simulando racha de 3 pérdidas consecutivas en Billetera de Práctica...")
        fake_trades = []
        for i in range(3):
            fake_trade = VirtualTrade(
                wallet_id=wallet.id,
                symbol="BTCUSDT",
                side="SELL",
                type="MARKET",
                strategy="AI_SIGNAL",
                reason="Simulated Trade for Evolution Test",
                quantity=0.001,
                price=65000.0,
                pnl=-15.0, # Pérdida de $15
                created_at=datetime.utcnow()
            )
            db.add(fake_trade)
            fake_trades.append(fake_trade)
            
        db.commit()
        for ft in fake_trades:
            db.refresh(ft)
            
        # 4. Disparar el ciclo de auto-reflexión y mutación
        logger.info("🧬 Ejecutando perform_macro_mutations()...")
        result = evo_agent.perform_macro_mutations(db, user_id)
        
        # 5. Auditar resultados
        logger.info("🔍 Auditando cambios en Base de Datos y Memoria:")
        db.refresh(config)
        logger.info(f"   - Estado: {result['status']}")
        logger.info(f"   - Mutación Aplicada: {result['mutation_applied']}")
        logger.info(f"   - Mensaje: {result['message']}")
        logger.info(f"   - Nueva Confianza en DB: {config.min_signal_confidence}% (Debería ser >= 80%)")
        logger.info(f"   - Nuevo Tamaño Posición en DB: ${config.max_position_size} USD (Debería ser <= 25.0)")
        logger.info(f"   - Nuevo Nivel de Riesgo en DB: {config.risk_level} (Debería ser conservative)")
        
        # Validar aserciones básicas
        assert config.min_signal_confidence >= 80, "Error: La confianza no se incrementó defensivamente."
        assert config.max_position_size <= 25.0, "Error: El tamaño de posición no se limitó de forma conservadora."
        assert config.risk_level == "conservative", "Error: El nivel de riesgo no mutó a conservador."
        logger.success("✅ ASERCIONES DE BASE DE DATOS COMPLETADAS CON ÉXITO.")
        
        # 6. Verificar memoria del agente agent_memory.json
        history = agent.memory.data.get("evolution_history", [])
        logger.info(f"🧠 Registros en Memoria de la IA (evolution_history): {len(history)} entradas.")
        if history:
            last_entry = history[-1]
            logger.info(f"   - Última Mutación Memorizada: {last_entry['message']}")
            logger.info(f"   - Parámetros: {last_entry['parameter_changes']}")
            assert last_entry["risk_regime"] == "HIGH_RISK", "Error: No se memorizó el régimen de alto riesgo."
            logger.success("✅ ASERCIONES DE MEMORIA NEURONAL IA COMPLETADAS CON ÉXITO.")
            
        # 7. Restaurar configuración original y limpiar trades de prueba
        logger.info("🧹 Limpiando base de datos y restaurando configuración original...")
        for ft in fake_trades:
            db.delete(ft)
            
        config.min_signal_confidence = orig_confidence  # type: ignore
        config.max_position_size = orig_position_size  # type: ignore
        config.risk_level = orig_risk_level  # type: ignore
        db.commit()
        logger.success("🎉 TEST DE EVOLUCIÓN COMPLETADO CON ÉXITO Y ENTORNO COMPLETAMENTE LIMPIO.")
        
    except Exception as e:
        logger.error(f"❌ Error durante el test de evolución: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_evolution_loop()
