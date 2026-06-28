# Job Scout

> **Job Scout doesn't help you find more jobs. It helps you recognize the right ones.**

Job Scout is a local-first job intelligence tool that evaluates opportunities through the lens of engineering problem space rather than keyword matching.

Instead of asking:

> *"Can I technically do this job?"*

Job Scout asks:

> *"Is this job worth my time and emotional energy?"*

The project is designed for experienced engineers who have learned that titles, frameworks, and tool lists rarely describe what the work actually is. Rather than optimizing for resume-driven development or keyword stuffing, Job Scout tries to identify the shape of the work, evaluate long-term alignment, and support more consistent application decisions.

Everything runs locally. Your profile, evaluations, and job history stay under your control.

## Philosophy

Most job search tooling optimizes for discoverability.

Job Scout optimizes for **fit**.

Instead of counting nouns, it evaluates:

- engineering problem shape
- role scope
- capability alignment
- operating environment
- identity consistency
- compensation
- practical risks

The goal is not to maximize interview count.

The goal is to improve the odds that the interviews are worth having.

## Current State

Current capabilities include:

- local-first CLI workflow
- manual job description ingestion
- SQLite-backed storage
- profile-driven evaluation
- capability extraction
- semantic role-shape classification
- environment and risk detection
- compensation extraction
- narrative recommendations
- application-tracking foundation

The system is intentionally human-in-the-loop.

Job Scout prepares structure, reasoning, and recommendations.

You decide what deserves an application.

## Design Principles

### Local First

Sensitive career information belongs on your machine.

Profiles, evaluations, and application history remain local by default.

### Problem Space over Keywords

Frameworks change.

Engineering problems persist.

Job Scout evaluates the work being described rather than only matching technologies.

### Identity Consistency

A stronger application should not require becoming a different engineer.

The evaluator rewards roles that align with professional identity and highlights roles that introduce unnecessary identity drift.

### Explainable Decisions

Every recommendation should answer:

> *Why?*

Scores are summaries.

Reasoning is the product.

## Setup

Requirements:

- Python 3.11+

Install the project in editable mode:

```bash
pip install -e .
```

## Usage

Display available commands:

```bash
python -m job_scout.cli --help
```

Current workflow:

```bash
python -m job_scout.cli ingest --file ./job.txt --source-system linkedin
python -m job_scout.cli evaluate 1
python -m job_scout.cli list
python -m job_scout.cli show 1
```

## Configuration

Optional environment overrides:

```bash
export JOB_SCOUT_DATA_DIR=./data
export JOB_SCOUT_DATABASE_PATH=./data/job_scout.db
export JOB_SCOUT_PROFILE_PATH=./profiles/user_profile.local.json
export JOB_SCOUT_EVALUATION_MODEL_PATH=./profiles/evaluation_model.json
export JOB_SCOUT_CAPABILITY_MODEL_PATH=./profiles/capability_model.json
```

## Profile and Models

Job Scout separates repository-owned evaluation logic from user-owned career information.

**Local user profile**

- `profiles/user_profile.example.json` - tracked template
- `profiles/user_profile.local.json` - ignored local profile with real values

Create your local profile:

```bash
cp profiles/user_profile.example.json profiles/user_profile.local.json
```

The local profile defines your:

- target roles
- preferred problem spaces
- constraints
- compensation expectations
- evaluation preferences

**Repository-owned evaluation configuration**

- `profiles/evaluation_model.json` - scoring model, thresholds, and evaluation behavior
- `profiles/capability_model.json` - capability ontology used to reason above tool names

The profile answers:

> **Who are you optimizing for?**

The models answer:

> **How should jobs be interpreted and evaluated?**

## Feedback Artifacts

Design reviews and evaluation feedback are kept in:

- `docs/feedback/`

This keeps scoring decisions and product evolution attached to the repository instead of buried in chat history.

## Contributing

Contributions are welcome, especially where they improve reasoning quality rather than just adding automation.

Good contribution areas include:

- evaluation-model refinement
- capability ontology expansion
- semantic shape detection
- ingestion workflows
- tracking and outcome analysis
- documentation and design feedback

If you want to contribute:

1. Open an issue or discussion with the problem you are trying to solve.
2. Keep changes local-first and explainable.
3. Prefer improvements to evaluation quality over volume-oriented automation.
4. Include tests or validation notes where behavior changes.

See `CONTRIBUTING.md` for working conventions.

## Project Structure

- `job_scout/cli.py` - CLI entry point
- `job_scout/config.py` - runtime configuration
- `job_scout/db.py` - SQLite schema and persistence helpers
- `job_scout/evaluator.py` - extraction and scoring orchestration
- `job_scout/evaluation_model_loader.py` - evaluation model loader
- `job_scout/capability_model_loader.py` - capability ontology loader
- `job_scout/profile_loader.py` - local profile loader
- `job_scout/models.py` - domain models
- `profiles/` - tracked evaluation configuration plus local profile template
- `docs/feedback/` - saved review artifacts and iteration context
- `CONTRIBUTING.md` - contribution guidelines
- `tests/` - project tests

## Roadmap

Planned capabilities include:

- email ingestion
- browser-assisted job capture
- resume generation
- cover letter generation
- artifact validation
- richer application tracking
- historical outcome analytics
- interview and response trend analysis

## Long-Term Vision

Job Scout is not intended to become another automated application bot.

Its purpose is to become a career decision-support system.

Eventually it should help answer questions like:

- which kinds of jobs consistently lead to interviews
- which environments produce the best outcomes
- which opportunities align with long-term direction
- which jobs should be ignored before emotional energy is spent pursuing them

Finding opportunities is easy.

Recognizing the right ones is the harder problem.

## License

Licensed under the AGPL-3.0.

See `LICENSE`.
