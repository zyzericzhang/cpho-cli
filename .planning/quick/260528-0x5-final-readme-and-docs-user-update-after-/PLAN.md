---
status: complete
created_at: "2026-05-27T16:39:47.700Z"
---

# Quick Docs Update

## Goal

Update README and `docs/user` after Phase 6-8 and real API verification.

## Work

- Replace stale v1.0 tone references with Explain v2 panel commands.
- Document knowledge/community KB and generated-output ignore behavior.
- Link user errors docs.
- Keep secret guidance explicit: real keys stay in env/local configs and are not committed.

## Verification

```bash
uv run pytest tests/test_docs_user.py tests/test_docs_opensource.py -q
uv run ruff check .
```

