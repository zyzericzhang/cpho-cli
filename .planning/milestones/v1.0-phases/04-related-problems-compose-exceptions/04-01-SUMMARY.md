---
phase: 04-related-problems-compose-exceptions
plan: 04-01
status: complete
completed_at: 2026-05-26
branch: feature/phase4
---

# 04-01 Summary: Boundary and Runtime Checkpoints

## Implemented

- Added `cpho_cli.core.boundary`.
- Added `ensure_workspace_available(...)` and `ensure_in_workspace(...)`.
- Extended runtime checkpoints with `step_id` and `status`.
- Runtime now writes checkpoints after passed steps and failed steps when `checkpoint_dir` is configured.

## Design Decisions

- Boundary checks use resolved paths; symlinks escaping the workspace are rejected.
- Existing `failed_step_id` remains in failed checkpoint records for resume compatibility.

## Verification

- `uv run pytest tests/test_boundary.py tests/test_runtime.py -q`
  - Result: 14 passed.
