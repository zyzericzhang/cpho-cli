# Phase 5 Verification

## Automated Commands

- `uv run pytest tests/test_docs_opensource.py -q`
- `uv run pytest tests/test_docs_user.py -q`
- `uv run pytest tests/test_docs_extensions_examples.py -q`
- `uv run pytest tests/test_phase05_acceptance.py tests/test_docs_opensource.py tests/test_docs_user.py tests/test_docs_extensions_examples.py -q`
  - Result: 8 passed.
- `uv run pytest -q`
  - Result: 415 passed, 5 existing PyMuPDF/SWIG deprecation warnings.

## Decisions Recorded

- README now reflects the Phase 3/4 command surface and removes obsolete `eval` language.
- Demo is a checked-in SVG transcript at `.github/assets/cpho-demo.svg`.
- Public IPhO PNG assets are deferred until source/license verification; examples are repository-local placeholders.
- Extension docs describe explicit Python command registration, not unimplemented auto-scanning.
