import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.v1.trading import get_real_trading_stats
from app.infrastructure.binance.client import get_binance_client

async def test_stats():
    print("📡 Conectando a Binance...")
    client = get_binance_client()
    
    if client.is_connected():
        print("💰 Obteniendo estadísticas de trading REAL...")
        # Simulamos la llamada a get_real_trading_stats
        # Como requiere token, llamamos directamente a la lógica de la función o extraemos sus cálculos
        current_value = client.get_wallet_value_usd()
        print(f"   Balance actual USD: ${current_value:.6f}")
        
        all_orders = []
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
        
        for sym in symbols:
            try:
                orders = client.client.get_all_orders(symbol=sym, limit=100)
                filled = [o for o in orders if o.get("status") == "FILLED"]
                print(f"    - {sym}: {len(orders)} órdenes totales, {len(filled)} FILLED")
                all_orders.extend(filled)
            except Exception as e:
                print(f"    - {sym}: Error al obtener órdenes: {e}")
                
        print(f"\n   Total de órdenes FILLED encontradas: {len(all_orders)}")
        
        # Calcular pnls
        pnls = []
        buy_orders = [o for o in all_orders if o.get("side") == "BUY"]
        sell_orders = [o for o in all_orders if o.get("side") == "SELL"]
        
        for sell in sell_orders:
            try:
                sell_total = float(sell.get("cummulativeQuoteQty", 0))
                if sell_total > 0:
                    matching_buys = [b for b in buy_orders 
                                    if b.get("symbol") == sell.get("symbol")
                                    and b.get("time", 0) < sell.get("time", 0)]
                    if matching_buys:
                        buy = max(matching_buys, key=lambda x: x.get("time", 0))
                        buy_total = float(buy.get("cummulativeQuoteQty", 0))
                        pnl = sell_total - buy_total
                        pnls.append(pnl)
            except Exception as e:
                pass
                
        print(f"   PnLs individuales calculados: {pnls}")
        total_pnl = sum(pnls)
        print(f"   Total PnL sumado: {total_pnl}")
        
        initial_capital = max(100, current_value - total_pnl)
        roi_percent = ((current_value - initial_capital) / initial_capital * 100) if initial_capital > 0 else 0
        print(f"   Capital Inicial Estimado: ${initial_capital:.4f}")
        print(f"   ROI Estimado: {roi_percent:.4f}%")
        
    else:
        print("❌ Error: No conectado a Binance.")

if __name__ == "__main__":
    asyncio.run(test_stats())
