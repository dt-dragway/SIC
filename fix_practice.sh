#!/bin/bash
# Script para arreglar Practice Wallet

echo "🔧 Arreglando Practice Wallet..."

# 1. Matar backend actual
echo "1. Deteniendo backend..."
pkill -f uvicorn
sleep 2

# 2. Resetear virtual wallets en DB
echo "2. Reseteando virtual wallets..."
cd backend
python3 << 'EOF'
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import VirtualWalletModel

db = SessionLocal()
try:
    # Borrar wallets existentes
    db.query(VirtualWalletModel).delete()
    db.commit()
    print("✅ Virtual wallets reseteadas")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
EOF

# 3. Iniciar backend en foreground para ver errores
echo "3. Iniciando backend..."
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
