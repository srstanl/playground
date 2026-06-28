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
- Tracking model placeholders

## Naming Convention
- Python package name: `job_scout`
- Top-level project directory: `job_scout`
- Future generated artifacts should use stable, readable names tied to company and role when available

## Output Targets
- Application code lives under `job_scout/`
- Tests live under `tests/`
- Local runtime artifacts should eventually live under ignored `data/` paths
