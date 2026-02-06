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
# from app.api.v1.ml import router as ml_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.onchain import router as onchain_router
from app.api.v1.derivatives import router as derivatives_router
from app.api.v1.defi import router as defi_router
from app.api.v1.automation import router as automation_router
from app.api.v1.risk import router as risk_router
from app.api.v1.ai_analysis import router as ai_analysis_router
from app.api.v1.neural import router as neural_router
from app.api.v1.market import router as market_router  # NUEVO
from app.api.v1.advanced_trading import router as advanced_trading_router  # NUEVO
from app.api.v1.sentiment import router as sentiment_router  # NUEVO
from app.api.v1.advanced_execution import router as advanced_execution_router  # NUEVO
from app.api.v1.liquidity import router as liquidity_router  # NUEVO

router = APIRouter()

# Montar sub-routers
router.include_router(auth_router, prefix="/auth", tags=["🔐 Auth"])
router.include_router(wallet_router, prefix="/wallet", tags=["💰 Wallet"])
router.include_router(trading_router, prefix="/trading", tags=["📈 Trading"])
router.include_router(advanced_trading_router, prefix="/trading", tags=["📈 Trading Avanzado"])  # NUEVO
router.include_router(practice_router, prefix="/practice", tags=["🎮 Práctica"])
router.include_router(p2p_router, prefix="/p2p", tags=["💱 P2P VES"])
router.include_router(signals_router, prefix="/signals", tags=["🎯 Señales IA"])
# router.include_router(ml_router, prefix="/ml", tags=["🧠 Machine Learning"])
router.include_router(knowledge_router, prefix="/knowledge", tags=["📚 Base Conocimientos"])
router.include_router(onchain_router, prefix="/onchain", tags=["🐋 On-Chain Analysis"])
router.include_router(derivatives_router, prefix="/derivatives", tags=["📊 Derivatives & Delta Neutral"])
router.include_router(defi_router, prefix="/defi", tags=["🔷 DeFi Advanced"])
router.include_router(automation_router, prefix="/automation", tags=["🤖 Automation & Backtesting"])
router.include_router(risk_router, prefix="/risk", tags=["⚖️ Risk Management"])
router.include_router(ai_analysis_router, prefix="/ai", tags=["🧠 AI Institutional Agent"])
router.include_router(neural_router, prefix="/neural", tags=["🕯️ Neural Engine - Señales Inteligentes"])
router.include_router(market_router, prefix="/market", tags=["📊 Market Data & Order Flow"])  # NUEVO
router.include_router(sentiment_router, prefix="/sentiment", tags=["📰 AI Sentiment Hub"])  # NUEVO
router.include_router(advanced_execution_router, prefix="/execution", tags=["⚡ Smart Execution (TWAP/VWAP)"])  # NUEVO
router.include_router(liquidity_router, prefix="/liquidity", tags=["🗺️ Liquidity & Heatmap"])  # NUEVO


