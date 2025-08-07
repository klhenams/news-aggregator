"""Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class NewsBase(BaseModel):
    """Base news model with common fields."""

    headline: str = Field(
        ..., min_length=1, max_length=500, description="News headline"
    )
    link: HttpUrl = Field(..., description="URL to the full article")
    source: str = Field(
        ..., min_length=1, max_length=100, description="News source name"
    )


class NewsCreate(NewsBase):
    """Model for creating news articles."""

    pass


class NewsResponse(NewsBase):
    """Model for news API responses."""

    id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    summary: Optional[str] = Field(None, max_length=1000, description="Article summary")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class NewsListResponse(BaseModel):
    """Model for paginated news list responses."""

    articles: List[NewsResponse]
    total: int
    page: int = 1
    per_page: int = 10


class NewsSearchRequest(BaseModel):
    """Model for news search requests."""

    query: str = Field(..., min_length=1, max_length=100)
    source: Optional[str] = Field(None, max_length=50)
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    dependencies: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        from_attributes = True
