"""
SIC Ultra - Sentiment Analysis Service
Analiza noticias y redes sociales para determinar la narrativa del mercado.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
from loguru import logger
import httpx

class SentimentService:
    """
    Servicio de Análisis de Sentimiento y Narrativas.
    En producción, consume APIs como NewsAPI, CryptoPanic o Twitter.
    """
    
    def __init__(self):
        self.sources = ["CryptoPanic", "LunarCrush", "Binance News"]
        self.categories = ["FRENCH_FUD", "REGULATION", "ADOPTION", "TECHNICAL", "WHALE_MOVE"]

    async def get_market_sentiment(self, symbol: str = "BTC") -> Dict[str, Any]:
        """
        Obtiene el sentimiento actual del mercado para un activo.
        """
        # Simulamos un análisis de sentimiento basado en "ruido" del mercado
        # En una implementación real, aquí haríamos web scraping o llamadas a APIs
        
        score = random.uniform(20, 80) # 0-100 (Bajo = Miedo, Alto = Codicia)
        
        # Determinar etiqueta
        if score > 70:
            label = "Codicia Extrema"
            color = "emerald"
        elif score > 55:
            label = "Codicia"
            color = "cyan"
        elif score > 45:
            label = "Neutral"
            color = "slate"
        elif score > 30:
            label = "Miedo"
            color = "rose"
        else:
            label = "Miedo Extremo"
            color = "red"

        # Generar noticias simuladas coherentes con el sentimiento
        news = self._generate_simulated_news(symbol, label)
        
        return {
            "symbol": symbol,
            "overall_score": score,
            "label": label,
            "color": color,
            "news_count": len(news),
            "top_narrative": news[0]["title"] if news else "Mercado en calma lateral",
            "news": news,
            "timestamp": datetime.now().isoformat()
        }

    def _generate_simulated_news(self, symbol: str, label: str) -> List[Dict[str, Any]]:
        """Genera noticias realistas basadas en el sentimiento actual"""
        coin = symbol.replace("USDT", "")
        
        bullish_news = [
            f"Adopción masiva: Gran banco central considera a {coin} como reserva.",
            f"Apple integra pagos con {coin} en su próxima actualización de iOS.",
            f"Inversión institucional: BlackRock aumenta su exposición a {coin} un 20%.",
            f"Actualización exitosa: El nuevo protocolo de {coin} reduce fees en 90%.",
            f"Quema masiva: Se retiran de circulación {random.randint(10, 100)}M de {coin}."
        ]
        
        bearish_news = [
            f"FUD en Asia: Rumores de nueva prohibición de minería de {coin}.",
            f"Regulación estricta: La SEC investiga a los principales validadores de {coin}.",
            f"Hack detectado: Vulnerabilidad crítica en un bridge de la red {coin}.",
            f"Liquidaciones masivas: Más de ${random.randint(50, 500)}M liquidados en posiciones LONG.",
            f"Inflación persistente: Datos del IPC afectan el apetito por riesgo en {coin}."
        ]
        
        neutral_news = [
            f"{coin} mantiene soporte clave mientras el mercado espera datos de la FED.",
            f"Consolidación lateral en {coin}: Bajos volúmenes el fin de semana.",
            f"Nuevo reporte técnico sobre la escalabilidad de {coin} se publica mañana.",
            f"Analistas divididos sobre el próximo movimiento de {coin} tras el halving."
        ]
        
        # Seleccionar noticias según el sentimiento
        news_list = []
        if "Codicia" in label:
            pool = bullish_news + neutral_news
        elif "Miedo" in label:
            pool = bearish_news + neutral_news
        else:
            pool = neutral_news
            
        selected = random.sample(pool, 4)
        
        for i, title in enumerate(selected):
            sentiment_point = random.choice(["bullish", "bearish", "neutral"]) if "Neutral" in label else \
                             ("bullish" if "Codicia" in label else "bearish")
            
            news_list.append({
                "id": i,
                "title": title,
                "source": random.choice(self.sources),
                "sentiment": sentiment_point,
                "impact_score": random.randint(30, 95),
                "time_ago": f"{random.randint(5, 59)}m"
            })
            
        return news_list

# Instancia global
sentiment_service = SentimentService()

def get_sentiment_service() -> SentimentService:
    return sentiment_service
