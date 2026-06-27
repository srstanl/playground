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

## Project Structure

- `job_scout/cli.py` - CLI entry point
- `job_scout/config.py` - runtime configuration
- `job_scout/db.py` - database boundary and connection helpers
- `job_scout/models.py` - domain models and schema definitions
- `job_scout/services/` - future orchestration services
- `tests/` - project tests

## License

AGPL-3.0. See `LICENSE`.
