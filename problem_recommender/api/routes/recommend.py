from __future__ import annotations

from fastapi import APIRouter

from api.dependencies import get_recommendation_service
from api.models import RecommendRequest, RecommendResponse, RecommendationItem

router = APIRouter(tags=["recommendations"])


@router.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest) -> RecommendResponse:
    recommendation_service = get_recommendation_service()
    user_progress = {
        problem_name: {"completed": True}
        for problem_name in request.completed_problems
    }
    results = recommendation_service.recommend(
        request.query,
        user_progress=user_progress,
        max_results=request.max_results,
    )
    return RecommendResponse(
        results=[RecommendationItem(**result) for result in results]
    )
