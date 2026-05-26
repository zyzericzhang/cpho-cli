---
phase: 03-skill-cross-cutting-core-skills
plan: 03-06
status: complete
completed_at: 2026-05-26
branch: feature/phase3
---

# 03-06 Summary: Probe Core Service

## Implemented

- Added `cpho_cli.models.probe` with `ProbeTurn` and `ProbeTranscript`.
- Added `cpho_cli.core.probe.run_probe(...)` for continuous Q+A probing.
- Added the built-in `probe` skill folder and `next_turn` prompt contract.
- Probe appends each completed Q+A turn immediately to an incremental markdown transcript.
- Probe atomically rewrites the final markdown into `## 问题` followed by `## 解答`.
- Probe exits on `/exit` or two empty answers and prompts at the soft `probe.max_rounds` limit.
- Probe injects Solve discrepancy context when available.

## Design Decisions

- Probe replaces the old Quiz/YAML idea with a single-question coaching loop.
- The loop lives in the service layer; the LLM prompt only generates the next question.
- The soft round limit prompts before the next provider call to avoid spending tokens on an unanswered question.
- No Anki, Obsidian, scoring, or YAML export behavior was added in this phase.

## Verification

- `uv run pytest tests/test_probe.py tests/test_skills.py -q`
  - Result: 10 passed before the Solve-context assertion was added, then re-run in final 03-06 verification.
