"""In-memory implementation of news repository."""
import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.logging import get_logger
from app.repositories.base import NewsRepository
from app.schemas import NewsCreate, NewsResponse

logger = get_logger(__name__)


class InMemoryNewsRepository(NewsRepository):
    """In-memory implementation of news repository."""

    def __init__(self) -> None:
        """Initialize the in-memory repository."""
        self._articles: Dict[str, NewsResponse] = {}
        self._url_index: Dict[str, str] = {}  # URL -> ID mapping
        self._lock = asyncio.Lock()
        logger.info("Initialized InMemoryNewsRepository")

    async def create(self, news_data: NewsCreate) -> NewsResponse:
        """Create a new news article."""
        async with self._lock:
            # Check if article already exists by URL
            existing_id = self._url_index.get(str(news_data.link))
            if existing_id and existing_id in self._articles:
                logger.warning(f"Article already exists: {news_data.link}")
                return self._articles[existing_id]

            # Create new article
            article_id = str(uuid.uuid4())
            article = NewsResponse(
                id=article_id,
                headline=news_data.headline,
                link=news_data.link,
                source=news_data.source,
                created_at=datetime.utcnow(),
            )

            self._articles[article_id] = article
            self._url_index[str(news_data.link)] = article_id

            logger.info(f"Created article in memory: {article_id}")
            return article

    async def get_by_id(self, article_id: str) -> Optional[NewsResponse]:
        """Get a news article by ID."""
        async with self._lock:
            return self._articles.get(article_id)

    async def get_by_url(self, url: str) -> Optional[NewsResponse]:
        """Get a news article by URL."""
        async with self._lock:
            article_id = self._url_index.get(url)
            if article_id:
                return self._articles.get(article_id)
            return None

    async def list(
        self, page: int = 1, per_page: int = 10, source: Optional[str] = None
    ) -> List[NewsResponse]:
        """Get paginated list of news articles."""
        async with self._lock:
            articles = list(self._articles.values())

            # Filter by source if specified
            if source:
                articles = [a for a in articles if a.source == source]

            # Sort by created_at descending
            articles.sort(key=lambda x: x.created_at, reverse=True)

            # Paginate
            start = (page - 1) * per_page
            end = start + per_page

            return articles[start:end]

    async def search(
        self,
        query: str,
        page: int = 1,
        per_page: int = 10,
        source: Optional[str] = None,
    ) -> List[NewsResponse]:
        """Search news articles by query."""
        async with self._lock:
            articles = list(self._articles.values())

            # Filter by query (case-insensitive)
            query_lower = query.lower()
            articles = [a for a in articles if query_lower in a.headline.lower()]

            # Filter by source if specified
            if source:
                articles = [a for a in articles if a.source == source]

            # Sort by created_at descending
            articles.sort(key=lambda x: x.created_at, reverse=True)

            # Paginate
            start = (page - 1) * per_page
            end = start + per_page

            return articles[start:end]

    async def count(self, source: Optional[str] = None) -> int:
        """Get total count of articles."""
        async with self._lock:
            if source:
                return sum(1 for a in self._articles.values() if a.source == source)
            return len(self._articles)

    async def delete(self, article_id: str) -> bool:
        """Delete a news article."""
        async with self._lock:
            article = self._articles.get(article_id)
            if article:
                # Remove from URL index
                self._url_index.pop(str(article.link), None)
                # Remove from articles
                del self._articles[article_id]
                logger.info(f"Deleted article from memory: {article_id}")
                return True
            return False

    async def update(
        self, article_id: str, updates: Dict[str, Any]
    ) -> Optional[NewsResponse]:
        """Update a news article."""
        async with self._lock:
            article = self._articles.get(article_id)
            if not article:
                return None

            # Create updated article
            updated_data = article.dict()
            updated_data.update(updates)

            # Handle URL changes in index
            old_url = str(article.link)
            new_url = updates.get("link", old_url)

            if old_url != new_url:
                self._url_index.pop(old_url, None)
                self._url_index[new_url] = article_id

            # Update article
            updated_article = NewsResponse(**updated_data)
            self._articles[article_id] = updated_article

            logger.info(f"Updated article in memory: {article_id}")
            return updated_article

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the data source."""
        return {
            "status": "healthy",
            "type": "in_memory",
            "article_count": len(self._articles),
            "memory_usage": f"{len(self._articles)} articles in memory",
        }

    async def cleanup(self) -> None:
        """Cleanup resources."""
        async with self._lock:
            self._articles.clear()
            self._url_index.clear()
            logger.info("Cleaned up InMemoryNewsRepository")

    # Additional utility methods for in-memory repository
    async def clear_all(self) -> None:
        """Clear all articles (useful for testing)."""
        await self.cleanup()

    async def bulk_create(self, articles: List[NewsCreate]) -> List[NewsResponse]:
        """Bulk create articles."""
        created_articles = []
        for article_data in articles:
            try:
                article = await self.create(article_data)
                created_articles.append(article)
            except Exception as e:
                logger.error(f"Failed to create article in bulk: {str(e)}")
                continue
        return created_articles
