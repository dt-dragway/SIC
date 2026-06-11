"""
Tests para módulos institucionales (Derivatives, DeFi, Risk)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestDerivatives:
    """Tests de Derivatives module"""
    
    def test_basis_opportunities(self):
        """API retorna oportunidades de basis trading"""
        # Necesita autenticación
        response = client.get("/api/v1/derivatives/basis-opportunities")
        # Sin token debe fallar
        assert response.status_code == 401
    
    def test_hedge_calculator(self):
        """Hedge calculator calcula correctamente"""
        request_data = {
            "spot_holdings": {"BTCUSDT": 1.0},
            "futures_positions": []
        }
        
        response = client.post(
            "/api/v1/derivatives/hedge-calculator",
            json=request_data
        )
        
        # Sin token debe fallar
        assert response.status_code == 401


class TestDeFi:
    """Tests de DeFi module"""
    
    def test_il_calculator(self):
        """IL calculator usa fórmula correcta"""
        # Caso conocido: precio 2x = ~5.7% IL
        request_data = {
            "initial_token_a": 1.0,
            "initial_token_b": 100.0,
            "initial_price_ratio": 100.0,
            "final_price_ratio": 200.0  # 2x
        }
        
        response = client.post(
            "/api/v1/defi/il-calculator",
            json=request_data
        )
        
        # Sin auth debe fallar
        assert response.status_code == 401


class TestRisk:
    """Tests de Risk Management"""
    
    def test_kelly_criterion(self):
        """Kelly criterion calcula position size correcto"""
        request_data = {
            "win_rate": 60.0,  # 60%
            "avg_win": 150.0,
            "avg_loss": 100.0
        }
        
        response = client.post(
            "/api/v1/risk/kelly-criterion",
            json=request_data
        )
        
        assert response.status_code == 401  # Sin auth
    
    def test_macro_correlation(self):
        """API retorna correlaciones macro"""
        response = client.get("/api/v1/risk/macro-correlation")
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
