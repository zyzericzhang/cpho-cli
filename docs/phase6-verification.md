# Phase 6 Verification

Date: 2026-05-27

## Scope

Phase 6 delivered:

- SkillPipeline metadata on existing `SkillSpec`.
- Private knowledge file parsing and validation.
- `KnowledgeResolver.find_for_problem(problem_id)`.
- Draft-first knowledge normalization and reviewed publish flow.
- `cpho knowledge normalize|publish|find`.

Community sync, Explain v2, model panel, and error index are Phase 7/8 work and are not documented here as shipped.

## Commands Run

- `uv run pytest tests/test_skills.py -q`
  - Result: 7 passed.
- `uv run pytest tests/test_knowledge.py -q`
  - Result: 7 passed.
- `uv run pytest tests/test_knowledge_cli.py tests/test_docs_user.py tests/test_cli.py -q`
  - Result: 6 passed.
- `uv run pytest tests/test_skills.py tests/test_knowledge.py tests/test_knowledge_cli.py tests/test_phase06_acceptance.py -q`
  - Result: 17 passed.
- `uv run ruff check .`
  - Result: all checks passed.
- `uv run pytest -q`
  - Result: 426 passed, 5 existing PyMuPDF/SWIG deprecation warnings.

## Acceptance Notes

- Acceptance test uses a tiny workspace shaped like the real physics workspace, including Chinese directory/PDF names.
- Knowledge files resolve by indexed canonical tag.
- Published private files are returned before future community matches.
- Existing built-in skill YAML loads unchanged.
- No API keys or local provider secrets are recorded in this document.

