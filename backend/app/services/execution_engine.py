"""
SIC Ultra - Persistent Execution Engine
Versión mejorada con persistencia en BD y capacidad de recuperación.
"""

import asyncio
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

        logger.info(f"⚡ Ejecutando TWAP ID {order_db_id}: {side} {total_quantity} {symbol}")
        
        num_intervals = max(5, duration_minutes)
        interval_seconds = (duration_minutes * 60) / num_intervals
        quantity_per_interval = total_quantity / num_intervals
        
        client = get_binance_client()
        executed_qty = 0.0
        
        try:
            for i in range(num_intervals):
                # En producción llamaríamos a client.create_order
                # Simulación de ejecución
                current_price = client.get_price(symbol)
                executed_qty += quantity_per_interval
                
                # Actualizar DB
                db_order = db.query(AlgorithmicOrder).filter(AlgorithmicOrder.id == order_db_id).first()
                if db_order:
                    db_order.executed_quantity = executed_qty
                    db_order.updated_at = datetime.utcnow()
                    db.commit()
                
                logger.debug(f"TWAP [{order_db_id}] Progress: {executed_qty}/{total_quantity}")
                await asyncio.sleep(interval_seconds)

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
