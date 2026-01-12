"""
SIC Ultra - Configuración Central

Todas las configuraciones del sistema usando Pydantic Settings.
Las variables se cargan desde .env automáticamente.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración principal de la aplicación"""
    
    # === App ===
    app_name: str = "SIC Ultra"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = Field(..., min_length=32)
    
    # === Database ===
    database_url: str = "postgresql://sic_user:sic_password@localhost:5432/sic_db"
    
    # === Redis ===
    redis_url: str = "redis://localhost:6379/0"
    
    # === Binance ===
    binance_api_key: str = ""
    binance_api_secret: str = ""
    binance_testnet: bool = True
    
    # === JWT Auth ===
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    remember_me_expire_days: int = 30
    trusted_device_expire_days: int = 30  # 2FA solo cada 30 días
    
    # === 2FA ===
    totp_issuer: str = "SIC Ultra"
    
    # === LLM (Inteligencia Artificial) ===
    deepseek_api_key: str = ""  # https://platform.deepseek.com
    openai_api_key: str = ""    # https://platform.openai.com
    ollama_model: str = "llama3"  # Modelo local (gratis)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la configuración cacheada.
    Usa @lru_cache para no leer .env en cada request.
    """
    return Settings()


# Instancia global
settings = get_settings()
