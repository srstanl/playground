"""Deterministic evaluation helpers for Job Scout."""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from functools import lru_cache
import json

from job_scout.config import get_settings
from job_scout.config.capability_model_loader import load_capability_model
from job_scout.evaluation.extractor import extract_job_posting
from job_scout.evaluation.recommender import (
    build_narrative,
    compute_confidence_score,
    compute_overall_score,
    headline_for,
    recommendation_for,
)
from job_scout.evaluation.scorer import score_extraction
from job_scout.config.evaluation_model_loader import load_evaluation_model
from job_scout.config.profile_loader import load_user_profile
from job_scout.domain.models import (
    CapabilityModel,
    EvaluationModel,
    EvaluationProvenance,
    EvaluationSummary,
    JobEvaluation,
    JobPosting,
    UserProfile,
)


@lru_cache(maxsize=1)
def get_default_evaluation_model() -> EvaluationModel:
    """Load the tracked repository evaluation model once per process."""
    return load_evaluation_model(get_settings().evaluation_model_path)


@lru_cache(maxsize=1)
def get_default_user_profile() -> UserProfile:
    """Load the local user profile once per process."""
    return load_user_profile(get_settings().profile_path)


@lru_cache(maxsize=1)
def get_default_capability_model() -> CapabilityModel:
    """Load the tracked capability ontology once per process."""
    return load_capability_model(get_settings().capability_model_path)


def evaluate_job_posting(
    job_posting: JobPosting,
    evaluation_model: EvaluationModel | None = None,
    user_profile: UserProfile | None = None,
    capability_model: CapabilityModel | None = None,
) -> JobEvaluation:
    """Evaluate a stored job posting with deterministic heuristics."""
    model = evaluation_model or get_default_evaluation_model()
    profile = user_profile or get_default_user_profile()
    capabilities = capability_model or get_default_capability_model()
    extraction = extract_job_posting(job_posting, model, capabilities)
    scoring = score_extraction(extraction, model, profile)
    overall_score = compute_overall_score(scoring.dimensions)
    confidence_score = compute_confidence_score(extraction, scoring.dimensions)
    recommendation = recommendation_for(
        overall_score,
        confidence_score,
        scoring.blocking_concerns,
        model,
    )
    headline = headline_for(extraction, recommendation, overall_score)
    narrative = build_narrative(extraction, scoring, recommendation)

    return JobEvaluation(
        job_posting_id=job_posting.id,
        summary=EvaluationSummary(
            headline=headline,
            recommendation=recommendation,
            overall_score=overall_score,
            confidence_score=confidence_score,
            narrative=narrative,
        ),
        extraction=extraction,
        scoring=scoring,
        provenance=EvaluationProvenance(
            source_system=job_posting.source_system,
            source_url=job_posting.source_url,
            evaluated_at=datetime.now(UTC),
        ),
    )


def evaluation_to_pretty_json(evaluation: JobEvaluation) -> str:
    """Serialize an evaluation result as stable pretty JSON."""
    payload = asdict(evaluation)
    return json.dumps(payload, indent=2, default=_json_default, sort_keys=True)


def _json_default(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"unsupported type: {type(value)!r}")
