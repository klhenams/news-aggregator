from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, engine
from app.schemas import HealthResponse
from app.core.config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get(
    "/health", 
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health of the application and its dependencies"
)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint."""
    dependencies = {}
    
    # Check database connection
    try:
        await db.execute("SELECT 1")
        dependencies["database"] = "healthy"
    except Exception as e:
        dependencies["database"] = f"unhealthy: {str(e)}"
    
    # Check external APIs (simplified)
    dependencies["reddit_api"] = "not_checked"  # Could add actual check
    dependencies["news_api"] = "not_checked"    # Could add actual check
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        dependencies=dependencies
    )


@router.get(
    "/ready",
    summary="Readiness Check",
    description="Check if the application is ready to serve traffic"
)
async def readiness_check():
    """Readiness check endpoint."""
    return {"status": "ready", "timestamp": datetime.utcnow()}
