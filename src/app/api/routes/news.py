from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import NewsServiceDep, NewsRepositoryDep
from app.services.news_providers import NewsAggregatorService
from app.repositories.factory import NewsRepositoryFactory, DataSourceType
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
    news_service: NewsServiceDep = Depends()
):
    """Get paginated news articles."""
    try:
        return await news_service.get_articles(page, per_page, source)
        
    except Exception as e:
        logger.error(f"Error getting news: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve news articles"
        )


@router.get(
    "/search",
    response_model=List[NewsResponse],
    summary="Search news articles",
    description="Search news articles by headline content"
)
async def search_news(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    source: str = Query(None, description="Filter by news source"),
    news_service: NewsServiceDep = Depends()
):
    """Search news articles by headline."""
    try:
        articles = await news_service.search_articles(q, page, per_page, source)
        return articles
        
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
    news_service: NewsServiceDep = Depends()
):
    """Fetch fresh articles from news sources."""
    try:
        aggregator = NewsAggregatorService()
        
        # Fetch articles from sources
        if source:
            fresh_articles = await aggregator.fetch_from_source(source)
        else:
            fresh_articles = await aggregator.fetch_all_articles()
        
        if not fresh_articles:
            logger.warning("No articles fetched from sources")
            return []
        
        # Store articles using the service
        stored_articles = await news_service.bulk_create_articles(fresh_articles)
        
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
    description="Get list of available news sources and data source types"
)
async def get_news_sources():
    """Get available news sources and data source information."""
    # News provider sources
    news_sources = [
        {"name": "reddit", "description": "Reddit /r/news"},
        {"name": "newsapi", "description": "NewsAPI.org"}
    ]
    
    # Available data source types
    data_sources = NewsRepositoryFactory.get_available_sources()
    
    return {
        "news_sources": news_sources,
        "data_source_types": data_sources
    }


@router.get(
    "/{article_id}",
    response_model=NewsResponse,
    summary="Get article by ID",
    description="Retrieve a specific article by its ID"
)
async def get_article(
    article_id: str,
    news_service: NewsServiceDep = Depends()
):
    """Get article by ID."""
    article = await news_service.get_article_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    return article


@router.put(
    "/{article_id}",
    response_model=NewsResponse,
    summary="Update article",
    description="Update an existing article"
)
async def update_article(
    article_id: str,
    updates: dict,
    news_service: NewsServiceDep = Depends()
):
    """Update an article."""
    article = await news_service.update_article(article_id, updates)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    return article


@router.delete(
    "/{article_id}",
    summary="Delete article",
    description="Delete an article by ID"
)
async def delete_article(
    article_id: str,
    news_service: NewsServiceDep = Depends()
):
    """Delete an article."""
    success = await news_service.delete_article(article_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    return {"message": "Article deleted successfully"}


@router.get(
    "/admin/health",
    summary="Repository health check",
    description="Check the health of the current data source"
)
async def repository_health(
    news_service: NewsServiceDep = Depends()
):
    """Check repository health."""
    return await news_service.health_check()


@router.post(
    "/admin/switch-datasource",
    summary="Switch data source (Development only)",
    description="Switch between different data sources. Use with caution!"
)
async def switch_data_source(
    data_source_type: str,
    repository: NewsRepositoryDep = Depends()
):
    """Switch data source type (for development/testing)."""
    try:
        available_sources = NewsRepositoryFactory.get_available_sources()
        
        if data_source_type not in available_sources:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data source. Available: {list(available_sources.keys())}"
            )
        
        # This is a simplified example - in production, you'd want more sophisticated
        # data source switching with proper migration/sync
        return {
            "message": f"Data source switching to {data_source_type} requested",
            "note": "Restart application with DATA_SOURCE={data_source_type} to apply",
            "current_repository": type(repository).__name__
        }
        
    except Exception as e:
        logger.error(f"Error switching data source: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to switch data source"
        )
