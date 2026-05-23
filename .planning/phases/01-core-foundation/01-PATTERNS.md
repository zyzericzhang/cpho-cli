# Phase 1: Core Foundation - Pattern Map

**Generated:** 2026-05-22
**Status:** Greenfield pattern map

## Codebase Inventory

The repository now has a `uv` src-layout implementation under `src/cpho_cli/`, tests under `tests/`, and Phase 1 core plumbing in place. Earlier Phase 1 started greenfield; future work should prefer the implementation patterns in code first, then the locked architecture decisions in:

- `.planning/phases/01-core-foundation/01-CONTEXT.md`
- `docs/architecture-decisions.md`
- `docs/product-spec.md`
- `.planning/PROJECT.md`

## File Role Map

| Planned Area | Planned Files | Closest Existing Analog | Pattern to Follow |
|--------------|---------------|-------------------------|-------------------|
| Project scaffold | `pyproject.toml`, `README.md`, `.gitignore` | None | uv src-layout, Python >=3.11, ruff + mypy + pytest commands |
| CLI shell | `src/cpho_cli/cli/app.py` | None | Thin adapter only; core returns values, CLI renders output |
| Config | `src/cpho_cli/core/config.py`, `src/cpho_cli/models/config.py` | `.planning/config.json` only conceptually | Default `config.local.yml`, optional `--config`, provider profiles, env fallback, no secrets in git |
| Workspace discovery | `src/cpho_cli/core/workspace.py` | None | Deterministic file system scan with ambiguity diagnostics |
| Document/OCR | `src/cpho_cli/core/documents.py`, `src/cpho_cli/core/ocr.py` | None | Project-owned DTOs wrapping external library outputs |
| Skill runtime | `src/cpho_cli/core/skills.py`, `src/cpho_cli/core/runtime.py` | GSD skill files conceptually | Skill folder with `SKILL.md`, YAML metadata, prompts, optional tools |
| LLM provider | `src/cpho_cli/core/llm.py` | None | Provider protocol + OpenRouter implementation |
| Solve orchestration | `src/cpho_cli/core/solve.py`, `src/cpho_cli/builtin_skills/solve/` | None | Built-in solve skill executes through generic runtime |
| Golden eval | `src/cpho_cli/core/eval.py`, `golden_tests/` | None | Per-problem YAML specs, pytest and CLI entrypoints |

## Data Flow

`cpho solve <problem.pdf>` should flow through:

1. CLI parses args and config overrides.
2. Core config loads `config.local.yml` by default unless `--config` is supplied, resolves the selected provider profile/API key, and resolves model parameters.
3. Workspace discovery pairs problem and answer key.
4. Document loader extracts/rasterizes pages.
5. OCR adapter returns normalized `OCRBlock` objects with confidence.
6. Skill runtime executes built-in solve DAG over a blackboard.
7. OpenRouter provider returns structured JSON validated by Pydantic.
8. Runtime writes trace/checkpoint JSONL.
9. Solver assembles final structured report with answer-key cross references and discrepancy flags.

## Notes for Planner

- Prefer existing implementation files as the source of local style and contracts.
- Every implementation task must create or update focused tests alongside production changes.
- Use the locked src-layout and core-shell split as the local pattern.
