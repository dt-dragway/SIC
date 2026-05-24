#!/bin/bash
# Script para ejecutar tests con el ambiente correcto

echo "🧪 Ejecutando Test Suite de SIC Ultra"
echo "======================================"

# Setear variable de entorno para deshabilitar rate limiting
export TESTING=true

# Limpiar cache de Python
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Ejecutar tests con coverage
python3 -m pytest tests/ -v --cov=app --cov-report=term --cov-report=html

echo ""
echo "✅ Tests completados"
echo "📊 Reporte HTML en: backend/htmlcov/index.html"
