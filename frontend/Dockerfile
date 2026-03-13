FROM node:20-alpine

WORKDIR /app

# Archivos de dependencia primero para aprovechar caché
COPY package.json package-lock.json* ./
RUN npm install

# Copiar el resto del código
COPY . .

# Comando por defecto para desarrollo
CMD ["npm", "run", "dev"]
