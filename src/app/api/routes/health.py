from datetime import datetime

from fastapi import APIRouter, Depends

from app.core.config import get_settings
from app.dependencies import NewsServiceDep
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health of the application and its dependencies",
)
async def health_check(news_service: NewsServiceDep = Depends()):
    """Health check endpoint."""
    # Get service health (includes repository health)
    service_health = await news_service.health_check()

    dependencies = {
        "news_service": service_health,
        "data_source": settings.data_source,
        "reddit_api": "not_checked",  # Could add actual check
        "news_api": "not_checked",  # Could add actual check
    }

    return HealthResponse(
        status="healthy", version=settings.app_version, dependencies=dependencies
    )


@router.get(
    "/ready",
    summary="Readiness Check",
    description="Check if the application is ready to serve traffic",
)
async def readiness_check():
    """Readiness check endpoint."""
    return {"status": "ready", "timestamp": datetime.utcnow()}
