---
phase: 03-skill-cross-cutting-core-skills
plan: 03-07
status: complete
completed_at: 2026-05-26
branch: feature/phase3
---

# 03-07 Summary: REPL and Index Integration

## Implemented

- Replaced Phase 3 placeholders with `/solve`, `/explain`, and `/probe` REPL commands.
- Removed `/quiz` registration from the built-in skill command surface.
- Added `cli.repl.adapters.skill_command` helpers for current problem resolution, provider/model setup, prompt input, confirmation, and text extraction.
- `/solve` stores accepted reports in `session.current_solve_report` and can persist confirmed discrepancies to index `user_tags`.
- `/explain` passes `session.current_solve_report` into the Explain service, confirms candidate tags, supports `+tag` append, and persists confirmed tags as `skill_name="explain"`.
- `/explain` and `/probe` warn without blocking when no prior Solve report exists.
- Successful `/explain` prints the Probe secondary entry prompt and starts `/probe` for the same problem when the user enters `/probe`.
- `/probe` uses `session.probe_max_rounds` and the shared prompt bridge.

## Design Decisions

- Command registration is explicit per skill rather than generic auto-registration because confirmation and handoff differ by skill.
- Solve discrepancy persistence is opt-in via `--persist-tags`.
- Explain candidate tags are always confirmed before index writeback.
- The REPL adapter does not implement ad hoc PDF answer OCR; it passes answer source context unless a text answer is available.

## Verification

- `uv run pytest tests/test_repl_builtin_commands.py tests/test_repl_runtime.py tests/test_index_api.py -q`
  - Result: 33 passed.
- `uv run ruff check src/cpho_cli/cli/repl/adapters/skill_command.py src/cpho_cli/cli/repl/commands/builtin_skills.py tests/test_repl_builtin_commands.py tests/test_index_api.py`
  - Result: all checks passed.
