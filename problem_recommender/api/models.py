from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    problem_count: int
    ai_available: bool


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language recommendation query")
    max_results: int = Field(5, ge=1, le=20)
    completed_problems: List[str] = Field(default_factory=list)


class RecommendationItem(BaseModel):
    name: str
    difficulty: str
    topics: List[str]
    language: Optional[str] = None
    file_path: str
    relevance_score: float
    recommendation_reason: str
    description: Optional[str] = None


class RecommendResponse(BaseModel):
    results: List[RecommendationItem]
