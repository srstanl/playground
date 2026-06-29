"""CLI entry point for Job Scout."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
import json
import sqlite3
import sys
from textwrap import shorten
from typing import cast

from job_scout.config import get_settings
from job_scout.db import (
    connect,
    create_application_record,
    create_job_posting,
    get_application_record,
    get_job_posting,
    initialize_database,
    list_application_records,
    list_job_postings,
    update_application_record,
)
from job_scout.evaluator import evaluate_job_posting, evaluation_to_pretty_json
from job_scout.models import ApplicationRecordCreate, JobPostingCreate


class CommandArgs(argparse.Namespace):
    command: str


class IngestArgs(CommandArgs):
    file: Path
    source_url: str | None
    source_system: str
    company: str | None
    title: str | None
    location: str | None


class IngestBatchArgs(CommandArgs):
    jsonl: Path


class ShowArgs(CommandArgs):
    job_id: int


class EvaluateArgs(CommandArgs):
    job_id: int
    as_json: bool


class TrackInitArgs(CommandArgs):
    job_id: int
    decision: str
    status: str
    outcome: str
    next_follow_up_at: str | None
    notes: str


class TrackShowArgs(CommandArgs):
    job_id: int


class TrackUpdateArgs(CommandArgs):
    job_id: int
    decision: str | None
    status: str | None
    outcome: str | None
    applied_at: str | None
    last_event_at: str | None
    next_follow_up_at: str | None
    resume_variant: str | None
    notes: str | None


class TrackListArgs(CommandArgs):
    status: str | None
    decision: str | None


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

BATCH_ALLOWED_FIELDS = {
    "raw_description",
    "source_type",
    "source_system",
    "source_url",
    "source_reference",
    "company",
    "title",
    "location",
}


def _database_path() -> Path:
    return get_settings().database_path


@contextmanager
def _connection():
    connection = connect(_database_path())
    initialize_database(connection)
    try:
        yield connection
    finally:
        connection.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="job-scout",
        description="Local-first job application intelligence assistant.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show scaffold status.")

    ingest_parser = subparsers.add_parser("ingest", help="Ingest a job description from a text file.")
    ingest_parser.add_argument("--file", required=True, type=Path)
    ingest_parser.add_argument("--source-url")
    ingest_parser.add_argument("--source-system", default="unknown")
    ingest_parser.add_argument("--company")
    ingest_parser.add_argument("--title")
    ingest_parser.add_argument("--location")

    ingest_batch_parser = subparsers.add_parser("ingest-batch", help="Ingest multiple job descriptions from a jsonl file.")
    ingest_batch_parser.add_argument("--jsonl", required=True, type=Path)

    subparsers.add_parser("list", help="List ingested jobs.")

    show_parser = subparsers.add_parser("show", help="Show one ingested job.")
    show_parser.add_argument("job_id", type=int)

    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate one ingested job.")
    evaluate_parser.add_argument("job_id", type=int)
    evaluate_parser.add_argument("--json", action="store_true", dest="as_json")

    track_parser = subparsers.add_parser("track", help="Manage tracked application records.")
    track_subparsers = track_parser.add_subparsers(dest="track_command", required=True)

    track_init = track_subparsers.add_parser("init", help="Create a tracking record for a job.")
    track_init.add_argument("job_id", type=int)
    track_init.add_argument("--decision", default="unreviewed")
    track_init.add_argument("--status", default="not_started")
    track_init.add_argument("--outcome", default="unknown")
    track_init.add_argument("--next-follow-up-at")
    track_init.add_argument("--notes", default="")

    track_show = track_subparsers.add_parser("show", help="Show one tracking record.")
    track_show.add_argument("job_id", type=int)

    track_update = track_subparsers.add_parser("update", help="Update one tracking record.")
    track_update.add_argument("job_id", type=int)
    track_update.add_argument("--decision")
    track_update.add_argument("--status")
    track_update.add_argument("--outcome")
    track_update.add_argument("--applied-at")
    track_update.add_argument("--last-event-at")
    track_update.add_argument("--next-follow-up-at")
    track_update.add_argument("--resume-variant")
    track_update.add_argument("--notes")

    track_list = track_subparsers.add_parser("list", help="List tracking records.")
    track_list.add_argument("--status")
    track_list.add_argument("--decision")

    return parser


def run(argv: list[str] | None = None) -> int:
    args = cast(CommandArgs, build_parser().parse_args(argv))

    if args.command == "status":
        print("job-scout scaffold initialized")
        return 0

    if args.command == "ingest":
        ingest_args = cast(IngestArgs, args)
        if not ingest_args.file.exists() or not ingest_args.file.is_file():
            raise SystemExit(f"job description file not found: {ingest_args.file}")
        raw_description = ingest_args.file.read_text(encoding="utf-8").strip()
        if not raw_description:
            raise SystemExit("job description file is empty")

        payload = JobPostingCreate(
            raw_description=raw_description,
            source_type="uploaded_file",
            source_system=ingest_args.source_system,
            source_url=ingest_args.source_url,
            source_reference=str(ingest_args.file),
            company=ingest_args.company,
            title=ingest_args.title,
            location=ingest_args.location,
        )
        with _connection() as connection:
            job = create_job_posting(connection, payload)
        print(f"Ingested job {job.id}: {job.title or 'untitled'}")
        return 0

    if args.command == "ingest-batch":
        batch_args = cast(IngestBatchArgs, args)
        if not batch_args.jsonl.exists() or not batch_args.jsonl.is_file():
            raise SystemExit(f"batch file not found: {batch_args.jsonl}")
        processed = 0
        ingested = 0
        failed = 0
        warnings = 0
        with _connection() as connection:
            for line_number, raw_line in enumerate(batch_args.jsonl.read_text(encoding="utf-8").splitlines(), start=1):
                stripped = raw_line.strip()
                if not stripped:
                    continue
                processed += 1
                try:
                    record = json.loads(stripped)
                except json.JSONDecodeError as error:
                    failed += 1
                    print(f"line {line_number}: error: invalid json ({error.msg})")
                    continue
                if not isinstance(record, dict):
                    failed += 1
                    print(f"line {line_number}: error: batch record must be a JSON object")
                    continue
                unknown_fields = sorted(set(record) - BATCH_ALLOWED_FIELDS)
                if unknown_fields:
                    warnings += 1
                    print(f"line {line_number}: warning: ignoring unknown fields: {', '.join(unknown_fields)}")
                raw_description = str(record.get("raw_description", "")).strip()
                if not raw_description:
                    failed += 1
                    print(f"line {line_number}: error: raw_description is required")
                    continue
                payload = JobPostingCreate(
                    raw_description=raw_description,
                    source_type=str(record.get("source_type") or "batch_jsonl"),
                    source_system=str(record.get("source_system") or "unknown"),
                    source_url=_string_or_none(record.get("source_url")),
                    source_reference=_string_or_none(record.get("source_reference")) or f"{batch_args.jsonl}:{line_number}",
                    company=_string_or_none(record.get("company")),
                    title=_string_or_none(record.get("title")),
                    location=_string_or_none(record.get("location")),
                )
                job = create_job_posting(connection, payload)
                ingested += 1
                print(f"line {line_number}: ingested job {job.id}: {job.title or 'untitled'}")
        print(f"summary: processed={processed} ingested={ingested} failed={failed} warnings={warnings}")
        return 0

    if args.command == "list":
        with _connection() as connection:
            jobs = list_job_postings(connection)

        if not jobs:
            print("No jobs ingested yet.")
            return 0

        for job in jobs:
            summary = shorten(job.raw_description.replace("\n", " "), width=70, placeholder="...")
            print(
                f"[{job.id}] {job.title or 'untitled'} | "
                f"{job.company or 'unknown company'} | "
                f"{job.status} | "
                f"{summary}"
            )
        return 0

    if args.command == "show":
        show_args = cast(ShowArgs, args)
        with _connection() as connection:
            try:
                job = get_job_posting(connection, show_args.job_id)
            except LookupError as error:
                raise SystemExit(str(error)) from error

        print(f"id: {job.id}")
        print(f"title: {job.title or ''}")
        print(f"company: {job.company or ''}")
        print(f"location: {job.location or ''}")
        print(f"source_type: {job.source_type}")
        print(f"source_system: {job.source_system}")
        print(f"source_url: {job.source_url or ''}")
        print(f"source_reference: {job.source_reference or ''}")
        print(f"status: {job.status}")
        print(f"created_at: {job.created_at.isoformat()}")
        print("")
        print(job.raw_description)
        return 0

    if args.command == "evaluate":
        evaluate_args = cast(EvaluateArgs, args)
        with _connection() as connection:
            try:
                job = get_job_posting(connection, evaluate_args.job_id)
            except LookupError as error:
                raise SystemExit(str(error)) from error

        evaluation = evaluate_job_posting(job)

        if evaluate_args.as_json:
            print(evaluation_to_pretty_json(evaluation))
            return 0

        print(f"job_id: {evaluation.job_posting_id}")
        print(f"headline: {evaluation.summary.headline}")
        print(f"recommendation: {evaluation.summary.recommendation}")
        print(f"overall_score: {evaluation.summary.overall_score}")
        print(f"confidence_score: {evaluation.summary.confidence_score}")
        print(f"narrative: {evaluation.summary.narrative}")
        if evaluation.extraction.semantic_shapes:
            print("")
            print("semantic_shapes:")
            for shape, score in sorted(
                evaluation.extraction.semantic_shapes.items(),
                key=lambda item: item[1],
                reverse=True,
            ):
                print(f"- {shape}: {score}/5")
        print("")
        print("dimensions:")
        for dimension in evaluation.scoring.dimensions:
            print(f"- {dimension.name}: {dimension.score}/5 ({dimension.weight:.2f})")
            print(f"  rationale: {dimension.rationale}")
        if evaluation.scoring.strengths:
            print("")
            print("strengths:")
            for strength in evaluation.scoring.strengths:
                print(f"- {strength}")
        if evaluation.scoring.gaps:
            print("")
            print("gaps:")
            for gap in evaluation.scoring.gaps:
                print(f"- {gap}")
        if evaluation.scoring.blocking_concerns:
            print("")
            print("blocking_concerns:")
            for concern in evaluation.scoring.blocking_concerns:
                print(f"- {concern}")
        if evaluation.scoring.review_flags:
            print("")
            print("review_flags:")
            for flag in evaluation.scoring.review_flags:
                print(f"- {flag}")
        if evaluation.scoring.risk_categories:
            print("")
            print("risks:")
            for category in ("informational", "onboarding", "moderate", "blocker"):
                items = evaluation.scoring.risk_categories.get(category, [])
                if not items:
                    continue
                print(f"- {category}:")
                for item in items:
                    print(f"  - {item}")
        return 0

    if args.command == "track":
        track_command = getattr(args, "track_command", None)
        if track_command == "init":
            track_args = cast(TrackInitArgs, args)
            _validate_tracking_fields(
                decision=track_args.decision,
                status=track_args.status,
                outcome=track_args.outcome,
                next_follow_up_at=_parse_datetime(track_args.next_follow_up_at),
            )
            with _connection() as connection:
                try:
                    get_job_posting(connection, track_args.job_id)
                except LookupError as error:
                    raise SystemExit(str(error)) from error
                try:
                    record = create_application_record(
                        connection,
                        ApplicationRecordCreate(
                            job_posting_id=track_args.job_id,
                            decision=track_args.decision,
                            status=track_args.status,
                            outcome=track_args.outcome,
                            next_follow_up_at=_parse_datetime(track_args.next_follow_up_at),
                            notes=track_args.notes,
                        ),
                    )
                except sqlite3.IntegrityError as error:
                    raise SystemExit(
                        f"tracking record for job {track_args.job_id} already exists; use `track update` instead"
                    ) from error
            print(f"Tracking initialized for job {record.job_posting_id} with status {record.status}.")
            return 0

        if track_command == "show":
            track_args = cast(TrackShowArgs, args)
            with _connection() as connection:
                try:
                    record = get_application_record(connection, track_args.job_id)
                except LookupError as error:
                    raise SystemExit(str(error)) from error
            _print_tracking_record(record)
            return 0

        if track_command == "update":
            track_args = cast(TrackUpdateArgs, args)
            parsed_applied_at = _parse_datetime(track_args.applied_at)
            parsed_last_event_at = _parse_datetime(track_args.last_event_at)
            parsed_next_follow_up_at = _parse_datetime(track_args.next_follow_up_at)
            with _connection() as connection:
                try:
                    existing = get_application_record(connection, track_args.job_id)
                    decision = track_args.decision if track_args.decision is not None else existing.decision
                    status = track_args.status if track_args.status is not None else existing.status
                    outcome = track_args.outcome if track_args.outcome is not None else existing.outcome
                    next_follow_up_at = (
                        parsed_next_follow_up_at
                        if track_args.next_follow_up_at is not None
                        else existing.next_follow_up_at
                    )
                    normalized_next_follow_up_at = _normalized_follow_up_for_outcome(next_follow_up_at, outcome)
                    _validate_tracking_fields(
                        decision=decision,
                        status=status,
                        outcome=outcome,
                        next_follow_up_at=normalized_next_follow_up_at,
                    )
                    record = update_application_record(
                        connection,
                        track_args.job_id,
                        decision=decision,
                        status=_terminal_status_for_outcome(status, outcome),
                        outcome=outcome,
                        applied_at=parsed_applied_at,
                        last_event_at=parsed_last_event_at,
                        next_follow_up_at=normalized_next_follow_up_at,
                        resume_variant=track_args.resume_variant,
                        notes=track_args.notes,
                    )
                except LookupError as error:
                    raise SystemExit(str(error)) from error
            print(f"Tracking updated for job {record.job_posting_id}.")
            return 0

        if track_command == "list":
            track_args = cast(TrackListArgs, args)
            if track_args.status is not None and track_args.status not in TRACK_STATUSES:
                raise SystemExit(f"invalid tracking status: {track_args.status}")
            if track_args.decision is not None and track_args.decision not in TRACK_DECISIONS:
                raise SystemExit(f"invalid tracking decision: {track_args.decision}")
            with _connection() as connection:
                records = list_application_records(connection, status=track_args.status, decision=track_args.decision)
            if not records:
                print("No tracked jobs yet.")
                return 0
            for record in records:
                print(
                    f"[{record.job_posting_id}] {record.decision} | {record.status} | "
                    f"{record.outcome} | follow_up={_format_datetime(record.next_follow_up_at)}"
                )
            return 0

    raise SystemExit(f"unsupported command: {args.command}")


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()


def _parse_datetime(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _format_datetime(value: datetime | None) -> str:
    return value.isoformat() if value else ""


def _print_tracking_record(record) -> None:
    print(f"job_posting_id: {record.job_posting_id}")
    print(f"decision: {record.decision}")
    print(f"status: {record.status}")
    print(f"outcome: {record.outcome}")
    print(f"applied_at: {_format_datetime(record.applied_at)}")
    print(f"last_event_at: {_format_datetime(record.last_event_at)}")
    print(f"next_follow_up_at: {_format_datetime(record.next_follow_up_at)}")
    print(f"resume_variant: {record.resume_variant}")
    print(f"notes: {record.notes}")
    print(f"created_at: {record.created_at.isoformat()}")
    print(f"updated_at: {record.updated_at.isoformat()}")


def _string_or_none(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


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
