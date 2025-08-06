from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status

from app.repositories.base import NewsRepository
from app.schemas import NewsCreate, NewsResponse, NewsListResponse
from app.core.logging import get_logger

logger = get_logger(__name__)


class NewsService:
    """Service layer for news operations with flexible repository support."""
    
    def __init__(self, repository: NewsRepository):
        self.repository = repository
    
    async def create_article(self, article_data: NewsCreate) -> NewsResponse:
        """Create a new news article."""
        try:
            article = await self.repository.create(article_data)
            logger.info(f"Created article: {article.id}")
            return article
            
        except Exception as e:
            logger.error(f"Error creating article: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create article"
            )
    
    async def get_articles(
        self, 
        page: int = 1, 
        per_page: int = 10,
        source: Optional[str] = None
    ) -> NewsListResponse:
        """Get paginated list of articles."""
        try:
            articles = await self.repository.list(page, per_page, source)
            total = await self.repository.count(source)
            
            return NewsListResponse(
                articles=articles,
                total=total,
                page=page,
                per_page=per_page
            )
            
        except Exception as e:
            logger.error(f"Error fetching articles: {str(e)}")
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
            articles = await self.repository.search(query, page, per_page, source)
            return articles
            
        except Exception as e:
            logger.error(f"Error searching articles: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search articles"
            )
    
    async def get_article_by_id(self, article_id: str) -> Optional[NewsResponse]:
        """Get article by ID."""
        try:
            return await self.repository.get_by_id(article_id)
        except Exception as e:
            logger.error(f"Error getting article by ID: {str(e)}")
            return None
    
    async def get_article_by_url(self, url: str) -> Optional[NewsResponse]:
        """Get article by URL."""
        try:
            return await self.repository.get_by_url(url)
        except Exception as e:
            logger.error(f"Error getting article by URL: {str(e)}")
            return None
    
    async def update_article(self, article_id: str, updates: dict) -> Optional[NewsResponse]:
        """Update an article."""
        try:
            return await self.repository.update(article_id, updates)
        except Exception as e:
            logger.error(f"Error updating article: {str(e)}")
            return None
    
    async def delete_article(self, article_id: str) -> bool:
        """Delete an article."""
        try:
            return await self.repository.delete(article_id)
        except Exception as e:
            logger.error(f"Error deleting article: {str(e)}")
            return False
    
    async def get_article_count(self, source: Optional[str] = None) -> int:
        """Get total count of articles."""
        try:
            return await self.repository.count(source)
        except Exception as e:
            logger.error(f"Error counting articles: {str(e)}")
            return 0
    
    async def bulk_create_articles(self, articles: List[NewsCreate]) -> List[NewsResponse]:
        """Bulk create articles."""
        try:
            # Check if repository supports bulk create
            if hasattr(self.repository, 'bulk_create'):
                return await self.repository.bulk_create(articles)
            else:
                # Fallback to individual creates
                created_articles = []
                for article_data in articles:
                    try:
                        article = await self.repository.create(article_data)
                        created_articles.append(article)
                    except Exception as e:
                        logger.error(f"Failed to create article in bulk: {str(e)}")
                        continue
                return created_articles
                
        except Exception as e:
            logger.error(f"Error in bulk create: {str(e)}")
            return []
    
    async def health_check(self) -> dict:
        """Check the health of the service and its repository."""
        try:
            repo_health = await self.repository.health_check()
            return {
                "service": "healthy",
                "repository": repo_health
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "service": "unhealthy",
                "error": str(e),
                "repository": {"status": "unknown"}
            }
