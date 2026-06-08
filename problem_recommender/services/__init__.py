"""Shared service layer for CLI and API surfaces."""

from .corpus_service import CorpusService
from .recommendation_service import RecommendationService

__all__ = ["CorpusService", "RecommendationService"]
