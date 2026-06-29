"""Database boundary for Job Scout."""

from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
import sqlite3

from job_scout.models import ApplicationRecord, ApplicationRecordCreate, JobPosting, JobPostingCreate


SCHEMA = """
CREATE TABLE IF NOT EXISTS job_postings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_system TEXT NOT NULL,
    source_url TEXT,
    source_reference TEXT,
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
    connection.commit()


def create_job_posting(
    connection: sqlite3.Connection,
    payload: JobPostingCreate,
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
            company,
            title,
            location,
            status,
            raw_description,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'new', ?, ?)
        """,
        (
            payload.source_type,
            payload.source_system,
            payload.source_url,
            payload.source_reference,
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
    connection.commit()
    return get_application_record_by_id(connection, cursor.lastrowid)


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
            decision if decision is not None else existing.decision,
            status if status is not None else existing.status,
            outcome if outcome is not None else existing.outcome,
            _iso_or_none(applied_at) if applied_at is not None else _iso_or_none(existing.applied_at),
            _iso_or_none(last_event_at) if last_event_at is not None else _iso_or_none(existing.last_event_at),
            _iso_or_none(next_follow_up_at) if next_follow_up_at is not None else _iso_or_none(existing.next_follow_up_at),
            resume_variant if resume_variant is not None else existing.resume_variant,
            notes if notes is not None else existing.notes,
            updated_at,
            job_posting_id,
        ),
    )
    connection.commit()
    return get_application_record(connection, job_posting_id)


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


def _datetime_or_none(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _iso_or_none(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
