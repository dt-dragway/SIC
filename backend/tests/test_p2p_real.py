import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.api.v1.p2p import analyze_p2p_offers
from app.ml.p2p_analyzer import P2POpportunityFinder
from app.api.v1.p2p import P2POffer

@pytest.mark.asyncio
async def test_analyze_p2p_offers_real_flow():
    # 1. Setup Mock Offers
    mock_offers = [
        P2POffer(
            advertiser="TrustedTrader",
            price=37.5,
            available=1000,
            min_amount=10,
            max_amount=1000,
            payment_methods=["Banesco"],
            completion_rate=99.9,
            orders_count=500
        ),
        P2POffer(
            advertiser="Newbie",
            price=37.0,
            available=100,
            min_amount=10,
            max_amount=50,
            payment_methods=["PagoMovil"],
            completion_rate=85.0,
            orders_count=10
        )
    ]

    # 2. Mock Opportunity Finder and LLM and Auth
    with patch("app.api.v1.p2p.get_opportunity_finder") as mock_get_finder, \
         patch("app.api.v1.p2p.verify_token") as mock_verify:
        
        mock_finder_instance = AsyncMock(spec=P2POpportunityFinder)
        # LLM should return a "smart" string
        mock_finder_instance.analyze_offer_context.return_value = "🤖 IA: Opción más segura por volumen y reputación."
        mock_get_finder.return_value = mock_finder_instance

        # 3. Call endpoint
        result = await analyze_p2p_offers(mock_offers, token="mock_token")

        # 4. Verify AI Selection Logic (should pick TrustedTrader due to high completion/orders)
        assert result["best_offer"]["advertiser"] == "TrustedTrader"
        
        # 5. Verify LLM usage
        mock_finder_instance.analyze_offer_context.assert_called_once()
        assert "IA:" in result["reason"]
        assert len(result["risky_advertisers"]) == 0 # Newbie is > 80% completion, so maybe not risky?
                                                     # Actually Newbie has 10 orders, checks > 5. OK.

@pytest.mark.asyncio
async def test_analyze_p2p_offers_risky_filter():
    mock_offers = [
        P2POffer(
            advertiser="Scammy",
            price=30.0,
            available=1000,
            min_amount=10,
            max_amount=1000,
            payment_methods=["Banesco"],
            completion_rate=50.0, # Very low
            orders_count=100
        )
    ]

    with patch("app.api.v1.p2p.get_opportunity_finder") as mock_get_finder, \
         patch("app.api.v1.p2p.verify_token") as mock_verify:
        
        mock_finder_instance = AsyncMock(spec=P2POpportunityFinder)
        mock_finder_instance.analyze_offer_context.return_value = "Analisis..."
        mock_get_finder.return_value = mock_finder_instance

        result = await analyze_p2p_offers(mock_offers, token="mock_token")

        # Verify it was flagged
        assert "Scammy" in result["risky_advertisers"]
