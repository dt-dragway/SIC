# SIC Ultra - Sistema Integral Criptofinanciero

Sistema de trading inteligente con IA para criptomonedas.

## Stack

- **Backend**: FastAPI + PostgreSQL + Redis
- **Frontend**: Next.js 14 + TradingView
- **ML**: PyTorch + XGBoost

## Requisitos

- Python 3.12+
- Node.js 20+
- Docker + Docker Compose
- PostgreSQL 16
- Redis 7

## Instalación

```bash
# Clonar y entrar al directorio
cd SIC

# Copiar variables de entorno
cp .env.example .env
# Editar .env con tus API keys de Binance

# Levantar con Docker
docker-compose up -d

# O desarrollo local
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

## Desarrollo

```bash
# Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

## Modos

- 🎮 **Práctica**: $100 virtuales, sin riesgo
- ⚔️ **Batalla Real**: Trading con tu wallet Binance

## Licencia

Privado - Uso personal
