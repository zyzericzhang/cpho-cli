---
phase: 05-user-manual-opensource
plan: 05-03
status: complete
completed_at: 2026-05-26
branch: feature/phase5
---

# 05-03 Summary: Extension Guide and Examples

## Implemented

- Added `docs/user/extensions.md`.
- Added `examples/README.md`, `sample-problem.md`, and `sample-answer.md`.
- Added tests for extension out-of-scope wording and examples.

## Design Decisions

- Documented explicit Python command registration instead of unimplemented auto-scanning.
- Used repository-local Markdown examples; public IPhO image assets are deferred pending source/license verification.

## Verification

- `uv run pytest tests/test_docs_extensions_examples.py -q`
