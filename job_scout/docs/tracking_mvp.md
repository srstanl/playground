# Job Scout Tracking MVP

## Purpose

Tracking is the third lane of Job Scout.

Ingestion answers:

- what did I capture?

Evaluation answers:

- should I care about this?

Tracking answers:

- what did I do next, what is pending, and what happened?

The MVP should stay operationally useful without trying to become a full CRM.

## Goals

The first tracking slice should make it easy to:

- mark whether a job was pursued
- track current application status
- record the most important dates
- keep lightweight notes and follow-up expectations
- preserve outcome data for later analysis

## Non-Goals

The MVP should not attempt to include:

- calendar integration
- email sync
- reminder delivery
- contact management as a full system
- rich event timelines for every micro-action
- automated reporting dashboards

Those can come later if the basic tracking model proves useful.

## MVP Scope

Tracking should be attached to an existing `JobPosting`.

One job posting may have zero or one active tracking record in v1.

That record should answer:

- was this job skipped, saved, or pursued?
- if pursued, where is it in the lifecycle?
- when was the last meaningful action taken?
- when should it be reviewed again?
- what was the result?

## Proposed Core Entity

### `ApplicationRecord`

Suggested v1 fields:

- `id`
- `job_posting_id`
- `decision`
- `status`
- `applied_at`
- `last_event_at`
- `next_follow_up_at`
- `outcome`
- `resume_variant`
- `notes`
- `created_at`
- `updated_at`

## Decision vs Status

These should remain separate.

### `decision`

This reflects the top-level human choice after evaluation.

Suggested values:

- `unreviewed`
- `saved`
- `skip`
- `apply`

### `status`

This reflects lifecycle state only if the opportunity is being actively tracked.

Suggested v1 values:

- `not_started`
- `application_ready`
- `applied`
- `recruiter_contact`
- `interviewing`
- `final_round`
- `offer`
- `rejected`
- `withdrawn`
- `closed`

## Outcome

Outcome should be explicit rather than inferred from status.

Suggested v1 values:

- `unknown`
- `no_response`
- `rejected`
- `withdrawn`
- `offer_declined`
- `offer_accepted`
- `position_closed`
- `hiring_paused`

This is useful because `closed` is not specific enough for future analytics.

## Lifecycle Rules

Basic expectations for v1:

- `skip` decision does not require a tracking lifecycle.
- `saved` means revisit later; it may have a `next_follow_up_at` without an `applied_at`.
- `apply` typically moves through `application_ready` -> `applied` -> later statuses.
- `position_closed` and `hiring_paused` should stop active follow-up unless the user chooses to revisit manually.
- terminal statuses are:
  - `offer`
  - `rejected`
  - `withdrawn`
  - `closed`

## Minimal CLI Surface

The first useful commands are:

```bash
python -m job_scout.cli track init <job_id>
python -m job_scout.cli track show <job_id>
python -m job_scout.cli track update <job_id> --decision apply --status applied
python -m job_scout.cli track note <job_id> --note "Recruiter replied, scheduling screen."
python -m job_scout.cli track list --status applied
```

The CLI should stay simple:

- initialize a tracking record
- view tracking state
- update status/decision/outcome
- append or replace notes
- filter tracked jobs

## Follow-Up Expectations

The MVP only needs one explicit follow-up field:

- `next_follow_up_at`

This is enough to support:

- “what needs attention this week?”
- “which applied jobs have gone stale?”

No reminder engine is required yet.

## Persistence Direction

Suggested v1 database shape:

### `application_records`

- one row per tracked job
- linked to `job_postings.id`

Optional future table:

### `application_events`

Do not build this in v1 unless the simple record proves insufficient.

If later needed, it can capture:

- status changes
- notes over time
- recruiter touchpoints
- interview milestones

## Analytics Intent

Tracking exists partly to support later analytics.

So the MVP should preserve enough structure to answer questions like:

- how many evaluated jobs were actually pursued?
- how many applications led to recruiter contact?
- which recommendation tiers produced interviews?
- which statuses tend to stall?

This means status and outcome fields should be normalized from the start.

## Recommended Delivery Order

1. Add and document the tracking data model.
2. Add persistence and repository helpers.
3. Add minimal CLI commands for init/show/update/list.
4. Add tests for lifecycle transitions and filtering.
5. Revisit whether event history is truly needed.

## Board Mapping

This document should satisfy planning needs for:

- `Task: Define v1 tracking scope and boundaries`
- `Task: Identify core tracking entities and lifecycle events`
- `Task: Define outcome and follow-up tracking expectations`

Implementation work can then be split separately.
