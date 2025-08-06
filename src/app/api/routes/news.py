from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.news_service import NewsService
from app.services.news_providers import NewsAggregatorService
from app.schemas import (
    NewsResponse, 
    NewsListResponse, 
    NewsSearchRequest,
    ErrorResponse
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/news", tags=["news"])


@router.get(
    "/",
    response_model=NewsListResponse,
    summary="Get news articles",
    description="Retrieve paginated list of news articles with optional source filtering"
)
async def get_news(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    source: str = Query(None, description="Filter by news source"),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated news articles."""
    try:
        news_service = NewsService(db)
        
        # Get articles and total count
        articles = await news_service.get_articles(page, per_page, source)
        total = await news_service.get_article_count(source)
        
        return NewsListResponse(
            articles=articles,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Error getting news: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve news articles"
        )


@router.get(
    "/search",
    response_model=NewsListResponse,
    summary="Search news articles",
    description="Search news articles by headline content"
)
async def search_news(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    source: str = Query(None, description="Filter by news source"),
    db: AsyncSession = Depends(get_db)
):
    """Search news articles by headline."""
    try:
        news_service = NewsService(db)
        articles = await news_service.search_articles(q, page, per_page, source)
        
        # For search, we don't need total count for performance
        return NewsListResponse(
            articles=articles,
            total=len(articles),
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Error searching news: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search news articles"
        )


@router.post(
    "/fetch",
    response_model=List[NewsResponse],
    summary="Fetch fresh articles",
    description="Fetch and store fresh articles from all news sources"
)
async def fetch_news(
    source: str = Query(None, description="Specific source to fetch from"),
    db: AsyncSession = Depends(get_db)
):
    """Fetch fresh articles from news sources."""
    try:
        aggregator = NewsAggregatorService()
        news_service = NewsService(db)
        
        # Fetch articles from sources
        if source:
            fresh_articles = await aggregator.fetch_from_source(source)
        else:
            fresh_articles = await aggregator.fetch_all_articles()
        
        if not fresh_articles:
            logger.warning("No articles fetched from sources")
            return []
        
        # Store articles in database
        stored_articles = []
        for article_data in fresh_articles:
            try:
                stored_article = await news_service.create_article(article_data)
                stored_articles.append(stored_article)
            except Exception as e:
                logger.error(f"Failed to store article: {str(e)}")
                # Continue with other articles
                continue
        
        logger.info(f"Successfully stored {len(stored_articles)} articles")
        return stored_articles
        
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch news articles"
        )


@router.get(
    "/sources",
    summary="Get available news sources",
    description="Get list of available news sources"
)
async def get_news_sources():
    """Get available news sources."""
    return {
        "sources": [
            {"name": "reddit", "description": "Reddit /r/news"},
            {"name": "newsapi", "description": "NewsAPI.org"}
        ]
    }
