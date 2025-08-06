"""
Example usage of the flexible data source factory pattern.

This demonstrates how to switch between different data sources
and how to extend the system with new repository implementations.
"""

import asyncio
from typing import List

from app.repositories.factory import NewsRepositoryFactory, DataSourceType
from app.repositories.base import NewsRepository
from app.services.news_service import NewsService
from app.schemas import NewsCreate, NewsResponse
from app.core.config import get_settings


async def example_memory_usage():
    """Example of using in-memory repository."""
    print("=== In-Memory Repository Example ===")
    
    # Create memory repository
    repo = await NewsRepositoryFactory.create_repository(DataSourceType.MEMORY)
    service = NewsService(repo)
    
    # Create some sample articles
    articles_data = [
        NewsCreate(
            headline="Breaking: Memory Storage Works!",
            link="https://example.com/memory1",
            source="test"
        ),
        NewsCreate(
            headline="Fast In-Memory Access Confirmed",
            link="https://example.com/memory2", 
            source="test"
        )
    ]
    
    # Add articles
    for article_data in articles_data:
        article = await service.create_article(article_data)
        print(f"Created: {article.headline} (ID: {article.id})")
    
    # List articles
    articles_list = await service.get_articles(page=1, per_page=10)
    print(f"Total articles: {articles_list.total}")
    
    # Search articles
    search_results = await service.search_articles("Memory")
    print(f"Search results for 'Memory': {len(search_results)} found")
    
    # Health check
    health = await service.health_check()
    print(f"Repository health: {health}")
    
    await repo.cleanup()


async def example_factory_switching():
    """Example of switching between different data sources."""
    print("\n=== Data Source Switching Example ===")
    
    # Get available sources
    sources = NewsRepositoryFactory.get_available_sources()
    print("Available data sources:")
    for source_type, description in sources.items():
        print(f"  - {source_type}: {description}")
    
    # Create repositories for different sources
    repositories = {}
    
    # Memory repository
    memory_repo = await NewsRepositoryFactory.create_repository(DataSourceType.MEMORY)
    repositories["memory"] = memory_repo
    
    # You could also create database repository (if DB is available)
    # db_session = get_db_session()  # Your DB session logic
    # db_repo = await NewsRepositoryFactory.create_repository(
    #     DataSourceType.DATABASE, 
    #     db_session=db_session
    # )
    # repositories["database"] = db_repo
    
    # Test with different repositories
    sample_article = NewsCreate(
        headline="Multi-Source Article",
        link="https://example.com/multi",
        source="demo"
    )
    
    for repo_name, repo in repositories.items():
        print(f"\nTesting with {repo_name} repository:")
        service = NewsService(repo)
        
        # Create article
        article = await service.create_article(sample_article)
        print(f"  Created article: {article.id}")
        
        # Get health
        health = await service.health_check()
        print(f"  Health: {health['service']}")
        
        await repo.cleanup()


async def example_custom_repository():
    """Example of implementing and registering a custom repository."""
    print("\n=== Custom Repository Example ===")
    
    # Example custom repository (Redis-like behavior but in-memory)
    class CacheNewsRepository(NewsRepository):
        """Example cache-based repository implementation."""
        
        def __init__(self, ttl_seconds: int = 3600):
            self.ttl_seconds = ttl_seconds
            self._cache = {}
            self._access_count = 0
            print(f"Initialized cache repository with TTL: {ttl_seconds}s")
        
        async def create(self, news_data: NewsCreate) -> NewsResponse:
            self._access_count += 1
            article_id = f"cache_{self._access_count}"
            
            article = NewsResponse(
                id=article_id,
                headline=news_data.headline,
                link=news_data.link,
                source=news_data.source
            )
            
            self._cache[article_id] = article
            return article
        
        async def get_by_id(self, article_id: str) -> NewsResponse:
            return self._cache.get(article_id)
        
        async def get_by_url(self, url: str) -> NewsResponse:
            for article in self._cache.values():
                if str(article.link) == url:
                    return article
            return None
        
        async def list(self, page: int = 1, per_page: int = 10, source: str = None) -> List[NewsResponse]:
            articles = list(self._cache.values())
            if source:
                articles = [a for a in articles if a.source == source]
            
            start = (page - 1) * per_page
            end = start + per_page
            return articles[start:end]
        
        async def search(self, query: str, page: int = 1, per_page: int = 10, source: str = None) -> List[NewsResponse]:
            articles = [a for a in self._cache.values() if query.lower() in a.headline.lower()]
            if source:
                articles = [a for a in articles if a.source == source]
            
            start = (page - 1) * per_page
            end = start + per_page
            return articles[start:end]
        
        async def count(self, source: str = None) -> int:
            if source:
                return sum(1 for a in self._cache.values() if a.source == source)
            return len(self._cache)
        
        async def delete(self, article_id: str) -> bool:
            if article_id in self._cache:
                del self._cache[article_id]
                return True
            return False
        
        async def update(self, article_id: str, updates: dict) -> NewsResponse:
            article = self._cache.get(article_id)
            if article:
                # Create updated article
                updated_data = article.dict()
                updated_data.update(updates)
                updated_article = NewsResponse(**updated_data)
                self._cache[article_id] = updated_article
                return updated_article
            return None
        
        async def health_check(self) -> dict:
            return {
                "status": "healthy",
                "type": "cache",
                "article_count": len(self._cache),
                "access_count": self._access_count,
                "ttl_seconds": self.ttl_seconds
            }
        
        async def cleanup(self):
            self._cache.clear()
            print("Cache repository cleaned up")
    
    # Register the custom repository
    NewsRepositoryFactory.register_repository(
        DataSourceType.REDIS,  # Using REDIS enum for our cache example
        CacheNewsRepository
    )
    
    # Create and use the custom repository
    cache_repo = await NewsRepositoryFactory.create_repository(
        DataSourceType.REDIS,
        ttl_seconds=300  # 5 minute TTL
    )
    
    service = NewsService(cache_repo)
    
    # Test the custom repository
    article_data = NewsCreate(
        headline="Cached Article Example",
        link="https://example.com/cached",
        source="cache_demo"
    )
    
    article = await service.create_article(article_data)
    print(f"Created cached article: {article.id}")
    
    health = await service.health_check()
    print(f"Cache repository health: {health}")
    
    await cache_repo.cleanup()


async def example_configuration_based():
    """Example of using configuration-based repository creation."""
    print("\n=== Configuration-Based Example ===")
    
    # This would use your app's configuration to determine the repository type
    # You can set DATA_SOURCE=memory in your environment to test this
    
    try:
        repo = await NewsRepositoryFactory.create_from_config()
        service = NewsService(repo)
        
        print(f"Created repository from config: {type(repo).__name__}")
        
        health = await service.health_check()
        print(f"Health check: {health}")
        
        await repo.cleanup()
        
    except Exception as e:
        print(f"Configuration-based creation failed (expected if no DB): {e}")


async def main():
    """Run all examples."""
    print("News Aggregator - Flexible Data Source Examples")
    print("=" * 50)
    
    await example_memory_usage()
    await example_factory_switching()
    await example_custom_repository()
    await example_configuration_based()
    
    print("\n=== Examples Complete ===")
    print("Key benefits of this approach:")
    print("1. Easy switching between data sources via configuration")
    print("2. Consistent interface across all repository types")
    print("3. Simple to add new data source implementations")
    print("4. Testable with different backends")
    print("5. Production flexibility without code changes")


if __name__ == "__main__":
    asyncio.run(main())
