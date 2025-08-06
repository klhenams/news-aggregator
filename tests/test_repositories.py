import asyncio
import pytest
from typing import List

from app.repositories.memory import InMemoryNewsRepository
from app.repositories.factory import NewsRepositoryFactory, DataSourceType
from app.schemas import NewsCreate


class TestInMemoryRepository:
    """Test cases for in-memory news repository."""
    
    @pytest.fixture
    async def repository(self):
        """Create a fresh in-memory repository for each test."""
        repo = InMemoryNewsRepository()
        yield repo
        await repo.cleanup()
    
    @pytest.fixture
    def sample_news(self):
        """Sample news data for testing."""
        return [
            NewsCreate(
                headline="Test Article 1",
                link="https://example.com/article1",
                source="test"
            ),
            NewsCreate(
                headline="Test Article 2", 
                link="https://example.com/article2",
                source="test"
            ),
            NewsCreate(
                headline="Different Source Article",
                link="https://example.com/article3", 
                source="other"
            )
        ]
    
    @pytest.mark.asyncio
    async def test_create_article(self, repository, sample_news):
        """Test creating a single article."""
        article_data = sample_news[0]
        result = await repository.create(article_data)
        
        assert result.headline == article_data.headline
        assert str(result.link) == str(article_data.link)
        assert result.source == article_data.source
        assert result.id is not None
        assert result.created_at is not None
    
    @pytest.mark.asyncio
    async def test_create_duplicate_article(self, repository, sample_news):
        """Test creating duplicate article returns existing one."""
        article_data = sample_news[0]
        
        # Create first time
        result1 = await repository.create(article_data)
        
        # Create duplicate
        result2 = await repository.create(article_data)
        
        assert result1.id == result2.id
        assert result1.headline == result2.headline
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, repository, sample_news):
        """Test getting article by ID."""
        article_data = sample_news[0]
        created = await repository.create(article_data)
        
        result = await repository.get_by_id(created.id)
        
        assert result is not None
        assert result.id == created.id
        assert result.headline == created.headline
    
    @pytest.mark.asyncio
    async def test_get_by_url(self, repository, sample_news):
        """Test getting article by URL."""
        article_data = sample_news[0]
        created = await repository.create(article_data)
        
        result = await repository.get_by_url(str(article_data.link))
        
        assert result is not None
        assert result.id == created.id
        assert str(result.link) == str(article_data.link)
    
    @pytest.mark.asyncio
    async def test_list_articles(self, repository, sample_news):
        """Test listing articles with pagination."""
        # Create multiple articles
        for article_data in sample_news:
            await repository.create(article_data)
        
        # Test basic listing
        results = await repository.list(page=1, per_page=10)
        assert len(results) == 3
        
        # Test pagination
        results = await repository.list(page=1, per_page=2)
        assert len(results) == 2
        
        # Test source filtering
        results = await repository.list(source="test")
        assert len(results) == 2
        assert all(r.source == "test" for r in results)
    
    @pytest.mark.asyncio
    async def test_search_articles(self, repository, sample_news):
        """Test searching articles."""
        # Create test articles
        for article_data in sample_news:
            await repository.create(article_data)
        
        # Search by headline content
        results = await repository.search("Test Article")
        assert len(results) == 2
        
        # Search with no results
        results = await repository.search("Nonexistent")
        assert len(results) == 0
        
        # Search with source filter
        results = await repository.search("Article", source="test")
        assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_count_articles(self, repository, sample_news):
        """Test counting articles."""
        # Initially empty
        count = await repository.count()
        assert count == 0
        
        # Add articles
        for article_data in sample_news:
            await repository.create(article_data)
        
        # Count all
        count = await repository.count()
        assert count == 3
        
        # Count by source
        count = await repository.count(source="test")
        assert count == 2
    
    @pytest.mark.asyncio
    async def test_delete_article(self, repository, sample_news):
        """Test deleting article."""
        article_data = sample_news[0]
        created = await repository.create(article_data)
        
        # Delete article
        success = await repository.delete(created.id)
        assert success is True
        
        # Verify deleted
        result = await repository.get_by_id(created.id)
        assert result is None
        
        # Delete non-existent
        success = await repository.delete("nonexistent")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_update_article(self, repository, sample_news):
        """Test updating article."""
        article_data = sample_news[0]
        created = await repository.create(article_data)
        
        # Update article
        updates = {"headline": "Updated Headline", "source": "updated"}
        result = await repository.update(created.id, updates)
        
        assert result is not None
        assert result.headline == "Updated Headline"
        assert result.source == "updated"
        assert result.id == created.id
    
    @pytest.mark.asyncio
    async def test_health_check(self, repository):
        """Test repository health check."""
        health = await repository.health_check()
        
        assert health["status"] == "healthy"
        assert health["type"] == "in_memory"
        assert "article_count" in health
    
    @pytest.mark.asyncio
    async def test_bulk_create(self, repository, sample_news):
        """Test bulk creating articles."""
        results = await repository.bulk_create(sample_news)
        
        assert len(results) == 3
        assert all(r.id is not None for r in results)
        
        # Verify they're all stored
        count = await repository.count()
        assert count == 3


class TestRepositoryFactory:
    """Test cases for repository factory."""
    
    @pytest.mark.asyncio
    async def test_create_memory_repository(self):
        """Test creating memory repository via factory."""
        repo = await NewsRepositoryFactory.create_repository(DataSourceType.MEMORY)
        
        assert isinstance(repo, InMemoryNewsRepository)
        await repo.cleanup()
    
    @pytest.mark.asyncio 
    async def test_get_available_sources(self):
        """Test getting available data sources."""
        sources = NewsRepositoryFactory.get_available_sources()
        
        assert isinstance(sources, dict)
        assert "memory" in sources
        assert "database" in sources
    
    @pytest.mark.asyncio
    async def test_singleton_repository(self):
        """Test singleton repository creation."""
        repo1 = await NewsRepositoryFactory.get_singleton_repository(DataSourceType.MEMORY)
        repo2 = await NewsRepositoryFactory.get_singleton_repository(DataSourceType.MEMORY)
        
        # Should be the same instance
        assert repo1 is repo2
        
        await NewsRepositoryFactory.cleanup_all_instances()
    
    def test_register_custom_repository(self):
        """Test registering custom repository type."""
        class CustomRepository(InMemoryNewsRepository):
            pass
        
        # Register custom repository
        NewsRepositoryFactory.register_repository(
            DataSourceType.REDIS,  # Using future type for test
            CustomRepository
        )
        
        # Verify it's registered
        sources = NewsRepositoryFactory.get_available_sources()
        assert "redis" in sources
