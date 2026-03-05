"""
SIC Ultra - Trade Marker System
Sistema para marcar y monitorear trades ejecutados en los gráficos
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import os

@dataclass
class TradeMarker:
    """Marcador de trade para visualización en gráficos"""
    id: str
    symbol: str
    side: str  # 'LONG' or 'SHORT'
    entry_price: float
    stop_loss: float
    take_profit: float
    quantity: float
    entry_time: datetime
    status: str  # 'ACTIVE', 'CLOSED', 'STOPPED', 'PROFIT_TAKEN'
    pnl: Optional[float] = None
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    confidence: Optional[float] = None
    tier: Optional[str] = None
    chart_marker_id: Optional[str] = None  # ID del marcador en el chart

class TradeMarkerManager:
    """Gestor de marcadores de trades para gráficos"""
    
    def __init__(self):
        self.active_trades: Dict[str, TradeMarker] = {}
        self.historical_trades: List[TradeMarker] = []
        self.chart_markers: Dict[str, str] = {}  # trade_id -> chart_marker_id
        self.data_file = os.path.join(os.path.dirname(__file__), "trade_markers.json")
        self._load_markers()
    
    def add_trade_marker(self, 
                         symbol: str,
                         side: str,
                         entry_price: float,
                         stop_loss: float,
                         take_profit: float,
                         quantity: float,
                         confidence: Optional[float] = None,
                         tier: Optional[str] = None) -> str:
        """Añade un nuevo marcador de trade"""
        
        trade_id = f"{symbol}_{side}_{int(datetime.utcnow().timestamp())}"
        
        marker = TradeMarker(
            id=trade_id,
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            quantity=quantity,
            entry_time=datetime.utcnow(),
            status='ACTIVE',
            confidence=confidence,
            tier=tier
        )
        
        self.active_trades[trade_id] = marker
        self._save_markers()
        
        return trade_id
    
    def close_trade_marker(self, 
                           trade_id: str,
                           exit_price: float,
                           pnl: float,
                           exit_reason: str = 'MANUAL') -> bool:
        """Cierra un marcador de trade"""
        
        if trade_id not in self.active_trades:
            return False
        
        marker = self.active_trades[trade_id]
        marker.exit_price = exit_price
        marker.exit_time = datetime.utcnow()
        marker.pnl = pnl
        
        # Determinar estado
        if exit_reason == 'STOP_LOSS':
            marker.status = 'STOPPED'
        elif exit_reason == 'TAKE_PROFIT':
            marker.status = 'PROFIT_TAKEN'
        else:
            marker.status = 'CLOSED'
        
        # Mover a históricos
        self.historical_trades.append(marker)
        del self.active_trades[trade_id]
        
        self._save_markers()
        return True
    
    def get_active_trades(self, symbol: Optional[str] = None) -> List[TradeMarker]:
        """Obtiene trades activos (opcionalmente filtrados por símbolo)"""
        active = list(self.active_trades.values())
        
        if symbol:
            active = [t for t in active if t.symbol == symbol]
        
        return active
    
    def get_historical_trades(self, 
                              symbol: Optional[str] = None,
                              days: Optional[int] = None) -> List[TradeMarker]:
        """Obtiene trades históricos"""
        historical = self.historical_trades.copy()
        
        if symbol:
            historical = [t for t in historical if t.symbol == symbol]
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            historical = [t for t in historical if t.entry_time > cutoff]
        
        return sorted(historical, key=lambda x: x.entry_time, reverse=True)
    
    def get_chart_data(self, symbol: str) -> Dict[str, Any]:
        """Obtiene datos para visualización en gráfico"""
        
        active_trades = self.get_active_trades(symbol)
        recent_trades = self.get_historical_trades(symbol, days=7)  # Últimos 7 días
        
        # Preparar marcadores para el gráfico
        chart_markers = []
        
        for trade in active_trades:
            marker = {
                'id': trade.id,
                'position': 'entry',
                'price': trade.entry_price,
                'time': trade.entry_time.isoformat(),
                'side': trade.side,
                'color': '#10b981' if trade.side == 'LONG' else '#ef4444',
                'label': f"{trade.side} @ ${trade.entry_price:.2f}",
                'confidence': trade.confidence,
                'tier': trade.tier,
                'status': trade.status,
                'sl': trade.stop_loss,
                'tp': trade.take_profit
            }
            chart_markers.append(marker)
            
            # Añadir SL y TP
            chart_markers.append({
                'id': f"{trade.id}_sl",
                'position': 'stop_loss',
                'price': trade.stop_loss,
                'time': trade.entry_time.isoformat(),
                'side': trade.side,
                'color': '#ef4444',
                'label': f"SL @ ${trade.stop_loss:.2f}",
                'line_style': 'dashed',
                'parent_trade': trade.id
            })
            
            chart_markers.append({
                'id': f"{trade.id}_tp",
                'position': 'take_profit',
                'price': trade.take_profit,
                'time': trade.entry_time.isoformat(),
                'side': trade.side,
                'color': '#10b981',
                'label': f"TP @ ${trade.take_profit:.2f}",
                'line_style': 'dashed',
                'parent_trade': trade.id
            })
        
        # Añadir trades cerrados recientes (marcas de salida)
        for trade in recent_trades:
            if trade.exit_price and trade.exit_time:
                exit_marker = {
                    'id': f"{trade.id}_exit",
                    'position': 'exit',
                    'price': trade.exit_price,
                    'time': trade.exit_time.isoformat(),
                    'side': 'SHORT' if trade.side == 'LONG' else 'LONG',  # Salida opuesta
                    'color': '#f59e0b',
                    'label': f"Exit @ ${trade.exit_price:.2f} ({trade.status})",
                    'pnl': trade.pnl,
                    'parent_trade': trade.id
                }
                chart_markers.append(exit_marker)
        
        return {
            'symbol': symbol,
            'markers': chart_markers,
            'active_count': len(active_trades),
            'recent_pnl': sum(t.pnl or 0 for t in recent_trades if t.pnl),
            'stats': self._calculate_symbol_stats(symbol)
        }
    
    def _calculate_symbol_stats(self, symbol: str) -> Dict[str, Any]:
        """Calcula estadísticas por símbolo"""
        
        all_trades = self.get_historical_trades(symbol) + self.get_active_trades(symbol)
        
        if not all_trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_pnl': 0,
                'best_trade': 0,
                'worst_trade': 0
            }
        
        completed_trades = [t for t in all_trades if t.pnl is not None]
        
        if not completed_trades:
            return {
                'total_trades': len(all_trades),
                'win_rate': 0,
                'avg_pnl': 0,
                'best_trade': 0,
                'worst_trade': 0
            }
        
        winning_trades = [t for t in completed_trades if t.pnl > 0]
        win_rate = (len(winning_trades) / len(completed_trades)) * 100
        
        pnls = [t.pnl for t in completed_trades]
        avg_pnl = sum(pnls) / len(pnls)
        best_trade = max(pnls)
        worst_trade = min(pnls)
        
        return {
            'total_trades': len(all_trades),
            'completed_trades': len(completed_trades),
            'win_rate': round(win_rate, 1),
            'avg_pnl': round(avg_pnl, 2),
            'best_trade': round(best_trade, 2),
            'worst_trade': round(worst_trade, 2)
        }
    
    def _load_markers(self):
        """Carga marcadores desde archivo"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                # Cargar trades activos
                for trade_data in data.get('active_trades', []):
                    # Convertir strings a datetime
                    trade_data['entry_time'] = datetime.fromisoformat(trade_data['entry_time'])
                    if trade_data.get('exit_time'):
                        trade_data['exit_time'] = datetime.fromisoformat(trade_data['exit_time'])
                    
                    marker = TradeMarker(**trade_data)
                    self.active_trades[marker.id] = marker
                
                # Cargar trades históricos
                for trade_data in data.get('historical_trades', []):
                    trade_data['entry_time'] = datetime.fromisoformat(trade_data['entry_time'])
                    if trade_data.get('exit_time'):
                        trade_data['exit_time'] = datetime.fromisoformat(trade_data['exit_time'])
                    
                    marker = TradeMarker(**trade_data)
                    self.historical_trades.append(marker)
                
                print(f"📊 Cargados {len(self.active_trades)} trades activos y {len(self.historical_trades)} históricos")
        
        except Exception as e:
            print(f"❌ Error cargando marcadores: {e}")
    
    def _save_markers(self):
        """Guarda marcadores a archivo"""
        try:
            data = {
                'active_trades': [asdict(trade) for trade in self.active_trades.values()],
                'historical_trades': [asdict(trade) for trade in self.historical_trades],
                'last_updated': datetime.utcnow().isoformat()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"💾 Guardados {len(self.active_trades)} trades activos y {len(self.historical_trades)} históricos")
        
        except Exception as e:
            print(f"❌ Error guardando marcadores: {e}")


# Instancia global
trade_marker_manager = TradeMarkerManager()


def get_trade_marker_manager() -> TradeMarkerManager:
    """Obtiene instancia del gestor de marcadores"""
    return trade_marker_manager