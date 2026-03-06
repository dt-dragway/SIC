"""
SIC Ultra - Automated Trading Service
Servicio de ejecución automática de señales IA para trading personal.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import json

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import User
from app.services.execution_engine import get_execution_engine


class SignalQueue:
    """Gestiona cola de señales aprobadas para ejecución automática."""
    
    def __init__(self):
        self.approved_signals: Dict[str, Dict] = {}  # symbol -> signal_data
        self.execution_history: List[Dict] = []
        self.max_queue_size = 50
        
    def add_approved_signal(self, signal: Dict, auto_execute_params: Dict):
        """Añade señal aprobada a la cola de ejecución."""
        symbol = signal.get('symbol')
        if not symbol:
            return False
            
        # Limitar tamaño de cola
        if len(self.approved_signals) >= self.max_queue_size:
            self._remove_oldest_signal()
            
        self.approved_signals[symbol] = {
            'signal': signal,
            'params': auto_execute_params,
            'added_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=2),
            'executed': False
        }
        
        logger.info(f"📋 Señal añadida a cola: {symbol} - {signal.get('confidence', 0)}%")
        return True
        
    def get_executable_signals(self) -> List[Dict]:
        """Retorna señales listas para ejecución."""
        executable = []
        now = datetime.utcnow()
        
        for symbol, data in self.approved_signals.items():
            if (not data['executed'] and 
                data['expires_at'] > now and
                self._should_execute_signal(data)):
                executable.append(data)
                
        return executable
        
    def mark_executed(self, symbol: str, success: bool, order_id: Optional[str] = None):
        """Marca señal como ejecutada."""
        if symbol in self.approved_signals:
            signal_data = self.approved_signals[symbol]
            signal_data['executed'] = True
            signal_data['executed_at'] = datetime.utcnow()
            signal_data['execution_success'] = success
            signal_data['order_id'] = order_id
            
            # Añadir al historial
            self.execution_history.append({
                'symbol': symbol,
                'signal': signal_data['signal'],
                'executed_at': signal_data['executed_at'],
                'success': success,
                'order_id': order_id
            })
            
            # Limitar historial
            if len(self.execution_history) > 100:
                self.execution_history = self.execution_history[-50:]
                
            logger.info(f"✅ Señal ejecutada: {symbol} - {'Éxito' if success else 'Fallo'}")
            
    def _remove_oldest_signal(self):
        """Elimina señal más antigua de la cola."""
        if self.approved_signals:
            oldest_symbol = min(self.approved_signals.keys(), 
                              key=lambda k: self.approved_signals[k]['added_at'])
            del self.approved_signals[oldest_symbol]
            
    def _should_execute_signal(self, signal_data: Dict) -> bool:
        """Valida si la señal debe ser ejecutada ahora."""
        # Validar confianza mínima
        min_confidence = signal_data['params'].get('min_confidence', 70)
        if signal_data['signal'].get('confidence', 0) < min_confidence:
            return False
            
        # Validar tier permitido
        allowed_tiers = signal_data['params'].get('allowed_tiers', ['S', 'A'])
        signal_tier = signal_data['signal'].get('tier', 'C')
        if signal_tier not in allowed_tiers:
            return False
            
        return True
        
    def get_queue_status(self) -> Dict:
        """Retorna estado actual de la cola."""
        return {
            'queue_size': len(self.approved_signals),
            'pending_signals': len([s for s in self.approved_signals.values() if not s['executed']]),
            'executed_today': len([s for s in self.execution_history 
                                 if s['executed_at'].date() == datetime.utcnow().date()]),
            'success_rate_24h': self._calculate_success_rate_24h()
        }
        
    def _calculate_success_rate_24h(self) -> float:
        """Calcula tasa de éxito últimas 24 horas."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_executions = [s for s in self.execution_history 
                            if s['executed_at'] > yesterday]
        
        if not recent_executions:
            return 0.0
            
        successful = len([s for s in recent_executions if s['success']])
        return (successful / len(recent_executions)) * 100


class AutoExecutionService:
    """Servicio principal de ejecución automática de señales."""
    
    def __init__(self):
        self.signal_queue = SignalQueue()
        # self.signal_generator se inicializará cuando se necesite
        self.execution_engine = get_execution_engine()
        self.running = False
        self.execution_task: Optional[asyncio.Task] = None
        self.check_interval = 30  # segundos
        self.max_daily_trades = 10
        self.emergency_stop = False
        
    async def start_automation(self, user_id: int, settings: Dict) -> bool:
        """Inicia el servicio de automatización."""
        if self.running:
            logger.warning("⚠️ Automatización ya está activa")
            return False
            
        # Validar configuración
        if not self._validate_settings(settings):
            logger.error("❌ Configuración inválida")
            return False
            
        # Cargar configuración de usuario
        await self._load_user_settings(user_id)
        
        self.running = True
        self.emergency_stop = False
        self.execution_task = asyncio.create_task(self._automation_loop())
        
        logger.info(f"🚀 Automatización iniciada para usuario {user_id}")
        return True
        
    async def stop_automation(self) -> bool:
        """Detiene el servicio de automatización."""
        if not self.running:
            return False
            
        self.running = False
        
        if self.execution_task:
            self.execution_task.cancel()
            try:
                await self.execution_task
            except asyncio.CancelledError:
                pass
                
        logger.info("🛑 Automatización detenida")
        return True
        
    async def _automation_loop(self):
        """Bucle principal de automatización."""
        logger.info("🔄 Iniciando bucle de automatización")
        
        while self.running and not self.emergency_stop:
            try:
                # Verificar condiciones de parada
                if self._should_stop_automation():
                    logger.warning("⚠️ Condiciones de parada detectadas")
                    await self.stop_automation()
                    break
                    
                # Generar nuevas señales
                await self._generate_new_signals()
                
                # Ejecutar señales pendientes
                await self._execute_pending_signals()
                
                # Esperar siguiente ciclo
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                logger.info("📋 Bucle de automatización cancelado")
                break
            except Exception as e:
                logger.error(f"❌ Error en bucle de automatización: {e}")
                await asyncio.sleep(5)  # Esperar antes de reintentar
                
    async def _generate_new_signals(self):
        """Genera nuevas señales para símbolos configurados."""
        # Obtener símbolos configurados para automación
        symbols = await self._get_automation_symbols()
        
        for symbol in symbols:
            try:
                # 1. Obtener pre-señal base del generador técnico
                from app.ml.signal_generator import get_signal_generator
                generator = get_signal_generator()
                base_signal = generator.analyze(symbol)
                
                if not base_signal:
                    continue
                    
                # 2. Solicitar 'High-Confidence Institutional Analysis' al SmartPool
                from app.ml.llm_connector import get_llm_manager
                llm = get_llm_manager()
                
                indicators = base_signal.get('timeframes', {}).get('1h', {}).get('indicators', {})
                patterns = [r for r in base_signal.get('reasoning', []) if '📊' in r]
                
                smartpool_analysis = await llm.analyze_market(
                    symbol=symbol,
                    current_price=base_signal.get('current_price', 0),
                    indicators=indicators,
                    patterns=patterns,
                    recent_signals=[] 
                )
                
                signal = base_signal.copy()
                if smartpool_analysis:
                    logger.info(f"🧠 SmartPool validó {symbol}: {smartpool_analysis.get('signal')} con {smartpool_analysis.get('confidence')}%")
                    signal['action'] = smartpool_analysis.get('signal', base_signal.get('type'))
                    signal['confidence'] = smartpool_analysis.get('confidence', base_signal.get('confidence', 0))
                    signal['reasoning'].insert(0, f"🤖 SmartPool: {smartpool_analysis.get('reasoning')}")
                else:
                    signal['action'] = base_signal.get('type')
                
                # Descartar si el veredicto final es HOLD
                if signal.get('action') == "HOLD":
                    continue
                    
                # Verificar si ya está en cola
                if symbol in self.signal_queue.approved_signals:
                    continue
                    
                # Añadir a cola si cumple criterios
                settings = await self._get_symbol_settings(symbol)
                if self._signal_meets_criteria(signal, settings):
                    self.signal_queue.add_approved_signal(signal, settings)
                    
            except Exception as e:
                logger.error(f"❌ Error generando señal para {symbol}: {e}")
                
    async def _execute_pending_signals(self):
        """Ejecuta señales pendientes en la cola."""
        executable_signals = self.signal_queue.get_executable_signals()
        
        for signal_data in executable_signals:
            try:
                symbol = signal_data['signal']['symbol']
                
                # Validar límites diarios
                if not self._check_daily_limits(symbol):
                    logger.warning(f"⚠️ Límite diario alcanzado para {symbol}")
                    continue
                    
                # Ejecutar orden
                success = await self._execute_signal_order(signal_data)
                
                # Marcar como ejecutada
                self.signal_queue.mark_executed(symbol, success)
                
                # Pequeña pausa entre ejecuciones
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error ejecutando señal: {e}")
                
    async def _execute_signal_order(self, signal_data: Dict) -> bool:
        """Ejecuta orden basada en señal con datos reales y aprendizaje."""
        signal = signal_data['signal']
        symbol = signal['symbol']
        
        # Determinar lado de la orden
        side = 'BUY' if signal['action'] == 'BUY' else 'SELL'
        
        # Calcular tamaño de posición
        quantity = await self._calculate_position_size(symbol, signal)
        
        if quantity <= 0:
            return False
            
        try:
            # Obtener precio real del mercado
            from app.infrastructure.binance.client import get_binance_client
            client = get_binance_client()
            real_price = client.get_price(symbol)
            
            if not real_price:
                logger.error(f"❌ No se pudo obtener precio real para {symbol}")
                return False
            
            # Ejecutar orden en modo práctica con datos reales
            logger.info(f"📈 Ejecutando orden: {side} {quantity} {symbol} @ ${real_price}")
            
            # Simular ejecución con precio real
            await asyncio.sleep(0.5)
            
            # Registrar resultado para aprendizaje de IA
            await self._record_trade_for_learning(
                symbol=symbol,
                side=side,
                quantity=quantity,
                entry_price=real_price,
                signal_data=signal_data
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando orden para {symbol}: {e}")
            return False
            
    async def _record_trade_for_learning(self, symbol: str, side: str, quantity: float, 
                                        entry_price: float, signal_data: Dict):
        """Registra trade para aprendizaje de IA con datos reales."""
        try:
            # Importar trading agent para aprendizaje
            from app.ml.trading_agent import get_trading_agent
            agent = get_trading_agent()
            
            # Generar ID único
            trade_id = f"auto_{symbol}_{int(datetime.utcnow().timestamp())}"
            
            # Extraer señales y patrones usados
            signals_used = []
            patterns_detected = []
            
            if 'reasoning' in signal_data['signal']:
                reasoning = signal_data['signal']['reasoning']
                # Extraer indicadores del reasoning
                signals_used = [r for r in reasoning if any(ind in r for ind in ['RSI', 'MACD', 'EMA', 'BB'])]
                # Extraer patrones
                patterns_detected = [r for r in reasoning if '📊' in r]
            
            # Registrar en learning engine (simulado por ahora, se actualizará con resultado real)
            agent.record_result(
                trade_id=trade_id,
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                exit_price=entry_price,  # Se actualizará cuando se cierre
                pnl=0.0,  # Se calculará cuando se cierre
                signals_used=signals_used,
                patterns_detected=patterns_detected
            )
            
            # Añadir marcador al gráfico
            from app.services.trade_markers import get_trade_marker_manager
            marker_manager = get_trade_marker_manager()
            
            marker_trade_id = marker_manager.add_trade_marker(
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                stop_loss=signal_data['signal'].get('stop_loss', entry_price * 0.98),
                take_profit=signal_data['signal'].get('take_profit', entry_price * 1.05),
                quantity=quantity,
                confidence=signal_data['signal'].get('confidence'),
                tier=signal_data['signal'].get('tier')
            )
            
            logger.info(f"🧚 Trade registrado para aprendizaje IA: {trade_id}")
            logger.info(f"📊 Marcador añadido al gráfico: {marker_trade_id}")
            
        except Exception as e:
            logger.error(f"❌ Error registrando trade para aprendizaje: {e}")
            
    def _validate_settings(self, settings: Dict) -> bool:
        """Valida configuración de automatización."""
        required_fields = ['max_daily_trades', 'max_position_size', 'min_signal_confidence']
        
        for field in required_fields:
            if field not in settings:
                logger.error(f"❌ Campo requerido faltante: {field}")
                return False
                
        # Validar rangos
        if settings['max_daily_trades'] < 1 or settings['max_daily_trades'] > 50:
            return False
            
        if settings['min_signal_confidence'] < 50 or settings['min_signal_confidence'] > 100:
            return False
            
        return True
        
    async def _load_user_settings(self, user_id: int):
        """Carga configuración de usuario desde BD."""
        # TODO: Implementar carga desde base de datos
        pass
        
    async def _get_automation_symbols(self) -> List[str]:
        """Retorna símbolos configurados para automatización."""
        # TODO: Obtener desde configuración de usuario
        return ['BTCUSDT', 'ETHUSDT']
        
    async def _get_symbol_settings(self, symbol: str) -> Dict:
        """Retorna configuración para símbolo específico."""
        # TODO: Obtener desde BD
        return {
            'min_confidence': 70,
            'allowed_tiers': ['S', 'A'],
            'max_position_size': 50
        }
        
    def _signal_meets_criteria(self, signal: Dict, settings: Dict) -> bool:
        """Verifica si señal cumple criterios de configuración."""
        confidence = signal.get('confidence', 0)
        tier = signal.get('tier', 'C')
        
        return (confidence >= settings['min_confidence'] and 
                tier in settings['allowed_tiers'])
                
    def _should_stop_automation(self) -> bool:
        """Verifica si se debe detener automatización."""
        # Verificar parada de emergencia
        if self.emergency_stop:
            return True
            
        # Verificar pérdidas diarias
        if self._check_daily_loss_limit():
            logger.warning("⚠️ Límite de pérdidas diario alcanzado")
            return True
            
        # Verificar trades consecutivos fallidos
        if self._check_consecutive_losses():
            logger.warning("⚠️ Demasiadas pérdidas consecutivas")
            return True
            
        return False
    
    def _check_daily_loss_limit(self) -> bool:
        """Verifica si se alcanzó límite de pérdidas diario."""
        # TODO: Implementar verificación de pérdidas diarias
        # Por ahora: 5% máximo de pérdidas diarias
        return False
        
    def _check_consecutive_losses(self) -> bool:
        """Verifica si hay demasiadas pérdidas consecutivas."""
        # TODO: Implementar verificación de trades consecutivos
        # Por ahora: máximo 5 pérdidas consecutivas
        return False
        
    def _check_daily_limits(self, symbol: str) -> bool:
        """Verifica límites diarios de trading."""
        # TODO: Implementar verificación de límites
        return True
        
    async def _calculate_position_size(self, symbol: str, signal: Dict) -> float:
        """Calcula tamaño de posición basado en señal y configuración."""
        # TODO: Implementar cálculo de tamaño
        return 0.001  # Placeholder
        
    def get_automation_status(self) -> Dict:
        """Retorna estado completo del servicio de automatización."""
        return {
            'running': self.running,
            'emergency_stop': self.emergency_stop,
            'queue_status': self.signal_queue.get_queue_status(),
            'check_interval': self.check_interval,
            'uptime': datetime.utcnow().isoformat() if self.running else None,
            'emergency_conditions': {
                'daily_loss_limit': self._check_daily_loss_limit(),
                'consecutive_losses': self._check_consecutive_losses(),
                'manual_stop': self.emergency_stop
            }
        }


# Instancia global del servicio
auto_execution_service = AutoExecutionService()


def get_auto_execution_service() -> AutoExecutionService:
    """Retorna instancia del servicio de ejecución automática."""
    return auto_execution_service