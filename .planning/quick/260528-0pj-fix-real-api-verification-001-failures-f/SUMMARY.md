---
status: complete
completed_at: "2026-05-27T16:36:00Z"
---

# Summary

## Completed

- Added shared fenced JSON extraction in `src/cpho_cli/core/json_utils.py`.
- Applied it to skill LLM handlers, knowledge normalize, and explain candidate tag parsing.
- Updated workspace discovery to ignore generated output directories such as `artifacts/`, `outputs/`, and `.cpho/`.
- Corrected REPL exit wording in README and `docs/user/probe.md`.
- Recorded Test 002 real API verification in `docs/test-002-real-api-verification.md`.

## Verification

```bash
uv run pytest tests/test_json_utils.py tests/test_workspace.py tests/test_skills.py tests/test_knowledge.py tests/test_docs_user.py -q
uv run pytest -q
uv run ruff check .
```

Results:

- Targeted: 25 passed.
- Full pytest: 456 passed, 5 PyMuPDF/SWIG warnings.
- Ruff: All checks passed.

Real API retests:

- `cpho solve`: passed and wrote report JSON/Markdown.
- `cpho knowledge normalize`: passed and wrote draft.
- `cpho index` fresh workspace with artifact PDF: scanned only 1 real problem.
- `cpho knowledge sync`: passed against a temporary real GitHub release, then release/tag were deleted.

