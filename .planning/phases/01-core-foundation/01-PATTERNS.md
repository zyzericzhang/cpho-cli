# Phase 1: Core Foundation - Pattern Map

**Generated:** 2026-05-22
**Status:** Greenfield pattern map

## Codebase Inventory

The repository currently has no `src/`, `tests/`, `pyproject.toml`, or implementation files. Phase 1 is greenfield. The closest authoritative patterns are therefore the locked architecture decisions in:

- `.planning/phases/01-core-foundation/01-CONTEXT.md`
- `docs/architecture-decisions.md`
- `docs/product-spec.md`
- `.planning/PROJECT.md`

## File Role Map

| Planned Area | Planned Files | Closest Existing Analog | Pattern to Follow |
|--------------|---------------|-------------------------|-------------------|
| Project scaffold | `pyproject.toml`, `README.md`, `.gitignore` | None | uv src-layout, Python >=3.11, ruff + mypy + pytest commands |
| CLI shell | `src/cpho_cli/cli/app.py` | None | Thin adapter only; core returns values, CLI renders output |
| Config | `src/cpho_cli/core/config.py`, `src/cpho_cli/models/config.py` | `.planning/config.json` only conceptually | YAML config, env overrides, no secrets in git |
| Workspace discovery | `src/cpho_cli/core/workspace.py` | None | Deterministic file system scan with ambiguity diagnostics |
| Document/OCR | `src/cpho_cli/core/documents.py`, `src/cpho_cli/core/ocr.py` | None | Project-owned DTOs wrapping external library outputs |
| Skill runtime | `src/cpho_cli/core/skills.py`, `src/cpho_cli/core/runtime.py` | GSD skill files conceptually | Skill folder with `SKILL.md`, YAML metadata, prompts, optional tools |
| LLM provider | `src/cpho_cli/core/llm.py` | None | Provider protocol + OpenRouter implementation |
| Solve orchestration | `src/cpho_cli/core/solve.py`, `src/cpho_cli/builtin_skills/solve/` | None | Built-in solve skill executes through generic runtime |
| Golden eval | `src/cpho_cli/core/eval.py`, `golden_tests/` | None | Per-problem YAML specs, pytest and CLI entrypoints |

## Data Flow

`cpho solve <problem.pdf>` should flow through:

1. CLI parses args and config overrides.
2. Core config resolves OpenRouter key and model parameters.
3. Workspace discovery pairs problem and answer key.
4. Document loader extracts/rasterizes pages.
5. OCR adapter returns normalized `OCRBlock` objects with confidence.
6. Skill runtime executes built-in solve DAG over a blackboard.
7. OpenRouter provider returns structured JSON validated by Pydantic.
8. Runtime writes trace/checkpoint JSONL.
9. Solver assembles final structured report with answer-key cross references and discrepancy flags.

## Notes for Planner

- No plan should reference prior implementation files because none exist.
- Every implementation task must create its own tests alongside new production files.
- Use the locked src-layout and core-shell split as the local pattern.

