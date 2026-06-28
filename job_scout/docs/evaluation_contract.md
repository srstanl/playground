# Evaluation Contract

## Purpose
Define the baseline contract for converting an ingested job posting into a structured evaluation result that is explainable, locally reproducible, and suitable for later tracking.

## Design Principles
- Evaluation is driven primarily by the job description content.
- Company metadata is tracked but does not affect baseline scoring.
- The system must separate extraction from scoring so failures are easier to diagnose.
- Every scored conclusion should be supported by explicit evidence from the posting or marked as an inference.
- Human review remains the final decision point.

## Contract Version
- Version: `v1`
- Scope: Milestone 2 baseline evaluation only

## Evaluation Input
The evaluator accepts one persisted `JobPosting` record plus optional user profile context.

### Required Input
- `job_posting.id`
- `job_posting.raw_description`

### Optional Input
- `job_posting.title`
- `job_posting.location`
- `job_posting.source_system`
- `job_posting.source_url`
- `job_posting.company`
- `user_profile.resume_summary`
- `user_profile.skills`
- `user_profile.target_roles`
- `user_profile.location_preferences`
- `user_profile.compensation_preferences`
- `user_profile.work_mode_preferences`

## Baseline Evaluation Phases

### Phase 1: Extraction
Normalize the job posting into structured fields.

#### Required Extraction Output
- `role_title_normalized`
- `role_summary`
- `seniority`
- `employment_type`
- `location_text`
- `work_mode`
- `required_skills`
- `preferred_skills`
- `required_experience`
- `preferred_experience`
- `responsibilities`
- `compensation`
- `visa_or_clearance_requirements`
- `domain_signals`
- `risks`
- `evidence`

#### Extraction Rules
- Preserve uncertainty explicitly; do not invent missing details.
- Use `unknown` or empty collections when the posting does not support a field.
- Capture short evidence snippets for important extracted fields.
- Distinguish clearly between stated requirements and inferred requirements.

### Phase 2: Scoring
Apply the rubric to the extracted structure, not directly to raw free text.

#### Baseline Scoring Dimensions
- `role_alignment`
- `skills_alignment`
- `seniority_alignment`
- `location_alignment`
- `compensation_alignment`
- `work_mode_alignment`
- `constraint_risk`
- `posting_quality`

#### Scoring Rules
- Score each dimension on a `0-5` scale.
- `0` means strong mismatch or blocking concern.
- `3` means neutral, partial match, or insufficient signal.
- `5` means strong match with clear evidence.
- `constraint_risk` is inverse-friendly: higher score means lower risk.
- Missing data must reduce confidence, not fabricate a match.
- `company` must not influence any baseline dimension score.

#### Recommended Baseline Weights
- `role_alignment`: `0.25`
- `skills_alignment`: `0.30`
- `seniority_alignment`: `0.15`
- `location_alignment`: `0.10`
- `compensation_alignment`: `0.05`
- `work_mode_alignment`: `0.05`
- `constraint_risk`: `0.05`
- `posting_quality`: `0.05`

#### Weighted Score Output
- Produce `overall_score` on a `0-100` scale.
- Compute `overall_score` from the weighted normalized dimension scores.
- Produce a separate `confidence_score` on a `0-100` scale.
- Confidence reflects evidence quality and data completeness, not candidate fit.

## Evaluation Output Schema
The evaluator returns one structured result per job posting.

```json
{
  "contract_version": "v1",
  "job_posting_id": 123,
  "summary": {
    "headline": "Short evaluator summary",
    "recommendation": "apply|consider|skip|needs_review",
    "overall_score": 0,
    "confidence_score": 0
  },
  "extraction": {
    "role_title_normalized": "platform engineer",
    "role_summary": "...",
    "seniority": "senior|mid|staff|principal|unknown",
    "employment_type": "full_time|contract|part_time|intern|unknown",
    "location_text": "...",
    "work_mode": "remote|hybrid|onsite|unknown",
    "required_skills": [],
    "preferred_skills": [],
    "required_experience": [],
    "preferred_experience": [],
    "responsibilities": [],
    "compensation": {
      "currency": null,
      "min": null,
      "max": null,
      "interval": null
    },
    "visa_or_clearance_requirements": [],
    "domain_signals": [],
    "risks": [],
    "evidence": []
  },
  "scoring": {
    "dimensions": [
      {
        "name": "skills_alignment",
        "score": 0,
        "weight": 0.30,
        "rationale": "...",
        "evidence": []
      }
    ],
    "strengths": [],
    "gaps": [],
    "blocking_concerns": []
  },
  "provenance": {
    "source_system": "linkedin",
    "source_url": "https://...",
    "evaluated_at": "ISO-8601 timestamp"
  }
}
```

## Recommendation Semantics
- `apply`: strong fit with manageable risk and adequate confidence
- `consider`: plausible fit but notable gaps or weaker evidence
- `needs_review`: insufficient signal or conflicting evidence
- `skip`: clear mismatch or blocking requirement

## Evidence Requirements
- At least one evidence item is required for every non-neutral score.
- Evidence must reference actual job-posting text or explicitly state that the point is inferred.
- The evaluator should prefer short snippets over long quotation dumps.

## Non-Goals for `v1`
- Resume rewriting
- Company-specific scoring adapters
- Historical outcome learning
- Automatic application submission
- Browser-session scraping

## Acceptance Criteria
A `v1` evaluation is acceptable only if it:
- runs on a locally stored job posting
- produces deterministic structured output for the same extracted data and rubric version
- exposes score breakdown by dimension
- surfaces strengths, gaps, and blocking concerns
- separates score from confidence
- excludes company metadata from baseline scoring
- supports later persistence and tracking without changing record identity

## Implementation Notes
Recommended implementation order:
1. Add extraction and evaluation result models.
2. Implement deterministic rubric application over extracted fields.
3. Add a CLI command such as `evaluate <job_id>`.
4. Persist evaluation results separately from raw job postings.
5. Add tests using representative postings with known expected outputs.
