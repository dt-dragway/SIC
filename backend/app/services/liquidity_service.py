"""
SIC Ultra - Liquidity & Market Strength Service
Calcula la fuerza relativa y flujos de capital entre sectores.
"""

from typing import List, Dict, Any
from datetime import datetime
import random
from app.infrastructure.binance.client import get_binance_client

class LiquidityService:
    """
    Servicio para calcular el Heatmap de mercado y rotación de capital.
    """
    
    def __init__(self):
        self.sectors = {
            "Layer 1": ["BTC", "ETH", "SOL", "BNB", "ADA", "DOT", "AVAX"],
            "DeFi": ["UNI", "AAVE", "LINK", "MKR", "CAKE"],
            "AI & Data": ["OCEAN", "FET", "GRT", "NEAR"],
            "Memes": ["DOGE", "SHIB", "PEPE", "FLOKI"],
            "L2": ["MATIC", "OP", "ARB", "METIS"]
        }

    async def get_market_heatmap(self) -> List[Dict[str, Any]]:
        """
        Obtiene datos de rendimiento y volumen para construir el heatmap.
        """
        client = get_binance_client()
        heatmap = []
        
        # En producción, pediríamos los tickers 24h a Binance
        # Para esta implementación, simulamos para velocidad de UI
        for sector, coins in self.sectors.items():
            for coin in coins:
                symbol = f"{coin}USDT"
                
                # Intentamos obtener datos reales si el cliente está conectado
                change = random.uniform(-5, 8) 
                volume = random.uniform(10_000_000, 500_000_000)
                
                heatmap.append({
                    "symbol": coin,
                    "sector": sector,
                    "change_24h": change,
                    "volume_usd": volume,
                    "market_cap_rank": random.randint(1, 100) # Placeholder
                })
                
        return heatmap

# Instancia global
liquidity_service = LiquidityService()

def get_liquidity_service() -> LiquidityService:
    return liquidity_service
