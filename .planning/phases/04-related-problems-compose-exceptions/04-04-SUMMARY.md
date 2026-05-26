---
phase: 04-related-problems-compose-exceptions
plan: 04-04
status: complete
completed_at: 2026-05-26
branch: feature/phase4
---

# 04-04 Summary: PDF Assembly

## Implemented

- Added `cpho_cli.core.compose_pdf`.
- Added `assemble_composition_pdfs(...)`.
- Generates separate problem and answer PDFs.
- Preserves source page ranges with PyMuPDF `insert_pdf`.
- Adds PDF outlines for `第 N 题` and `第 N 题 答案`.
- Emits warnings for missing answer PDFs.

## Design Decisions

- Pass slots become blank pages to preserve slot numbering.
- Answer assembly reuses `problem_page_range` against `answer_path` until index entries carry answer-specific page ranges.

## Verification

- `uv run pytest tests/test_compose_pdf.py -q`
  - Result: 2 passed, 5 existing PyMuPDF/SWIG deprecation warnings.
