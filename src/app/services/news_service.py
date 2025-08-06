from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError

from app.models.news import News
from app.schemas import NewsCreate, NewsResponse
from app.core.logging import get_logger

logger = get_logger(__name__)


class NewsService:
    """Service layer for news operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create_article(self, article_data: NewsCreate) -> NewsResponse:
        """Create a new news article."""
        try:
            # Check if article already exists (by URL)
            existing = await self._get_article_by_url(str(article_data.link))
            if existing:
                logger.warning(f"Article already exists: {article_data.link}")
                return NewsResponse.from_orm(existing)
            
            # Create new article
            db_article = News(
                headline=article_data.headline,
                link=str(article_data.link),
                source=article_data.source,
                created_at=datetime.utcnow()
            )
            
            self.db.add(db_article)
            await self.db.commit()
            await self.db.refresh(db_article)
            
            logger.info(f"Created new article: {db_article.id}")
            return NewsResponse.from_orm(db_article)
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error creating article: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create article"
            )
    
    async def get_articles(
        self, 
        page: int = 1, 
        per_page: int = 10,
        source: Optional[str] = None
    ) -> List[NewsResponse]:
        """Get paginated list of articles."""
        try:
            query = select(News)
            
            if source:
                query = query.where(News.source == source)
                
            query = query.order_by(News.created_at.desc())
            query = query.offset((page - 1) * per_page).limit(per_page)
            
            result = await self.db.execute(query)
            articles = result.scalars().all()
            
            return [NewsResponse.from_orm(article) for article in articles]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching articles: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch articles"
            )
    
    async def search_articles(
        self, 
        query: str, 
        page: int = 1, 
        per_page: int = 10,
        source: Optional[str] = None
    ) -> List[NewsResponse]:
        """Search articles by headline text."""
        try:
            search_query = select(News).where(
                News.headline.ilike(f"%{query}%")
            )
            
            if source:
                search_query = search_query.where(News.source == source)
                
            search_query = search_query.order_by(News.created_at.desc())
            search_query = search_query.offset((page - 1) * per_page).limit(per_page)
            
            result = await self.db.execute(search_query)
            articles = result.scalars().all()
            
            return [NewsResponse.from_orm(article) for article in articles]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error searching articles: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search articles"
            )
    
    async def get_article_count(self, source: Optional[str] = None) -> int:
        """Get total count of articles."""
        try:
            from sqlalchemy import func
            
            query = select(func.count(News.id))
            if source:
                query = query.where(News.source == source)
                
            result = await self.db.execute(query)
            return result.scalar() or 0
            
        except SQLAlchemyError as e:
            logger.error(f"Database error counting articles: {str(e)}")
            return 0
    
    async def _get_article_by_url(self, url: str) -> Optional[News]:
        """Get article by URL (internal method)."""
        try:
            query = select(News).where(News.link == url)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            return None
