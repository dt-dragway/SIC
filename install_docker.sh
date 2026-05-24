#!/bin/bash

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🐳 Iniciando instalación de Docker para SIC Ultra...${NC}"

# 1. Actualizar repositorios
echo "Actualizando listas de paquetes..."
apt-get update

# 2. Instalar Docker
echo "Instalando Docker y Docker Compose..."
apt-get install -y docker.io docker-compose

# 3. Configurar permisos
echo "Configurando permisos de usuario..."
# Obtener el usuario real si se ejecuta con sudo
REAL_USER=${SUDO_USER:-$USER}
usermod -aG docker $REAL_USER

# 4. Iniciar servicio
echo "Iniciando servicio Docker..."
systemctl start docker
systemctl enable docker

echo -e "${GREEN}✅ Instalación completada.${NC}"
echo -e "${BLUE}⚠️  IMPORTANTE: Para que los cambios surtan efecto, debes cerrar sesión y volver a entrar, o ejecutar: ${NC}"
echo -e "    ${GREEN}newgrp docker${NC}"
