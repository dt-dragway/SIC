"""
SIC Ultra - Automated Trading API
Endpoints para controlar trading automático con IA.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from loguru import logger

from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import User
from app.api.v1.auth import get_current_user
from app.services.auto_execution import get_auto_execution_service


# Pydantic models
class AutomationSettings(BaseModel):
    enabled: bool = Field(False, description="Activar trading automático")
    max_daily_trades: int = Field(10, ge=1, le=50, description="Máximo de trades diarios")
    max_position_size: float = Field(50.0, ge=1.0, le=1000.0, description="Tamaño máximo de posición (USD)")
    min_signal_confidence: int = Field(70, ge=50, le=100, description="Confianza mínima de señal (%)")
    allowed_tiers: List[str] = Field(default=['S', 'A'], description="Tiers de señal permitidos")
    risk_level: str = Field('moderate', pattern='^(conservative|moderate|aggressive)$', description="Nivel de riesgo")
    pause_on_high_volatility: bool = Field(True, description="Pausar en alta volatilidad")
    check_interval_seconds: int = Field(30, ge=10, le=300, description="Intervalo de revisión (segundos)")
    practice_mode_only: bool = Field(True, description="Usar solo modo práctica")


class AutomationStatus(BaseModel):
    running: bool
    emergency_stop: bool
    queue_status: Dict
    check_interval: int
    uptime: Optional[str] = None
    settings: Optional[AutomationSettings] = None
    emergency_conditions: Optional[Dict[str, bool]] = None


class SymbolAutomationConfig(BaseModel):
    symbol: str
    enabled: bool
    min_confidence: int = Field(70, ge=50, le=100)
    max_position_size: float = Field(50.0, ge=1.0, le=1000.0)
    allowed_tiers: List[str] = Field(default=['S', 'A'])


class StartAutomationRequest(BaseModel):
    settings: AutomationSettings
    symbols: List[SymbolAutomationConfig] = Field(default=[], description="Configuración por símbolo")


router = APIRouter()


@router.post("/start", response_model=Dict[str, Any])
async def start_automation(
    request: StartAutomationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Inicia el servicio de trading automático.
    """
    try:
        # Validar que no esté corriendo
        auto_service = get_auto_execution_service()
        if auto_service.running:
            raise HTTPException(status_code=400, detail="La automatización ya está activa")
        
        # Validar configuración
        settings_dict = request.settings.dict()
        
        # Iniciar servicio en background
        success = await auto_service.start_automation(current_user.id, settings_dict)
        
        if not success:
            raise HTTPException(status_code=400, detail="Error al iniciar automatización")
        
        # Guardar configuración en base de datos
        # TODO: Implementar guardado de configuración
        
        logger.info(f"🚀 Automatización iniciada por usuario {current_user.id}")
        
        return {
            "success": True,
            "message": "Automatización iniciada correctamente",
            "status": auto_service.get_automation_status(),
            "started_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error iniciando automatización: {e}")
        raise HTTPException(status_code=500, detail=f"Error al iniciar automatización: {str(e)}")


@router.post("/stop", response_model=Dict[str, Any])
async def stop_automation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Detiene el servicio de trading automático.
    """
    try:
        auto_service = get_auto_execution_service()
        
        if not auto_service.running:
            raise HTTPException(status_code=400, detail="La automatización no está activa")
        
        success = await auto_service.stop_automation()
        
        if not success:
            raise HTTPException(status_code=400, detail="Error al detener automatización")
        
        logger.info(f"🛑 Automatización detenida por usuario {current_user.id}")
        
        return {
            "success": True,
            "message": "Automatización detenida correctamente",
            "stopped_at": datetime.utcnow().isoformat(),
            "final_status": auto_service.get_automation_status()
        }
        
    except Exception as e:
        logger.error(f"❌ Error deteniendo automatización: {e}")
        raise HTTPException(status_code=500, detail=f"Error al detener automatización: {str(e)}")


@router.get("/status", response_model=AutomationStatus)
async def get_automation_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estado actual del servicio de automatización.
    """
    try:
        auto_service = get_auto_execution_service()
        status = auto_service.get_automation_status()
        
        # Cargar configuración guardada
        # TODO: Cargar configuración desde BD
        
        return AutomationStatus(**status)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estado: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener estado: {str(e)}")


@router.post("/emergency-stop", response_model=Dict[str, Any])
async def emergency_stop(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Activa parada de emergencia inmediata.
    """
    try:
        auto_service = get_auto_execution_service()
        
        # Activar parada de emergencia
        auto_service.emergency_stop = True
        
        # Detener servicio
        await auto_service.stop_automation()
        
        logger.warning(f"🚨 PARADA DE EMERGENCIA activada por usuario {current_user.id}")
        
        return {
            "success": True,
            "message": "Parada de emergencia activada",
            "stopped_at": datetime.utcnow().isoformat(),
            "reason": "Emergency stop activated by user"
        }
        
    except Exception as e:
        logger.error(f"❌ Error en parada de emergencia: {e}")
        raise HTTPException(status_code=500, detail=f"Error en parada de emergencia: {str(e)}")


@router.get("/queue", response_model=Dict[str, Any])
async def get_signal_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estado de la cola de señales.
    """
    try:
        auto_service = get_auto_execution_service()
        queue_status = auto_service.signal_queue.get_queue_status()
        
        # Obtener señales pendientes
        pending_signals = []
        for symbol, data in auto_service.signal_queue.approved_signals.items():
            if not data['executed']:
                pending_signals.append({
                    'symbol': symbol,
                    'signal': data['signal'],
                    'added_at': data['added_at'].isoformat(),
                    'expires_at': data['expires_at'].isoformat(),
                    'params': data['params']
                })
        
        return {
            "queue_status": queue_status,
            "pending_signals": pending_signals,
            "execution_history": auto_service.signal_queue.execution_history[-10:]  # Últimos 10
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo cola: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener cola: {str(e)}")


@router.post("/settings", response_model=Dict[str, Any])
async def update_automation_settings(
    settings: AutomationSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza configuración de automatización.
    """
    try:
        # Guardar configuración en base de datos
        # TODO: Implementar guardado de configuración
        
        logger.info(f"⚙️ Configuración actualizada por usuario {current_user.id}")
        
        return {
            "success": True,
            "message": "Configuración actualizada correctamente",
            "settings": settings.dict(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error actualizando configuración: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar configuración: {str(e)}")


@router.get("/settings", response_model=AutomationSettings)
async def get_automation_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna configuración actual de automatización.
    """
    try:
        # Cargar configuración desde base de datos
        # TODO: Implementar carga de configuración
        
        # Configuración por defecto
        default_settings = AutomationSettings()
        
        return default_settings
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo configuración: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener configuración: {str(e)}")


@router.get("/performance", response_model=Dict[str, Any])
async def get_automation_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna métricas de rendimiento del trading automático.
    """
    try:
        auto_service = get_auto_execution_service()
        
        # Obtener historial de ejecuciones
        history = auto_service.signal_queue.execution_history
        
        # Calcular métricas
        total_executions = len(history)
        successful_executions = len([h for h in history if h['success']])
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        # Ejecuciones últimas 24h
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_history = [h for h in history if h['executed_at'] > yesterday]
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": round(success_rate, 2),
            "executions_24h": len(recent_history),
            "success_rate_24h": auto_service.signal_queue._calculate_success_rate_24h(),
            "queue_status": auto_service.signal_queue.get_queue_status(),
            "last_execution": history[-1]['executed_at'].isoformat() if history else None
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo rendimiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener rendimiento: {str(e)}")


@router.post("/test-signal", response_model=Dict[str, Any])
async def test_signal_generation(
    symbol: str = Query(..., description="Símbolo a probar"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Genera señal de prueba para un símbolo.
    """
    try:
        auto_service = get_auto_execution_service()
        
        # Generar señal
        signal = await auto_service.signal_generator.generate_signal(symbol)
        
        if not signal:
            return {
                "success": False,
                "message": f"No se pudo generar señal para {symbol}",
                "symbol": symbol
            }
        
        return {
            "success": True,
            "message": "Señal generada correctamente",
            "signal": signal,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error generando señal de prueba: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando señal: {str(e)}")