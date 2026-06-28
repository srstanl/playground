"""Database boundary for Job Scout."""

from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
import sqlite3

from job_scout.models import JobPosting, JobPostingCreate


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
