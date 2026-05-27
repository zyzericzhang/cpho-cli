---
phase: 07-explain-v2
plan: 07-04
status: complete
completed: 2026-05-27
key-files:
  - src/cpho_cli/models/explain.py
  - src/cpho_cli/core/explain.py
  - src/cpho_cli/builtin_skills/explain/prompts/
  - tests/test_explain.py
---

# 07-04 Summary: Explain v2 Panels

## Outcome

Replaced production Explain Tone models and orchestration with Explain v2 panel generation.

## Tasks Completed

| Task | Result | Commit |
|------|--------|--------|
| Explain v2 models and prompts | Added panel/provenance models and panel prompts for approach, answer replacement, and alternative methods | `aad10c3` |
| Knowledge-first panel generation | `run_explain` now queries `KnowledgeResolver`, injects knowledge references, writes selected panels only, and records provenance | `aad10c3` |

## Verification

- `uv run pytest tests/test_explain.py -q`
  - Result: 2 passed.
- `uv run ruff check src/cpho_cli/models/explain.py src/cpho_cli/core/explain.py tests/test_explain.py`
  - Result: all checks passed.

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

Production Explain no longer imports `ExplainTone`; REPL/docs integration follows in 07-05.

