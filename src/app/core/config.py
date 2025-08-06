import os
from functools import lru_cache
from typing import List

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "News Aggregator"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Security
    secret_key: str
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # API Keys
    news_api_key: str
    reddit_user_agent: str = "NewsAggregator/1.0"
    
    # Database
    database_url: str = "sqlite:///./news.db"
    
    # External APIs
    news_api_base_url: str = "https://newsapi.org/v2"
    reddit_api_base_url: str = "https://www.reddit.com"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Cache
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 300
    
    # Data Source Configuration
    data_source: str = "database"  # Options: memory, database, redis, etc.
    
    # HTTP Client
    request_timeout: int = 30
    max_retries: int = 3
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('allowed_hosts', pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
