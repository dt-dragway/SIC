"""
SIC Ultra - Persistent Execution Engine
Versión mejorada con persistencia en BD y capacidad de recuperación.
"""

import asyncio
import random
import math
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger
import json

from app.infrastructure.binance.client import get_binance_client
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import AlgorithmicOrder

class ExecutionEngine:
    def __init__(self):
        self.active_tasks = {} # order_id -> task

    async def execute_twap(
        self, 
        symbol: str, 
        side: str, 
        total_quantity: float, 
        duration_minutes: int, 
        user_id_int: int,
        order_db_id: Optional[int] = None
    ):
        """
        TWAP Persistente.
        """
        db = SessionLocal()
        
        # Si no tiene ID de DB, creamos el registro
        if order_db_id is None:
            order = AlgorithmicOrder(
                user_id=user_id_int,
                symbol=symbol,
                side=side,
                algo_type="TWAP",
                total_quantity=total_quantity,
                duration_minutes=duration_minutes,
                status="RUNNING"
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            order_db_id = order.id
            logger.info(f"🆕 Nueva orden TWAP registrada en DB: ID {order_db_id}")

        logger.info(f"⚡ Ejecutando TWAP Stealth ID {order_db_id}: {side} {total_quantity} {symbol}")
        
        num_intervals = max(5, duration_minutes)
        
        # STEALTH: Intervalos con jitter log-normal (anti-detección HFT)
        base_interval = (duration_minutes * 60) / num_intervals
        intervals = [base_interval * random.lognormvariate(0, 0.35) for _ in range(num_intervals)]
        # Normalizar para mantener duración total
        interval_total = sum(intervals)
        intervals = [i * (duration_minutes * 60) / interval_total for i in intervals]
        
        # STEALTH: Cantidades variables por slice (±20%)
        qty_weights = [random.uniform(0.8, 1.2) for _ in range(num_intervals)]
        qty_total = sum(qty_weights)
        quantities = [(w / qty_total) * total_quantity for w in qty_weights]
        
        client = get_binance_client()
        executed_qty = 0.0
        
        try:
            for i in range(num_intervals):
                # En producción llamaríamos a client.create_order
                current_price = client.get_price(symbol)
                slice_qty = quantities[i]
                executed_qty += slice_qty
                
                # Actualizar DB
                db_order = db.query(AlgorithmicOrder).filter(AlgorithmicOrder.id == order_db_id).first()
                if db_order:
                    db_order.executed_quantity = executed_qty
                    db_order.updated_at = datetime.utcnow()
                    db.commit()
                
                logger.debug(
                    f"TWAP [{order_db_id}] Slice {i+1}/{num_intervals}: "
                    f"qty={slice_qty:.6f} | Progress: {executed_qty:.6f}/{total_quantity}"
                )
                await asyncio.sleep(intervals[i])

            # Finalizar
            db_order = db.query(AlgorithmicOrder).filter(AlgorithmicOrder.id == order_db_id).first()
            if db_order:
                db_order.status = "COMPLETED"
                db.commit()
            logger.success(f"✅ TWAP {order_db_id} completado con éxito.")

        except Exception as e:
            logger.error(f"❌ Error en TWAP {order_db_id}: {e}")
            db_order = db.query(AlgorithmicOrder).filter(AlgorithmicOrder.id == order_db_id).first()
            if db_order:
                db_order.status = "FAILED"
                db.commit()
        finally:
            db.close()

    async def execute_vwap(
        self,
        symbol: str,
        side: str,
        total_quantity: float,
        duration_minutes: int,
        user_id_int: int,
        order_db_id: Optional[int] = None
    ):
        """
        VWAP (Volume Weighted Average Price) Execution.
        
        Matemática VWAP:
            VWAP = Σ(Price_i × Volume_i) / Σ(Volume_i)
        
        Smart Slicing:
            1. Obtener volumen histórico por intervalo (klines)
            2. Normalizar perfil de volumen
            3. Asignar qty por slice proporcional al volumen esperado
            4. Aplicar jitter stealth (±15%) para anti-detección
        
        El objetivo es ejecutar MÁS cantidad cuando el volumen es ALTO
        (menor impacto en el precio) y MENOS cuando es BAJO.
        """
        db = SessionLocal()
        
        # Registrar en DB si es nueva
        if order_db_id is None:
            order = AlgorithmicOrder(
                user_id=user_id_int,
                symbol=symbol,
                side=side,
                algo_type="VWAP",
                total_quantity=total_quantity,
                duration_minutes=duration_minutes,
                status="RUNNING"
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            order_db_id = order.id
            logger.info(f"🆕 Nueva orden VWAP registrada en DB: ID {order_db_id}")
        
        logger.info(f"📊 Ejecutando VWAP Stealth ID {order_db_id}: {side} {total_quantity} {symbol}")
        
        client = get_binance_client()
        num_intervals = max(5, duration_minutes)
        
        # === 1. Obtener perfil de volumen histórico ===
        volume_profile = await self._get_volume_profile(client, symbol, num_intervals)
        
        # === 2. Calcular qty por slice basado en volumen ===
        vol_sum = sum(volume_profile)
        if vol_sum == 0:
            # Fallback: distribución uniforme si no hay datos de volumen
            volume_weights = [1.0 / num_intervals] * num_intervals
            logger.warning(f"⚠️ Sin datos de volumen para {symbol}, usando distribución uniforme")
        else:
            volume_weights = [v / vol_sum for v in volume_profile]
        
        # === 3. Aplicar jitter stealth (±15%) ===
        jittered_weights = [w * random.uniform(0.85, 1.15) for w in volume_weights]
        jitter_sum = sum(jittered_weights)
        quantities = [(w / jitter_sum) * total_quantity for w in jittered_weights]
        
        # === 4. Intervalos con jitter temporal ===
        base_interval = (duration_minutes * 60) / num_intervals
        intervals = [base_interval * random.lognormvariate(0, 0.25) for _ in range(num_intervals)]
        interval_total = sum(intervals)
        intervals = [i * (duration_minutes * 60) / interval_total for i in intervals]
        
        # === 5. Ejecutar ===
        executed_qty = 0.0
        vwap_numerator = 0.0  # Σ(Price × Qty)
        
        try:
            for i in range(num_intervals):
                current_price = client.get_price(symbol)
                
                if current_price is None or current_price <= 0:
                    logger.warning(f"VWAP [{order_db_id}] Slice {i+1}: Precio no disponible, reintentando...")
                    await asyncio.sleep(2)
                    current_price = client.get_price(symbol)
                    if current_price is None or current_price <= 0:
                        continue  # Skip this slice
                
                slice_qty = quantities[i]
                executed_qty += slice_qty
                vwap_numerator += current_price * slice_qty
                
                # VWAP actual hasta ahora
                current_vwap = vwap_numerator / executed_qty if executed_qty > 0 else 0
                
                # Actualizar DB
                db_order = db.query(AlgorithmicOrder).filter(
                    AlgorithmicOrder.id == order_db_id
                ).first()
                if db_order:
                    db_order.executed_quantity = executed_qty
                    db_order.avg_price = current_vwap
                    db_order.updated_at = datetime.utcnow()
                    db.commit()
                
                logger.debug(
                    f"VWAP [{order_db_id}] Slice {i+1}/{num_intervals}: "
                    f"qty={slice_qty:.6f} @ ${current_price:.2f} | "
                    f"VWAP=${current_vwap:.2f} | "
                    f"Progress: {executed_qty:.6f}/{total_quantity}"
                )
                
                await asyncio.sleep(intervals[i])
            
            # Finalizar
            final_vwap = vwap_numerator / executed_qty if executed_qty > 0 else 0
            db_order = db.query(AlgorithmicOrder).filter(
                AlgorithmicOrder.id == order_db_id
            ).first()
            if db_order:
                db_order.status = "COMPLETED"
                db_order.avg_price = final_vwap
                db.commit()
            
            logger.success(
                f"✅ VWAP {order_db_id} completado | "
                f"VWAP final=${final_vwap:.2f} | Qty={executed_qty:.6f}"
            )
            
        except Exception as e:
            logger.error(f"❌ Error en VWAP {order_db_id}: {e}")
            db_order = db.query(AlgorithmicOrder).filter(
                AlgorithmicOrder.id == order_db_id
            ).first()
            if db_order:
                db_order.status = "FAILED"
                db.commit()
        finally:
            db.close()
    
    async def _get_volume_profile(
        self, client, symbol: str, num_intervals: int
    ) -> List[float]:
        """
        Obtener perfil de volumen histórico para distribución VWAP.
        
        Usa klines del día anterior en los mismos intervalos horarios
        para estimar dónde se concentra el volumen.
        """
        try:
            # Intentar obtener klines de las últimas 24h
            klines = client.get_klines(
                symbol=symbol,
                interval="1h",
                limit=min(24, num_intervals)
            )
            
            if klines and len(klines) > 0:
                volumes = [float(k[5]) for k in klines]  # k[5] = volume
                
                # Si tenemos menos intervals que klines, resamplear
                if len(volumes) < num_intervals:
                    # Repetir el patrón para llenar
                    extended = []
                    while len(extended) < num_intervals:
                        extended.extend(volumes)
                    volumes = extended[:num_intervals]
                elif len(volumes) > num_intervals:
                    # Comprimir: promediar groups
                    step = len(volumes) / num_intervals
                    compressed = []
                    for i in range(num_intervals):
                        start_idx = int(i * step)
                        end_idx = int((i + 1) * step)
                        segment = volumes[start_idx:end_idx]
                        compressed.append(sum(segment) / len(segment) if segment else 1.0)
                    volumes = compressed
                
                return volumes
        except Exception as e:
            logger.error(f"Error obteniendo volume profile: {e}")
        
        # Fallback: perfil de volumen típico crypto (más volumen en US/Asia sessions)
        if num_intervals <= 24:
            typical_profile = [
                0.8, 0.6, 0.5, 0.4, 0.5, 0.7,  # 00-06 UTC (Asia late)
                1.2, 1.5, 1.3, 1.0, 0.8, 0.7,  # 06-12 UTC (Europe)
                1.4, 1.8, 2.0, 1.6, 1.3, 1.0,  # 12-18 UTC (US overlap)
                0.9, 0.8, 0.7, 0.6, 0.7, 0.8   # 18-24 UTC (US late)
            ]
            # Tomar los primeros num_intervals
            return typical_profile[:num_intervals]
        
        # Default: uniform
        return [1.0] * num_intervals

    async def recover_orders(self):
        """
        Recuperar órdenes que quedaron en RUNNING tras un reinicio.
        """
        logger.info("📡 Buscando órdenes algorítmicas para recuperar...")
        db = SessionLocal()
        try:
            pending_orders = db.query(AlgorithmicOrder).filter(AlgorithmicOrder.status == "RUNNING").all()
            for order in pending_orders:
                logger.warning(f"🔄 Recuperando orden {order.id} ({order.symbol})")
                # Reiniciar tarea en segundo plano
                remaining_qty = order.total_quantity - order.executed_quantity
                if remaining_qty > 0:
                    asyncio.create_task(self.execute_twap(
                        order.symbol, order.side, remaining_qty, 
                        order.duration_minutes, order.user_id, order.id
                    ))
        finally:
            db.close()

execution_engine = ExecutionEngine()

def get_execution_engine() -> ExecutionEngine:
    return execution_engine
