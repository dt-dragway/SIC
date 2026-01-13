"""
Tests para Institutional AI Agent

Verifica que la IA selecciona y usa las herramientas correctamente.
"""

import pytest
from app.services.ai_agent import InstitutionalAgent


class TestToolSelection:
    """Tests de selección inteligente de herramientas"""
    
    def setup_method(self):
        self.agent = InstitutionalAgent()
    
    def test_select_tools_for_buy_query(self):
        """Cuando usuario pregunta si comprar, debe usar microstructure + risk + onchain"""
        query = "¿Debería comprar BTC ahora?"
        tools = self.agent._select_tools(query)
        
        assert "microstructure" in tools
        assert "risk" in tools
        assert "onchain" in tools
    
    def test_select_tools_for_delta_neutral(self):
        """Para Delta Neutral debe usar derivatives + risk"""
        query = "¿Cómo puedo ganar sin riesgo de precio?"
        tools = self.agent._select_tools(query)
        
        assert "derivatives" in tools
        assert "risk" in tools
    
    def test_select_tools_for_il_question(self):
        """Para IL debe usar defi"""
        query = "¿Cómo evito impermanent loss en Uniswap?"
        tools = self.agent._select_tools(query)
        
        assert "defi" in tools
    
    def test_select_tools_for_whale_alerts(self):
        """Para ballenas debe usar onchain"""
        query = "¿Hay movimientos de ballenas en BTC?"
        tools = self.agent._select_tools(query)
        
        assert "onchain" in tools
    
    def test_select_tools_for_backtest(self):
        """Para backtesting debe usar automation"""
        query = "Quiero probar mi estrategia con datos históricos"
        tools = self.agent._select_tools(query)
        
        assert "automation" in tools


class TestRecommendation:
    """Tests de generación de recomendaciones"""
    
    def setup_method(self):
        self.agent = InstitutionalAgent()
    
    def test_recommendation_with_positive_funding(self):
        """Funding positivo aumenta confianza"""
        analysis = {
            "data": {
                "microstructure": {
                    "funding_rate": {"fundingRate": 0.0005}  # Positivo
                }
            }
        }
        
        rec = self.agent._generate_recommendation(analysis)
        assert rec["confidence"] > 50
        assert "Funding Rate positivo" in str(rec["reasoning"])
    
    def test_recommendation_with_whale_outflow(self):
        """Ballenas retirando de exchanges es alcista"""
        analysis = {
            "data": {
                "onchain": {
                    "summary": {"net_flow_usd": -1000000}  # Negativo = saliendo
                }
            }
        }
        
        rec = self.agent._generate_recommendation(analysis)
        assert rec["confidence"] > 50
        assert "retirando" in str(rec["reasoning"])
    
    def test_recommendation_calculates_position_size(self):
        """Kelly Criterion define position size"""
        analysis = {
            "data": {
                "risk": {
                    "kelly_criterion": {"recommended_position": 12.5}
                }
            }
        }
        
        rec = self.agent._generate_recommendation(analysis)
        assert rec["position_size"] == 12.5


@pytest.mark.asyncio
class TestIntegration:
    """Tests de integración end-to-end (requieren backend running)"""
    
    @pytest.mark.skip(reason="Requires running backend")
    async def test_full_analysis(self):
        """Test completo de análisis"""
        agent = InstitutionalAgent()
        
        # Mock token (en test real usarías uno válido)
        token = "mock_token"
        
        result = await agent.analyze_comprehensive(
            symbol="BTCUSDT",
            user_query="Análisis completo de BTC",
            token=token
        )
        
        assert "tools_used" in result
        assert "recommendation" in result
        assert result["recommendation"]["action"] in ["BUY", "SELL", "HOLD"]
        assert 0 <= result["recommendation"]["confidence"] <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
