import sys
import os
import json
from datetime import datetime

# Add backend to path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import VirtualWallet, VirtualTrade, User
from app.infrastructure.binance.client import get_binance_client

def reset_wallet():
    print("🔄 INICIANDO RESET DE BILLETERA DE PRÁCTICA (LOW FUNDS SIMULATION)...")
    db = SessionLocal()
    client = get_binance_client()
    
    # 1. Obtener billetera de usuario admin (User ID: 1)
    user_id = 1
    wallet = db.query(VirtualWallet).filter(VirtualWallet.user_id == user_id).first()
    
    if not wallet:
        print("❌ Error: No se encontró billetera virtual para el usuario 1.")
        db.close()
        return
        
    print(f"✅ Billetera encontrada (ID: {wallet.id})")
    
    # 2. Borrar historial de trades previos para iniciar desde cero
    print("🧹 Borrando historial de trades virtuales anteriores...")
    db.query(VirtualTrade).filter(VirtualTrade.wallet_id == wallet.id).delete()
    
    # 3. Calcular balances dinámicos
    # $50 USDT + $10 equivalente en cada una de las principales cryptos
    cryptos = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOT", "MATIC", "DOGE", "LINK"]
    new_balances = {"USDT": 50.0}
    
    print("\n📈 Consultando precios en Binance para calcular equivalencias de $10 USD:")
    for crypto in cryptos:
        symbol = f"{crypto}USDT"
        try:
            price = client.get_price(symbol)
            if price and price > 0:
                amount = 10.0 / price
                # Redondear a 8 decimales (estándar de cripto)
                new_balances[crypto] = round(amount, 8)
                usd_val = new_balances[crypto] * price
                print(f"   - {crypto}: ${price:,.2f} -> {new_balances[crypto]} {crypto} (Valor: ${usd_val:.2f})")
            else:
                print(f"   ⚠️ No se pudo obtener precio para {crypto}")
        except Exception as e:
            print(f"   ❌ Error consultando {crypto}: {e}")
            
    # 4. Guardar en base de datos
    wallet.balances = json.dumps(new_balances)
    wallet.initial_capital = 150.0  # $50 USDT + 10 cryptos * $10 = $150 total
    db.commit()
    
    print("\n💾 ¡Base de datos actualizada con éxito!")
    print(f"💼 Capital Inicial Registrado: ${wallet.initial_capital} USD")
    print(f"📦 JSON de Balances guardado: {wallet.balances}")
    
    db.close()
    print("\n🚀 RESET COMPLETADO CORRECTAMENTE. TODO LISTO DESDE CERO.")

if __name__ == "__main__":
    reset_wallet()
