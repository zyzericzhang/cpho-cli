---
phase: 04-related-problems-compose-exceptions
plan: 04-02
status: complete
completed_at: 2026-05-26
branch: feature/phase4
---

# 04-02 Summary: Related Problems Skill

## Implemented

- Added `cpho_cli.core.related.find_related_report(...)`.
- Added markdown export for related-problem reports.
- Added `SessionState.last_related`.
- Added REPL `/search-related [problem_id] [--top N] [--min-shared N]`.
- Registered related command in the REPL command installer.

## Design Decisions

- Reused existing `find_related_problems()` scoring.
- Kept `last_related` as explicit session state, not an implicit compose input.
- Did not mutate index machine tags or user tags.

## Verification

- `uv run pytest tests/test_related.py tests/test_repl_related_commands.py -q`
  - Result: 2 passed.
