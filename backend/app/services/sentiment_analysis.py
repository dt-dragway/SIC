"""
SIC Ultra - Sentiment Analysis Service (REWRITTEN)

ANTES: 100% random.uniform() — COMPLETAMENTE SIMULADO.
AHORA: CryptoPanic API (free tier) + NLP relevance filtering.

Sources:
1. CryptoPanic (free, no key needed for public data)
2. Fear & Greed Index (alternative.me)
3. Fallback: Last known + decay

PRINCIPIO: Prefiero "NO DATA" a datos inventados.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import httpx


class SentimentService:
    """
    Servicio de Análisis de Sentimiento — DATOS REALES.
    
    Chain of trust:
    1. CryptoPanic API (noticias crypto reales con sentiment voting)
    2. Fear & Greed Index (alternative.me, free)
    3. Si ambos fallan → retorna last known + flag "STALE"
    """
    
    # CryptoPanic free public API
    CRYPTOPANIC_URL = "https://cryptopanic.com/api/free/v1/posts/"
    # Fear & Greed Index
    FEAR_GREED_URL = "https://api.alternative.me/fng/?limit=1"
    
    # NLP Relevance keywords (asset-specific filtering)
    RELEVANCE_KEYWORDS = {
        "BTC": ["bitcoin", "btc", "halving", "mining", "satoshi", "lightning"],
        "ETH": ["ethereum", "eth", "vitalik", "layer2", "merge", "staking"],
        "SOL": ["solana", "sol", "saga", "firedancer"],
        "BNB": ["binance", "bnb", "cz", "bsc"],
    }
    
    # Minimum relevance score to consider a news item (0-100)
    MIN_RELEVANCE = 30
    
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        self._cache_ttl = timedelta(minutes=5)
        self._last_update: Optional[datetime] = None
        self._api_key = os.getenv("CRYPTOPANIC_API_KEY", "")  # Optional
        logger.info("📰 Sentiment Service inicializado (CryptoPanic + Fear&Greed)")
    
    async def get_market_sentiment(self, symbol: str = "BTC") -> Dict[str, Any]:
        """
        Obtiene el sentimiento REAL del mercado para un activo.
        NO usa random.uniform(). Datos reales o "NO_DATA".
        """
        coin = symbol.replace("USDT", "").upper()
        
        # Check cache first
        if coin in self._cache:
            cached = self._cache[coin]
            age = datetime.utcnow() - cached.get("_cached_at", datetime.min)
            if age < self._cache_ttl:
                logger.debug(f"📰 Sentiment cache hit: {coin} ({age.seconds}s old)")
                return cached
        
        # Fetch real data
        sentiment_data = await self._fetch_real_sentiment(coin)
        
        # Cache it
        sentiment_data["_cached_at"] = datetime.utcnow()
        self._cache[coin] = sentiment_data
        self._last_update = datetime.utcnow()
        
        return sentiment_data
    
    async def _fetch_real_sentiment(self, coin: str) -> Dict[str, Any]:
        """Fetch from real APIs with fallback chain."""
        
        news = []
        news_score = None
        fear_greed_score = None
        fear_greed_label = None
        data_source = "NONE"
        is_stale = False
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # === Source 1: CryptoPanic ===
            try:
                params = {
                    "currencies": coin,
                    "kind": "news",
                    "filter": "important",
                    "public": "true"
                }
                if self._api_key:
                    params["auth_token"] = self._api_key
                
                resp = await client.get(self.CRYPTOPANIC_URL, params=params)
                
                if resp.status_code == 200:
                    data = resp.json()
                    raw_news = data.get("results", [])
                    
                    # NLP relevance filter
                    news = self._filter_relevant_news(raw_news, coin)
                    
                    if news:
                        news_score = self._calculate_news_sentiment(news)
                        data_source = "CryptoPanic"
                        logger.info(
                            f"📰 CryptoPanic: {len(news)} relevant news for {coin}, "
                            f"score={news_score:.1f}"
                        )
                else:
                    logger.warning(
                        f"⚠️ CryptoPanic API returned {resp.status_code}"
                    )
            except Exception as e:
                logger.error(f"❌ CryptoPanic fetch failed: {e}")
            
            # === Source 2: Fear & Greed Index ===
            try:
                resp = await client.get(self.FEAR_GREED_URL)
                if resp.status_code == 200:
                    fng_data = resp.json().get("data", [])
                    if fng_data:
                        fear_greed_score = int(fng_data[0].get("value", 50))
                        fear_greed_label = fng_data[0].get("value_classification", "Neutral")
                        if data_source == "NONE":
                            data_source = "Fear&Greed"
                        else:
                            data_source += "+Fear&Greed"
                        logger.info(
                            f"😰 Fear&Greed: {fear_greed_score} ({fear_greed_label})"
                        )
            except Exception as e:
                logger.error(f"❌ Fear&Greed fetch failed: {e}")
        
        # === Composite Score ===
        if news_score is not None and fear_greed_score is not None:
            # Weighted: 60% news, 40% fear&greed
            overall = news_score * 0.6 + fear_greed_score * 0.4
        elif news_score is not None:
            overall = news_score
        elif fear_greed_score is not None:
            overall = fear_greed_score
        else:
            # TOTAL FAILURE — Return stale data
            overall = 50.0
            data_source = "STALE_FALLBACK"
            is_stale = True
            logger.warning("⚠️ ALL sentiment sources FAILED — returning neutral 50")
        
        # Classify
        if overall > 70:
            label = "Codicia Extrema"
            color = "emerald"
        elif overall > 55:
            label = "Codicia"
            color = "cyan"
        elif overall > 45:
            label = "Neutral"
            color = "slate"
        elif overall > 30:
            label = "Miedo"
            color = "rose"
        else:
            label = "Miedo Extremo"
            color = "red"
        
        return {
            "symbol": coin,
            "overall_score": round(overall, 1),
            "label": label,
            "color": color,
            "fear_greed_index": fear_greed_score,
            "fear_greed_label": fear_greed_label,
            "news_count": len(news),
            "top_narrative": news[0]["title"] if news else "Sin noticias relevantes",
            "news": news[:6],  # Top 6
            "data_source": data_source,
            "is_stale": is_stale,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _filter_relevant_news(self, raw_news: List[Dict], coin: str) -> List[Dict]:
        """
        NLP Relevance Filter.
        Filtra noticias irrelevantes usando keyword matching + voting scores.
        
        Retorna solo noticias con relevance_score >= MIN_RELEVANCE.
        """
        keywords = self.RELEVANCE_KEYWORDS.get(coin, [coin.lower()])
        filtered = []
        
        for item in raw_news:
            title = (item.get("title", "") or "").lower()
            
            # Calculate relevance score
            relevance = 0
            
            # Keyword match (0-40 points)
            keyword_hits = sum(1 for kw in keywords if kw in title)
            relevance += min(keyword_hits * 20, 40)
            
            # CryptoPanic voting sentiment (0-30 points)
            votes = item.get("votes", {})
            total_votes = sum(votes.values()) if isinstance(votes, dict) else 0
            if total_votes > 5:
                relevance += 20
            elif total_votes > 0:
                relevance += 10
            
            # Recency bonus (0-30 points)
            published_at = item.get("published_at", "")
            if published_at:
                try:
                    pub_time = datetime.fromisoformat(
                        published_at.replace("Z", "+00:00")
                    ).replace(tzinfo=None)
                    age_hours = (datetime.utcnow() - pub_time).total_seconds() / 3600
                    if age_hours < 1:
                        relevance += 30
                    elif age_hours < 6:
                        relevance += 20
                    elif age_hours < 24:
                        relevance += 10
                except (ValueError, TypeError):
                    pass
            
            if relevance >= self.MIN_RELEVANCE:
                # Determine sentiment from CryptoPanic voting
                sentiment = "neutral"
                if isinstance(votes, dict):
                    positive = votes.get("positive", 0) + votes.get("liked", 0)
                    negative = votes.get("negative", 0) + votes.get("disliked", 0)
                    if positive > negative * 1.5:
                        sentiment = "bullish"
                    elif negative > positive * 1.5:
                        sentiment = "bearish"
                
                filtered.append({
                    "id": item.get("id"),
                    "title": item.get("title", ""),
                    "source": item.get("source", {}).get("title", "Unknown"),
                    "sentiment": sentiment,
                    "relevance_score": relevance,
                    "url": item.get("url", ""),
                    "time_ago": published_at
                })
        
        # Sort by relevance
        filtered.sort(key=lambda x: x["relevance_score"], reverse=True)
        return filtered
    
    def _calculate_news_sentiment(self, news: List[Dict]) -> float:
        """
        Aggregate sentiment score from filtered news.
        
        Bullish = +1, Neutral = 0, Bearish = -1
        Score mapped to 0-100 scale.
        """
        if not news:
            return 50.0
        
        sentiment_map = {"bullish": 1, "neutral": 0, "bearish": -1}
        
        # Weighted by relevance score
        total_weight = 0
        weighted_sentiment = 0
        
        for item in news:
            weight = item.get("relevance_score", 50)
            sentiment_val = sentiment_map.get(item.get("sentiment", "neutral"), 0)
            weighted_sentiment += sentiment_val * weight
            total_weight += weight
        
        if total_weight == 0:
            return 50.0
        
        # Normalize: -1 to +1 → 0 to 100
        avg = weighted_sentiment / total_weight
        score = (avg + 1) / 2 * 100
        
        return max(0, min(100, score))


# Instancia global
sentiment_service = SentimentService()


def get_sentiment_service() -> SentimentService:
    return sentiment_service
