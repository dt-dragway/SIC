"""
Security Headers Middleware

Implementa headers de seguridad según OWASP best practices.
"""

from fastapi import Request
from fastapi.responses import Response

async def security_headers_middleware(request: Request, call_next):
    """Agrega headers de seguridad a todas las respuestas"""
    
    response: Response = await call_next(request)
    
    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # unsafe-* necesario para React
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' http://localhost:8000 ws://localhost:*; "
        "frame-ancestors 'none'"
    )
    
    # Prevenir MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Prevenir clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # XSS Protection (legacy pero no daña)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions Policy (antes Feature Policy)
    response.headers["Permissions-Policy"] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=()"
    )
    
    return response
