"""
SIC Ultra - Redis Client with Circuit Breaker

Patron Circuit Breaker para Redis:
- CLOSED: Redis funciona normalmente
- OPEN: Redis falló N veces → usar fallback in-memory
- HALF_OPEN: Probar si Redis se recuperó

Fallback: TTL dictionary cache en memoria.
"""

import os
import time
from typing import Any, Optional, Dict
from datetime import datetime
from enum import Enum
from loguru import logger

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("⚠️ redis package not installed — using in-memory cache only")


class CircuitState(str, Enum):
    CLOSED = "CLOSED"        # Normal operation
    OPEN = "OPEN"            # Redis failed, using fallback
    HALF_OPEN = "HALF_OPEN"  # Testing if Redis recovered


class InMemoryTTLCache:
    """
    Fallback cache cuando Redis no está disponible.
    Simple dict con TTL por key.
    """
    
    def __init__(self, default_ttl: int = 300):
        self._store: Dict[str, tuple] = {}  # key → (value, expiry_timestamp)
        self._default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[str]:
        if key in self._store:
            value, expiry = self._store[key]
            if time.time() < expiry:
                return value
            else:
                del self._store[key]
        return None
    
    def set(self, key: str, value: str, ex: int = None) -> bool:
        ttl = ex or self._default_ttl
        self._store[key] = (value, time.time() + ttl)
        # Cleanup expired keys periodically
        if len(self._store) > 1000:
            self._cleanup()
        return True
    
    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None
    
    def exists(self, key: str) -> bool:
        val = self.get(key)
        return val is not None
    
    def _cleanup(self):
        """Remove expired keys."""
        now = time.time()
        expired = [k for k, (_, exp) in self._store.items() if now >= exp]
        for k in expired:
            del self._store[k]


class ResilientRedisClient:
    """
    Redis client con Circuit Breaker + fallback a in-memory cache.
    
    Garantía: El sistema NUNCA falla porque Redis está caído.
    
    Circuit Breaker settings:
    - failure_threshold: 3 fallos consecutivos → OPEN
    - recovery_timeout: 30s en OPEN → probar HALF_OPEN
    - success_threshold: 2 éxitos en HALF_OPEN → CLOSED
    """
    
    def __init__(
        self,
        redis_url: str = None,
        failure_threshold: int = 3,
        recovery_timeout: int = 30,
        success_threshold: int = 2
    ):
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._success_threshold = success_threshold
        
        # Circuit state
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        
        # Fallback cache
        self._fallback = InMemoryTTLCache()
        
        # Redis connection
        self._redis = None
        self._connect_redis()
        
        logger.info(
            f"🔌 Redis Client inicializado | URL={self._redis_url} | "
            f"Circuit Breaker: threshold={failure_threshold}, timeout={recovery_timeout}s"
        )
    
    def _connect_redis(self):
        """Intentar conexión a Redis."""
        if not REDIS_AVAILABLE:
            self._state = CircuitState.OPEN
            logger.warning("⚠️ Redis package not available, using in-memory fallback")
            return
        
        try:
            self._redis = redis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_timeout=3,
                socket_connect_timeout=3,
                retry_on_timeout=True
            )
            self._redis.ping()
            self._state = CircuitState.CLOSED
            logger.info("✅ Redis conectado correctamente")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self._redis = None
            self._state = CircuitState.OPEN
    
    def _should_try_redis(self) -> bool:
        """Determinar si debemos intentar usar Redis."""
        if self._state == CircuitState.CLOSED:
            return True
        
        if self._state == CircuitState.OPEN:
            # Check recovery timeout
            if self._last_failure_time is None:
                return False
            elapsed = time.time() - self._last_failure_time
            if elapsed >= self._recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
                logger.info("🔄 Circuit Breaker → HALF_OPEN (probando Redis)")
                return True
            return False
        
        if self._state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def _record_success(self):
        """Registrar éxito de Redis."""
        self._failure_count = 0
        
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self._success_threshold:
                self._state = CircuitState.CLOSED
                logger.info("✅ Circuit Breaker → CLOSED (Redis recuperado)")
    
    def _record_failure(self):
        """Registrar fallo de Redis."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        self._success_count = 0
        
        if self._failure_count >= self._failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(
                f"🔴 Circuit Breaker → OPEN ({self._failure_count} fallos consecutivos). "
                f"Usando fallback in-memory."
            )
    
    # === Public API (same interface as redis-py) ===
    
    def get(self, key: str) -> Optional[str]:
        """Get a value. Falls back to in-memory if Redis is down."""
        if self._should_try_redis() and self._redis:
            try:
                result = self._redis.get(key)
                self._record_success()
                return result
            except Exception as e:
                self._record_failure()
                logger.debug(f"Redis GET failed: {e}, using fallback")
        
        return self._fallback.get(key)
    
    def set(self, key: str, value: str, ex: int = 300) -> bool:
        """Set a value with TTL. Writes to both Redis and fallback."""
        # Always write to fallback for resilience
        self._fallback.set(key, value, ex)
        
        if self._should_try_redis() and self._redis:
            try:
                self._redis.set(key, value, ex=ex)
                self._record_success()
                return True
            except Exception as e:
                self._record_failure()
                logger.debug(f"Redis SET failed: {e}, stored in fallback")
        
        return True  # Fallback always succeeds
    
    def delete(self, key: str) -> bool:
        """Delete a key from both Redis and fallback."""
        self._fallback.delete(key)
        
        if self._should_try_redis() and self._redis:
            try:
                self._redis.delete(key)
                self._record_success()
                return True
            except Exception as e:
                self._record_failure()
        
        return True
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if self._should_try_redis() and self._redis:
            try:
                result = self._redis.exists(key)
                self._record_success()
                return bool(result)
            except Exception as e:
                self._record_failure()
        
        return self._fallback.exists(key)
    
    def get_circuit_state(self) -> Dict:
        """Get current circuit breaker status for monitoring."""
        return {
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "redis_connected": self._redis is not None,
            "using_fallback": self._state == CircuitState.OPEN,
            "last_failure": (
                datetime.fromtimestamp(self._last_failure_time).isoformat()
                if self._last_failure_time else None
            )
        }


# === Singleton ===
_resilient_redis: Optional[ResilientRedisClient] = None


def get_redis_client() -> ResilientRedisClient:
    """Get the resilient Redis client with circuit breaker."""
    global _resilient_redis
    if _resilient_redis is None:
        _resilient_redis = ResilientRedisClient()
    return _resilient_redis
