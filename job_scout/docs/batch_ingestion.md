# Job Scout Batch Ingestion

## Purpose

Batch ingestion exists for cases where multiple job descriptions are captured at once and should be imported without repeating the single-file workflow for each posting.

The first supported batch format should prioritize reliable parsing over convenience heuristics.

## Supported v1 Format

The v1 batch format is `jsonl` (newline-delimited JSON).

Each non-empty line represents exactly one job posting.

## Why `jsonl` First

- explicit record boundaries
- partial failure handling is straightforward
- metadata can travel with each job
- easier to validate than freeform pasted text
- easier to retry and debug than one large multi-job blob

## CLI Contract

```bash
python -m job_scout.cli ingest-batch --jsonl ./jobs.jsonl
```

## Record Shape

### Required

- `source_system`
- `raw_description`

### Optional

- `source_url`
- `external_ids`
- `company`
- `title`
- `location`

## Example

```json
{"source_system":"linkedin","source_url":"https://example.com/jobs/1","external_ids":{"linkedin":"li-123","greenhouse":"gh-789"},"company":"Example Co","title":"Platform Engineer","location":"Remote","raw_description":"Full JD text here"}
{"source_system":"indeed","source_url":"https://example.com/jobs/2","external_ids":{"indeed":"indeed-456"},"company":"Another Co","title":"Senior DevOps Engineer","location":"Remote US","raw_description":"Full JD text here"}
```

## Validation Rules

- blank lines are ignored
- invalid JSON fails only that line
- `source_system` must exist and be non-empty
- `raw_description` must exist and be non-empty
- `external_ids`, when present, must be a JSON object of `{source_name: external_id}`
- unknown fields are ignored but surfaced as warnings
- valid rows should still ingest even if other rows fail

## `external_ids`

`external_ids` is the structured identifier mapping for a posting across source systems.

- keys are upstream source names such as `linkedin`, `greenhouse`, or `lever`
- values are opaque posting identifiers from those systems
- Job Scout preserves these values exactly as supplied
- manual CLI ingest still accepts `--external-id` as shorthand for `{<source_system>: <external_id>}`

## Output Expectations

Batch ingest should print:

- one success line per ingested record
- one error line per failed record, including line number
- one warning line per ignored field group, including line number
- a final summary with:
  - total processed
  - ingested
  - failed
  - warnings

## Non-Goals

The v1 batch ingest path does not attempt:

- duplicate detection
- delimiter guessing in freeform text
- auto-splitting one pasted blob into postings
- schema evolution or migration logic

## Deferred Format

A human-oriented delimited text format may be added later for copy/paste-heavy workflows, but it should come after `jsonl` proves insufficient.
