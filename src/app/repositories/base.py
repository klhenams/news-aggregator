"""Abstract base repository interface for news data sources."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.schemas import NewsCreate, NewsResponse


class NewsRepository(ABC):
    """Abstract base class for news data repositories."""

    @abstractmethod
    async def create(self, news_data: NewsCreate) -> NewsResponse:
        """Create a new news article."""
        pass

    @abstractmethod
    async def get_by_id(self, article_id: str) -> Optional[NewsResponse]:
        """Get a news article by ID."""
        pass

    @abstractmethod
    async def get_by_url(self, url: str) -> Optional[NewsResponse]:
        """Get a news article by URL."""
        pass

    @abstractmethod
    async def list(
        self, page: int = 1, per_page: int = 10, source: Optional[str] = None
    ) -> List[NewsResponse]:
        """Get paginated list of news articles."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        page: int = 1,
        per_page: int = 10,
        source: Optional[str] = None,
    ) -> List[NewsResponse]:
        """Search news articles by query."""
        pass

    @abstractmethod
    async def count(self, source: Optional[str] = None) -> int:
        """Get total count of articles."""
        pass

    @abstractmethod
    async def delete(self, article_id: str) -> bool:
        """Delete a news article."""
        pass

    @abstractmethod
    async def update(
        self, article_id: str, updates: Dict[str, Any]
    ) -> Optional[NewsResponse]:
        """Update a news article."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the data source."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources."""
        pass
