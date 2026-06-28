# Job Scout

Job Scout is a local-first job application intelligence assistant for reviewing job descriptions, evaluating fit, and tracking opportunities.

This repository starts with a Python-first structure intended to support:

- manual job description ingestion
- local SQLite-backed storage
- CLI-first workflows
- modular evaluation and tracking services

## Initial Scope

The initial scaffold prepares the project for the first delivery lane:

- Python package structure
- CLI entry point
- database module boundary
- domain model boundary
- test package
- SQLite-backed ingestion flow
- list and show commands for stored job postings

Implementation of ingestion, evaluation, and tracking behavior follows in later commits.

## Setup

1. Install Python 3.11+
2. Create a virtual environment
3. Install the package in editable mode:

```bash
pip install -e .
```

## Usage

Run the CLI:

```bash
python -m job_scout.cli --help
```

Milestone 1 commands:

```bash
python -m job_scout.cli ingest --file ./job.txt --source-system linkedin
python -m job_scout.cli list
python -m job_scout.cli show 1
```

Optional environment overrides:

```bash
export JOB_SCOUT_DATA_DIR=./data
export JOB_SCOUT_DATABASE_PATH=./data/job_scout.db
export JOB_SCOUT_PROFILE_PATH=./profiles/user_profile.local.json
export JOB_SCOUT_EVALUATION_MODEL_PATH=./profiles/evaluation_model.json
```

## User Profile

Job Scout uses a tracked template plus an ignored local profile file, similar to `.env` conventions:

- `profiles/user_profile.example.json` - tracked generic profile shape for the repo
- `profiles/user_profile.local.json` - ignored local profile with your actual evaluation inputs

Copy the example and fill in your real values:

```bash
cp profiles/user_profile.example.json profiles/user_profile.local.json
```

The runtime default expects the local file at:

```bash
profiles/user_profile.local.json
```

## Evaluation Model

Job Scout also uses a tracked evaluation model file for shared scoring behavior:

- `profiles/evaluation_model.json` - tracked scoring model, signal catalog, weights, and thresholds

This file is repository-owned configuration, not a local secret. It defines how the evaluator interprets postings before applying your local profile.

## Project Structure

- `job_scout/cli.py` - CLI entry point and Milestone 1 commands
- `job_scout/config.py` - runtime configuration
- `job_scout/db.py` - SQLite schema and repository helpers
- `job_scout/evaluation_model_loader.py` - tracked evaluation model loader
- `job_scout/evaluator.py` - extraction and scoring orchestration
- `job_scout/models.py` - job posting models and ingestion payloads
- `profiles/evaluation_model.json` - tracked evaluation-model configuration
- `profiles/user_profile.example.json` - tracked profile template
- `job_scout/services/` - future orchestration services
- `tests/` - project tests

## License

AGPL-3.0. See `LICENSE`.
