from enum import Enum
from typing import Dict, Type, Optional
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import NewsRepository
from app.repositories.memory import InMemoryNewsRepository
from app.repositories.database import DatabaseNewsRepository
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DataSourceType(str, Enum):
    """Enumeration of supported data source types."""
    MEMORY = "memory"
    DATABASE = "database"
    REDIS = "redis"          # Future implementation
    ELASTICSEARCH = "elasticsearch"  # Future implementation
    MONGODB = "mongodb"      # Future implementation
    FILE = "file"           # Future implementation


class NewsRepositoryFactory:
    """Factory for creating news repository instances."""
    
    _repositories: Dict[DataSourceType, Type[NewsRepository]] = {
        DataSourceType.MEMORY: InMemoryNewsRepository,
        DataSourceType.DATABASE: DatabaseNewsRepository,
        # Future repositories can be registered here
    }
    
    _instances: Dict[str, NewsRepository] = {}
    
    @classmethod
    def register_repository(
        cls, 
        data_source_type: DataSourceType, 
        repository_class: Type[NewsRepository]
    ):
        """Register a new repository implementation."""
        cls._repositories[data_source_type] = repository_class
        logger.info(f"Registered repository for {data_source_type}: {repository_class.__name__}")
    
    @classmethod
    def get_available_sources(cls) -> Dict[str, str]:
        """Get available data source types and their descriptions."""
        descriptions = {
            DataSourceType.MEMORY: "In-memory storage (volatile, fast access)",
            DataSourceType.DATABASE: "SQL database storage (persistent, ACID compliant)",
            DataSourceType.REDIS: "Redis cache storage (fast, persistent cache)",
            DataSourceType.ELASTICSEARCH: "Elasticsearch storage (full-text search)",
            DataSourceType.MONGODB: "MongoDB storage (document-based, flexible schema)",
            DataSourceType.FILE: "File-based storage (simple persistence)"
        }
        
        return {
            source.value: descriptions.get(source, "Custom repository implementation")
            for source in cls._repositories.keys()
        }
    
    @classmethod
    async def create_repository(
        cls,
        data_source_type: DataSourceType,
        db_session: Optional[AsyncSession] = None,
        **kwargs
    ) -> NewsRepository:
        """Create a repository instance based on data source type."""
        
        if data_source_type not in cls._repositories:
            available = list(cls._repositories.keys())
            raise ValueError(
                f"Unsupported data source type: {data_source_type}. "
                f"Available types: {available}"
            )
        
        repository_class = cls._repositories[data_source_type]
        
        # Create instance based on type
        if data_source_type == DataSourceType.MEMORY:
            repository = repository_class()
            
        elif data_source_type == DataSourceType.DATABASE:
            if db_session is None:
                raise ValueError("Database session is required for database repository")
            repository = repository_class(db_session)
            
        else:
            # For future implementations, pass kwargs
            repository = repository_class(**kwargs)
        
        logger.info(f"Created repository: {repository_class.__name__}")
        return repository
    
    @classmethod
    async def create_from_config(
        cls, 
        db_session: Optional[AsyncSession] = None
    ) -> NewsRepository:
        """Create repository based on application configuration."""
        settings = get_settings()
        
        # Determine data source from configuration
        # You can add a DATA_SOURCE setting to your configuration
        data_source = getattr(settings, 'data_source', 'database')
        
        # Map string to enum
        try:
            data_source_type = DataSourceType(data_source.lower())
        except ValueError:
            logger.warning(f"Invalid data source '{data_source}', falling back to database")
            data_source_type = DataSourceType.DATABASE
        
        return await cls.create_repository(data_source_type, db_session)
    
    @classmethod
    async def get_singleton_repository(
        cls,
        data_source_type: DataSourceType,
        db_session: Optional[AsyncSession] = None,
        **kwargs
    ) -> NewsRepository:
        """Get or create a singleton repository instance."""
        instance_key = f"{data_source_type.value}_{id(db_session) if db_session else 'none'}"
        
        if instance_key not in cls._instances:
            cls._instances[instance_key] = await cls.create_repository(
                data_source_type, db_session, **kwargs
            )
        
        return cls._instances[instance_key]
    
    @classmethod
    async def cleanup_all_instances(cls):
        """Cleanup all repository instances."""
        for instance in cls._instances.values():
            try:
                await instance.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up repository instance: {str(e)}")
        
        cls._instances.clear()
        logger.info("Cleaned up all repository instances")


# Convenience functions for common use cases
async def create_memory_repository() -> NewsRepository:
    """Create an in-memory repository."""
    return await NewsRepositoryFactory.create_repository(DataSourceType.MEMORY)


async def create_database_repository(db_session: AsyncSession) -> NewsRepository:
    """Create a database repository."""
    return await NewsRepositoryFactory.create_repository(
        DataSourceType.DATABASE, 
        db_session=db_session
    )


@lru_cache()
def get_repository_factory() -> NewsRepositoryFactory:
    """Get the repository factory singleton."""
    return NewsRepositoryFactory()


# Example of how to add new data sources:
"""
class RedisNewsRepository(NewsRepository):
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        # Initialize Redis connection
    
    async def create(self, news_data: NewsCreate) -> NewsResponse:
        # Redis implementation
        pass
    
    # ... implement other methods

# Register the new repository
NewsRepositoryFactory.register_repository(
    DataSourceType.REDIS, 
    RedisNewsRepository
)

# Use it
redis_repo = await NewsRepositoryFactory.create_repository(
    DataSourceType.REDIS,
    redis_url="redis://localhost:6379"
)
"""
