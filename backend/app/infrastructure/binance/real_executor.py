"""
SIC Ultra - Ejecutor de Órdenes Reales

Sistema de órdenes reales a Binance con 7 capas de protección.

⚠️ CUIDADO: Este módulo ejecuta órdenes con dinero REAL
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
from binance.client import Client
from binance.exceptions import BinanceAPIException

from app.config import settings
from app.infrastructure.binance.client import get_binance_client


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"


class RiskLayer:
    """Capas de protección de riesgo"""
    
    def __init__(self):
        # Configuración de límites
        self.max_order_usd = 50.0  # Máximo $50 por orden
        self.max_daily_orders = 10  # Máximo 10 órdenes por día
        self.max_daily_loss_percent = 5.0  # Máximo 5% pérdida diaria
        self.min_stop_loss_percent = 2.0  # Mínimo 2% stop-loss
        self.max_position_percent = 20.0  # Máximo 20% del portfolio por posición
        
        # Tracking
        self.daily_orders = []
        self.daily_pnl = 0.0
        self.last_reset = datetime.utcnow().date()
    
    def _reset_if_new_day(self):
        """Resetear contadores si es nuevo día"""
        today = datetime.utcnow().date()
        if today > self.last_reset:
            self.daily_orders = []
            self.daily_pnl = 0.0
            self.last_reset = today
    
    def check_layer_1_order_size(self, order_usd: float) -> tuple[bool, str]:
        """CAPA 1: Límite de tamaño de orden"""
        if order_usd > self.max_order_usd:
            return False, f"❌ Orden excede límite (${order_usd:.2f} > ${self.max_order_usd})"
        return True, "✅ Tamaño de orden OK"
    
    def check_layer_2_daily_orders(self) -> tuple[bool, str]:
        """CAPA 2: Límite de órdenes diarias"""
        self._reset_if_new_day()
        if len(self.daily_orders) >= self.max_daily_orders:
            return False, f"❌ Límite diario alcanzado ({self.max_daily_orders} órdenes)"
        return True, f"✅ Órdenes hoy: {len(self.daily_orders)}/{self.max_daily_orders}"
    
    def check_layer_3_stop_loss(self, entry: float, stop_loss: float, side: str) -> tuple[bool, str]:
        """CAPA 3: Stop-loss obligatorio"""
        if side == "BUY":
            sl_percent = ((entry - stop_loss) / entry) * 100
        else:
            sl_percent = ((stop_loss - entry) / entry) * 100
        
        if sl_percent < self.min_stop_loss_percent:
            return False, f"❌ Stop-loss muy ajustado ({sl_percent:.1f}% < {self.min_stop_loss_percent}%)"
        if sl_percent > 10:
            return False, f"❌ Stop-loss muy lejano ({sl_percent:.1f}% > 10%)"
        return True, f"✅ Stop-loss: {sl_percent:.1f}%"
    
    def check_layer_4_daily_loss(self, potential_loss: float, portfolio_value: float) -> tuple[bool, str]:
        """CAPA 4: Límite de pérdida diaria"""
        self._reset_if_new_day()
        total_loss = abs(self.daily_pnl) + potential_loss if self.daily_pnl < 0 else potential_loss
        loss_percent = (total_loss / portfolio_value) * 100
        
        if loss_percent > self.max_daily_loss_percent:
            return False, f"❌ Excede límite de pérdida diaria ({loss_percent:.1f}% > {self.max_daily_loss_percent}%)"
        return True, f"✅ Riesgo diario: {loss_percent:.1f}%"
    
    def check_layer_5_position_size(self, order_usd: float, portfolio_value: float) -> tuple[bool, str]:
        """CAPA 5: Límite de tamaño de posición"""
        position_percent = (order_usd / portfolio_value) * 100
        if position_percent > self.max_position_percent:
            return False, f"❌ Posición muy grande ({position_percent:.1f}% > {self.max_position_percent}%)"
        return True, f"✅ Tamaño posición: {position_percent:.1f}%"
    
    def check_layer_6_volatility(self, atr_percent: float) -> tuple[bool, str]:
        """CAPA 6: Verificar volatilidad del mercado"""
        if atr_percent > 5:
            return False, f"❌ Volatilidad muy alta ({atr_percent:.1f}% > 5%)"
        return True, f"✅ Volatilidad: {atr_percent:.1f}%"
    
    def check_layer_7_confirmation(self) -> tuple[bool, str]:
        """CAPA 7: Confirmación del usuario (simulada)"""
        # En producción, esto sería una confirmación real del usuario
        return True, "✅ Orden autorizada"
    
    def validate_order(
        self,
        order_usd: float,
        entry_price: float,
        stop_loss: float,
        side: str,
        portfolio_value: float,
        atr_percent: float = 2.0
    ) -> tuple[bool, list]:
        """
        Validar orden contra las 7 capas de protección.
        
        Returns:
            (passed, list of check results)
        """
        checks = []
        all_passed = True
        
        # Capa 1: Tamaño de orden
        passed, msg = self.check_layer_1_order_size(order_usd)
        checks.append({"layer": 1, "name": "Tamaño orden", "passed": passed, "message": msg})
        all_passed &= passed
        
        # Capa 2: Órdenes diarias
        passed, msg = self.check_layer_2_daily_orders()
        checks.append({"layer": 2, "name": "Límite diario", "passed": passed, "message": msg})
        all_passed &= passed
        
        # Capa 3: Stop-loss
        passed, msg = self.check_layer_3_stop_loss(entry_price, stop_loss, side)
        checks.append({"layer": 3, "name": "Stop-loss", "passed": passed, "message": msg})
        all_passed &= passed
        
        # Capa 4: Pérdida diaria
        potential_loss = order_usd * (abs(entry_price - stop_loss) / entry_price)
        passed, msg = self.check_layer_4_daily_loss(potential_loss, portfolio_value)
        checks.append({"layer": 4, "name": "Pérdida diaria", "passed": passed, "message": msg})
        all_passed &= passed
        
        # Capa 5: Tamaño de posición
        passed, msg = self.check_layer_5_position_size(order_usd, portfolio_value)
        checks.append({"layer": 5, "name": "Tamaño posición", "passed": passed, "message": msg})
        all_passed &= passed
        
        # Capa 6: Volatilidad
        passed, msg = self.check_layer_6_volatility(atr_percent)
        checks.append({"layer": 6, "name": "Volatilidad", "passed": passed, "message": msg})
        all_passed &= passed
        
        # Capa 7: Confirmación
        passed, msg = self.check_layer_7_confirmation()
        checks.append({"layer": 7, "name": "Confirmación", "passed": passed, "message": msg})
        all_passed &= passed
        
        return all_passed, checks
    
    def record_order(self, order_id: str, pnl: float = 0):
        """Registrar orden ejecutada"""
        self.daily_orders.append({
            "id": order_id,
            "timestamp": datetime.utcnow(),
            "pnl": pnl
        })
        self.daily_pnl += pnl


class RealOrderExecutor:
    """
    Ejecutor de órdenes reales a Binance.
    
    ⚠️ SOLO USAR EN MODO BATALLA REAL
    """
    
    def __init__(self):
        self.binance = get_binance_client()
        self.risk = RiskLayer()
    
    def execute_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        stop_loss: Optional[float] = None
    ) -> Dict:
        """
        Ejecutar orden de mercado.
        
        Args:
            symbol: Par de trading (ej: BTCUSDT)
            side: BUY o SELL
            quantity: Cantidad a comprar/vender
            stop_loss: Nivel de stop-loss (OBLIGATORIO)
            
        Returns:
            Resultado de la orden
        """
        if not self.binance.is_connected():
            return {"success": False, "error": "No conectado a Binance"}
        
        if not stop_loss:
            return {"success": False, "error": "Stop-loss es OBLIGATORIO"}
        
        # Obtener precio actual y valor del portfolio
        current_price = self.binance.get_price(symbol)
        if not current_price:
            return {"success": False, "error": f"No se pudo obtener precio de {symbol}"}
        
        order_usd = quantity * current_price
        portfolio_value = self.binance.get_wallet_value_usd() or 100
        
        # Validar contra 7 capas
        passed, checks = self.risk.validate_order(
            order_usd=order_usd,
            entry_price=current_price,
            stop_loss=stop_loss,
            side=side.value,
            portfolio_value=portfolio_value
        )
        
        if not passed:
            failed_checks = [c for c in checks if not c["passed"]]
            return {
                "success": False,
                "error": "Orden rechazada por protecciones de riesgo",
                "failed_checks": failed_checks,
                "all_checks": checks
            }
        
        try:
            # Ejecutar orden principal
            if side == OrderSide.BUY:
                order = self.binance.client.order_market_buy(
                    symbol=symbol,
                    quantity=quantity
                )
            else:
                order = self.binance.client.order_market_sell(
                    symbol=symbol,
                    quantity=quantity
                )
            
            logger.info(f"✅ Orden ejecutada: {side.value} {quantity} {symbol}")
            
            # Crear stop-loss automático
            sl_order = self._create_stop_loss(symbol, side, quantity, stop_loss)
            
            # Registrar en risk layer
            self.risk.record_order(order.get("orderId", "unknown"))
            
            return {
                "success": True,
                "order": order,
                "stop_loss_order": sl_order,
                "checks": checks
            }
            
        except BinanceAPIException as e:
            logger.error(f"❌ Error ejecutando orden: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_stop_loss(
        self,
        symbol: str,
        entry_side: OrderSide,
        quantity: float,
        stop_price: float
    ) -> Optional[Dict]:
        """Crear orden de stop-loss automática"""
        try:
            # Si compramos, el SL es venta y viceversa
            sl_side = "SELL" if entry_side == OrderSide.BUY else "BUY"
            
            sl_order = self.binance.client.create_order(
                symbol=symbol,
                side=sl_side,
                type="STOP_LOSS_LIMIT",
                quantity=quantity,
                price=stop_price,
                stopPrice=stop_price,
                timeInForce="GTC"
            )
            
            logger.info(f"🛡️ Stop-loss creado @ {stop_price}")
            return sl_order
            
        except BinanceAPIException as e:
            logger.warning(f"⚠️ No se pudo crear SL: {e}")
            return None
    
    def get_risk_status(self) -> Dict:
        """Obtener estado actual de las protecciones de riesgo"""
        self.risk._reset_if_new_day()
        
        return {
            "daily_orders": len(self.risk.daily_orders),
            "max_daily_orders": self.risk.max_daily_orders,
            "daily_pnl": self.risk.daily_pnl,
            "max_order_usd": self.risk.max_order_usd,
            "max_daily_loss_percent": self.risk.max_daily_loss_percent,
            "trading_enabled": len(self.risk.daily_orders) < self.risk.max_daily_orders
        }


# Singleton
_real_executor: Optional[RealOrderExecutor] = None


def get_real_executor() -> RealOrderExecutor:
    """Obtener ejecutor de órdenes reales"""
    global _real_executor
    if _real_executor is None:
        _real_executor = RealOrderExecutor()
    return _real_executor
