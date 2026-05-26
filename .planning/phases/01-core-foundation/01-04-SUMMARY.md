---
phase: 01-core-foundation
plan: "04"
subsystem: solve-pipeline
tags:
  - llm
  - openrouter
  - solve
requires:
  - 01-02
  - 01-03
provides:
  - OpenRouter provider
  - built-in solve skill
  - solve report schemas
  - cpho solve wiring
affects:
  - src/cpho_cli/core/llm.py
  - src/cpho_cli/core/solve.py
  - src/cpho_cli/cli/app.py
  - src/cpho_cli/builtin_skills/solve/
tech-stack:
  added:
    - httpx
    - OpenRouter chat completions API shape
  patterns:
    - provider abstraction
    - structured output schema payloads
key-files:
  created:
    - src/cpho_cli/core/llm.py
    - src/cpho_cli/core/solve.py
    - src/cpho_cli/models/llm.py
    - src/cpho_cli/models/solve.py
    - src/cpho_cli/builtin_skills/solve/SKILL.md
    - src/cpho_cli/builtin_skills/solve/skill.yml
    - src/cpho_cli/builtin_skills/solve/prompts/normalize.md.j2
    - src/cpho_cli/builtin_skills/solve/prompts/derive.md.j2
    - src/cpho_cli/builtin_skills/solve/prompts/cross_check.md.j2
    - src/cpho_cli/builtin_skills/solve/prompts/final_report.md.j2
    - tests/test_llm.py
    - tests/test_solve.py
  modified:
    - src/cpho_cli/cli/app.py
key-decisions:
  - "OpenRouter errors redact the API key."
  - "Solve reports require official answer references on derivation steps."
requirements-completed:
  - CORE-01
  - CORE-04
duration: "batch execution"
completed: "2026-05-22"
---

# Phase 1 Plan 04: Solve Pipeline Summary

OpenRouter provider, built-in solve skill, structured solve models, and `cpho solve` wiring are implemented.

## Commits

| Commit | Description |
|--------|-------------|
| `e4c577d` | Implemented OpenRouter provider, solve skill assets, solve models, and CLI wiring |
| `7c6e5ef` | Fixed non-dry-run solve path to call the LLM provider and validate `SolveReport` JSON |

## What Changed

- Added `OpenRouterProvider` with JSON schema payload support and redacted provider errors.
- Added built-in `solve` skill folder with seven D-09 step ids.
- Added Pydantic solve report models requiring official answer references.
- Added `solve_problem` and `cpho solve` dry-run path.

## Verification

- `uv run pytest tests/test_llm.py tests/test_solve.py tests/test_cli.py -q` passed.
- `uv run cpho solve --help` passed.
- Full `uv run pytest -q` passed: 30 tests.
- `uv run ruff check .` passed.
- `uv run mypy .` passed.

## Deviations from Plan

**[Rule 1 - Goal gap] Non-dry-run solve initially wrote a placeholder report instead of calling the LLM provider** -- Found during verifier-style self-check. Fixed by adding a failing test for provider invocation, then wiring `solve_problem` to call `LLMProvider.complete(..., response_model=SolveReport)` and validate the returned JSON in `7c6e5ef`.

**Total deviations:** 1 auto-fixed.
**Impact:** The real solve path now uses the provider abstraction instead of placeholder output.

## Self-Check: PASSED

Plan 04 requirements and acceptance criteria are satisfied.
