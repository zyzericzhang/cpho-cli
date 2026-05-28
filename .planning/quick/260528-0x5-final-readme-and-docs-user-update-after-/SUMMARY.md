---
status: complete
completed_at: "2026-05-27T16:40:00Z"
---

# Summary

Updated README and `docs/user` to match the verified Phase 6-8 state.

Verification:

- `uv run pytest tests/test_docs_user.py tests/test_docs_opensource.py -q` -> 5 passed.
- `uv run ruff check .` -> All checks passed.

