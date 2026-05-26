# Phase 4 Boundary Decisions

Workspace boundary checks use `Path.resolve()` before comparing paths. This means symlinks that point outside the workspace are rejected in v1, which is safer for compose/PDF file IO and matches the Phase 4 requirement to avoid file escape.

Runtime checkpoints are now written after every successful step as well as on failures. The record keeps `failed_step_id` for compatibility with existing resume code, but new checkpoint files also include `step_id` and `status` so future resume UI can distinguish passed and failed checkpoints.

