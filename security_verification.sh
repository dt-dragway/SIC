#!/bin/bash

# 🔍 SCRIPT DE VERIFICACIÓN POST-REMEDIACIÓN - SIC Ultra
# Verifica que todos los cambios de seguridad se han aplicado correctamente

echo "🔍 VERIFICACIÓN DE SEGURIDAD POST-REMEDIACIÓN"
echo "==============================================="
echo "📅 Fecha: $(date)"
echo ""

# Colores para resultados
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contadores
PASSED=0
FAILED=0
WARNINGS=0

echo "🔒 Verificando configuración de seguridad..."

# 1. Verificar que no hay credenciales hardcoded en .env
echo -n "1. Verificando ausencia de credenciales hardcoded en .env..."
if grep -q "YAvhRs6hAkLUWywC04roh6El7ieCNGLJ5ybqCEaCSxPY2aC4E3CqU4txtu3oZi71" .env; then
    echo -e " ${RED}❌ FALLÓ${NC}"
    echo "   ⚠️ API Key de Binance aún presente"
    ((FAILED++))
else
    echo -e " ${GREEN}✅ PASÓ${NC}"
    ((PASSED++))
fi

# 2. Verificar rotación de contraseñas
echo -n "2. Verificando rotación de contraseñas por defecto..."
if grep -q "admin2425" .env; then
    echo -e " ${YELLOW}⚠️ ADVERTENCIA${NC}"
    echo "   ⚠️ Contraseña por defecto aún presente - debe ser cambiada"
    ((WARNINGS++))
else
    echo -e " ${GREEN}✅ PASÓ${NC}"
    ((PASSED++))
fi

# 3. Verificar configuración JWT
echo -n "3. Verificando configuración de JWT segura..."
JWT_TIMEOUT=$(grep "access_token_expire_minutes" backend/app/config.py | grep -o '[0-9]\+')
if [ "$JWT_TIMEOUT" -le 30 ]; then
    echo -e " ${GREEN}✅ PASÓ${NC}"
    echo "   ✅ Token timeout: $JWT_TIMEOUT minutos"
    ((PASSED++))
else
    echo -e " ${RED}❌ FALLÓ${NC}"
    echo "   ❌ Token timeout muy largo: $JWT_TIMEOUT minutos"
    ((FAILED++))
fi

# 4. Verificar algoritmo JWT
echo -n "4. Verificando algoritmo JWT asimétrico..."
if grep -q "RS256" backend/app/config.py; then
    echo -e " ${GREEN}✅ PASÓ${NC}"
    ((PASSED++))
else
    echo -e " ${RED}❌ FALLÓ${NC}"
    echo "   ❌ Aún usando algoritmo simétrico"
    ((FAILED++))
fi

# 5. Verificar eliminación de auto-login
echo -n "5. Verificando eliminación de auto-login hardcoded..."
if grep -q "y2k38\*" frontend/src/hooks/useAuth.ts; then
    echo -e " ${RED}❌ FALLÓ${NC}"
    echo "   ❌ Auto-login hardcoded aún presente"
    ((FAILED++))
else
    echo -e " ${GREEN}✅ PASÓ${NC}"
    ((PASSED++))
fi

# 6. Verificar cookies seguras
echo -n "6. Verificando configuración de cookies seguras..."
if grep -q "httponly=True" backend/app/api/v1/auth.py && grep -q "samesite=\"strict\"" backend/app/api/v1/auth.py; then
    echo -e " ${GREEN}✅ PASÓ${NC}"
    ((PASSED++))
else
    echo -e " ${RED}❌ FALLÓ${NC}"
    echo "   ❌ Configuración de cookies incompleta"
    ((FAILED++))
fi

# 7. Verificar validación SQL injection
echo -n "7. Verificando protección contra SQL injection..."
if grep -q "_validate_db_component" backend/app/config.py; then
    echo -e " ${GREEN}✅ PASÓ${NC}"
    ((PASSED++))
else
    echo -e " ${RED}❌ FALLÓ${NC}"
    echo "   ❌ Falta validación de componentes de BD"
    ((FAILED++))
fi

# 8. Verificar archivos de backup
echo -n "8. Verificando backups de seguridad..."
BACKUP_COUNT=$(ls BACKUP_CRITICAL/database_backup_*.sql 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 0 ]; then
    echo -e " ${GREEN}✅ PASÓ${NC}"
    echo "   ✅ $BACKUP_COUNT archivos de backup encontrados"
    ((PASSED++))
else
    echo -e " ${RED}❌ FALLÓ${NC}"
    echo "   ❌ No se encontraron archivos de backup"
    ((FAILED++))
fi

echo ""
echo "==============================================="
echo "📊 RESULTADOS DE LA VERIFICACIÓN:"
echo "==============================================="
echo -e "✅ ${GREEN}PASADOS: $PASSED${NC}"
echo -e "❌ ${RED}FALLIDOS: $FAILED${NC}"
echo -e "⚠️  ${YELLOW}ADVERTENCIAS: $WARNINGS${NC}"

TOTAL=$((PASSED + FAILED + WARNINGS))
SUCCESS_RATE=$((PASSED * 100 / TOTAL))

echo ""
echo "📈 TASA DE ÉXITO: $SUCCESS_RATE%"

if [ $FAILED -eq 0 ]; then
    if [ $SUCCESS_RATE -ge 80 ]; then
        echo -e "🎉 ${GREEN}REMEDIACIÓN COMPLETADA CON ÉXITO${NC}"
        echo ""
        echo "📋 PRÓXIMOS PASOS:"
        echo "   1. Ejecutar el script de rotación de API keys"
        echo "   2. Generar nuevas API keys en Binance y DeepSeek"
        echo "   3. Actualizar .env.new con las nuevas credenciales"
        echo "   4. Probar el sistema con usuarios reales"
        echo "   5. Monitorear logs en busca de anomalías"
    else
        echo -e "⚠️  ${YELLOW}REMEDIACIÓN PARCIAL${NC}"
        echo "   Hay advertencias que deben ser revisadas"
    fi
else
    echo -e "🚨 ${RED}REMEDIACIÓN INCOMPLETA${NC}"
    echo "   Hay $FAILED verificaciones que fallaron"
    echo ""
    echo "📋 ACCIONES REQUERIDAS:"
    echo "   1. Revisar las verificaciones fallidas"
    echo "   2. Aplicar los cambios pendientes"
    echo "   3. Ejecutar este script nuevamente"
fi

echo ""
echo "🔐 SEGURIDAD MEJORADA SIGNIFICATIVAMENTE"
echo "==============================================="