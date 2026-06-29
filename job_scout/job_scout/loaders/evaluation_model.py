"""Loader for the tracked Job Scout evaluation model."""

from __future__ import annotations

import json
from pathlib import Path

from job_scout.models import EvaluationModel, RecommendationThresholds, RiskRule


def load_evaluation_model(path: Path) -> EvaluationModel:
    """Load an evaluation model from JSON."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    thresholds_payload = payload.get("thresholds", {})
    risk_payload = payload.get("risk_rules", [])
    return EvaluationModel(
        model_version=payload.get("model_version", "v1"),
        skill_keywords=list(payload.get("skill_keywords", [])),
        domain_keywords=list(payload.get("domain_keywords", [])),
        authorization_patterns=list(payload.get("authorization_patterns", [])),
        preferred_skill_markers=list(payload.get("preferred_skill_markers", [])),
        work_mode_terms=dict(payload.get("work_mode_terms", {})),
        dimensions=dict(payload.get("dimensions", {})),
        thresholds=RecommendationThresholds(
            apply=thresholds_payload.get("apply", 75),
            consider=thresholds_payload.get("consider", 55),
            needs_review=thresholds_payload.get("needs_review", 40),
            minimum_confidence=thresholds_payload.get("minimum_confidence", 45),
        ),
        risk_rules=[
            RiskRule(
                label=item.get("label", ""),
                patterns=list(item.get("patterns", [])),
            )
            for item in risk_payload
        ],
    )
