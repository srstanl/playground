# Contributing to Job Scout

Thank you for considering a contribution.

Job Scout is not trying to become a mass-application bot. The bar for changes is whether they improve decision quality, explainability, and long-term usefulness.

## What Good Contributions Look Like

Strong contributions usually improve one or more of these areas:

- evaluation quality
- reasoning clarity
- capability modeling
- semantic shape detection
- ingestion reliability
- tracking and outcome analysis
- documentation of design intent

## Principles

When contributing, optimize for these constraints:

- **Local first**: avoid moving sensitive career data off-machine by default.
- **Problem-space reasoning**: prefer capability and work-shape reasoning over keyword counting.
- **Explainability**: recommendations should remain understandable and defensible.
- **Identity consistency**: avoid changes that reward generic resume optimization over coherent career direction.
- **Human in the loop**: the system supports judgment; it should not replace it.

## Process

1. Start with the problem, not the implementation.
2. Open an issue or document the change intent clearly in the PR.
3. Keep changes focused and scoped.
4. Add or update tests when behavior changes.
5. Update docs when the evaluation model, workflow, or project philosophy changes.

## Development Notes

- Python `3.11+` is the expected baseline.
- Install locally with:

```bash
pip install -e .
```

- Run tests with:

```bash
python -m unittest tests.test_smoke
```

## High-Value Areas

Some contribution areas are especially useful:

- better capability ontology design
- improved semantic-shape inference
- cleaner risk categorization
- more reliable ingestion paths
- tracking and analytics primitives
- feedback-loop tooling that preserves human review

## Pull Request Guidance

A good pull request should explain:

- what problem it addresses
- why the current behavior is insufficient
- how the change improves evaluation quality or project clarity
- how the change was validated

## Code of Ownership

This project currently has a single maintainer, but outside contributions are still welcome. `CODEOWNERS` exists to keep review expectations explicit as the project grows.
