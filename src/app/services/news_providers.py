import asyncio
from typing import List, Dict, Any
from abc import ABC, abstractmethod

from app.utils.async_http_client import get_http_client, HTTPClientError
from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas import NewsCreate

logger = get_logger(__name__)


class NewsProvider(ABC):
    """Abstract base class for news providers."""
    
    @abstractmethod
    async def fetch_articles(self) -> List[NewsCreate]:
        """Fetch articles from the news source."""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of the news source."""
        pass


class RedditNewsProvider(NewsProvider):
    """Reddit news provider."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.reddit_api_base_url
        
    def get_source_name(self) -> str:
        return "reddit"
    
    async def fetch_articles(self) -> List[NewsCreate]:
        """Fetch top news articles from Reddit."""
        try:
            http_client = await get_http_client()
            url = f"{self.base_url}/r/news/top.json"
            params = {"limit": 10}
            
            response = await http_client.get(
                url=url,
                params=params,
                auth_required=False
            )
            
            return self._parse_reddit_response(response)
            
        except HTTPClientError as e:
            logger.error(f"Failed to fetch Reddit articles: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Reddit articles: {str(e)}")
            return []
    
    def _parse_reddit_response(self, response: Dict[str, Any]) -> List[NewsCreate]:
        """Parse Reddit API response into NewsCreate objects."""
        articles = []
        
        try:
            if "data" in response and "children" in response["data"]:
                for post in response["data"]["children"]:
                    post_data = post.get("data", {})
                    
                    # Skip self posts without external URLs
                    url = post_data.get("url", "")
                    if not url or url.startswith("https://www.reddit.com"):
                        continue
                    
                    headline = post_data.get("title", "").strip()
                    if headline:
                        articles.append(NewsCreate(
                            headline=headline,
                            link=url,
                            source=self.get_source_name()
                        ))
                        
        except Exception as e:
            logger.error(f"Error parsing Reddit response: {str(e)}")
            
        logger.info(f"Parsed {len(articles)} articles from Reddit")
        return articles


class NewsAPIProvider(NewsProvider):
    """NewsAPI.org provider."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.news_api_base_url
        
    def get_source_name(self) -> str:
        return "newsapi"
    
    async def fetch_articles(self) -> List[NewsCreate]:
        """Fetch top headlines from NewsAPI."""
        try:
            http_client = await get_http_client()
            url = f"{self.base_url}/top-headlines"
            
            params = {
                "category": "general",
                "pageSize": 10,
                "page": 1,
                "country": "us"  # You can make this configurable
            }
            
            response = await http_client.get(
                url=url,
                params=params,
                auth_required=True,
                api_key=self.settings.news_api_key
            )
            
            return self._parse_newsapi_response(response)
            
        except HTTPClientError as e:
            logger.error(f"Failed to fetch NewsAPI articles: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching NewsAPI articles: {str(e)}")
            return []
    
    def _parse_newsapi_response(self, response: Dict[str, Any]) -> List[NewsCreate]:
        """Parse NewsAPI response into NewsCreate objects."""
        articles = []
        
        try:
            if "articles" in response:
                for article in response["articles"]:
                    headline = article.get("title", "").strip()
                    url = article.get("url", "").strip()
                    
                    if headline and url:
                        articles.append(NewsCreate(
                            headline=headline,
                            link=url,
                            source=self.get_source_name()
                        ))
                        
        except Exception as e:
            logger.error(f"Error parsing NewsAPI response: {str(e)}")
            
        logger.info(f"Parsed {len(articles)} articles from NewsAPI")
        return articles


class NewsAggregatorService:
    """Service for aggregating news from multiple sources."""
    
    def __init__(self):
        self.providers: List[NewsProvider] = [
            RedditNewsProvider(),
            NewsAPIProvider(),
        ]
    
    async def fetch_all_articles(self) -> List[NewsCreate]:
        """Fetch articles from all configured providers."""
        all_articles = []
        
        # Fetch from all providers concurrently
        tasks = [provider.fetch_articles() for provider in self.providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                provider_name = self.providers[i].get_source_name()
                logger.error(f"Provider {provider_name} failed: {str(result)}")
            elif isinstance(result, list):
                all_articles.extend(result)
        
        logger.info(f"Aggregated {len(all_articles)} articles from {len(self.providers)} providers")
        return all_articles
    
    async def fetch_from_source(self, source: str) -> List[NewsCreate]:
        """Fetch articles from a specific source."""
        for provider in self.providers:
            if provider.get_source_name() == source:
                return await provider.fetch_articles()
        
        logger.warning(f"Unknown news source: {source}")
        return []
