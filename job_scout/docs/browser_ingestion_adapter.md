# Browser Tab Ingestion Adapter

## Purpose

Job Scout should be able to ingest a job posting from the current browser tab without pushing browser-specific logic into the evaluator or persistence core.

The browser adapter boundary is:

- adapter contract: `job_scout.adapters.browser.BrowserTabJobCapture`
- application workflow: `job_scout.application.ingest.ingest_browser_tab_capture(...)`

The evaluator remains transport-agnostic. It still receives a persisted `JobPosting` record and evaluates that record the same way it evaluates CLI or batch-ingested jobs.

## Stable Capture Contract

`BrowserTabJobCapture` represents the minimum stable payload a browser integration should produce:

- `source_system`
- `page_url`
- `raw_description`
- `captured_at`
- optional normalized fields:
  - `company`
  - `title`
  - `location`
  - `external_ids`
- optional browser metadata:
  - `page_title`
  - `browser_name`
  - `window_id`
  - `tab_id`
  - `capture_method`
  - `selected_text`

Only the normalized posting fields cross into the core ingest payload. Browser metadata stays adapter-facing, with a compact reference string stored as `source_reference`.

## Browser Metadata Needed

A future Chrome/Codex adapter should capture:

- canonical page URL for traceability
- source system name such as `linkedin`, `greenhouse`, or `lever`
- extracted full job description text
- extracted title, company, and location when available
- source-specific identifiers when they can be inferred
- capture timestamp
- capture method such as full tab text vs selected text

Useful but non-essential metadata:

- browser name
- window ID
- tab ID
- page title

These fields are useful for debugging capture quality and replaying ingestion flows, but they should not affect evaluation behavior.

## Flow

1. Browser integration captures tab metadata and normalized job content.
2. Adapter constructs `BrowserTabJobCapture`.
3. Application layer converts it to `JobPostingInput`.
4. Persistence stores it as a regular `job_postings` row with `source_type="browser_tab"`.
5. Existing `evaluate` and `track` flows operate on the persisted record unchanged.

## Non-Goals

This boundary does not yet implement:

- live browser automation
- HTML parsing inside the evaluator
- schema changes for storing full browser metadata
- browser-specific scoring behavior
