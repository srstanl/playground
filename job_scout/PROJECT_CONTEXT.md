# Project Context: Job Scout

## Goal
Build a local-first job application intelligence assistant that helps ingest job descriptions, evaluate fit, and track opportunities without auto-applying.

## Default Assumptions
- Job Scout is a developer-facing productivity tool and should default to a Python backend and CLI-first experience.
- Sensitive user data remains local by default.
- Human review is required before any recommendation becomes an action.
- Initial delivery prioritizes ingestion and evaluation before deeper tracking and artifact generation.

## Engineering Rules
- Always evaluate necessary environment variables before attempting to fix potential false positives from the editor.
- Company metadata is tracked by default but must not influence rubric scoring unless an explicit, defensible company-specific evaluation rule is defined.

## Initial Scope
- Manual job description ingestion
- Local SQLite-backed storage
- Job evaluation scaffolding
- Application tracking MVP

## Current Status
- Manual ingestion is implemented and persisted locally.
- Batch ingestion is implemented for `jsonl` input with per-line validation and partial-failure tolerance.
- Profile-driven evaluation is implemented with capability-aware reasoning, semantic shapes, explainable scoring, and narrative output.
- Tracking now has a first usable slice:
  - `track init`
  - `track show`
  - `track update`
  - `track list`
- Tracking records currently support:
  - decision
  - lifecycle status
  - explicit outcome
  - follow-up date
  - notes
- Terminal outcomes such as `position_closed` and `hiring_paused` now stop active follow-up by default.

## Next Recommended Work
- Add richer lifecycle rules where needed.
- Decide whether notes should remain a single field or move toward event history later.
- Determine when tracking data is stable enough to support analytics queries.
- Decide whether a human-oriented multi-job delimiter format is worth adding beyond `jsonl`.

## Naming Convention
- Python package name: `job_scout`
- Top-level project directory: `job_scout`
- Future generated artifacts should use stable, readable names tied to company and role when available

## Output Targets
- Application code lives under `job_scout/`
- Tests live under `tests/`
- Local runtime artifacts should eventually live under ignored `data/` paths
- Design notes and milestone contracts live under `docs/`
