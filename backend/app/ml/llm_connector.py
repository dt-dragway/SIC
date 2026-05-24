"""
SIC Ultra - Conector LLM para Análisis Inteligente

Conecta con modelos de lenguaje profesionales:
- DeepSeek API
- OpenAI GPT-4
- Ollama (local, sin costo)

El LLM analiza el contexto del mercado y proporciona
razonamiento avanzado para las señales de trading.
"""

import httpx
from typing import Optional, Dict, List
from datetime import datetime
from loguru import logger
from abc import ABC, abstractmethod

from app.config import settings


# === Base LLM Interface ===

class LLMProvider(ABC):
    """Interface base para proveedores de LLM"""
    
    @abstractmethod
    async def analyze(self, prompt: str) -> Optional[str]:
        """Enviar prompt y obtener respuesta"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verificar si el proveedor está disponible"""
        pass



# === CENTIBOT SmartPool Provider ===

class SmartPoolProvider(LLMProvider):
    """
    Conector para CENTIBOT SmartPool (Alto Nivel / Multimodelo)
    """
    
    def __init__(self):
        self.url = getattr(settings, 'centibot_url', "http://localhost:7500/api/send")
        
    def is_available(self) -> bool:
        try:
            import socket
            from urllib.parse import urlparse
            parsed = urlparse(self.url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 7500
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                s.connect((host, port))
                return True
        except Exception:
            return False
            
    async def analyze(self, prompt: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.url,
                    json={
                        "text": f"Eres el SmartPool de análisis institucional. Analiza estos datos y da una señal clara:\n\n{prompt}\n\nResponde estrictamente con: SIGNAL: BUY/SELL/HOLD, CONFIDENCE: %, REASON: ..."
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "ok":
                        return data.get("response", "")
                return None
        except Exception as e:
            logger.error(f"SmartPool connection error: {e}")
            return None


# === DeepSeek Provider ===

class DeepSeekProvider(LLMProvider):
    """
    Conector para DeepSeek API.
    
    DeepSeek es más económico que OpenAI y tiene buen rendimiento
    para análisis financiero.
    
    Pricing: ~$0.14 / 1M tokens (muy económico)
    """
    
    BASE_URL = "https://api.deepseek.com/v1/chat/completions"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'deepseek_api_key', None)
        self.model = "deepseek-chat"  # Modelo principal
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def analyze(self, prompt: str) -> Optional[str]:
        if not self.is_available():
            return None
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": """Eres un analista de trading profesional. 
                                Analizas datos de mercado y proporcionas señales claras.
                                Responde siempre en español y sé conciso.
                                Formato: SIGNAL: BUY/SELL/HOLD, CONFIDENCE: %, REASON: ..."""
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"DeepSeek error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"DeepSeek connection error: {e}")
            return None


# === OpenAI Provider ===

class OpenAIProvider(LLMProvider):
    """
    Conector para OpenAI API.
    
    Usa GPT-4 Turbo para análisis más sofisticado.
    
    Pricing: ~$10 / 1M tokens (más caro pero potente)
    """
    
    BASE_URL = "https://api.openai.com/v1/chat/completions"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'openai_api_key', None)
        self.model = "gpt-4-turbo-preview"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def analyze(self, prompt: str) -> Optional[str]:
        if not self.is_available():
            return None
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": """You are a professional crypto trading analyst.
                                Analyze market data and provide clear signals.
                                Always respond in Spanish. Be concise.
                                Format: SIGNAL: BUY/SELL/HOLD, CONFIDENCE: %, REASON: ..."""
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"OpenAI error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"OpenAI connection error: {e}")
            return None


# === Ollama Provider (Local, Gratis) ===

class OllamaProvider(LLMProvider):
    """
    Conector para Ollama (ejecución local).
    
    Ejecuta modelos como Llama 3, Mistral, etc. en tu PC.
    
    💰 Gratis (corre en tu máquina)
    ⚡ Rápido (sin latencia de red)
    🔒 Privado (datos no salen de tu PC)
    
    Requiere instalar Ollama: https://ollama.ai
    """
    
    BASE_URL = "http://localhost:11434/api/generate"
    
    def __init__(self, model: Optional[str] = None):
        self.model = model or getattr(settings, 'ollama_model', 'gemma:2b')
    
    def is_available(self) -> bool:
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                s.connect(("localhost", 11434))
                return True
        except Exception:
            return False
    
    async def analyze(self, prompt: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    json={
                        "model": self.model,
                        "prompt": f"""Eres un analista de trading profesional.
                        Analiza estos datos y da una señal clara.
                        
                        {prompt}
                        
                        Responde con: SIGNAL: BUY/SELL/HOLD, CONFIDENCE: %, REASON: ...""",
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            return None


# === OpenRouter Provider (Online, Multi-Modelo) ===

class OpenRouterProvider(LLMProvider):
    """
    Conector para OpenRouter API.
    
    Acceso unificado a más de 200 modelos: Claude, GPT-4, Mistral,
    Llama 3, Gemini, DeepSeek, etc. con una sola API Key.
    
    💰 Modelos GRATUITOS disponibles:
     - meta-llama/llama-3.1-8b-instruct:free
     - mistralai/mistral-7b-instruct:free
    💎 Modelos de pago (muy económicos):
     - deepseek/deepseek-chat
     - anthropic/claude-3-haiku
    
    Regístrate gratis en: https://openrouter.ai
    """
    
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'openrouter_api_key', '')
        # Modelo por defecto: Llama 3.1 8B GRATUITO
        self.model = model or getattr(settings, 'openrouter_model', 'meta-llama/llama-3.1-8b-instruct:free')
    
    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())
    
    async def analyze(self, prompt: str) -> Optional[str]:
        if not self.is_available():
            return None
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://sic-ultra.local",
                        "X-Title": "SIC Ultra - Trading AI"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Eres un analista de trading cripto profesional de nivel institucional. "
                                    "Tu misión es analizar datos de mercado en tiempo real y proporcionar "
                                    "señales de alta precisión para el sistema SIC Ultra. "
                                    "Responde siempre en español. Sé conciso y directo. "
                                    "Formato estricto: SIGNAL: BUY/SELL/HOLD, CONFIDENCE: %, REASON: ..."
                                )
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.2,
                        "max_tokens": 400
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    model_used = data.get("model", self.model)
                    logger.info(f"🌐 OpenRouter respuesta OK. Modelo: {model_used}")
                    return content
                else:
                    logger.error(f"OpenRouter error {response.status_code}: {response.text[:200]}")
                    return None
                    
        except Exception as e:
            logger.error(f"OpenRouter connection error: {e}")
            return None


# === LLM Manager ===

class LLMManager:
    """
    Gestor de LLMs con fallback automático.
    
    Orden de prioridad:
    1. CentiBot SmartPool (si está disponible)
    2. DeepSeek (económico y bueno)
    3. OpenAI (potente pero caro)
    4. OpenRouter (🌐 multi-modelo online - NUEVO)
    5. Ollama (local y gratis)
    6. Sin LLM (usa solo ML local)
    """
    
    def __init__(self):
        self.providers: List[LLMProvider] = [
            SmartPoolProvider(),
            DeepSeekProvider(),
            OpenAIProvider(),
            OpenRouterProvider(),  # 🌐 NUEVO: OpenRouter antes que Ollama
            OllamaProvider()
        ]
        self._active_provider: Optional[LLMProvider] = None
        self._find_active_provider()
    
    def _find_active_provider(self):
        """Encontrar el primer proveedor disponible"""
        for provider in self.providers:
            if provider.is_available():
                self._active_provider = provider
                logger.info(f"🤖 LLM activo: {provider.__class__.__name__}")
                return
        
        logger.warning("⚠️ Ningún LLM disponible. Usando solo ML local.")
    
    @property
    def is_available(self) -> bool:
        return self._active_provider is not None
    
    @property
    def provider_name(self) -> str:
        if self._active_provider:
            return self._active_provider.__class__.__name__
        return "None"
    
    async def analyze_market(
        self,
        symbol: str,
        current_price: float,
        indicators: Dict,
        patterns: List[str],
        recent_signals: List[Dict]
    ) -> Optional[Dict]:
        """
        Análisis de mercado usando LLM.
        
        El LLM recibe contexto completo y proporciona:
        - Señal con razonamiento
        - Nivel de confianza
        - Factores de riesgo
        """
        if not self._active_provider:
            return None
        
        # Construir prompt con contexto
        prompt = f"""
        ANÁLISIS DE MERCADO: {symbol}
        
        📊 Precio actual: ${current_price:,.2f}
        
        📈 Indicadores técnicos:
        - RSI: {indicators.get('rsi', 'N/A')}
        - MACD Histogram: {indicators.get('macd', 'N/A')}
        - Tendencia: {indicators.get('trend', 'N/A')}
        - ATR (volatilidad): {indicators.get('atr', 'N/A')}
        
        🔍 Patrones detectados: {', '.join(patterns) if patterns else 'Ninguno'}
        
        📜 Últimas señales generadas:
        {self._format_recent_signals(recent_signals)}
        
        Proporciona tu análisis con:
        1. SIGNAL: BUY, SELL, o HOLD
        2. CONFIDENCE: porcentaje de confianza (0-100)
        3. REASON: explicación breve
        4. RISK: factores de riesgo a considerar
        5. TARGETS: niveles de entrada, stop-loss y take-profit sugeridos
        """
        
        response = None
        tried_providers = []
        
        # Intentar con el proveedor activo primero
        if self._active_provider:
            tried_providers.append(self._active_provider)
            try:
                response = await self._active_provider.analyze(prompt)
            except Exception as e:
                logger.error(f"❌ Error en proveedor LLM activo ({self._active_provider.__class__.__name__}): {e}")
        
        # Si el proveedor activo falla o no devuelve respuesta, intentar con los demás proveedores disponibles
        if not response:
            for provider in self.providers:
                if provider not in tried_providers and provider.is_available():
                    logger.warning(f"🔄 Fallback LLM: El proveedor activo falló. Intentando con {provider.__class__.__name__}...")
                    tried_providers.append(provider)
                    try:
                        response = await provider.analyze(prompt)
                        if response:
                            # Actualizar el proveedor activo para futuras llamadas
                            self._active_provider = provider
                            logger.success(f"🤖 LLM activo cambiado dinámicamente a: {provider.__class__.__name__}")
                            break
                    except Exception as e:
                        logger.error(f"❌ Error en proveedor de fallback LLM ({provider.__class__.__name__}): {e}")
        
        if response:
            return self._parse_llm_response(response, symbol, current_price)
            
        return None
    
    def _format_recent_signals(self, signals: List[Dict]) -> str:
        if not signals:
            return "No hay señales previas"
        
        lines = []
        for s in signals[-3:]:  # Últimas 3
            lines.append(f"- {s.get('direction', '?')} @ ${s.get('price', 0):,.2f} ({s.get('result', 'pendiente')})")
        
        return "\n".join(lines)
    
    def _parse_llm_response(self, response: str, symbol: str, price: float) -> Dict:
        """Parsear respuesta del LLM"""
        result = {
            "symbol": symbol,
            "price": price,
            "signal": "HOLD",
            "confidence": 50,
            "reasoning": response,
            "source": self.provider_name,
            "timestamp": datetime.utcnow()
        }
        
        # Extraer señal
        response_upper = response.upper()
        if "SIGNAL: BUY" in response_upper or "SEÑAL: COMPRA" in response_upper:
            result["signal"] = "BUY"
        elif "SIGNAL: SELL" in response_upper or "SEÑAL: VENTA" in response_upper:
            result["signal"] = "SELL"
        
        # Extraer confianza
        import re
        confidence_match = re.search(r'CONFIDENCE:\s*(\d+)', response_upper)
        if confidence_match:
            result["confidence"] = min(int(confidence_match.group(1)), 100)
        
        return result


# === Singleton ===

_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """Obtener gestor de LLMs"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager
