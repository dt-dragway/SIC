"""
Middleware de Rate Limiting para SIC Ultra

Protege contra brute force y DDoS attacks.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import os
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    """Rate limiter simple basado en memoria"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = {}
    
    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Verifica si una key excedió el rate limit.
        
        Args:
            key: Identificador único (IP, user_id, etc)
            max_requests: Máximo de requests permitidos
            window_seconds: Ventana de tiempo en segundos
        """
        now = datetime.now()
        
        # Verificar si está bloqueado temporalmente
        if key in self.blocked_ips:
            if now < self.blocked_ips[key]:
                return True
            else:
                del self.blocked_ips[key]
        
        # Limpiar requests antiguos
        cutoff = now - timedelta(seconds=window_seconds)
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]
        
        # Verificar límite
        if len(self.requests[key]) >= max_requests:
            # Bloquear por 5 minutos
            self.blocked_ips[key] = now + timedelta(minutes=5)
            return True
        
        # Registrar request actual
        self.requests[key].append(now)
        return False


# Instancia global
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Middleware para aplicar rate limiting"""
    
    # Skip en modo test
    if os.getenv("TESTING") == "true":
        return await call_next(request)
    
    # Obtener IP del cliente
    client_ip = request.client.host
    
    # Paths con rate limiting estricto
    strict_paths = {
        "/api/v1/auth/login": (5, 60),  # 5 requests por minuto
        "/api/v1/auth/register": (3, 300),  # 3 requests por 5 minutos
        "/api/v1/auth/2fa/verify": (10, 60),  # 10 por minuto
    }
    
    # Verificar si el path requiere rate limiting
    for path, (max_req, window) in strict_paths.items():
        if request.url.path == path:
            if rate_limiter.is_rate_limited(client_ip, max_req, window):
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests. Please try again later.",
                        "retry_after": 300
                    }
                )
    
    # Rate limit general (más permisivo)
    if rate_limiter.is_rate_limited(f"general_{client_ip}", 100, 60):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )
    
    response = await call_next(request)
    return response
