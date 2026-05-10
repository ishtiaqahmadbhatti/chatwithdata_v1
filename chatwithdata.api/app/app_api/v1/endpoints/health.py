from fastapi import APIRouter
from app.app_models.schemas import HealthCheckResponse
from app.app_core.config import settings

router = APIRouter()


@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        database={
            "dynamodb_active": settings.dynamodb_active,
            "dynamodb_prefix": settings.dynamodb_table_prefix,
            "aws_region": settings.aws_region,
            "postgres_active": settings.database_active
        }
    )
