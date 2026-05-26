---
phase: 05-user-manual-opensource
plan: 05-01
status: complete
completed_at: 2026-05-26
branch: feature/phase5
---

# 05-01 Summary: README and Open Source Metadata

## Implemented

- Rewrote README around the current Phase 3/4 command surface.
- Added SVG terminal demo asset.
- Added MIT license, contributing guide, code of conduct, and issue templates.
- Added `.claude/` to `.gitignore`.

## Design Decisions

- Removed obsolete `cpho eval` README references.
- Used a checked-in SVG transcript instead of invoking an external asciinema recorder.
- Deferred third-party public problem image assets until license/source verification.

## Verification

- `uv run pytest tests/test_docs_opensource.py -q`
