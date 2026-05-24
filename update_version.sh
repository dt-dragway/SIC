#!/bin/bash

# update_version.sh
# Uso: ./update_version.sh 1.2.3

NEW_VERSION=$1

if [ -z "$NEW_VERSION" ]; then
    echo "❌ Error: Debes especificar la nueva versión."
    echo "Uso: ./update_version.sh <nueva_version>"
    exit 1
fi

echo "🔄 Actualizando proyecto a versión: $NEW_VERSION"

# 1. Actualizar Backend (.env)
if [ -f "backend/.env" ]; then
    # Si existe APP_VERSION, reemplazarlo
    if grep -q "APP_VERSION=" "backend/.env"; then
        sed -i "s/APP_VERSION=\".*\"/APP_VERSION=\"$NEW_VERSION\"/" "backend/.env"
    else
        # Si no existe, agregarlo al final
        echo "APP_VERSION=\"$NEW_VERSION\"" >> "backend/.env"
    fi
    echo "✅ Backend (.env) actualizado."
else
    echo "⚠️ Warning: backend/.env no encontrado."
fi

# 2. Actualizar Frontend (package.json)
if [ -f "frontend/package.json" ]; then
    # Usar una herramienta temporal o sed simple para actualizar json
    # Para asegurar compatibilidad, usaremos sed buscando "version": "..."
    sed -i "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" "frontend/package.json"
    echo "✅ Frontend (package.json) actualizado."
else
    echo "⚠️ Warning: frontend/package.json no encontrado."
fi

echo "🚀 Versión actualizada exitosamente a $NEW_VERSION"
