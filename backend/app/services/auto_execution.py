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
        """Retorna estado actual de la cola consultando la base de datos para estadísticas diarias."""
        db = SessionLocal()
        try:
            from app.infrastructure.database.models import VirtualTrade, AgentTrade
            from datetime import date
            
            today = date.today()
            
            # Contar trades realizados hoy (VirtualTrade con strategy AI_AUTO + AgentTrade)
            today_v_trades = db.query(VirtualTrade).filter(
                VirtualTrade.strategy == "AI_AUTO",
                VirtualTrade.created_at >= today
            ).all()
            
            today_a_trades = db.query(AgentTrade).filter(
                AgentTrade.created_at >= today
            ).all()
            
            executed_today = len(today_v_trades) + len(today_a_trades)
            
            # Calcular tasa de éxito de las últimas 24 horas (usando AgentTrade como referencia real)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_trades = db.query(AgentTrade).filter(AgentTrade.created_at >= yesterday).all()
            
            if not recent_trades:
                success_rate_24h = 0.0
            else:
                successful = len([t for t in recent_trades if t.pnl > 0])
                success_rate_24h = (successful / len(recent_trades)) * 100
                
        except Exception as e:
            logger.error(f"❌ Error calculando estadísticas de cola en DB: {e}")
            executed_today = len([s for s in self.execution_history 
                                 if s['executed_at'].date() == datetime.utcnow().date()])
            success_rate_24h = self._calculate_success_rate_24h()
        finally:
            db.close()
            
        return {
            'queue_size': len(self.approved_signals),
            'pending_signals': len([s for s in self.approved_signals.values() if not s['executed']]),
            'executed_today': executed_today,
            'success_rate_24h': success_rate_24h
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
        self.scan_logs: List[Dict] = []
        
    def add_scan_log(self, symbol: str, message: str):
        self.scan_logs.append({
            "id": int(datetime.utcnow().timestamp() * 1000) + len(self.scan_logs),
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": symbol,
            "message": message
        })
        if len(self.scan_logs) > 50:
            self.scan_logs = self.scan_logs[-50:]
        
        # También imprimir en los logs del servidor para mayor visibilidad
        logger.info(f"🔍 [Escáner IA - {symbol}] {message}")
        
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
        
        self.user_id = user_id
        self.running = True
        self.emergency_stop = False
        self.execution_task = asyncio.create_task(self._automation_loop())
        
        # Persistir estado activo en la base de datos
        await self._update_enabled_status(user_id, True)
        
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
                
        # Persistir estado inactivo en la base de datos
        if hasattr(self, 'user_id'):
            await self._update_enabled_status(self.user_id, False)
            
        logger.info("🛑 Automatización detenida")
        return True
        
    async def _automation_loop(self):
        """Bucle principal de automatización."""
        logger.info("🔄 Iniciando bucle de automatización")
        
        while self.running and not self.emergency_stop:
            try:
                # Recargar configuración en caliente desde la base de datos para capturar mutaciones
                if hasattr(self, 'user_id'):
                    await self._load_user_settings(self.user_id)
                    
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
                
    async def _scan_single_symbol(self, symbol: str):
        """Escanea un único símbolo de forma asíncrona para procesamiento paralelo concurrente."""
        try:
            # 1. Obtener pre-señal base del generador técnico
            from app.ml.signal_generator import get_signal_generator
            generator = get_signal_generator()
            # Ejecutar análisis pesado en hilo de fondo para no bloquear el bucle principal de Uvicorn
            base_signal = await asyncio.to_thread(generator.analyze, symbol)
            
            if not base_signal:
                self.add_scan_log(symbol, "Análisis técnico: Señal neutral (confianza insuficiente)")
                return
            
            action = base_signal.get('type', 'HOLD').upper()
            confidence = base_signal.get('confidence', 0)
            
            if action == "HOLD":
                self.add_scan_log(symbol, "Análisis técnico: HOLD | Sin alineación clara de timeframes.")
                return
                
            # Verificar si el tipo de mercado está deshabilitado granularmente
            is_spot = action in ('BUY', 'SELL')
            is_futures = action in ('LONG', 'SHORT')
            
            spot_enabled = self.settings.get('spot_enabled', True)
            futures_enabled = self.settings.get('futures_enabled', True)
            
            if is_spot and not spot_enabled:
                self.add_scan_log(symbol, "IA Spot pausada por el usuario")
                logger.info(f"⏸️ [IA Spot] Señal técnica {action} para {symbol} descartada porque la IA Spot está pausada.")
                return
                
            if is_futures and not futures_enabled:
                self.add_scan_log(symbol, "IA Futuros pausada por el usuario")
                logger.info(f"⏸️ [IA Futuros] Señal técnica {action} para {symbol} descartada porque la IA Futuros está pausada.")
                return
                
            # 2. Solicitar 'High-Confidence Institutional Analysis' al SmartPool
            from app.ml.llm_connector import get_llm_manager
            llm = get_llm_manager()
            
            indicators = base_signal.get('timeframes', {}).get('1h', {}).get('indicators', {})
            patterns = [r for r in base_signal.get('reasoning', []) if '📊' in r]
            
            self.add_scan_log(symbol, f"Validando señal técnica {action} ({confidence}%) con SmartPool IA (Timeout: 10s)...")
            
            smartpool_analysis = None
            try:
                smartpool_analysis = await asyncio.wait_for(
                    llm.analyze_market(
                        symbol=symbol,
                        current_price=base_signal.get('current_price', 0),
                        indicators=indicators,
                        patterns=patterns,
                        recent_signals=[] 
                    ),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.warning(f"⏳ Timeout de 10s en SmartPool para {symbol}")
                self.add_scan_log(symbol, "⏳ Timeout de IA: El modelo no respondió a tiempo. Se descarta la validación IA.")
            except Exception as e:
                logger.error(f"❌ Error en análisis LLM para {symbol}: {e}")
                self.add_scan_log(symbol, f"❌ Error en validación IA: {str(e)}")
            
            signal = base_signal.copy()
            if smartpool_analysis:
                logger.info(f"🧠 SmartPool validó {symbol}: {smartpool_analysis.get('signal')} con {smartpool_analysis.get('confidence')}%")
                # Normalizar el action: BUY/LONG -> BUY, SELL/SHORT -> SELL, resto HOLD
                raw_action = str(smartpool_analysis.get('signal', base_signal.get('type', 'HOLD'))).upper()
                signal['action'] = 'BUY' if raw_action in ('BUY', 'LONG') else 'SELL' if raw_action in ('SELL', 'SHORT') else 'HOLD'
                signal['confidence'] = smartpool_analysis.get('confidence', base_signal.get('confidence', 0))
                signal['reasoning'].insert(0, f"🤖 SmartPool: {smartpool_analysis.get('reasoning')}")
            else:
                raw_action = str(base_signal.get('type', 'HOLD')).upper()
                signal['action'] = 'BUY' if raw_action in ('BUY', 'LONG') else 'SELL' if raw_action in ('SELL', 'SHORT') else 'HOLD'
            
            final_action = signal.get('action')
            final_confidence = signal.get('confidence', 0)
            reason = signal.get('reasoning', ["Sin detalles"])[0]
            
            # Doble verificación posterior al SmartPool
            is_spot_final = raw_action in ('BUY', 'SELL')
            is_futures_final = raw_action in ('LONG', 'SHORT')
            
            if is_spot_final and not spot_enabled:
                self.add_scan_log(symbol, "IA Spot pausada por el usuario")
                logger.info(f"⏸️ [IA Spot] Veredicto SmartPool {raw_action} para {symbol} descartado porque la IA Spot está pausada.")
                return
                
            if is_futures_final and not futures_enabled:
                self.add_scan_log(symbol, "IA Futuros pausada por el usuario")
                logger.info(f"⏸️ [IA Futuros] Veredicto SmartPool {raw_action} para {symbol} descartado porque la IA Futuros está pausada.")
                return
            
            self.add_scan_log(symbol, f"Resultado SmartPool: {final_action} (Confianza: {final_confidence}%) | {reason}")
            
            # Descartar si el veredicto final es HOLD
            if final_action == "HOLD":
                return
                
            # Verificar si ya está en cola
            if symbol in self.signal_queue.approved_signals:
                self.add_scan_log(symbol, f"Señal {final_action} ya se encuentra en cola de ejecución.")
                return
                
            # Añadir a cola si cumple criterios
            settings = await self._get_symbol_settings(symbol)
            if self._signal_meets_criteria(signal, settings):
                self.signal_queue.add_approved_signal(signal, settings)
                self.add_scan_log(symbol, f"🔥 ¡SEÑAL APROBADA! Añadida a cola para ejecución: {final_action}")
            else:
                self.add_scan_log(symbol, f"⚠️ Señal descartada por filtros de configuración: {final_action} (Confianza: {final_confidence}%)")
                
        except Exception as e:
            logger.error(f"❌ Error generando señal para {symbol}: {e}")
            self.add_scan_log(symbol, f"❌ Error en análisis: {str(e)}")

    async def _generate_new_signals(self):
        """Genera nuevas señales para símbolos configurados en paralelo concurrentemente."""
        # Obtener símbolos configurados para automación
        symbols = await self._get_automation_symbols()
        if not symbols:
            return
            
        # Lanzar escaneo paralelo concurrente (Stealth Performance Boost)
        tasks = [self._scan_single_symbol(symbol) for symbol in symbols]
        await asyncio.gather(*tasks)
                
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
        # El generador emite type='LONG'/'SHORT', el LLM puede emitir 'BUY'/'SELL'
        action = signal.get('action', signal.get('type', 'HOLD')).upper()
        side = 'BUY' if action in ('BUY', 'LONG') else 'SELL'
        
        # Validación de seguridad granular en caliente en tiempo de ejecución
        original_action = signal.get('type', 'HOLD').upper()
        is_spot_trade = original_action in ('BUY', 'SELL') or action in ('BUY', 'SELL')
        is_futures_trade = original_action in ('LONG', 'SHORT') or action in ('LONG', 'SHORT')
        
        spot_enabled = self.settings.get('spot_enabled', True)
        futures_enabled = self.settings.get('futures_enabled', True)
        
        if is_spot_trade and not spot_enabled:
            logger.warning(f"⏸️ [IA Spot] Abortando ejecución automática para {symbol} porque la IA Spot está pausada en caliente.")
            return False
            
        if is_futures_trade and not futures_enabled:
            logger.warning(f"⏸️ [IA Futuros] Abortando ejecución automática para {symbol} porque la IA Futuros está pausada en caliente.")
            return False
        
        # Calcular tamaño de posición
        quantity = await self._calculate_position_size(symbol, signal)
        
        if quantity <= 0:
            return False
            
        try:
            # Obtener precio real del mercado
            from app.infrastructure.binance.client import get_binance_client
            client = get_binance_client()
            real_price = await asyncio.to_thread(client.get_price, symbol)
            
            if not real_price:
                logger.error(f"❌ No se pudo obtener precio real para {symbol}")
                return False
            
            # Ejecutar orden en modo práctica con datos reales
            logger.info(f"📈 Ejecutando orden: {side} {quantity} {symbol} @ ${real_price}")
            
            # Si estamos en modo práctica, realizar deducciones/depósitos en caliente en la wallet virtual del usuario
            is_practice = signal_data['params'].get('practice_mode_only', True)
            if is_practice:
                user_id = self.user_id if hasattr(self, 'user_id') else 1
                wallet_success = await self._update_practice_wallet_balance(
                    user_id=user_id,
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    price=real_price
                )
                if not wallet_success:
                    logger.warning(f"⚠️ Se abortó la orden automática de {symbol} por fondos insuficientes en la wallet de práctica.")
                    return False
            
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

    async def _update_practice_wallet_balance(self, user_id: int, symbol: str, side: str, quantity: float, price: float) -> bool:
        """
        Actualiza el saldo de la wallet de práctica ante cada compra/venta del bot IA
        y registra persistentemente la operación en el historial (virtual_trades) con strategy='AI_AUTO'.
        """
        db = SessionLocal()
        try:
            from app.api.v1.practice import get_or_create_wallet
            from app.infrastructure.database.models import VirtualTrade as VirtualTradeModel
            import json as json_lib
            
            wallet = get_or_create_wallet(db, user_id)
            balances = json_lib.loads(wallet.balances) if wallet.balances else {"USDT": 50.0}
            
            base_asset = symbol.replace("USDT", "").replace("BUSD", "").upper()
            total_amount = quantity * price
            fee = total_amount * 0.001
            
            if side.upper() == "BUY":
                usdt_balance = float(balances.get("USDT", 0))
                if usdt_balance >= total_amount + fee:
                    balances["USDT"] = round(usdt_balance - total_amount - fee, 2)
                    current_asset_balance = float(balances.get(base_asset, 0))
                    balances[base_asset] = round(current_asset_balance + quantity, 8)
                    logger.info(f"💰 [IA AUTO] Compra: Descontados {total_amount + fee:.2f} USDT. Sumados {quantity} {base_asset}")
                else:
                    logger.warning(f"⚠️ [IA AUTO] Saldo insuficiente en práctica para comprar {symbol}")
                    return False
            elif side.upper() == "SELL":
                asset_balance = float(balances.get(base_asset, 0))
                if asset_balance >= quantity:
                    balances[base_asset] = round(asset_balance - quantity, 8)
                    usdt_balance = float(balances.get("USDT", 0))
                    balances["USDT"] = round(usdt_balance + total_amount - fee, 2)
                    
                    if balances[base_asset] <= 0.00000001:
                        del balances[base_asset]
                    logger.info(f"💰 [IA AUTO] Venta: Descontados {quantity} {base_asset}. Sumados {total_amount - fee:.2f} USDT")
                else:
                    logger.warning(f"⚠️ [IA AUTO] Saldo insuficiente en práctica para vender {symbol}")
                    return False
            
            # Guardar balances actualizados
            wallet.balances = json_lib.dumps(balances)
            
            # Registrar el trade de automatización en la base de datos de práctica
            pnl_amount = 0.0
            if side.upper() == "SELL":
                # Buscar el último BUY de este símbolo en la wallet de práctica para calcular P&L
                last_buy = db.query(VirtualTradeModel).filter(
                    VirtualTradeModel.wallet_id == wallet.id,
                    VirtualTradeModel.symbol == symbol,
                    VirtualTradeModel.side == "BUY"
                ).order_by(VirtualTradeModel.created_at.desc()).first()
                if last_buy:
                    pnl_amount = round((price - last_buy.price) * quantity, 2)
                    
            pnl_amount = round(pnl_amount, 2)
            new_trade = VirtualTradeModel(
                wallet_id=wallet.id,
                symbol=symbol,
                side=side.upper(),
                type="MARKET",
                strategy="AI_AUTO",
                reason="Ejecución automática del bot IA 24/7",
                quantity=quantity,
                price=price,
                pnl=pnl_amount,
                created_at=datetime.utcnow()
            )
            db.add(new_trade)
            db.commit()
            logger.success(f"📈 [IA AUTO] Guardado trade en historial de práctica: {side} {quantity} {symbol} @ ${price}")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando wallet de práctica en auto-trading: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
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
        db = SessionLocal()
        try:
            from app.infrastructure.database.models import AutomationConfig
            config = db.query(AutomationConfig).filter(AutomationConfig.user_id == user_id).first()
            if config:
                self.settings = {
                    'max_daily_trades': config.max_daily_trades,
                    'max_position_size': config.max_position_size,
                    'min_signal_confidence': config.min_signal_confidence,
                    'allowed_tiers': config.allowed_tiers or ['S', 'A'],
                    'risk_level': config.risk_level,
                    'pause_on_high_volatility': config.pause_on_high_volatility,
                    'check_interval_seconds': config.check_interval_seconds,
                    'practice_mode_only': config.practice_mode_only,
                    'spot_enabled': config.spot_enabled if hasattr(config, 'spot_enabled') else True,
                    'futures_enabled': config.futures_enabled if hasattr(config, 'futures_enabled') else True
                }
                self.check_interval = config.check_interval_seconds or 30
                self.max_daily_trades = config.max_daily_trades or 10
                logger.info(f"⚙️ Configuración recargada de BD para usuario {user_id}: Confianza Mínima={self.settings['min_signal_confidence']}%, Posición Máxima=${self.settings['max_position_size']} USD, Modo Práctica={self.settings['practice_mode_only']}, Spot={self.settings['spot_enabled']}, Futuros={self.settings['futures_enabled']}")
            else:
                self.settings = {
                    'max_daily_trades': 10,
                    'max_position_size': 50.0,
                    'min_signal_confidence': 70,
                    'allowed_tiers': ['S', 'A'],
                    'risk_level': 'moderate',
                    'pause_on_high_volatility': True,
                    'check_interval_seconds': 30,
                    'practice_mode_only': True,
                    'spot_enabled': True,
                    'futures_enabled': True
                }
                self.check_interval = 30
                self.max_daily_trades = 10
                logger.warning(f"⚠️ No se encontró AutomationConfig para usuario {user_id}. Usando valores por defecto.")
        finally:
            db.close()
        
    async def _update_enabled_status(self, user_id: int, enabled: bool):
        """Actualiza el estado 'enabled' en la base de datos de manera persistente."""
        db = SessionLocal()
        try:
            from app.infrastructure.database.models import AutomationConfig
            config = db.query(AutomationConfig).filter(AutomationConfig.user_id == user_id).first()
            if config:
                config.enabled = enabled
                db.commit()
                logger.info(f"💾 Estado de automatización persistido en DB para usuario {user_id}: enabled={enabled}")
            else:
                config = AutomationConfig(user_id=user_id, enabled=enabled)
                db.add(config)
                db.commit()
                logger.info(f"💾 Nueva configuración creada y persistida en DB para usuario {user_id}: enabled={enabled}")
        except Exception as e:
            logger.error(f"❌ Error persistiendo estado de automatización para usuario {user_id}: {e}")
            db.rollback()
        finally:
            db.close()
        
    async def _get_automation_symbols(self) -> List[str]:
        """Retorna símbolos configurados para automatización."""
        return [
            'BTCUSDT', 
            'ETHUSDT', 
            'SOLUSDT', 
            'BNBUSDT',
            'XRPUSDT',
            'NEARUSDT',
            'LINKUSDT', 
            'DOGEUSDT',
            'SAGAUSDT',
            'NILUSDT',
            'RIFUSDT',
            'DEXEUSDT'
        ]
        
    async def _get_symbol_settings(self, symbol: str) -> Dict:
        """Retorna configuración para símbolo específico basada en configuración de usuario."""
        if hasattr(self, 'settings') and self.settings:
            return {
                'min_confidence': self.settings.get('min_signal_confidence', 70),
                'allowed_tiers': self.settings.get('allowed_tiers', ['S', 'A']),
                'max_position_size': self.settings.get('max_position_size', 50.0),
                'practice_mode_only': self.settings.get('practice_mode_only', True)
            }
        return {
            'min_confidence': 70,
            'allowed_tiers': ['S', 'A'],
            'max_position_size': 50.0,
            'practice_mode_only': True
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
        """Calcula tamaño de posición (quantity) basado en señal, precio actual y configuración de la DB."""
        try:
            price = signal.get('current_price') or signal.get('entry_price')
            if not price or price <= 0:
                # Intentar obtener el precio de Binance
                try:
                    from app.infrastructure.binance.client import get_binance_client
                    client = get_binance_client()
                    price = client.get_price(symbol)
                except Exception:
                    price = None
                    
            if not price or price <= 0:
                logger.error(f"❌ No se pudo obtener precio para calcular tamaño de posición de {symbol}")
                return 0.0
                
            # Obtener tamaño de posición máximo en USD de la configuración
            max_position_size_usd = 50.0
            if hasattr(self, 'settings') and self.settings:
                max_position_size_usd = self.settings.get('max_position_size', 50.0)
                
            # Calcular cantidad
            quantity = max_position_size_usd / price
            
            # Redondear según el símbolo para evitar problemas con la precisión de Binance
            symbol_upper = symbol.upper()
            if "BTC" in symbol_upper:
                quantity = round(quantity, 6)
            elif "ETH" in symbol_upper:
                quantity = round(quantity, 5)
            elif "SOL" in symbol_upper:
                quantity = round(quantity, 4)
            elif "LINK" in symbol_upper:
                quantity = round(quantity, 3)
            elif "BNB" in symbol_upper:
                quantity = round(quantity, 4)
            elif any(x in symbol_upper for x in ["ADA", "XRP", "MATIC", "DOGE"]):
                quantity = round(quantity, 1)
            else:
                quantity = round(quantity, 2)
                
            logger.info(f"📐 Posición calculada para {symbol}: ${max_position_size_usd} USD / ${price} = {quantity} unidades")
            return quantity
        except Exception as e:
            logger.error(f"❌ Error al calcular tamaño de posición para {symbol}: {e}")
            return 0.0
        
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