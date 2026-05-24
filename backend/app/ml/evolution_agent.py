"""
SIC Ultra - Meta-Agente de Evolución y Auto-Optimización IA

Bucle de retroalimentación analítico de alto nivel que:
- Audita el desempeño histórico real del bot.
- Detecta rachas de pérdidas consecutivas (Drawdown Streaks) o mercados inestables.
- Mutará de forma autónoma y en tiempo real la configuración persistente en base de datos (AutomationConfig).
- Guarda de forma indestructible las lecciones y mutaciones dentro de agent_memory.json.
"""

import json as json_lib
import os
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.ml.trading_agent import get_trading_agent
from app.infrastructure.database.models import VirtualTrade, AgentTrade, AutomationConfig, VirtualWallet

class EvolutionAgent:
    """
    Meta-Agente de Evolución y Auto-Reflexión.
    Modifica la configuración de riesgo basándose en el desempeño de trading real.
    """
    
    def __init__(self):
        logger.info("🧠 Meta-Agente de Evolución IA inicializado")
        
    def self_reflect(self, db: Session, user_id: int) -> Dict:
        """
        Analizar en caliente el desempeño histórico y realizar auto-diagnóstico.
        """
        try:
            # 1. Obtener la wallet del usuario para rastrear sus trades
            wallet = db.query(VirtualWallet).filter(VirtualWallet.user_id == user_id).first()
            if not wallet:
                return {"status": "error", "message": "Billetera no encontrada"}
                
            # 2. Consultar los últimos 20 trades de práctica del usuario
            recent_trades = db.query(VirtualTrade).filter(
                VirtualTrade.wallet_id == wallet.id
            ).order_by(VirtualTrade.created_at.desc()).limit(20).all()
            
            # 3. Calcular racha de pérdidas consecutivas
            consecutive_losses = 0
            for t in recent_trades:
                # Los trades de venta son los que tienen P&L realizado
                if t.side == "SELL":
                    if (t.pnl or 0) < 0:
                        consecutive_losses += 1
                    else:
                        break # Romper racha si hay ganancia
            
            # 4. Calcular tasa de éxito reciente (Win Rate %)
            sell_trades = [t for t in recent_trades if t.side == "SELL"]
            winning_trades = [t for t in sell_trades if (t.pnl or 0) > 0]
            win_rate = (len(winning_trades) / len(sell_trades) * 100) if sell_trades else 100.0
            
            # 5. Determinar el régimen de riesgo del mercado
            risk_regime = "NORMAL"
            reason = "Condiciones normales y estables de rentabilidad"
            
            if consecutive_losses >= 3:
                risk_regime = "HIGH_RISK"
                reason = f"Racha perdedora consecutiva detectada ({consecutive_losses} pérdidas)"
            elif win_rate < 50.0 and len(sell_trades) >= 3:
                risk_regime = "UNSTABLE"
                reason = f"Tasa de éxito reciente inestable ({win_rate:.1f}% en los últimos trades)"
                
            return {
                "status": "success",
                "risk_regime": risk_regime,
                "reason": reason,
                "consecutive_losses": consecutive_losses,
                "win_rate_recent": win_rate,
                "trades_evaluated_count": len(sell_trades)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en auto-reflexión de evolución IA: {e}")
            return {"status": "error", "message": str(e)}

    def perform_macro_mutations(self, db: Session, user_id: int) -> Dict:
        """
        Ejecuta las mutaciones de código y parámetros del bot de forma dinámica en la DB.
        """
        try:
            # 1. Obtener diagnóstico
            analysis = self.self_reflect(db, user_id)
            if analysis["status"] == "error":
                return analysis
                
            risk_regime = analysis["risk_regime"]
            
            # 2. Buscar o crear configuración de automatización del usuario
            config = db.query(AutomationConfig).filter(
                AutomationConfig.user_id == user_id
            ).first()
            
            if not config:
                logger.info(f"⚙️ Creando nueva AutomationConfig para usuario {user_id}")
                config = AutomationConfig(
                    user_id=user_id,
                    max_daily_trades=10,
                    max_position_size=50.0,
                    min_signal_confidence=70,
                    risk_level="moderate"
                )
                db.add(config)
                db.commit()
                db.refresh(config)
                
            old_confidence = config.min_signal_confidence
            old_pos_size = config.max_position_size
            old_risk = config.risk_level
            
            mutation_applied = False
            mutation_msg = ""
            
            # 3. Lógica de mutación anti-frágil en base de datos
            if risk_regime == "HIGH_RISK":
                # Racha perdedora severa -> Maximizar defensas
                new_confidence = min(85, max(old_confidence, 80)) # Subir filtro de confianza
                new_pos_size = min(old_pos_size, 25.0) if old_pos_size > 10.0 else old_pos_size # Evitar subir riesgo en posiciones ultra bajas
                new_risk = "conservative"
                
                if old_confidence != new_confidence or old_pos_size != new_pos_size or old_risk != new_risk:
                    config.min_signal_confidence = new_confidence
                    config.max_position_size = new_pos_size
                    config.risk_level = new_risk
                    config.updated_at = datetime.utcnow()
                    mutation_applied = True
                    mutation_msg = (
                        f"🛡️ MUTACIÓN DEFENSIVA: Umbral de confianza incrementado a {new_confidence}% (antes {old_confidence}%) "
                        f"y tamaño de posición reducido a ${new_pos_size} USD debido a una racha de "
                        f"{analysis['consecutive_losses']} pérdidas consecutivas."
                    )
                    
            elif risk_regime == "UNSTABLE":
                # Inestabilidad leve -> Ajustar moderadamente
                new_confidence = min(80, max(old_confidence, 76))
                
                if old_confidence != new_confidence:
                    config.min_signal_confidence = new_confidence
                    config.updated_at = datetime.utcnow()
                    mutation_applied = True
                    mutation_msg = (
                        f"⚠️ MUTACIÓN DE ESTABILIZACIÓN: Umbral de confianza incrementado a {new_confidence}% "
                        f"(antes {old_confidence}%) por tasa de éxito baja del {analysis['win_rate_recent']:.1f}%."
                    )
                    
            else: # NORMAL
                # Mercado saludable -> Retornar paulatinamente a parámetros equilibrados
                new_confidence = 70
                new_pos_size = 50.0
                new_risk = "moderate"
                
                if old_confidence > 70 or old_pos_size < 50.0 or old_risk != "moderate":
                    config.min_signal_confidence = new_confidence
                    config.max_position_size = new_pos_size
                    config.risk_level = new_risk
                    config.updated_at = datetime.utcnow()
                    mutation_applied = True
                    mutation_msg = (
                        f"🚀 MUTACIÓN DE CRECIMIENTO: Parámetros optimizados restablecidos a niveles normales "
                        f"(Confianza: {new_confidence}%, Posición: ${new_pos_size} USD) al normalizarse el win rate."
                    )

            if mutation_applied:
                db.commit()
                logger.success(f"🧬 Mutación guardada en DB: {mutation_msg}")
                
                # 4. Registrar la lección en la memoria neuronal en agent_memory.json
                agent = get_trading_agent()
                if "evolution_history" not in agent.memory.data:
                    agent.memory.data["evolution_history"] = []
                    
                evolution_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "mutation_applied": True,
                    "risk_regime": risk_regime,
                    "reason": analysis["reason"],
                    "metrics": {
                        "consecutive_losses": analysis["consecutive_losses"],
                        "win_rate_recent": round(analysis["win_rate_recent"], 2)
                    },
                    "parameter_changes": {
                        "confidence": f"{old_confidence}% -> {config.min_signal_confidence}%",
                        "position_size": f"${old_pos_size} -> ${config.max_position_size}",
                        "risk_level": f"{old_risk} -> {config.risk_level}"
                    },
                    "message": mutation_msg
                }
                agent.memory.data["evolution_history"].append(evolution_entry)
                
                # Mantener los últimos 100 registros de evolución
                if len(agent.memory.data["evolution_history"]) > 100:
                    agent.memory.data["evolution_history"] = agent.memory.data["evolution_history"][-100:]
                    
                agent.memory.save()
            else:
                mutation_msg = "Parámetros óptimos ya ajustados. No se requirieron nuevas mutaciones."
                
            return {
                "status": "success",
                "mutation_applied": mutation_applied,
                "message": mutation_msg,
                "config": {
                    "max_daily_trades": config.max_daily_trades,
                    "max_position_size": config.max_position_size,
                    "min_signal_confidence": config.min_signal_confidence,
                    "risk_level": config.risk_level,
                    "pause_on_high_volatility": config.pause_on_high_volatility
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error aplicando mutaciones de evolución IA: {e}")
            db.rollback()
            return {"status": "error", "message": str(e)}

# === Singleton ===
_evolution_agent: Optional[EvolutionAgent] = None

def get_evolution_agent() -> EvolutionAgent:
    """Obtener instancia única del meta-agente de evolución"""
    global _evolution_agent
    if _evolution_agent is None:
        _evolution_agent = EvolutionAgent()
    return _evolution_agent
