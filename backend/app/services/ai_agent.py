"""
SIC Ultra - Institutional AI Agent

Agente de IA que usa automáticamente todas las herramientas institucionales
para dar análisis completos sin intervención manual del usuario.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from loguru import logger

from app.config import settings


class InstitutionalAgent:
    """
    IA Autónoma que decide qué herramientas institucionales usar
    basándose en el contexto de la consulta del usuario.
    """
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.available_tools = {
            "microstructure": {
                "order_book": "/trading/depth/{symbol}",
                "funding_rate": "/trading/funding/{symbol}"
            },
            "onchain": {
                "whale_alerts": "/onchain/whale-feed",
                "whale_summary": "/onchain/whale-summary"
            },
            "derivatives": {
                "basis_opportunities": "/derivatives/basis-opportunities",
                "hedge_calculator": "/derivatives/hedge-calculator"
            },
            "defi": {
                "il_calculator": "/defi/il-calculator",
                "contract_audit": "/defi/contract-audit"
            },
            "automation": {
                "backtest": "/automation/backtest"
            },
            "risk": {
                "kelly_criterion": "/risk/kelly-criterion",
                "macro_correlation": "/risk/macro-correlation"
            }
        }
    
    def _select_tools(self, user_query: str) -> List[str]:
        """
        Selección inteligente de herramientas basada en la consulta.
        """
        query_lower = user_query.lower()
        tools_to_use = []
        
        # Keywords para cada categoría
        keywords = {
            "microstructure": ["spread", "order book", "libro de ordenes", "profundidad", "funding"],
            "onchain": ["ballena", "whale", "transferencia", "blockchain", "on-chain"],
            "derivatives": ["delta", "neutral", "basis", "hedge", "cobertura", "sin riesgo"],
            "defi": ["impermanent", "pérdida", "liquidity", "liquidez", "pool", "contrato"],
            "automation": ["backtest", "estrategia", "prueba", "simular", "histórico"],
            "risk": ["kelly", "riesgo", "risk", "cuánto invertir", "position size", "correlación"]
        }
        
        # Detectar herramientas necesarias
        for category, words in keywords.items():
            if any(word in query_lower for word in words):
                tools_to_use.append(category)
        
        # Análisis general siempre incluye microstructure + risk
        if "analiz" in query_lower or "compr" in query_lower or "vend" in query_lower:
            if "microstructure" not in tools_to_use:
                tools_to_use.append("microstructure")
            if "risk" not in tools_to_use:
                tools_to_use.append("risk")
            if "onchain" not in tools_to_use:
                tools_to_use.append("onchain")
        
        return tools_to_use
    
    async def _call_tool(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None, token: str = None) -> Dict:
        """Llamada HTTP a herramienta"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        async with httpx.AsyncClient() as client:
            try:
                if method == "GET":
                    response = await client.get(url, headers=headers, timeout=10.0)
                else:
                    response = await client.post(url, json=data, headers=headers, timeout=10.0)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Tool call failed: {endpoint} - {response.status_code}")
                    return {}
            except Exception as e:
                logger.error(f"Error calling tool {endpoint}: {e}")
                return {}
    
    async def analyze_comprehensive(
        self,
        symbol: str,
        user_query: str,
        token: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Análisis comprehensivo usando múltiples herramientas.
        
        Args:
            symbol: Par de trading (ej: BTCUSDT)
            user_query: Pregunta del usuario
            token: JWT token
            context: Contexto adicional (balance, posiciones, etc)
        
        Returns:
            Dict con análisis completo y recomendación
        """
        tools_selected = self._select_tools(user_query)
        logger.info(f"🤖 Agent using tools: {tools_selected}")
        
        results = {
            "symbol": symbol,
            "query": user_query,
            "tools_used": tools_selected,
            "data": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Ejecutar herramientas seleccionadas
        if "microstructure" in tools_selected:
            order_book = await self._call_tool(f"/trading/depth/{symbol}", token=token)
            funding = await self._call_tool(f"/trading/funding/{symbol}", token=token)
            results["data"]["microstructure"] = {
                "order_book": order_book,
                "funding_rate": funding
            }
        
        if "onchain" in tools_selected:
            blockchain = symbol.replace("USDT", "").replace("BUSD", "")
            whales = await self._call_tool(f"/onchain/whale-feed?blockchain={blockchain}&limit=10", token=token)
            whale_summary = await self._call_tool(f"/onchain/whale-summary?blockchain={blockchain}", token=token)
            results["data"]["onchain"] = {
                "whale_alerts": whales,
                "summary": whale_summary
            }
        
        if "derivatives" in tools_selected:
            basis_opps = await self._call_tool("/derivatives/basis-opportunities", token=token)
            results["data"]["derivatives"] = {
                "basis_opportunities": basis_opps
            }
        
        if "risk" in tools_selected:
            # Asumimos win rate 60%, avg win 150, avg loss 100 como defaults
            # En producción, estos vendrían del historial real del usuario
            kelly_data = {
                "win_rate": context.get("win_rate", 60) if context else 60,
                "avg_win": context.get("avg_win", 150) if context else 150,
                "avg_loss": context.get("avg_loss", 100) if context else 100
            }
            kelly = await self._call_tool("/risk/kelly-criterion", method="POST", data=kelly_data, token=token)
            correlation = await self._call_tool("/risk/macro-correlation", token=token)
            results["data"]["risk"] = {
                "kelly_criterion": kelly,
                "macro_correlation": correlation
            }
        
        # Generar recomendación basada en resultados
        recommendation = self._generate_recommendation(results)
        results["recommendation"] = recommendation
        
        return results
    
    def _generate_recommendation(self, analysis: Dict) -> Dict[str, Any]:
        """
        Genera recomendación inteligente basada en análisis multi-tool.
        """
        data = analysis.get("data", {})
        recommendation = {
            "action": "HOLD",  # BUY, SELL, HOLD
            "confidence": 50,
            "reasoning": [],
            "position_size": 0.0,
            "alerts": []
        }
        
        confidence_factors = []
        
        # Análisis de microestructura
        if "microstructure" in data:
            funding = data["microstructure"].get("funding_rate", {})
            if funding:
                fr = funding.get("fundingRate", 0)
                if fr > 0.0001:  # Funding positivo
                    confidence_factors.append(10)
                    recommendation["reasoning"].append(f"✅ Funding Rate positivo ({fr*100:.4f}%)")
                elif fr < -0.0001:
                    confidence_factors.append(-10)
                    recommendation["reasoning"].append(f"⚠️ Funding Rate negativo ({fr*100:.4f}%)")
        
        # Análisis on-chain
        if "onchain" in data:
            summary = data["onchain"].get("summary", {})
            if summary:
                net_flow = summary.get("net_flow_usd", 0)
                if net_flow > 0:  # Flujo neto hacia exchanges (bajista)
                    confidence_factors.append(-15)
                    recommendation["reasoning"].append(f"🐋 Ballenas enviando a exchanges (${net_flow:,.0f})")
                elif net_flow < 0:  # Flujo neto saliendo de exchanges (alcista)
                    confidence_factors.append(15)
                    recommendation["reasoning"].append(f"🐋 Ballenas retirando de exchanges (${abs(net_flow):,.0f})")
        
        # Análisis de derivatives
        if "derivatives" in data:
            opps = data["derivatives"].get("basis_opportunities", [])
            if opps:
                best_opp = max(opps, key=lambda x: x.get("apr_estimate", 0))
                if best_opp.get("recommended", False):
                    confidence_factors.append(20)
                    recommendation["reasoning"].append(
                        f"📊 Oportunidad Delta Neutral: APR {best_opp.get('apr_estimate', 0):.1f}%"
                    )
                    recommendation["alerts"].append({
                        "type": "DELTA_NEUTRAL",
                        "message": f"Considera Delta Neutral en {best_opp.get('symbol')}"
                    })
        
        # Análisis de riesgo (Kelly Criterion)
        if "risk" in data:
            kelly = data["risk"].get("kelly_criterion", {})
            if kelly:
                recommended_pos = kelly.get("recommended_position", 0)
                recommendation["position_size"] = recommended_pos
                recommendation["reasoning"].append(
                    f"⚖️ Kelly recomienda {recommended_pos:.1f}% del capital"
                )
        
        # Calcular confianza total
        total_confidence = 50 + sum(confidence_factors)
        recommendation["confidence"] = max(0, min(100, total_confidence))
        
        # Decisión final
        if recommendation["confidence"] >= 70:
            recommendation["action"] = "BUY"
        elif recommendation["confidence"] <= 30:
            recommendation["action"] = "SELL"
        else:
            recommendation["action"] = "HOLD"
        
        return recommendation


# Instancia global
institutional_agent = InstitutionalAgent()
