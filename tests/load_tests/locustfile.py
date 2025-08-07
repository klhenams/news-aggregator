"""Load testing script for the News Aggregator API using Locust."""

from locust import HttpUser, between, task


class NewsAggregatorUser(HttpUser):
    """Simulated user for load testing the News Aggregator API."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Called when a user starts."""
        # You can add authentication here if needed
        pass

    @task(10)
    def get_health(self):
        """Test health endpoint (most frequent)."""
        self.client.get("/health")

    @task(5)
    def get_articles(self):
        """Test getting articles."""
        self.client.get("/api/v1/news/articles")

    @task(3)
    def get_articles_with_pagination(self):
        """Test paginated articles."""
        self.client.get("/api/v1/news/articles?page=1&per_page=10")

    @task(2)
    def search_articles(self):
        """Test searching articles."""
        search_terms = ["technology", "python", "api", "news"]
        for term in search_terms:
            self.client.get(f"/api/v1/news/search?query={term}")

    @task(1)
    def get_specific_source(self):
        """Test filtering by source."""
        sources = ["techcrunch", "reddit", "hackernews"]
        for source in sources:
            self.client.get(f"/api/v1/news/articles?source={source}")

    @task(1)
    def create_article(self):
        """Test creating an article."""
        article_data = {
            "headline": "Test Article from Load Test",
            "link": f"https://example.com/test-{self.environment.runner.user_count}",
            "source": "load-test",
        }
        self.client.post("/api/v1/news/articles", json=article_data)


class AdminUser(HttpUser):
    """Admin user for testing administrative endpoints."""

    wait_time = between(5, 10)  # Admins make fewer requests
    weight = 1  # Only 1 admin for every 10 regular users

    @task
    def get_system_health(self):
        """Test system health endpoint."""
        self.client.get("/health/detailed")

    @task
    def get_metrics(self):
        """Test metrics endpoint if available."""
        self.client.get("/metrics")
