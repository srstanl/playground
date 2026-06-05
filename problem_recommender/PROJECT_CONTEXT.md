# Project Context: Problem Generation Engine

## Goal
Generate interview-style programming problems (business-oriented by default) with matching Java skeletons and JUnit tests.

## Default Assumptions
- Business-oriented framing unless a specific domain context is provided.
- Roles and levels influence framing, but the algorithmic core stays interview-appropriate.

## Naming Convention
Generated files follow:

```
{subject}-{level}-{role}-{difficulty}-{context?}.{ext}
```

- `context` is optional and only included if the prompt provides a domain (e.g., `healthcare`).
- Example (no context): `queues-senior-swe-medium.java`
- Example (with context): `queues-senior-swe-medium-healthcare.java`

### Test Files
- JUnit test files use the same base name plus `-test.java`.
- Example: `queues-senior-swe-medium-test.java`

## Output Targets
- Curated Java problem files live under `java/`.
- JUnit tests live alongside their matching Java files in `java/`.

## Content Guidelines
- Java skeletons include:
  - Clear problem statement + business framing
  - Method signature
  - TODO implementation stub
- JUnit tests include:
  - At least two concrete test cases
  - Deterministic expected outputs

## Core Patterns (Default Set)
- bfs-dfs
- hashmaps
- two-pointer-sorting
- sliding-window
- binary-search
- dynamic-programming
- priority-queue
- greedy
- union-find
- topological-sort
- backtracking

## Example Prompt
"queues senior swe java medium healthcare"

## Example Output
- `java/queues-senior-swe-medium-healthcare.java`
- `java/queues-senior-swe-medium-healthcare-test.java`
