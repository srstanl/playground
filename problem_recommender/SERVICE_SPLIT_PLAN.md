# Problem Recommender Service Split Plan

## Purpose
Define the target module layout and shared service interfaces for supporting both:
- a CLI product surface
- a deployed web/API product surface

The rule is simple:
- core behavior is shared
- CLI and web are thin adapters over the same services

## Target Architecture

```text
problem_recommender/
├── api/                         # FastAPI app, HTTP routes, request/response models
├── cli/                         # interactive shell, CLI commands, rich output
├── domain/                      # core entities and business rules
├── services/                    # orchestration layer used by both CLI and API
├── adapters/                    # filesystem, model provider, persistence, test runners
├── java/                        # curated Java corpus
├── generated_problems/          # generated artifacts
├── data/                        # local state and cached metadata
├── tests/                       # unit, integration, API parity tests
├── main.py                      # CLI entrypoint wrapper
└── README.md
```

## Design Principle
The CLI and API should match in capability, not necessarily in user experience.

That means both surfaces should support:
- recommend problems
- generate problems
- list generated problems
- run tests
- view progress and insights
- rescan the corpus

But only the CLI needs things like:
- interactive prompts
- rich terminal formatting
- local file-path shortcuts tuned for humans

## Core Layers

### `domain/`
Contains the stable business concepts.

Suggested modules:
- `domain/problems.py`
- `domain/recommendations.py`
- `domain/generation.py`
- `domain/testing.py`
- `domain/progress.py`
- `domain/insights.py`

Suggested entities:
- `ProblemRecord`
- `RecommendationRequest`
- `RecommendationResult`
- `GenerationRequest`
- `GeneratedProblemRecord`
- `TestExecutionRequest`
- `TestExecutionResult`
- `ProgressSnapshot`
- `InsightReport`

This layer should not know about:
- FastAPI
- Rich/CLI prompts
- raw filesystem paths beyond typed values
- specific model provider SDKs

### `services/`
Contains shared use-case orchestration.

Suggested services:
- `RecommendationService`
- `GenerationService`
- `TestingService`
- `ProgressService`
- `CorpusService`
- `InsightService`

These services coordinate adapters and return domain objects.

### `adapters/`
Contains implementation details for IO and integration points.

Suggested adapters:
- `adapters/filesystem/problem_repository.py`
- `adapters/filesystem/generated_problem_repository.py`
- `adapters/filesystem/progress_repository.py`
- `adapters/filesystem/feedback_repository.py`
- `adapters/models/openai_generator.py`
- `adapters/models/github_models_generator.py`
- `adapters/testing/java_test_runner.py`
- `adapters/testing/python_test_runner.py`
- `adapters/testing/javascript_test_runner.py`
- `adapters/testing/csharp_test_runner.py`

The existing modules are close to this layer already:
- `problem_analyzer.py`
- `problem_generator.py`
- `feedback_engine.py`
- `progress_tracker.py`
- `test_executor.py`

They should be refactored behind narrower interfaces rather than called directly by the CLI forever.

## Surface Layers

### `cli/`
Owns terminal interaction only.

Suggested modules:
- `cli/app.py`
- `cli/commands/recommend.py`
- `cli/commands/generate.py`
- `cli/commands/test.py`
- `cli/commands/insights.py`
- `cli/presenters/*.py`

Responsibilities:
- prompt collection
- command routing
- rendering tables/panels/messages
- translating service results into terminal output

### `api/`
Owns deployed service behavior.

Suggested modules:
- `api/app.py`
- `api/routes/recommend.py`
- `api/routes/generate.py`
- `api/routes/test.py`
- `api/routes/progress.py`
- `api/routes/admin.py`
- `api/models.py`

Responsibilities:
- HTTP routing
- request validation
- response serialization
- health/readiness endpoints
- auth hooks later if needed

## First Shared Service Interfaces

### `RecommendationService`
Primary job: return ranked recommendations from one request.

Suggested interface:

```python
class RecommendationService:
    def recommend(self, request: RecommendationRequest) -> list[RecommendationResult]:
        ...
```

Inputs should capture:
- query text
- max results
- preferred languages
- target role
- optional difficulty preferences

Dependencies:
- problem corpus repository
- rules engine
- optional AI ranker
- feedback/profile repository

### `GenerationService`
Primary job: generate and persist a new problem artifact.

Suggested interface:

```python
class GenerationService:
    def generate(self, request: GenerationRequest) -> GeneratedProblemRecord:
        ...
```

Inputs should capture:
- prompt/query
- language
- role
- difficulty
- persistence mode

Dependencies:
- generator provider adapter
- generated problem repository
- optional metadata repository

### `TestingService`
Primary job: execute tests for a submitted solution and return normalized results.

Suggested interface:

```python
class TestingService:
    def run(self, request: TestExecutionRequest) -> TestExecutionResult:
        ...
```

Inputs should capture:
- problem identifier
- solution path or submitted source
- language
- execution mode

Dependencies:
- problem repository
- language-specific test runner
- progress/feedback repositories

### `ProgressService`
Primary job: manage attempts, completions, and summary stats.

Suggested interface:

```python
class ProgressService:
    def mark_attempted(self, problem_name: str) -> None:
        ...

    def mark_completed(self, problem_name: str) -> None:
        ...

    def get_snapshot(self) -> ProgressSnapshot:
        ...
```

### `InsightService`
Primary job: translate feedback and progress into human-readable learning signals.

Suggested interface:

```python
class InsightService:
    def get_report(self) -> InsightReport:
        ...
```

### `CorpusService`
Primary job: rescan and expose the curated problem corpus.

Suggested interface:

```python
class CorpusService:
    def rescan(self) -> list[ProblemRecord]:
        ...

    def list_problems(self) -> list[ProblemRecord]:
        ...
```

## Parity Rules Between CLI and API

The CLI and API should call the same service methods for core actions.

Parity targets:
- CLI `generate` and API `POST /generate` use `GenerationService.generate`
- CLI recommendation flow and API `POST /recommend` use `RecommendationService.recommend`
- CLI `test` and API `POST /test` use `TestingService.run`
- CLI `insights` and API `GET /insights` use `InsightService.get_report`
- CLI `rescan` and API admin rescan route use `CorpusService.rescan`

If CLI and API start branching in logic, the architecture is drifting.

## Recommended Endpoint Mapping

Suggested initial API surface:
- `GET /health`
- `POST /recommend`
- `POST /generate`
- `GET /generated`
- `POST /test`
- `GET /progress`
- `GET /insights`
- `POST /admin/rescan`

## Suggested Refactor Order

### Step 1
Create `services/` and extract:
- `RecommendationService`
- `CorpusService`

This enables:
- CLI staying functional
- first API slice for recommendations

### Step 2
Move generation into `GenerationService` and isolate provider adapters.

### Step 3
Move test execution behind `TestingService` with language-specific runners.

### Step 4
Add `api/` with FastAPI and wire the first endpoints.

### Step 5
Refactor `main.py` into a thin CLI bootstrap that delegates to `cli/app.py` and shared services.

## Minimum First Slice
The smallest worthwhile implementation is:
- extract `RecommendationService`
- extract `CorpusService`
- add FastAPI app with:
  - `GET /health`
  - `POST /recommend`
- keep CLI using the same service objects

That gives immediate proof that the deployed surface and local CLI can share real behavior.

## Decision
Keep the CLI as its own component.
Do not make the API a second implementation.
Make both surfaces consumers of the same service layer.
