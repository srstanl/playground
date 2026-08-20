"""CLI entry point for Job Scout."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime
import json
from pathlib import Path
import sys
from textwrap import shorten
from typing import cast

from job_scout.application.evaluate import evaluate_job
from job_scout.application.ingest import (
    IngestBatchResult,
    fetch_job,
    fetch_jobs,
    ingest_batch,
    ingest_job_description,
    ingest_job_text,
)
from job_scout.application.track import (
    TRACK_DECISIONS,
    TRACK_OUTCOMES,
    TRACK_STATUSES,
    fetch_tracking_history,
    fetch_tracking_record,
    fetch_tracking_records,
    initialize_tracking,
    update_tracking,
)
from job_scout.config import get_settings
from job_scout.domain.models import ApplicationEvent, ApplicationRecord
from job_scout.evaluator import evaluation_to_pretty_json
from job_scout.persistence.sqlite import connect, initialize_database


class CommandArgs(argparse.Namespace):
    command: str


class IngestArgs(CommandArgs):
    file: Path
    external_id: str | None
    source_url: str | None
    source_system: str
    company: str | None
    title: str | None
    location: str | None


class IngestBatchArgs(CommandArgs):
    jsonl: Path


class IngestTextArgs(CommandArgs):
    external_id: str | None
    source_url: str | None
    source_system: str
    company: str | None
    title: str | None
    location: str | None


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


class TrackHistoryArgs(CommandArgs):
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
    ingest_parser.add_argument("--source-system", required=True)
    ingest_parser.add_argument("--company")
    ingest_parser.add_argument("--title")
    ingest_parser.add_argument("--location")
    ingest_parser.add_argument("--external-id")

    ingest_batch_parser = subparsers.add_parser("ingest-batch", help="Ingest multiple job descriptions from a jsonl file.")
    ingest_batch_parser.add_argument("--jsonl", required=True, type=Path)

    ingest_text_parser = subparsers.add_parser(
        "ingest-text",
        help="Ingest a job description from pasted stdin text.",
    )
    ingest_text_parser.add_argument("--source-url")
    ingest_text_parser.add_argument("--source-system", required=True)
    ingest_text_parser.add_argument("--company")
    ingest_text_parser.add_argument("--title")
    ingest_text_parser.add_argument("--location")
    ingest_text_parser.add_argument("--external-id")

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

    track_history = track_subparsers.add_parser("history", help="Show tracking event history.")
    track_history.add_argument("job_id", type=int)

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
        job = ingest_job_description(
            file_path=ingest_args.file,
            source_system=ingest_args.source_system,
            source_url=ingest_args.source_url,
            company=ingest_args.company,
            title=ingest_args.title,
            location=ingest_args.location,
            external_id=ingest_args.external_id,
            connection_factory=_connection,
        )
        print(f"Ingested job {job.id}: {job.title or 'untitled'}")
        return 0

    if args.command == "ingest-batch":
        batch_args = cast(IngestBatchArgs, args)
        result = ingest_batch(jsonl_path=batch_args.jsonl, connection_factory=_connection)
        _print_batch_ingest_result(result)
        return 0

    if args.command == "ingest-text":
        ingest_text_args = cast(IngestTextArgs, args)
        raw_description = sys.stdin.read()
        job = ingest_job_text(
            raw_description=raw_description,
            source_system=ingest_text_args.source_system,
            source_url=ingest_text_args.source_url,
            company=ingest_text_args.company,
            title=ingest_text_args.title,
            location=ingest_text_args.location,
            external_id=ingest_text_args.external_id,
            connection_factory=_connection,
        )
        print(f"Ingested job {job.id}: {job.title or 'untitled'}")
        return 0

    if args.command == "list":
        jobs = fetch_jobs(connection_factory=_connection)
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
        try:
            job = fetch_job(job_id=show_args.job_id, connection_factory=_connection)
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
        print(f"external_ids: {json.dumps(job.external_ids, sort_keys=True)}")
        print(f"status: {job.status}")
        print(f"created_at: {job.created_at.isoformat()}")
        print("")
        print(job.raw_description)
        return 0

    if args.command == "evaluate":
        evaluate_args = cast(EvaluateArgs, args)
        try:
            evaluation = evaluate_job(job_id=evaluate_args.job_id, connection_factory=_connection)
        except LookupError as error:
            raise SystemExit(str(error)) from error

        if evaluate_args.as_json:
            print(evaluation_to_pretty_json(evaluation))
            return 0

        print(f"job_id: {evaluation.job_posting_id}")
        print(f"headline: {evaluation.summary.headline}")
        print(f"recommendation: {evaluation.summary.recommendation}")
        print(f"overall_score: {evaluation.summary.overall_score}")
        print(f"confidence_score: {evaluation.summary.confidence_score}")
        print(f"narrative: {evaluation.summary.narrative}")
        print(f"engineering_persona: {evaluation.extraction.engineering_persona}")
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
            try:
                record = initialize_tracking(
                    job_id=track_args.job_id,
                    decision=track_args.decision,
                    status=track_args.status,
                    outcome=track_args.outcome,
                    next_follow_up_at=_parse_datetime(track_args.next_follow_up_at),
                    notes=track_args.notes,
                    connection_factory=_connection,
                )
            except LookupError as error:
                raise SystemExit(str(error)) from error
            print(f"Tracking initialized for job {record.job_posting_id} with status {record.status}.")
            return 0

        if track_command == "show":
            track_args = cast(TrackShowArgs, args)
            try:
                record = fetch_tracking_record(job_id=track_args.job_id, connection_factory=_connection)
            except LookupError as error:
                raise SystemExit(str(error)) from error
            _print_tracking_record(record)
            return 0

        if track_command == "history":
            track_args = cast(TrackHistoryArgs, args)
            try:
                events = fetch_tracking_history(job_id=track_args.job_id, connection_factory=_connection)
            except LookupError as error:
                raise SystemExit(str(error)) from error
            _print_tracking_history(events)
            return 0

        if track_command == "update":
            track_args = cast(TrackUpdateArgs, args)
            parsed_applied_at = _parse_datetime(track_args.applied_at)
            parsed_last_event_at = _parse_datetime(track_args.last_event_at)
            parsed_next_follow_up_at = _parse_datetime(track_args.next_follow_up_at)
            try:
                record = update_tracking(
                    job_id=track_args.job_id,
                    decision=track_args.decision,
                    status=track_args.status,
                    outcome=track_args.outcome,
                    applied_at=parsed_applied_at,
                    last_event_at=parsed_last_event_at,
                    next_follow_up_at=parsed_next_follow_up_at if track_args.next_follow_up_at is not None else None,
                    resume_variant=track_args.resume_variant,
                    notes=track_args.notes,
                    connection_factory=_connection,
                )
            except LookupError as error:
                raise SystemExit(str(error)) from error
            print(f"Tracking updated for job {record.job_posting_id}.")
            return 0

        if track_command == "list":
            track_args = cast(TrackListArgs, args)
            records = fetch_tracking_records(
                status=track_args.status,
                decision=track_args.decision,
                connection_factory=_connection,
            )
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

def _parse_datetime(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _format_datetime(value: datetime | None) -> str:
    return value.isoformat() if value else ""


def _print_tracking_record(record: ApplicationRecord) -> None:
    print(f"id: {record.id}")
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


def _print_tracking_history(events: list[ApplicationEvent]) -> None:
    if not events:
        print("No tracking history yet.")
        return
    for event in events:
        print(
            f"[{event.event_at.isoformat()}] {event.event_type} "
            f"changed={','.join(event.changed_fields) or 'none'}"
        )
        print(
            f"  decision={event.decision} status={event.status} "
            f"outcome={event.outcome} follow_up={_format_datetime(event.next_follow_up_at)}"
        )

def _print_batch_ingest_result(result: IngestBatchResult) -> None:
    for message in result.messages:
        print(message)
    print(
        "summary: "
        f"processed={result.processed} "
        f"ingested={result.ingested} "
        f"failed={result.failed} "
        f"warnings={result.warnings}"
    )


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
