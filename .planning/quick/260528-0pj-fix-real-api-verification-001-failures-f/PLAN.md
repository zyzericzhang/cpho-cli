---
status: in_progress
created_at: "2026-05-27T16:30:38.665Z"
source_report: docs/test-001-real-api-verification.md
---

# Quick Fix: Real API Verification 001 Failures

## Goal

Fix the small issues found in `docs/test-001-real-api-verification.md` before running verification round 002.

## Scope

1. Add a shared JSON extraction helper that accepts fenced JSON while preserving strict dict/schema validation.
2. Use it in skill runtime LLM handlers, knowledge normalize, and explain tag extraction.
3. Stop workspace discovery from indexing generated artifacts directories.
4. Correct user docs for topic browse workspace argument and REPL exit wording.

## Verification

```bash
uv run pytest tests/test_json_utils.py tests/test_skills.py tests/test_knowledge.py tests/test_workspace.py tests/test_docs_user.py -q
uv run pytest -q
uv run ruff check .
```

