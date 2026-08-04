"""Database boundary for Job Scout."""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import sqlite3

from job_scout.domain.models import (
    ApplicationEvent,
    ApplicationRecord,
    ApplicationRecordCreate,
    JobPosting,
    JobPostingInput,
)


SCHEMA = """
CREATE TABLE IF NOT EXISTS job_postings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_system TEXT NOT NULL,
    source_url TEXT,
    source_reference TEXT,
    external_id TEXT,
    external_ids_json TEXT NOT NULL DEFAULT '{}',
    company TEXT,
    title TEXT,
    location TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    raw_description TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS application_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_posting_id INTEGER NOT NULL UNIQUE,
    decision TEXT NOT NULL,
    status TEXT NOT NULL,
    outcome TEXT NOT NULL,
    applied_at TEXT,
    last_event_at TEXT,
    next_follow_up_at TEXT,
    resume_variant TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(job_posting_id) REFERENCES job_postings(id)
);

CREATE TABLE IF NOT EXISTS application_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_record_id INTEGER NOT NULL,
    job_posting_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    event_at TEXT NOT NULL,
    changed_fields_json TEXT NOT NULL DEFAULT '[]',
    decision TEXT NOT NULL,
    status TEXT NOT NULL,
    outcome TEXT NOT NULL,
    applied_at TEXT,
    last_event_at TEXT,
    next_follow_up_at TEXT,
    resume_variant TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    FOREIGN KEY(application_record_id) REFERENCES application_records(id),
    FOREIGN KEY(job_posting_id) REFERENCES job_postings(id)
);
"""


def connect(database_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection for the configured path."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    """Create database schema if needed."""
    connection.executescript(SCHEMA)
    _ensure_job_postings_column(connection, "external_id", "TEXT")
    _ensure_job_postings_column(connection, "external_ids_json", "TEXT NOT NULL DEFAULT '{}'")
    connection.execute(
        """
        UPDATE job_postings
        SET external_ids_json = json_object(source_system, external_id)
        WHERE
            external_id IS NOT NULL
            AND TRIM(external_id) != ''
            AND (external_ids_json IS NULL OR TRIM(external_ids_json) = '' OR external_ids_json = '{}')
        """
    )
    connection.commit()


def create_job_posting(
    connection: sqlite3.Connection,
    payload: JobPostingInput,
    *,
    source_type: str,
    source_reference: str | None = None,
) -> JobPosting:
    """Insert a new job posting and return the persisted record."""
    created_at = datetime.now(UTC).isoformat()
    cursor = connection.execute(
        """
        INSERT INTO job_postings (
            source_type,
            source_system,
            source_url,
            source_reference,
            external_id,
            external_ids_json,
            company,
            title,
            location,
            status,
            raw_description,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?, ?)
        """,
        (
            source_type,
            payload.source_system,
            payload.source_url,
            source_reference,
            payload.external_ids.get(payload.source_system),
            json.dumps(payload.external_ids, sort_keys=True),
            payload.company,
            payload.title,
            payload.location,
            payload.raw_description,
            created_at,
        ),
    )
    connection.commit()
    return get_job_posting(connection, cursor.lastrowid)


def list_job_postings(connection: sqlite3.Connection) -> list[JobPosting]:
    """Return all job postings ordered by newest first."""
    rows = connection.execute(
        """
        SELECT
            id,
            source_type,
            source_system,
            source_url,
            source_reference,
            external_id,
            external_ids_json,
            company,
            title,
            location,
            status,
            raw_description,
            created_at
        FROM job_postings
        ORDER BY id DESC
        """
    ).fetchall()
    return [_row_to_job_posting(row) for row in rows]


def get_job_posting(connection: sqlite3.Connection, job_id: int) -> JobPosting:
    """Return a single job posting by ID."""
    row = connection.execute(
        """
        SELECT
            id,
            source_type,
            source_system,
            source_url,
            source_reference,
            external_id,
            external_ids_json,
            company,
            title,
            location,
            status,
            raw_description,
            created_at
        FROM job_postings
        WHERE id = ?
        """,
        (job_id,),
    ).fetchone()
    if row is None:
        raise LookupError(f"job posting {job_id} not found")
    return _row_to_job_posting(row)


def create_application_record(
    connection: sqlite3.Connection,
    payload: ApplicationRecordCreate,
) -> ApplicationRecord:
    """Create one tracking record for a job posting."""
    created_at = datetime.now(UTC).isoformat()
    cursor = connection.execute(
        """
        INSERT INTO application_records (
            job_posting_id,
            decision,
            status,
            outcome,
            applied_at,
            last_event_at,
            next_follow_up_at,
            resume_variant,
            notes,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.job_posting_id,
            payload.decision,
            payload.status,
            payload.outcome,
            _iso_or_none(payload.applied_at),
            _iso_or_none(payload.last_event_at),
            _iso_or_none(payload.next_follow_up_at),
            payload.resume_variant,
            payload.notes,
            created_at,
            created_at,
        ),
    )
    record = get_application_record_by_id(connection, cursor.lastrowid)
    _insert_application_event(
        connection,
        record=record,
        event_type="tracking_initialized",
        changed_fields=[
            "decision",
            "status",
            "outcome",
            "next_follow_up_at",
            "notes",
        ],
        event_at=record.created_at,
    )
    connection.commit()
    return record


def get_application_record(connection: sqlite3.Connection, job_posting_id: int) -> ApplicationRecord:
    """Return a tracking record by job posting id."""
    row = connection.execute(
        """
        SELECT
            id,
            job_posting_id,
            decision,
            status,
            outcome,
            applied_at,
            last_event_at,
            next_follow_up_at,
            resume_variant,
            notes,
            created_at,
            updated_at
        FROM application_records
        WHERE job_posting_id = ?
        """,
        (job_posting_id,),
    ).fetchone()
    if row is None:
        raise LookupError(f"application record for job posting {job_posting_id} not found")
    return _row_to_application_record(row)


def get_application_record_by_id(connection: sqlite3.Connection, application_record_id: int) -> ApplicationRecord:
    """Return a tracking record by its own id."""
    row = connection.execute(
        """
        SELECT
            id,
            job_posting_id,
            decision,
            status,
            outcome,
            applied_at,
            last_event_at,
            next_follow_up_at,
            resume_variant,
            notes,
            created_at,
            updated_at
        FROM application_records
        WHERE id = ?
        """,
        (application_record_id,),
    ).fetchone()
    if row is None:
        raise LookupError(f"application record {application_record_id} not found")
    return _row_to_application_record(row)


def list_application_records(
    connection: sqlite3.Connection,
    *,
    status: str | None = None,
    decision: str | None = None,
) -> list[ApplicationRecord]:
    """List tracked jobs, optionally filtered by status or decision."""
    conditions: list[str] = []
    params: list[str] = []
    if status:
        conditions.append("status = ?")
        params.append(status)
    if decision:
        conditions.append("decision = ?")
        params.append(decision)
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    rows = connection.execute(
        f"""
        SELECT
            id,
            job_posting_id,
            decision,
            status,
            outcome,
            applied_at,
            last_event_at,
            next_follow_up_at,
            resume_variant,
            notes,
            created_at,
            updated_at
        FROM application_records
        {where_clause}
        ORDER BY updated_at DESC, id DESC
        """,
        tuple(params),
    ).fetchall()
    return [_row_to_application_record(row) for row in rows]


def list_application_events(
    connection: sqlite3.Connection,
    *,
    job_posting_id: int,
) -> list[ApplicationEvent]:
    """Return tracking events for one job posting in chronological order."""
    rows = connection.execute(
        """
        SELECT
            id,
            application_record_id,
            job_posting_id,
            event_type,
            event_at,
            changed_fields_json,
            decision,
            status,
            outcome,
            applied_at,
            last_event_at,
            next_follow_up_at,
            resume_variant,
            notes
        FROM application_events
        WHERE job_posting_id = ?
        ORDER BY event_at ASC, id ASC
        """,
        (job_posting_id,),
    ).fetchall()
    return [_row_to_application_event(row) for row in rows]


def update_application_record(
    connection: sqlite3.Connection,
    job_posting_id: int,
    *,
    decision: str | None = None,
    status: str | None = None,
    outcome: str | None = None,
    applied_at: datetime | None = None,
    last_event_at: datetime | None = None,
    next_follow_up_at: datetime | None = None,
    resume_variant: str | None = None,
    notes: str | None = None,
) -> ApplicationRecord:
    """Update fields on an existing tracking record."""
    existing = get_application_record(connection, job_posting_id)
    resolved_decision = decision if decision is not None else existing.decision
    resolved_status = status if status is not None else existing.status
    resolved_outcome = outcome if outcome is not None else existing.outcome
    resolved_applied_at = applied_at if applied_at is not None else existing.applied_at
    resolved_last_event_at = last_event_at if last_event_at is not None else existing.last_event_at
    resolved_next_follow_up_at = (
        next_follow_up_at if next_follow_up_at is not None else existing.next_follow_up_at
    )
    resolved_resume_variant = resume_variant if resume_variant is not None else existing.resume_variant
    resolved_notes = notes if notes is not None else existing.notes
    changed_fields = _changed_tracking_fields(
        existing=existing,
        decision=resolved_decision,
        status=resolved_status,
        outcome=resolved_outcome,
        applied_at=resolved_applied_at,
        last_event_at=resolved_last_event_at,
        next_follow_up_at=resolved_next_follow_up_at,
        resume_variant=resolved_resume_variant,
        notes=resolved_notes,
    )
    if not changed_fields:
        return existing
    updated_at = datetime.now(UTC).isoformat()
    connection.execute(
        """
        UPDATE application_records
        SET
            decision = ?,
            status = ?,
            outcome = ?,
            applied_at = ?,
            last_event_at = ?,
            next_follow_up_at = ?,
            resume_variant = ?,
            notes = ?,
            updated_at = ?
        WHERE job_posting_id = ?
        """,
        (
            resolved_decision,
            resolved_status,
            resolved_outcome,
            _iso_or_none(resolved_applied_at),
            _iso_or_none(resolved_last_event_at),
            _iso_or_none(resolved_next_follow_up_at),
            resolved_resume_variant,
            resolved_notes,
            updated_at,
            job_posting_id,
        ),
    )
    record = get_application_record(connection, job_posting_id)
    _insert_application_event(
        connection,
        record=record,
        event_type="tracking_updated",
        changed_fields=changed_fields,
        event_at=record.updated_at,
    )
    connection.commit()
    return record


def _row_to_job_posting(row: sqlite3.Row) -> JobPosting:
    return JobPosting(
        id=row["id"],
        source_type=row["source_type"],
        source_system=row["source_system"],
        source_url=row["source_url"],
        source_reference=row["source_reference"],
        company=row["company"],
        title=row["title"],
        location=row["location"],
        status=row["status"],
        raw_description=row["raw_description"],
        created_at=datetime.fromisoformat(row["created_at"]),
        external_ids=_external_ids_from_row(row),
    )


def _row_to_application_record(row: sqlite3.Row) -> ApplicationRecord:
    return ApplicationRecord(
        id=row["id"],
        job_posting_id=row["job_posting_id"],
        decision=row["decision"],
        status=row["status"],
        outcome=row["outcome"],
        applied_at=_datetime_or_none(row["applied_at"]),
        last_event_at=_datetime_or_none(row["last_event_at"]),
        next_follow_up_at=_datetime_or_none(row["next_follow_up_at"]),
        resume_variant=row["resume_variant"],
        notes=row["notes"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _row_to_application_event(row: sqlite3.Row) -> ApplicationEvent:
    changed_fields = json.loads(row["changed_fields_json"]) if row["changed_fields_json"] else []
    if not isinstance(changed_fields, list):
        changed_fields = []
    return ApplicationEvent(
        id=row["id"],
        application_record_id=row["application_record_id"],
        job_posting_id=row["job_posting_id"],
        event_type=row["event_type"],
        event_at=datetime.fromisoformat(row["event_at"]),
        changed_fields=[str(value) for value in changed_fields],
        decision=row["decision"],
        status=row["status"],
        outcome=row["outcome"],
        applied_at=_datetime_or_none(row["applied_at"]),
        last_event_at=_datetime_or_none(row["last_event_at"]),
        next_follow_up_at=_datetime_or_none(row["next_follow_up_at"]),
        resume_variant=row["resume_variant"],
        notes=row["notes"],
    )


def _datetime_or_none(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _iso_or_none(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _external_ids_from_row(row: sqlite3.Row) -> dict[str, str]:
    raw_json = row["external_ids_json"]
    if raw_json:
        try:
            decoded = json.loads(raw_json)
        except json.JSONDecodeError:
            decoded = {}
        if isinstance(decoded, dict):
            return {
                str(key): str(value)
                for key, value in decoded.items()
                if str(key).strip() and str(value).strip()
            }
    external_id = row["external_id"]
    source_system = row["source_system"]
    if external_id and source_system:
        return {str(source_system): str(external_id)}
    return {}


def _ensure_job_postings_column(connection: sqlite3.Connection, column_name: str, column_type: str) -> None:
    existing_columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(job_postings)").fetchall()
    }
    if column_name not in existing_columns:
        connection.execute(f"ALTER TABLE job_postings ADD COLUMN {column_name} {column_type}")


def _insert_application_event(
    connection: sqlite3.Connection,
    *,
    record: ApplicationRecord,
    event_type: str,
    changed_fields: list[str],
    event_at: datetime,
) -> None:
    connection.execute(
        """
        INSERT INTO application_events (
            application_record_id,
            job_posting_id,
            event_type,
            event_at,
            changed_fields_json,
            decision,
            status,
            outcome,
            applied_at,
            last_event_at,
            next_follow_up_at,
            resume_variant,
            notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.id,
            record.job_posting_id,
            event_type,
            event_at.isoformat(),
            json.dumps(sorted(set(changed_fields))),
            record.decision,
            record.status,
            record.outcome,
            _iso_or_none(record.applied_at),
            _iso_or_none(record.last_event_at),
            _iso_or_none(record.next_follow_up_at),
            record.resume_variant,
            record.notes,
        ),
    )


def _changed_tracking_fields(
    *,
    existing: ApplicationRecord,
    decision: str,
    status: str,
    outcome: str,
    applied_at: datetime | None,
    last_event_at: datetime | None,
    next_follow_up_at: datetime | None,
    resume_variant: str,
    notes: str,
) -> list[str]:
    changed_fields: list[str] = []
    if decision != existing.decision:
        changed_fields.append("decision")
    if status != existing.status:
        changed_fields.append("status")
    if outcome != existing.outcome:
        changed_fields.append("outcome")
    if applied_at != existing.applied_at:
        changed_fields.append("applied_at")
    if last_event_at != existing.last_event_at:
        changed_fields.append("last_event_at")
    if next_follow_up_at != existing.next_follow_up_at:
        changed_fields.append("next_follow_up_at")
    if resume_variant != existing.resume_variant:
        changed_fields.append("resume_variant")
    if notes != existing.notes:
        changed_fields.append("notes")
    return changed_fields
