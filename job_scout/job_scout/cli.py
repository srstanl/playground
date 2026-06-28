"""CLI entry point for Job Scout."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from textwrap import shorten
from typing import cast

from job_scout.config import get_settings
from job_scout.db import connect, create_job_posting, get_job_posting, initialize_database, list_job_postings
from job_scout.evaluator import evaluate_job_posting, evaluation_to_pretty_json
from job_scout.models import JobPostingCreate


class CommandArgs(argparse.Namespace):
    command: str


class IngestArgs(CommandArgs):
    file: Path
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


def _database_path() -> Path:
    return get_settings().database_path


def _connection():
    connection = connect(_database_path())
    initialize_database(connection)
    return connection


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

    subparsers.add_parser("list", help="List ingested jobs.")

    show_parser = subparsers.add_parser("show", help="Show one ingested job.")
    show_parser.add_argument("job_id", type=int)

    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate one ingested job.")
    evaluate_parser.add_argument("job_id", type=int)
    evaluate_parser.add_argument("--json", action="store_true", dest="as_json")

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

    raise SystemExit(f"unsupported command: {args.command}")


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
