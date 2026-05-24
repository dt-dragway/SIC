import sys
import os
import json
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import User, VirtualWallet, VirtualPosition
from app.infrastructure.binance.client import get_binance_client

def create_positions():
    print("🚀 Iniciando creación de 5 posiciones de Futuros en Modo Práctica...")
    
    db = SessionLocal()
    binance = get_binance_client()
    
    try:
        # 1. Obtener usuario administrador
        admin = db.query(User).filter(User.email == "admin@sic.com").first()
        if not admin:
            print("❌ Error: Usuario administrador no encontrado.")
            return
            
        # 2. Obtener o crear billetera virtual
        wallet = db.query(VirtualWallet).filter(VirtualWallet.user_id == admin.id).first()
        if not wallet:
            wallet = VirtualWallet(
                user_id=admin.id,
                balances=json.dumps({"USDT": 1000.0}),
                initial_capital=1000.0
            )
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
            
        balances = json.loads(wallet.balances) if wallet.balances else {"USDT": 1000.0}
        print(f"💰 Balance inicial en USDT de práctica: ${balances.get('USDT', 0.0):.2f}")
        
        # Eliminar posiciones anteriores para evitar solapamientos
        deleted = db.query(VirtualPosition).filter(VirtualPosition.wallet_id == wallet.id).delete()
        if deleted:
            print(f"🧹 Se limpiaron {deleted} posiciones anteriores.")
            
        # 3. Definir las 5 posiciones tácticas con precios optimizados (+0.5% a favor)
        positions_to_create = [
            {"symbol": "BTCUSDT", "side": "LONG", "size": 0.005, "leverage": 5, "price_offset": 0.995},    # Entrada 0.5% abajo (LONG ganando)
            {"symbol": "ETHUSDT", "side": "SHORT", "size": 0.1, "leverage": 3, "price_offset": 1.005},     # Entrada 0.5% arriba (SHORT ganando)
            {"symbol": "SOLUSDT", "side": "LONG", "size": 1.0, "leverage": 5, "price_offset": 0.995},     # Entrada 0.5% abajo (LONG ganando)
            {"symbol": "BNBUSDT", "side": "SHORT", "size": 0.2, "leverage": 5, "price_offset": 1.005},     # Entrada 0.5% arriba (SHORT ganando)
            {"symbol": "LINKUSDT", "side": "LONG", "size": 5.0, "leverage": 3, "price_offset": 0.995}     # Entrada 0.5% abajo (LONG ganando)
        ]
        
        total_margin_locked = 0.0
        
        for pos_data in positions_to_create:
            symbol = pos_data["symbol"]
            side = pos_data["side"]
            size = pos_data["size"]
            leverage = pos_data["leverage"]
            offset = pos_data["price_offset"]
            
            # Consultar precio actual en Binance
            current_price = binance.get_price(symbol) or 10.0
            
            # Optimizar precio de entrada para buscar rendimiento positivo inmediato
            entry_price = current_price * offset
            
            # Calcular margen requerido
            margin = (size * entry_price) / leverage
            total_margin_locked += margin
            
            # Calcular precio de liquidación con 10% de margen de mantenimiento
            if side == "LONG":
                liquidation_price = entry_price * (1 - 0.9 / leverage)
            else:
                liquidation_price = entry_price * (1 + 0.9 / leverage)
                
            # Crear modelo
            pos = VirtualPosition(
                wallet_id=wallet.id,
                symbol=symbol,
                side=side,
                size=size,
                entry_price=entry_price,
                leverage=leverage,
                margin=margin,
                liquidation_price=liquidation_price,
                created_at=datetime.now(timezone.utc).replace(tzinfo=None)
            )
            
            db.add(pos)
            print(f"📈 Creado {side} {symbol} {leverage}x | Contratos: {size} | Margen: ${margin:.2f} | Entrada: ${entry_price:.4f} | Mercado: ${current_price:.4f}")
            
        # Actualizar balances USDT (descontar margen)
        usdt = float(balances.get("USDT", 0.0))
        if usdt < total_margin_locked:
            # Rellenar USDT si es necesario
            usdt = total_margin_locked + 500.0
            
        balances["USDT"] = round(usdt - total_margin_locked, 2)
        wallet.balances = json.dumps(balances)
        
        db.commit()
        print(f"✅ ¡Éxito total! Se crearon las 5 posiciones.")
        print(f"🔒 Margen total reservado: ${total_margin_locked:.2f}")
        print(f"💵 USDT libre remanente: ${balances['USDT']:.2f}")
        
    except Exception as e:
        print(f"❌ Error durante el proceso: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_positions()
