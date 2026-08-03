"""Application workflows for job tracking."""

from __future__ import annotations

from datetime import datetime
import sqlite3
from typing import Callable, ContextManager

from job_scout.domain.models import ApplicationEvent, ApplicationRecord, ApplicationRecordCreate
from job_scout.persistence.sqlite import (
    create_application_record,
    get_application_record,
    get_job_posting,
    list_application_events,
    list_application_records,
    update_application_record,
)


ConnectionFactory = Callable[[], ContextManager]

TRACK_DECISIONS = {
    "unreviewed",
    "saved",
    "skip",
    "apply",
}

TRACK_STATUSES = {
    "not_started",
    "application_ready",
    "applied",
    "recruiter_contact",
    "interviewing",
    "final_round",
    "offer",
    "rejected",
    "withdrawn",
    "closed",
}

TRACK_OUTCOMES = {
    "unknown",
    "no_response",
    "rejected",
    "withdrawn",
    "offer_declined",
    "offer_accepted",
    "position_closed",
    "hiring_paused",
}

TERMINAL_OUTCOMES = {
    "rejected",
    "withdrawn",
    "offer_declined",
    "offer_accepted",
    "position_closed",
    "hiring_paused",
}


def initialize_tracking(
    *,
    job_id: int,
    decision: str,
    status: str,
    outcome: str,
    next_follow_up_at: datetime | None,
    notes: str,
    connection_factory: ConnectionFactory,
) -> ApplicationRecord:
    """Create a tracking record for a job posting."""
    _validate_tracking_fields(
        decision=decision,
        status=status,
        outcome=outcome,
        next_follow_up_at=next_follow_up_at,
    )
    with connection_factory() as connection:
        get_job_posting(connection, job_id)
        try:
            return create_application_record(
                connection,
                ApplicationRecordCreate(
                    job_posting_id=job_id,
                    decision=decision,
                    status=status,
                    outcome=outcome,
                    next_follow_up_at=next_follow_up_at,
                    notes=notes,
                ),
            )
        except sqlite3.IntegrityError as error:
            raise SystemExit(
                f"tracking record for job {job_id} already exists; use `track update` instead"
            ) from error


def fetch_tracking_record(*, job_id: int, connection_factory: ConnectionFactory) -> ApplicationRecord:
    """Fetch one tracking record by job ID."""
    with connection_factory() as connection:
        return get_application_record(connection, job_id)


def update_tracking(
    *,
    job_id: int,
    decision: str | None,
    status: str | None,
    outcome: str | None,
    applied_at: datetime | None,
    last_event_at: datetime | None,
    next_follow_up_at: datetime | None,
    resume_variant: str | None,
    notes: str | None,
    connection_factory: ConnectionFactory,
) -> ApplicationRecord:
    """Update an existing tracking record."""
    with connection_factory() as connection:
        existing = get_application_record(connection, job_id)
        resolved_decision = decision if decision is not None else existing.decision
        resolved_status = status if status is not None else existing.status
        resolved_outcome = outcome if outcome is not None else existing.outcome
        resolved_next_follow_up_at = (
            next_follow_up_at if next_follow_up_at is not None else existing.next_follow_up_at
        )
        normalized_next_follow_up_at = _normalized_follow_up_for_outcome(
            resolved_next_follow_up_at,
            resolved_outcome,
        )
        _validate_tracking_fields(
            decision=resolved_decision,
            status=resolved_status,
            outcome=resolved_outcome,
            next_follow_up_at=normalized_next_follow_up_at,
        )
        return update_application_record(
            connection,
            job_id,
            decision=resolved_decision,
            status=_terminal_status_for_outcome(resolved_status, resolved_outcome),
            outcome=resolved_outcome,
            applied_at=applied_at,
            last_event_at=last_event_at,
            next_follow_up_at=normalized_next_follow_up_at,
            resume_variant=resume_variant,
            notes=notes,
        )


def fetch_tracking_records(
    *,
    status: str | None,
    decision: str | None,
    connection_factory: ConnectionFactory,
) -> list[ApplicationRecord]:
    """List tracking records with optional filters."""
    if status is not None and status not in TRACK_STATUSES:
        raise SystemExit(f"invalid tracking status: {status}")
    if decision is not None and decision not in TRACK_DECISIONS:
        raise SystemExit(f"invalid tracking decision: {decision}")
    with connection_factory() as connection:
        return list_application_records(connection, status=status, decision=decision)


def fetch_tracking_history(
    *,
    job_id: int,
    connection_factory: ConnectionFactory,
) -> list[ApplicationEvent]:
    """Return the durable tracking event history for one job."""
    with connection_factory() as connection:
        get_application_record(connection, job_id)
        return list_application_events(connection, job_posting_id=job_id)


def _validate_tracking_fields(
    *,
    decision: str,
    status: str,
    outcome: str,
    next_follow_up_at: datetime | None,
) -> None:
    if decision not in TRACK_DECISIONS:
        raise SystemExit(f"invalid tracking decision: {decision}")
    if status not in TRACK_STATUSES:
        raise SystemExit(f"invalid tracking status: {status}")
    if outcome not in TRACK_OUTCOMES:
        raise SystemExit(f"invalid tracking outcome: {outcome}")
    if decision == "skip" and status not in {"not_started", "closed"}:
        raise SystemExit("decision `skip` cannot be combined with an active lifecycle status")
    if decision == "apply" and status == "not_started":
        raise SystemExit("decision `apply` requires a tracking status beyond `not_started`")
    if outcome in TERMINAL_OUTCOMES and next_follow_up_at is not None:
        raise SystemExit("terminal outcomes cannot keep an active follow-up date")


def _terminal_status_for_outcome(status: str, outcome: str) -> str:
    return "closed" if outcome in TERMINAL_OUTCOMES else status


def _normalized_follow_up_for_outcome(next_follow_up_at: datetime | None, outcome: str) -> datetime | None:
    return None if outcome in TERMINAL_OUTCOMES else next_follow_up_at
