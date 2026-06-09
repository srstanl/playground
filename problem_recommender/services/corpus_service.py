from __future__ import annotations

from typing import Any, Dict, List, Optional

from shared.problem_analyzer import ProblemAnalyzer


class CorpusService:
    """Owns problem-corpus loading and refresh behavior."""

    def __init__(self, analyzer: Optional[ProblemAnalyzer] = None):
        self.analyzer = analyzer or ProblemAnalyzer()
        self._problems: List[Dict[str, Any]] = []

    def load_problems(self) -> List[Dict[str, Any]]:
        if not self._problems:
            self._problems = self.analyzer.load_problems()
        return self._problems

    def rescan_problems(self) -> List[Dict[str, Any]]:
        self._problems = self.analyzer.scan_problems()
        return self._problems

    @property
    def problems(self) -> List[Dict[str, Any]]:
        return self._problems
