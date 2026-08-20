"""Application workflows for job ingestion and retrieval."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Callable, ContextManager

from job_scout.adapters.browser import BrowserTabJobCapture
from job_scout.domain.models import JobPosting, JobPostingInput
from job_scout.persistence.sqlite import (
    create_job_posting,
    get_job_posting,
    list_job_postings,
)


ConnectionFactory = Callable[[], ContextManager]

BATCH_ALLOWED_FIELDS = {
    "source_system",
    "source_url",
    "external_id",
    "external_ids",
    "company",
    "title",
    "location",
    "raw_description",
}


@dataclass(frozen=True)
class IngestBatchResult:
    """Summary and emitted messages for a batch ingest run."""

    processed: int
    ingested: int
    failed: int
    warnings: int
    messages: list[str]


def ingest_job_description(
    *,
    file_path: Path,
    source_system: str,
    source_url: str | None,
    company: str | None,
    title: str | None,
    location: str | None,
    external_id: str | None,
    connection_factory: ConnectionFactory,
) -> JobPosting:
    """Ingest one job description from a local text file."""
    if not file_path.exists() or not file_path.is_file():
        raise SystemExit(f"job description file not found: {file_path}")
    raw_description = file_path.read_text(encoding="utf-8").strip()
    if not raw_description:
        raise SystemExit("job description file is empty")

    payload = JobPostingInput(
        source_system=source_system,
        raw_description=raw_description,
        source_url=source_url,
        company=company,
        title=title,
        location=location,
        external_ids=_external_ids_from_inputs(source_system, external_id),
    )
    return _ingest_payload(
        payload=payload,
        source_type="uploaded_file",
        source_reference=str(file_path),
        connection_factory=connection_factory,
    )


def ingest_job_text(
    *,
    raw_description: str,
    source_system: str,
    source_url: str | None,
    company: str | None,
    title: str | None,
    location: str | None,
    external_id: str | None,
    connection_factory: ConnectionFactory,
) -> JobPosting:
    """Ingest one job description provided directly as pasted text."""
    normalized_description = raw_description.strip()
    if not normalized_description:
        raise SystemExit("job description text is empty")

    payload = JobPostingInput(
        source_system=source_system,
        raw_description=normalized_description,
        source_url=source_url,
        company=company,
        title=title,
        location=location,
        external_ids=_external_ids_from_inputs(source_system, external_id),
    )
    return _ingest_payload(
        payload=payload,
        source_type="stdin_text",
        source_reference="stdin",
        connection_factory=connection_factory,
    )


def ingest_batch(*, jsonl_path: Path, connection_factory: ConnectionFactory) -> IngestBatchResult:
    """Ingest multiple job descriptions from a jsonl file."""
    if not jsonl_path.exists() or not jsonl_path.is_file():
        raise SystemExit(f"batch file not found: {jsonl_path}")

    processed = 0
    ingested = 0
    failed = 0
    warnings = 0
    messages: list[str] = []

    with connection_factory() as connection:
        for line_number, raw_line in enumerate(
            jsonl_path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            stripped = raw_line.strip()
            if not stripped:
                continue
            processed += 1
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as error:
                failed += 1
                messages.append(f"line {line_number}: error: invalid json ({error.msg})")
                continue
            if not isinstance(record, dict):
                failed += 1
                messages.append(f"line {line_number}: error: batch record must be a JSON object")
                continue
            unknown_fields = sorted(set(record) - BATCH_ALLOWED_FIELDS)
            if unknown_fields:
                warnings += 1
                messages.append(
                    f"line {line_number}: warning: ignoring unknown fields: {', '.join(unknown_fields)}"
                )
            source_system = _string_or_none(record.get("source_system"))
            if source_system is None:
                failed += 1
                messages.append(f"line {line_number}: error: source_system is required")
                continue
            raw_description = str(record.get("raw_description", "")).strip()
            if not raw_description:
                failed += 1
                messages.append(f"line {line_number}: error: raw_description is required")
                continue
            payload = JobPostingInput(
                source_system=source_system,
                raw_description=raw_description,
                source_url=_string_or_none(record.get("source_url")),
                company=_string_or_none(record.get("company")),
                title=_string_or_none(record.get("title")),
                location=_string_or_none(record.get("location")),
                external_ids=_external_ids_from_batch_record(record, source_system),
            )
            job = create_job_posting(
                connection,
                payload,
                source_type="batch_jsonl",
                source_reference=f"{jsonl_path}:{line_number}",
            )
            ingested += 1
            messages.append(f"line {line_number}: ingested job {job.id}: {job.title or 'untitled'}")

    return IngestBatchResult(
        processed=processed,
        ingested=ingested,
        failed=failed,
        warnings=warnings,
        messages=messages,
    )


def ingest_browser_tab_capture(
    *,
    capture: BrowserTabJobCapture,
    connection_factory: ConnectionFactory,
) -> JobPosting:
    """Ingest one job description captured from a browser tab."""
    payload = capture.to_job_posting_input()
    if not payload.source_system:
        raise SystemExit("browser capture source_system is required")
    if not payload.source_url:
        raise SystemExit("browser capture page_url is required")
    return _ingest_payload(
        payload=payload,
        source_type="browser_tab",
        source_reference=capture.source_reference(),
        connection_factory=connection_factory,
    )


def fetch_job(*, job_id: int, connection_factory: ConnectionFactory) -> JobPosting:
    """Fetch one persisted job posting."""
    with connection_factory() as connection:
        return get_job_posting(connection, job_id)


def fetch_jobs(*, connection_factory: ConnectionFactory) -> list[JobPosting]:
    """Fetch all persisted job postings."""
    with connection_factory() as connection:
        return list_job_postings(connection)


def _ingest_payload(
    *,
    payload: JobPostingInput,
    source_type: str,
    source_reference: str,
    connection_factory: ConnectionFactory,
) -> JobPosting:
    with connection_factory() as connection:
        return create_job_posting(
            connection,
            payload,
            source_type=source_type,
            source_reference=source_reference,
        )


def _string_or_none(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _external_ids_from_inputs(source_system: str, external_id: str | None) -> dict[str, str]:
    normalized_external_id = _string_or_none(external_id)
    if normalized_external_id is None:
        return {}
    return {source_system: normalized_external_id}


def _external_ids_from_batch_record(record: dict[str, object], source_system: str) -> dict[str, str]:
    external_ids_value = record.get("external_ids")
    if external_ids_value is not None:
        if not isinstance(external_ids_value, dict):
            raise SystemExit("external_ids must be a JSON object when provided")
        return {
            str(key).strip(): str(value).strip()
            for key, value in external_ids_value.items()
            if str(key).strip() and str(value).strip()
        }
    return _external_ids_from_inputs(source_system, _string_or_none(record.get("external_id")))
