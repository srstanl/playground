# Project Context: Playground

## Purpose
`playground` is the workspace for experiments, prototypes, and low-commitment exploration.

Projects here are allowed to be rough, incomplete, or short-lived. The point is to learn quickly, test ideas, and discover whether something deserves more intentional investment.

## Operating Intent
- Prefer cheap experimentation over premature hardening.
- Keep just enough structure to preserve useful findings and next steps.
- Move projects out only when they show clear value and sustained direction.

## Relationship to Other Repositories
- `playground`: experiments, spikes, and early product shaping.
- `incubator`: selected candidates under active maturation with explicit backlog and exit criteria.
- `portfolio`: polished references, platform assets, and showcase-quality implementations.

## Repository Governance
- `main` branch protection for `playground` is managed from the shared ruleset baseline stored in `portfolio/scripts/github/rulesets/`.
- This is intentional: repository rules are treated as shared platform governance rather than duplicated per repository.

## Current Focus
- `problem_recommender` is the current highest-signal project in this repository.
- The active direction is to keep the CLI surface intact while shaping shared service logic, a deployable API boundary, and an eventual React UI MVP.

## Current Status
- Shared recommendation and corpus services have been extracted for reuse.
- A FastAPI MVP slice exists with health and recommend endpoints.
- The next delivery lane is tightening API contracts, runtime assumptions, and CI/CD onboarding readiness.
- React UI scope is now explicit enough to track as a parallel MVP lane rather than a vague future idea.

## Immediate Next Steps
1. Finish the request/response and testing contracts for the API lane.
2. Tighten storage, config, and observability assumptions.
3. Continue React UI MVP planning and shell implementation.
4. Decide when `problem_recommender` has earned transfer into `incubator`.

## Session Conventions
- Keyword: `start session`
- Meaning: begin a new work session by recapping the previous session and checking the board for the next task.
- `start session` checklist:
  1. Review `PROJECT_CONTEXT.md` for current status, decisions, and immediate next steps.
  2. Check the active board/epic and confirm the next `Ready` or planned task.
  3. Summarize repo state (clean vs in-flight changes).
  4. Propose the next concrete work item before making edits.

- Keyword: `save state`
- Meaning: current task reached a stopping point and work should be stored durably in remote history without waiting for follow-up prompts.
- `save state` checklist:
  1. Update `PROJECT_CONTEXT.md` (state, decisions, next action).
  2. Update impacted README/docs for accuracy.
  3. Run quick validation for touched areas when feasible.
  4. Summarize the changes and current git status.
  5. Check the current branch name; if it is `main`, create and switch to a new branch before committing.
  6. Commit the current work with a clear message.
  7. Push the current branch to remote.
  8. Call out any known validation gaps, CI blockers, or follow-up risks.

- Keyword: `end session`
- Meaning: session is ending.
- `end session` checklist:
  1. Update `PROJECT_CONTEXT.md` (state, decisions, next actions).
  2. Update impacted README/docs for accuracy.
  3. Run quick validation for touched areas when feasible.
  4. Update the active board/task state if progress changed during the session.
  5. Summarize the session changes and current repo state.
  6. Check the current branch name; if it is `main`, create and switch to a new branch before committing.
  7. Commit the current work with a clear message.
  8. Push the current branch to remote.
  9. Call out any known CI blockers, unresolved risks, or next recommended starting point.
