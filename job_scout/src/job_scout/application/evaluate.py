"""Application workflow for evaluating persisted jobs."""

from __future__ import annotations

from typing import Callable, ContextManager

from job_scout.evaluator import evaluate_job_posting
from job_scout.domain.models import JobEvaluation

from job_scout.application.ingest import fetch_job


ConnectionFactory = Callable[[], ContextManager]


def evaluate_job(*, job_id: int, connection_factory: ConnectionFactory) -> JobEvaluation:
    """Evaluate one persisted job posting by ID."""
    job = fetch_job(job_id=job_id, connection_factory=connection_factory)
    return evaluate_job_posting(job)
