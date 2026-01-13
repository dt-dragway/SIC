"""
Conftest - Fixtures compartidos para todos los tests
"""

import pytest
import os
from fastapi.testclient import TestClient

# Deshabilitar rate limiting en tests
os.environ["TESTING"] = "true"

from app.main import app


@pytest.fixture
def client():
    """Test client para FastAPI"""
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """Token de autenticación válido"""
    # Registrar usuario de prueba
    unique_email = f"testuser_{os.urandom(4).hex()}@example.com"
    client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": "TestPass123!",
        "name": "Test User"
    })
    
    # Login
    response = client.post("/api/v1/auth/login", data={
        "username": unique_email,
        "password": "TestPass123!"
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        pytest.fail(f"Failed to get auth token: {response.status_code} - {response.text}")


@pytest.fixture
def auth_headers(auth_token):
    """Headers con autenticación"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="session")
def test_symbol():
    """Símbolo de prueba"""
    return "BTCUSDT"
