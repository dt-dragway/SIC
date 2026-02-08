"""
SIC Ultra - Configuración Central

Todas las configuraciones del sistema usando Pydantic Settings.
Las variables se cargan desde .env automáticamente.
Last modification: Force reload for env update
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración principal de la aplicación"""
    
    # === App ===
    app_name: str = "SIC Ultra"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = Field(..., min_length=32)
    
    
    # === Database ===
    postgres_user: str = Field(default="sic_user", env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")  # MUST be in .env
    postgres_db: str = Field(default="sic_db", env="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    database_url: str = ""  # Se construye en __init__
    
    def __init__(self, **data):
        super().__init__(**data)
        # Construir database_url de forma segura con validación
        if not self.database_url:
            # Validar y sanitizar componentes de la URL
            validated_user = self._validate_db_component(self.postgres_user)
            validated_password = self._validate_db_component(self.postgres_password)
            validated_host = self._validate_db_component(self.postgres_host)
            validated_port = str(int(self.postgres_port))  # Asegurar que es un puerto válido
            
            # URL encoding para prevenir SQL injection
            import urllib.parse
            encoded_user = urllib.parse.quote_plus(validated_user)
            encoded_password = urllib.parse.quote_plus(validated_password)
            encoded_db = urllib.parse.quote_plus(self.postgres_db)
            
            self.database_url = f"postgresql://{encoded_user}:{encoded_password}@{validated_host}:{validated_port}/{encoded_db}"
    
    def _validate_db_component(self, component: str) -> str:
        """Valida y sanitiza componentes de la base de datos"""
        if not component:
            raise ValueError("Componente de base de datos no puede ser vacío")
        
        # Permitir solo caracteres alfanuméricos y algunos símbolos seguros
        import re
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', component):
            raise ValueError(f"Componente inválido: {component}")
        
        return component.strip()
    
    # === Redis ===
    redis_url: str = "redis://localhost:6379/0"
    
    # === Binance ===
    binance_api_key: str = ""
    binance_api_secret: str = ""
    binance_testnet: bool = True
    
    # === JWT Auth ===
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"  # Usar HS256 para compatibilidad con secret en texto plano
    access_token_expire_minutes: int = 30      # 30 minutos (antes 1 año)
    refresh_token_expire_days: int = 7         # 7 días (antes 1 año)
    remember_me_expire_days: int = 30           # 30 días (antes 1 año)
    trusted_device_expire_days: int = 7        # 7 días para 2FA (antes 1 año)
    
    # === 2FA ===
    totp_issuer: str = "SIC Ultra"
    
    # === LLM (Inteligencia Artificial) ===
    deepseek_api_key: str = ""  # https://platform.deepseek.com
    openai_api_key: str = ""    # https://platform.openai.com
    ollama_model: str = "llama3"  # Modelo local (gratis)
    
    # === Admin Account (OBLIGATORIO desde .env) ===
    admin_email: str = Field(..., min_length=5)  # Obligatorio desde .env
    admin_password: str = Field(..., min_length=12)  # MÍNIMO 12 CARACTERES desde .env
    
    class Config:
        import os
        # Usar ruta absoluta para evitar problemas con espacios o cwd
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # backend/app -> backend
        root_dir = os.path.dirname(base_dir) # backend -> SIC
        env_file = os.path.join(root_dir, ".env")
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
