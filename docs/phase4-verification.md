# Phase 4 Verification

## Automated Commands

- `uv run pytest tests/test_boundary.py tests/test_runtime.py -q`
- `uv run pytest tests/test_related.py tests/test_repl_related_commands.py -q`
- `uv run pytest tests/test_composition_models.py tests/test_composition_selection.py -q`
- `uv run pytest tests/test_compose_pdf.py -q`
- `uv run pytest tests/test_compose_cli.py tests/test_repl_compose_commands.py tests/test_topic_cli.py tests/test_repl_phase02_2_acceptance.py -q`
- `uv run pytest tests/test_phase04_acceptance.py -q`
- `uv run pytest tests/test_boundary.py tests/test_runtime.py tests/test_related.py tests/test_repl_related_commands.py tests/test_composition_models.py tests/test_composition_selection.py tests/test_compose_pdf.py tests/test_compose_cli.py tests/test_repl_compose_commands.py tests/test_topic_cli.py tests/test_repl_phase02_2_acceptance.py tests/test_phase04_acceptance.py -q`
  - Result: 37 passed, 5 existing PyMuPDF/SWIG deprecation warnings.
- `uv run pytest -q`
  - Result: 407 passed, 5 existing PyMuPDF/SWIG deprecation warnings.

## Real Workspace Policy

Acceptance tests read `/Users/ericzhang/Desktop/物理竞赛资料` only to copy a representative PDF into `tmp_path`. All indexes, composition files, related markdown, and assembled PDFs are written under the temporary workspace.

## Key Decisions

- Related search remains a thin wrapper over `find_related_problems()` and stores `last_related` only in REPL session state.
- Composition YAML supersedes the old `cpho compose --topic/--tags` printed filter command.
- PDF assembly preserves source pages with PyMuPDF `insert_pdf`; no formula re-rendering or watermarking is performed.
- Pass slots become blank pages to preserve slot numbering.
- Because `IndexEntry` does not have answer page ranges, v1 uses `problem_page_range` against `answer_path` for answer PDFs.
- Workspace boundary checks use resolved paths; symlinks escaping the workspace are rejected.
