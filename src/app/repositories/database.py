"""Database implementation of news repository using SQLAlchemy."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.database import News
from app.repositories.base import NewsRepository
from app.schemas import NewsCreate, NewsResponse

logger = get_logger(__name__)


class DatabaseNewsRepository(NewsRepository):
    """Database implementation of news repository using SQLAlchemy."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize the database repository."""
        self.db = db_session
        logger.info("Initialized DatabaseNewsRepository")

    async def create(self, news_data: NewsCreate) -> NewsResponse:
        """Create a new news article."""
        try:
            # Check if article already exists by URL
            existing = await self.get_by_url(str(news_data.link))
            if existing:
                logger.warning(f"Article already exists: {news_data.link}")
                return existing

            # Create new article
            db_article = News(
                headline=news_data.headline,
                link=str(news_data.link),
                source=news_data.source,
                created_at=datetime.utcnow(),
            )

            self.db.add(db_article)
            await self.db.commit()
            await self.db.refresh(db_article)

            logger.info(f"Created article in database: {db_article.id}")
            return self._to_response(db_article)

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error creating article: {str(e)}")
            raise RuntimeError(f"Failed to create article: {str(e)}")

    async def get_by_id(self, article_id: str) -> Optional[NewsResponse]:
        """Get a news article by ID."""
        try:
            # Handle both string and int IDs
            id_value: Union[int, str]
            if isinstance(article_id, str) and article_id.isdigit():
                id_value = int(article_id)
            elif isinstance(article_id, str):
                return None  # Invalid ID format for database
            else:
                id_value = article_id

            query = select(News).where(News.id == id_value)
            result = await self.db.execute(query)
            article = result.scalar_one_or_none()

            return self._to_response(article) if article else None

        except SQLAlchemyError as e:
            logger.error(f"Database error getting article by ID: {str(e)}")
            return None

    async def get_by_url(self, url: str) -> Optional[NewsResponse]:
        """Get a news article by URL."""
        try:
            query = select(News).where(News.link == url)
            result = await self.db.execute(query)
            article = result.scalar_one_or_none()

            return self._to_response(article) if article else None

        except SQLAlchemyError as e:
            logger.error(f"Database error getting article by URL: {str(e)}")
            return None

    async def list(
        self, page: int = 1, per_page: int = 10, source: Optional[str] = None
    ) -> List[NewsResponse]:
        """Get paginated list of news articles."""
        try:
            query = select(News)

            if source:
                query = query.where(News.source == source)

            query = query.order_by(News.created_at.desc())
            query = query.offset((page - 1) * per_page).limit(per_page)

            result = await self.db.execute(query)
            articles = result.scalars().all()

            return [self._to_response(article) for article in articles]

        except SQLAlchemyError as e:
            logger.error(f"Database error listing articles: {str(e)}")
            return []

    async def search(
        self,
        query: str,
        page: int = 1,
        per_page: int = 10,
        source: Optional[str] = None,
    ) -> List[NewsResponse]:
        """Search news articles by query."""
        try:
            search_query = select(News).where(
                or_(
                    News.headline.ilike(f"%{query}%"),
                    (
                        News.summary.ilike(f"%{query}%")
                        if hasattr(News, "summary")
                        else False
                    ),
                )
            )

            if source:
                search_query = search_query.where(News.source == source)

            search_query = search_query.order_by(News.created_at.desc())
            search_query = search_query.offset((page - 1) * per_page).limit(per_page)

            result = await self.db.execute(search_query)
            articles = result.scalars().all()

            return [self._to_response(article) for article in articles]

        except SQLAlchemyError as e:
            logger.error(f"Database error searching articles: {str(e)}")
            return []

    async def count(self, source: Optional[str] = None) -> int:
        """Get total count of articles."""
        try:
            query = select(func.count(News.id))
            if source:
                query = query.where(News.source == source)

            result = await self.db.execute(query)
            return result.scalar() or 0

        except SQLAlchemyError as e:
            logger.error(f"Database error counting articles: {str(e)}")
            return 0

    async def delete(self, article_id: str) -> bool:
        """Delete a news article."""
        try:
            # Handle both string and int IDs
            id_value: Union[int, str]
            if isinstance(article_id, str) and article_id.isdigit():
                id_value = int(article_id)
            elif isinstance(article_id, str):
                return False  # Invalid ID format
            else:
                id_value = article_id

            query = select(News).where(News.id == id_value)
            result = await self.db.execute(query)
            article = result.scalar_one_or_none()

            if article:
                await self.db.delete(article)
                await self.db.commit()
                logger.info(f"Deleted article from database: {id_value}")
                return True

            return False

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error deleting article: {str(e)}")
            return False

    async def update(
        self, article_id: str, updates: Dict[str, Any]
    ) -> Optional[NewsResponse]:
        """Update a news article."""
        try:
            # Handle both string and int IDs
            id_value: Union[int, str]
            if isinstance(article_id, str) and article_id.isdigit():
                id_value = int(article_id)
            elif isinstance(article_id, str):
                return None  # Invalid ID format
            else:
                id_value = article_id

            query = select(News).where(News.id == id_value)
            result = await self.db.execute(query)
            article = result.scalar_one_or_none()

            if not article:
                return None

            # Update fields
            for field, value in updates.items():
                if hasattr(article, field):
                    setattr(article, field, value)

            # Update timestamp
            article.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(article)

            logger.info(f"Updated article in database: {id_value}")
            return self._to_response(article)

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error updating article: {str(e)}")
            return None

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the data source."""
        try:
            # Test database connection
            await self.db.execute(select(1))

            # Get basic stats
            total_count = await self.count()

            return {
                "status": "healthy",
                "type": "database",
                "article_count": total_count,
                "connection": "active",
            }

        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "type": "database",
                "error": str(e),
                "connection": "failed",
            }

    async def cleanup(self):
        """Cleanup resources."""
        try:
            if self.db:
                await self.db.close()
            logger.info("Cleaned up DatabaseNewsRepository")
        except Exception as e:
            logger.error(f"Error cleaning up database repository: {str(e)}")

    def _to_response(self, article: News) -> NewsResponse:
        """Convert database model to response model."""
        return NewsResponse(
            id=str(article.id),
            headline=article.headline,
            link=article.link,
            source=article.source,
            created_at=article.created_at,
            summary=getattr(article, "summary", None),
        )

    # Additional database-specific methods
    async def bulk_create(self, articles: List[NewsCreate]) -> List[NewsResponse]:
        """Bulk create articles."""
        try:
            created_articles = []

            for article_data in articles:
                try:
                    # Check if exists
                    existing = await self.get_by_url(str(article_data.link))
                    if existing:
                        created_articles.append(existing)
                        continue

                    # Create new
                    db_article = News(
                        headline=article_data.headline,
                        link=str(article_data.link),
                        source=article_data.source,
                        created_at=datetime.utcnow(),
                    )
                    self.db.add(db_article)
                    created_articles.append(self._to_response(db_article))

                except Exception as e:
                    logger.error(f"Failed to prepare article for bulk create: {str(e)}")
                    continue

            if created_articles:
                await self.db.commit()
                logger.info(f"Bulk created {len(created_articles)} articles")

            return created_articles

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error in bulk create: {str(e)}")
            return []

    async def get_sources(self) -> List[str]:
        """Get list of unique sources."""
        try:
            query = select(News.source).distinct()
            result = await self.db.execute(query)
            sources = result.scalars().all()
            return list(sources)

        except SQLAlchemyError as e:
            logger.error(f"Database error getting sources: {str(e)}")
            return []
