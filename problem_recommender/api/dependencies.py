from __future__ import annotations

from functools import lru_cache

from shared.feedback_engine import FeedbackEngine
from services import CorpusService, RecommendationService


@lru_cache(maxsize=1)
def get_recommendation_service() -> RecommendationService:
    corpus_service = CorpusService()
    feedback_engine = FeedbackEngine()
    return RecommendationService(corpus_service, feedback_engine=feedback_engine)
