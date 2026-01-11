"""
SIC Ultra - Analizador P2P Inteligente

Sistema de IA para encontrar OPORTUNIDADES DE ORO en el mercado P2P:
1. Analiza spreads y detecta arbitraje
2. Estudia patrones de traders exitosos
3. Predice mejores momentos para operar
4. Minimiza riesgos y maximiza ganancias

Este módulo trabaja con:
- Ollama + Base de conocimientos
- Datos reales de Binance P2P
- Sistema de scoring de oportunidades
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from loguru import logger
import statistics

from app.infrastructure.binance.p2p import BinanceP2PClient


class OpportunityType(str, Enum):
    ARBITRAGE = "ARBITRAGE"      # Comprar bajo, vender alto
    TIMING = "TIMING"            # Mejor momento del día
    VOLUME = "VOLUME"            # Alto volumen = mejores tasas
    TRADER = "TRADER"            # Copiar trader exitoso


@dataclass
class GoldenOpportunity:
    """Oportunidad de oro detectada"""
    type: OpportunityType
    score: float  # 0-100 (mayor = mejor)
    action: str   # BUY o SELL
    
    # Detalles
    current_price: float
    target_price: float
    potential_profit_percent: float
    
    # Riesgo
    risk_level: str  # LOW, MEDIUM, HIGH
    risk_factors: List[str]
    
    # Timing
    valid_until: datetime
    best_time: Optional[str]
    
    # Razonamiento
    reasoning: List[str]


class P2PTraderStudy:
    """
    Estudia patrones de traders P2P exitosos.
    
    Analiza:
    - Horarios de operación
    - Precios ofrecidos
    - Métodos de pago preferidos
    - Tasas de completación
    """
    
    def __init__(self):
        self.top_traders_data = {}
        self.patterns = {}
    
    def analyze_trader(self, trader_data: Dict) -> Dict:
        """Analizar un trader específico"""
        nickname = trader_data.get("advertiserNo", "unknown")
        
        analysis = {
            "nickname": nickname,
            "completion_rate": trader_data.get("monthFinishRate", 0) * 100,
            "order_count": trader_data.get("monthOrderCount", 0),
            "is_merchant": trader_data.get("userType") == "merchant",
            "trust_score": 0
        }
        
        # Calcular trust score
        completion = analysis["completion_rate"]
        orders = analysis["order_count"]
        
        trust = 0
        if completion >= 98:
            trust += 40
        elif completion >= 95:
            trust += 30
        elif completion >= 90:
            trust += 20
        
        if orders >= 1000:
            trust += 40
        elif orders >= 500:
            trust += 30
        elif orders >= 100:
            trust += 20
        elif orders >= 50:
            trust += 10
        
        if analysis["is_merchant"]:
            trust += 20
        
        analysis["trust_score"] = min(trust, 100)
        
        return analysis
    
    def get_best_traders(self, offers: List[Dict], min_trust: int = 70) -> List[Dict]:
        """Obtener los mejores traders de una lista de ofertas"""
        traders = []
        
        for offer in offers:
            advertiser = offer.get("advertiser", {})
            analysis = self.analyze_trader(advertiser)
            
            if analysis["trust_score"] >= min_trust:
                traders.append({
                    **analysis,
                    "price": float(offer.get("adv", {}).get("price", 0)),
                    "available": float(offer.get("adv", {}).get("tradableQuantity", 0))
                })
        
        return sorted(traders, key=lambda x: x["trust_score"], reverse=True)


class P2POpportunityFinder:
    """
    Buscador de oportunidades de oro en P2P.
    
    Estrategias:
    1. ARBITRAGE: Detectar spread > 2% entre compra/venta
    2. TIMING: Identificar mejores horarios (menos competencia)
    3. VOLUME: Encontrar ofertas con mejor tasa por volumen
    4. TRADER: Copiar estrategias de traders top
    """
    
    def __init__(self):
        self.p2p_client = BinanceP2PClient()
        self.trader_study = P2PTraderStudy()
        self.historical_spreads = []
    
    async def find_opportunities(
        self,
        amount_usdt: float = 100,
        min_score: int = 60
    ) -> List[GoldenOpportunity]:
        """
        Buscar todas las oportunidades de oro disponibles.
        """
        opportunities = []
        
        # Obtener datos del mercado
        buy_offers = await self.p2p_client.get_offers("BUY", "USDT", "VES", rows=20)
        sell_offers = await self.p2p_client.get_offers("SELL", "USDT", "VES", rows=20)
        
        if not buy_offers or not sell_offers:
            return []
        
        # 1. Buscar arbitraje
        arb = await self._find_arbitrage(buy_offers, sell_offers, amount_usdt)
        if arb and arb.score >= min_score:
            opportunities.append(arb)
        
        # 2. Buscar mejor timing
        timing = self._analyze_timing()
        if timing and timing.score >= min_score:
            opportunities.append(timing)
        
        # 3. Analizar mejores traders para copiar
        trader_opps = self._find_trader_opportunities(buy_offers, sell_offers)
        for opp in trader_opps:
            if opp.score >= min_score:
                opportunities.append(opp)
        
        # Ordenar por score
        opportunities.sort(key=lambda x: x.score, reverse=True)
        
        return opportunities
    
    async def _find_arbitrage(
        self,
        buy_offers: List,
        sell_offers: List,
        amount: float
    ) -> Optional[GoldenOpportunity]:
        """Detectar oportunidad de arbitraje"""
        
        if not buy_offers or not sell_offers:
            return None
        
        # Mejor precio de compra (el más bajo)
        best_buy = min(
            [float(o.get("adv", {}).get("price", 999999)) for o in buy_offers]
        )
        
        # Mejor precio de venta (el más alto)
        best_sell = max(
            [float(o.get("adv", {}).get("price", 0)) for o in sell_offers]
        )
        
        # Calcular spread
        spread_percent = ((best_sell - best_buy) / best_buy) * 100
        
        # Guardar histórico
        self.historical_spreads.append({
            "timestamp": datetime.utcnow(),
            "spread": spread_percent
        })
        
        # Mantener solo últimas 24 horas
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.historical_spreads = [
            s for s in self.historical_spreads 
            if s["timestamp"] > cutoff
        ]
        
        # Calcular score basado en spread
        if spread_percent < 0.5:
            return None  # No hay oportunidad
        
        # Score más alto para spreads grandes
        if spread_percent >= 3:
            score = 95
        elif spread_percent >= 2:
            score = 85
        elif spread_percent >= 1.5:
            score = 75
        elif spread_percent >= 1:
            score = 65
        else:
            score = 50
        
        # Calcular ganancia potencial
        potential_profit = amount * (spread_percent / 100)
        
        # Evaluar riesgo
        risk_factors = []
        risk_level = "LOW"
        
        if spread_percent > 5:
            risk_factors.append("Spread muy alto - posible manipulación")
            risk_level = "MEDIUM"
        
        if amount > 1000:
            risk_factors.append("Monto alto - mayor exposición")
            risk_level = "MEDIUM"
        
        return GoldenOpportunity(
            type=OpportunityType.ARBITRAGE,
            score=score,
            action="BUY_THEN_SELL",
            current_price=best_buy,
            target_price=best_sell,
            potential_profit_percent=round(spread_percent, 2),
            risk_level=risk_level,
            risk_factors=risk_factors if risk_factors else ["Operación estándar"],
            valid_until=datetime.utcnow() + timedelta(minutes=15),
            best_time=None,
            reasoning=[
                f"🔥 Spread actual: {spread_percent:.2f}%",
                f"💰 Comprar a: {best_buy:,.2f} VES/USDT",
                f"💵 Vender a: {best_sell:,.2f} VES/USDT",
                f"📈 Ganancia potencial: ${potential_profit:.2f} ({spread_percent:.2f}%)",
                "⚡ Ejecutar rápido antes de que cambie el spread"
            ]
        )
    
    def _analyze_timing(self) -> Optional[GoldenOpportunity]:
        """Analizar mejores horarios para operar"""
        
        now = datetime.utcnow()
        hour = now.hour
        
        # Horarios con menos competencia (basado en patrones típicos)
        best_hours = {
            # Madrugada (menos traders)
            (2, 6): {"score": 85, "reason": "Madrugada: menos competencia, mejores spreads"},
            # Mediodía (almuerzo)
            (12, 14): {"score": 70, "reason": "Hora de almuerzo: actividad reducida"},
            # Tarde-noche (alta actividad)
            (18, 22): {"score": 50, "reason": "Horario pico: mucha competencia"},
        }
        
        for (start, end), data in best_hours.items():
            if start <= hour < end:
                return GoldenOpportunity(
                    type=OpportunityType.TIMING,
                    score=data["score"],
                    action="WAIT" if data["score"] < 60 else "OPERATE",
                    current_price=0,
                    target_price=0,
                    potential_profit_percent=0,
                    risk_level="LOW",
                    risk_factors=[],
                    valid_until=datetime.utcnow() + timedelta(hours=1),
                    best_time="02:00-06:00 UTC" if data["score"] < 60 else "Ahora",
                    reasoning=[
                        f"⏰ Horario actual: {hour}:00 UTC",
                        f"📊 {data['reason']}",
                        "💡 Los mejores spreads suelen aparecer en madrugada"
                    ]
                )
        
        return None
    
    def _find_trader_opportunities(
        self,
        buy_offers: List,
        sell_offers: List
    ) -> List[GoldenOpportunity]:
        """Encontrar oportunidades basadas en traders top"""
        
        opportunities = []
        
        # Analizar mejores traders de compra
        best_buyers = self.trader_study.get_best_traders(buy_offers, min_trust=80)
        
        if best_buyers:
            top = best_buyers[0]
            opportunities.append(GoldenOpportunity(
                type=OpportunityType.TRADER,
                score=top["trust_score"],
                action="BUY",
                current_price=top["price"],
                target_price=top["price"],
                potential_profit_percent=0,
                risk_level="LOW",
                risk_factors=["Trader verificado con alta reputación"],
                valid_until=datetime.utcnow() + timedelta(hours=1),
                best_time=None,
                reasoning=[
                    f"👤 Trader top: {top['nickname'][:10]}...",
                    f"✅ Tasa completación: {top['completion_rate']:.1f}%",
                    f"📦 Órdenes completadas: {top['order_count']}",
                    f"💰 Precio: {top['price']:,.2f} VES/USDT",
                    "🛡️ Bajo riesgo: trader con excelente historial"
                ]
            ))
        
        return opportunities
    
    def get_market_summary(
        self,
        buy_offers: List,
        sell_offers: List
    ) -> Dict:
        """Resumen del mercado P2P actual"""
        
        if not buy_offers or not sell_offers:
            return {"error": "No hay datos disponibles"}
        
        buy_prices = [float(o.get("adv", {}).get("price", 0)) for o in buy_offers]
        sell_prices = [float(o.get("adv", {}).get("price", 0)) for o in sell_offers]
        
        best_buy = min(buy_prices)
        worst_buy = max(buy_prices)
        best_sell = max(sell_prices)
        worst_sell = min(sell_prices)
        
        spread = ((best_sell - best_buy) / best_buy) * 100
        
        return {
            "buy": {
                "best": best_buy,
                "worst": worst_buy,
                "avg": statistics.mean(buy_prices),
                "offers": len(buy_offers)
            },
            "sell": {
                "best": best_sell,
                "worst": worst_sell,
                "avg": statistics.mean(sell_prices),
                "offers": len(sell_offers)
            },
            "spread": {
                "percent": round(spread, 2),
                "absolute": round(best_sell - best_buy, 2),
                "is_opportunity": spread >= 1.5
            },
            "recommendation": "BUY_NOW" if spread >= 2 else "WAIT" if spread < 1 else "MONITOR",
            "timestamp": datetime.utcnow()
        }


# === Singleton ===

_opportunity_finder: Optional[P2POpportunityFinder] = None


def get_opportunity_finder() -> P2POpportunityFinder:
    global _opportunity_finder
    if _opportunity_finder is None:
        _opportunity_finder = P2POpportunityFinder()
    return _opportunity_finder
