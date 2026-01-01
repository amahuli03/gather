"""Health check endpoint."""
from fastapi import APIRouter
from src.api.models import HealthResponse

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(status="healthy")


