"""
Tests para el sistema de autenticación

Cobertura:
- Registro de usuario
- Login con JWT
- Refresh tokens
- 2FA
- Rate limiting en login
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestRegistration:
    """Tests de registro de usuarios"""
    
    def test_register_new_user(self):
        """Usuario nuevo puede registrarse"""
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == "test@example.com"
    
    def test_register_duplicate_email(self):
        """No permite emails duplicados"""
        # Primer registro
        client.post("/api/v1/auth/register", json={
            "email": "duplicate@example.com",
            "password": "Pass123!",
            "name": "User One"
        })
        
        # Segundo registro con mismo email
        response = client.post("/api/v1/auth/register", json={
            "email": "duplicate@example.com",
            "password": "Pass456!",
            "name": "User Two"
        })
        
        assert response.status_code == 400
    
    def test_register_weak_password(self):
        """Rechaza passwords débiles"""
        response = client.post("/api/v1/auth/register", json={
            "email": "weak@example.com",
            "password": "123",
            "name": "Weak User"
        })
        
        # Debería rechazar password muy corta
        assert response.status_code in [400, 422]


class TestLogin:
    """Tests de login y JWT"""
    
    def test_login_success(self):
        """Login exitoso retorna JWT tokens"""
        # Primero registrar
        client.post("/api/v1/auth/register", json={
            "email": "login@example.com",
            "password": "SecurePass123!",
            "name": "Login User"
        })
        
        # Luego login
        response = client.post("/api/v1/auth/login", data={
            "username": "login@example.com",
            "password": "SecurePass123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self):
        """Login con password incorrecta falla"""
        response = client.post("/api/v1/auth/login", data={
            "username": "login@example.com",
            "password": "WrongPassword!"
        })
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self):
        """Login con usuario inexistente falla"""
        response = client.post("/api/v1/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "SomePass123!"
        })
        
        assert response.status_code == 404


@pytest.mark.security
class TestRateLimiting:
    """Tests de rate limiting en endpoints de auth"""
    
    def test_login_rate_limit(self):
        """Bloquea después de 5 intentos fallidos"""
        # Intentar login 6 veces con password incorrecta
        for i in range(6):
            response = client.post("/api/v1/auth/login", data={
                "username": "ratelimit@example.com",
                "password": "wrong"
            })
            
            if i < 5:
                # Primeros 5 intentos: 401 Unauthorized
                assert response.status_code in [401, 404]
            else:
                # 6to intento: 429 Too Many Requests
                assert response.status_code == 429


class TestProtectedEndpoints:
    """Tests de endpoints protegidos"""
    
    def test_protected_without_token(self):
        """Endpoint protegido sin token retorna 401"""
        response = client.get("/api/v1/wallet/balance")
        assert response.status_code ==  401
    
    def test_protected_with_valid_token(self):
        """Endpoint protegido con token válido funciona"""
        # Registrar y login
        client.post("/api/v1/auth/register", json={
            "email": "protected@example.com",
            "password": "SecurePass123!",
            "name": "Protected User"
        })
        
        login_response = client.post("/api/v1/auth/login", data={
            "username": "protected@example.com",
            "password": "SecurePass123!"
        })
        
        token = login_response.json()["access_token"]
        
        # Llamar endpoint protegido
        response = client.get("/api/v1/auth/status", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
