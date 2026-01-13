"""
SIC Ultra - API V1 Router

Agrupa todos los endpoints de la API v1.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.wallet import router as wallet_router
from app.api.v1.trading import router as trading_router
from app.api.v1.practice import router as practice_router
from app.api.v1.p2p import router as p2p_router
from app.api.v1.signals import router as signals_router
from app.api.v1.ml import router as ml_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.onchain import router as onchain_router

router = APIRouter()

# Montar sub-routers
router.include_router(auth_router, prefix="/auth", tags=["🔐 Auth"])
router.include_router(wallet_router, prefix="/wallet", tags=["💰 Wallet"])
router.include_router(trading_router, prefix="/trading", tags=["📈 Trading"])
router.include_router(practice_router, prefix="/practice", tags=["🎮 Práctica"])
router.include_router(p2p_router, prefix="/p2p", tags=["💱 P2P VES"])
router.include_router(signals_router, prefix="/signals", tags=["🎯 Señales IA"])
router.include_router(ml_router, prefix="/ml", tags=["🧠 Machine Learning"])
router.include_router(knowledge_router, prefix="/knowledge", tags=["📚 Base Conocimientos"])
router.include_router(onchain_router, prefix="/onchain", tags=["🐋 On-Chain Analysis"])


