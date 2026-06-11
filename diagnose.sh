#!/bin/bash
# Script de diagnóstico rápido

echo "🔍 Diagnóstico de Wallet y Practice Mode"
echo "========================================"

# 1. Ver variables de entorno de Binance (sin mostrar claves completas)
echo ""
echo "1. Configuración Binance:"
if [ -f .env ]; then
    echo "   BINANCE_API_KEY: $(grep BINANCE_API_KEY .env | cut -d'=' -f2 | cut -c1-10)..."
    echo "   BINANCE_TESTNET: $(grep BINANCE_TESTNET .env | cut -d'=' -f2)"
else
    echo "   ⚠️  Archivo .env no encontrado"
fi

# 2. Test del endpoint de wallet
echo ""
echo "2. Test endpoint /wallet:"
curl -s http://localhost:8000/api/v1/wallet -H "Authorization: Bearer test" | head -100

# 3. Test del endpoint de practice
echo ""
echo "3. Test endpoint /practice/wallet:"
curl -s http://localhost:8000/api/v1/practice/wallet -H "Authorization: Bearer test" | head -100

# 4. Ver logs recientes del backend
echo ""
echo "4. Logs recientes backend:"
ps aux | grep uvicorn | grep -v grep | head -2
