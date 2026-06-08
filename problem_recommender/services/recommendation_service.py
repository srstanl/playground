from __future__ import annotations

from typing import Any, Dict, List, Optional

from shared.rules_engine import RulesEngine
from services.corpus_service import CorpusService


class RecommendationService:
    """Coordinates recommendation behavior across shared adapters."""

    def __init__(
        self,
        corpus_service: CorpusService,
        feedback_engine: Optional[Any] = None,
    ):
        self.corpus_service = corpus_service
        self.feedback_engine = feedback_engine
        self.problems: List[Dict[str, Any]] = []
        self.rules_engine: Optional[RulesEngine] = None
        self.agent: Optional[Any] = None
        self.initialization_error: Optional[Exception] = None
        self.load_corpus()

    def load_corpus(self) -> List[Dict[str, Any]]:
        problems = self.corpus_service.load_problems()
        self._refresh_engines(problems)
        return self.problems

    def refresh_corpus(self) -> List[Dict[str, Any]]:
        problems = self.corpus_service.rescan_problems()
        self._refresh_engines(problems)
        return self.problems

    def recommend(
        self,
        query: str,
        user_progress: Optional[Dict[str, Any]] = None,
        max_results: int = 5,
    ) -> List[Dict[str, Any]]:
        if self.agent:
            return self.agent.get_recommendations(
                query,
                user_progress,
                max_results=max_results,
            )
        if not self.rules_engine:
            return []
        return self.rules_engine.recommend(query, max_results=max_results)

    @property
    def has_ai_client(self) -> bool:
        return bool(self.agent and self.agent.client)

    def _refresh_engines(self, problems: List[Dict[str, Any]]) -> None:
        self.problems = problems
        self.rules_engine = RulesEngine(problems, feedback_engine=self.feedback_engine)
        self.initialization_error = None
        try:
            from shared.ai_agent import AIAgent

            self.agent = AIAgent(
                problems,
                rules_engine=self.rules_engine,
                feedback_engine=self.feedback_engine,
            )
        except Exception as exc:
            self.agent = None
            self.initialization_error = exc
