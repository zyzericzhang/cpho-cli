---
phase: 04-related-problems-compose-exceptions
type: patterns
created_at: 2026-05-26
branch: feature/phase4
---

# Phase 4 Patterns

## Keep Core Services Thin

Follow Phase 3: core services own deterministic work and markdown/PDF outputs; CLI/REPL only parse arguments, resolve current problem/workspace, and print results.

## Seeded Index Tests

Phase 4 should continue using seeded `.cpho/index.jsonl` fixtures for related/compose logic. Full real-workspace indexing is too expensive for normal tests.

## PDF Handling

Use PyMuPDF directly:

- `fitz.open(source)` for input.
- `output.insert_pdf(source, from_page=start_zero, to_page=end_zero)` for page preservation.
- `output.set_toc(...)` for `第 N 题` bookmarks.

Do not render LaTeX, crop pages, watermark, or re-layout in v1.

## Boundaries

Every user-provided path should be resolved and checked against the workspace root before heavy IO. Use `resolve()` comparison and emit Chinese errors.

## GSD Slices

Plan order should make later work depend on stable foundations:

1. Boundary/checkpoint foundation.
2. Related service and REPL state.
3. Composition schema and selection.
4. PDF assembly.
5. CLI/REPL command integration.
6. Acceptance and docs.

