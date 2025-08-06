from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.factory import NewsRepositoryFactory, DataSourceType
from app.repositories.base import NewsRepository
from app.services.news_service import NewsService
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def get_news_repository(
    db: AsyncSession = Depends(get_db)
) -> NewsRepository:
    """
    Dependency for getting news repository based on configuration.
    
    This allows switching between different data sources via configuration
    without changing application code.
    """
    settings = get_settings()
    
    try:
        # Create repository based on configuration
        if settings.data_source.lower() == "memory":
            # For memory, we use a singleton to maintain state across requests
            repository = await NewsRepositoryFactory.get_singleton_repository(
                DataSourceType.MEMORY
            )
        else:
            # For database, create per-request to use the session
            repository = await NewsRepositoryFactory.create_repository(
                DataSourceType.DATABASE,
                db_session=db
            )
        
        return repository
        
    except Exception as e:
        logger.error(f"Failed to create repository: {str(e)}")
        # Fallback to memory repository
        logger.warning("Falling back to memory repository")
        return await NewsRepositoryFactory.create_repository(DataSourceType.MEMORY)


async def get_news_service(
    repository: NewsRepository = Depends(get_news_repository)
) -> NewsService:
    """Dependency for getting news service with configured repository."""
    return NewsService(repository)


# Specific repository dependencies for when you need a particular type
async def get_memory_repository() -> NewsRepository:
    """Get in-memory repository dependency."""
    return await NewsRepositoryFactory.get_singleton_repository(DataSourceType.MEMORY)


async def get_database_repository(
    db: AsyncSession = Depends(get_db)
) -> NewsRepository:
    """Get database repository dependency."""
    return await NewsRepositoryFactory.create_repository(
        DataSourceType.DATABASE,
        db_session=db
    )


# Convenience type annotations
NewsRepositoryDep = Annotated[NewsRepository, Depends(get_news_repository)]
NewsServiceDep = Annotated[NewsService, Depends(get_news_service)]
MemoryRepositoryDep = Annotated[NewsRepository, Depends(get_memory_repository)]
DatabaseRepositoryDep = Annotated[NewsRepository, Depends(get_database_repository)]
