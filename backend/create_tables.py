"""
Script para crear tablas de modo práctica
"""
import sys
sys.path.append('.')

from app.infrastructure.database.session import engine
from app.infrastructure.database import models

# Crear todas las tablas
print("🔧 Creando tablas de base de datos...")
models.Base.metadata.create_all(bind=engine)
print("✅ Tablas creadas exitosamente")
print("   - virtual_wallets")
print("   - virtual_trades")
print("   - signals")
print("   - alerts")
print("   - transactions")
