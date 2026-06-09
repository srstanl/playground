from __future__ import annotations

from fastapi import APIRouter

from api.dependencies import get_recommendation_service
from api.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    recommendation_service = get_recommendation_service()
    return HealthResponse(
        status="ok",
        problem_count=len(recommendation_service.problems),
        ai_available=recommendation_service.has_ai_client,
    )
