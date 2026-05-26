---
phase: 03-skill-cross-cutting-core-skills
plan: 03-05
status: complete
completed_at: 2026-05-26
branch: feature/phase3
---

# 03-05 Summary: Explain Core Service

## Implemented

- Added `cpho_cli.models.explain` with tone, streamed chunk, per-tone output, and merged result models.
- Added `cpho_cli.core.explain.run_explain(...)` for multi-tone Explain generation.
- Added the built-in `explain` skill folder with teacher, dense, and brief prompt sets plus tag extraction.
- Each selected tone runs through two streamed calls: stage-one explanation and sentence-level explanation.
- Solve discrepancies are passed into Explain prompts when a `SolveReport` is available.
- Explain writes one merged `.explain.md` file through the Phase 3 export helper.
- Candidate tags are returned as untrusted candidates for later confirmation.

## Design Decisions

- Tone fan-out is kept outside `SkillRuntime`; the service uses `asyncio.gather` and isolated buffers per tone.
- Streaming is prose-only. Candidate tags use a complete JSON response after prose generation finishes.
- Missing Solve context is explicit in prompts instead of implicit or omitted.
- Candidate tags are not persisted here; REPL/index confirmation belongs to 03-07.

## Verification

- `uv run pytest tests/test_explain.py tests/test_skills.py -q`
  - Result: 7 passed.
