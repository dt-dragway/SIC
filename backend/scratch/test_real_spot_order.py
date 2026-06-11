import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.binance.client import get_binance_client

async def test_real_spot_order():
    print("📡 Conectando a Binance con tus API Keys...")
    client = get_binance_client()
    
    if not client.is_connected():
        print("❌ Error: No se pudo conectar a Binance.")
        return
        
    print("\n🔍 Validando tu balance real en USDT...")
    bal = client.get_balance("USDT")
    usdt_free = bal["free"] if bal else 0.0
    print(f"   Saldo actual: {usdt_free} USDT")
    
    symbol = "BTCUSDT"
    price = client.get_price(symbol)
    print(f"   Precio actual de {symbol}: ${price:.2f} USDT")
    
    # Binance requiere mínimo 5-10 USDT por orden real.
    # Explicamos esto y enviamos una orden de validación sintáctica (Test Order)
    print(f"\n⚡ Enviando ORDEN DE PRUEBA (Test Order) a Binance SPOT para comprar 10 USDT de BTC...")
    print("   (Esta prueba valida tus claves, firmas, límites del exchange y conectividad real sin descontar saldo)")
    
    try:
        # Calcular cantidad para 10 USDT
        qty = round(10.0 / price, 6)
        
        # Enviar test order a Binance (POST /api/v3/order/test)
        client.client.create_test_order(
            symbol=symbol,
            side="BUY",
            type="MARKET",
            quantity=qty
        )
        print("\n✅ ¡ÉXITO TOTAL! Binance REAL aceptó y validó la orden de prueba sintáctica.")
        print("   Tus API Keys están 100% integradas y autorizadas para colocar órdenes de Spot.")
    except Exception as e:
        print(f"\n❌ Error al enviar la orden de prueba: {e}")

if __name__ == "__main__":
    asyncio.run(test_real_spot_order())
