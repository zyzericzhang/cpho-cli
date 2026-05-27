---
phase: 02-tag-indexing
plan: "01"
subsystem: core-index
tags: [pydantic, jsonl, yaml, vocabulary, strictmodel]
requires:
  - phase: 01-core-foundation
    provides: StrictModel, YAML config loading patterns, JSONL trace patterns
provides:
  - Strict Pydantic schemas for index entries, vocabulary, fingerprints, notebook notes, and run stats
  - Atomic JSONL index read/write helpers with index-specific exceptions
  - Three-layer vocabulary loader with alias normalization and pending candidate reader
affects: [phase-02-tag-indexing, phase-03-skill-system, phase-04-knowledge-network]
tech-stack:
  added: []
  patterns:
    - StrictModel for all new index schemas
    - Atomic tmp-file plus Path.replace writes for JSONL index storage
    - Builtin to workspace to private vocabulary merge with last-layer-wins precedence
key-files:
  created:
    - src/cpho_cli/models/index.py
    - src/cpho_cli/core/index/__init__.py
    - src/cpho_cli/core/index/storage.py
    - src/cpho_cli/core/index/vocabulary.py
    - tests/test_index_models.py
    - tests/test_index_storage.py
    - tests/test_index_vocabulary.py
  modified: []
key-decisions:
  - "Forced vocabulary tag layer from file location while preserving schema defaults for other fields."
  - "Kept builtin vocabulary content and package-data changes out of this plan as assigned to Plan 02-06."
patterns-established:
  - "Index models inherit StrictModel and use Field(default_factory=list) for mutable lists."
  - "Index storage writes complete JSONL files through .tmp files followed by Path.replace."
  - "Vocabulary aliases normalize with NFKC, casefolding, and punctuation stripping."
requirements-completed: [IDX-01, IDX-03]
duration: about 20min
completed: 2026-05-23
---

# Phase 02 Plan 01: Index Data Models, JSONL Storage & Vocabulary Foundation Summary

**Strict index schemas with atomic JSONL storage and three-layer controlled vocabulary loading**

## Performance

- **Duration:** about 20 min
- **Started:** 2026-05-23T09:03:00Z
- **Completed:** 2026-05-23T09:22:40Z
- **Tasks:** 3/3
- **Files modified:** 8

## Accomplishments

- Added the Phase 2 index schema foundation: canonical tags, candidate tags, fingerprints, notebook entries, index rows, and run stats.
- Added atomic JSONL storage for `.cpho/index.jsonl`, including missing-index errors and blank-line tolerant loading.
- Added vocabulary YAML loading for builtin, workspace, private, and pending layers with deterministic alias indexing.

## Task Commits

1. **Task 1: Define all Pydantic schemas in models/index.py** - `0ad32b6` (`feat`)
2. **Task 2: JSONL storage layer with atomic writes** - `0ec3b77` (`feat`)
3. **Task 3: Three-layer vocabulary loader + alias normalization** - `a0ab883` (`feat`)

**Plan metadata:** committed separately after summary self-check.

## Files Created/Modified

- `src/cpho_cli/models/index.py` - StrictModel schemas and enums for Phase 2 index data.
- `src/cpho_cli/core/index/__init__.py` - Index exception hierarchy.
- `src/cpho_cli/core/index/storage.py` - Atomic JSONL write and load helpers.
- `src/cpho_cli/core/index/vocabulary.py` - Vocabulary YAML loader, merger, alias normalization, and pending candidate reader.
- `tests/test_index_models.py` - Schema round-trip, strict validation, and reserved-field tests.
- `tests/test_index_storage.py` - JSONL storage, overwrite, atomic temp cleanup, missing-file, blank-line, and UTF-8 tests.
- `tests/test_index_vocabulary.py` - Vocabulary normalization, merge precedence, strict YAML validation, layer override, and pending candidate tests.
- `.planning/phases/02-tag-indexing/02-01-SUMMARY.md` - This execution summary.

## Decisions Made

- Forced `CanonicalTag.layer` from the loader argument so workspace/private files cannot mislabel their layer.
- Did not create `src/cpho_cli/vocabulary/builtin.yml` or update package data; the plan explicitly assigns builtin vocabulary content to Plan 02-06.
- Preserved default `TagVisibility.PUBLIC` behavior from the schema instead of adding layer-specific visibility policy not requested by Plan 02-01.

## Deviations from Plan

None - plan executed exactly as written.

**Total deviations:** 0 auto-fixed.
**Impact on plan:** No scope changes.

## Issues Encountered

- The first test patch was accidentally applied in the main checkout because the patch tool used the session default directory. The accidental untracked file was removed immediately, before production implementation. Subsequent edits used absolute paths verified inside `/Users/ericzhang/Desktop/cpho-cli-wt-02-01`.

## Known Stubs

None. Reserved empty/default fields such as `free_text_notes`, `user_tags`, `qa_history_sha256`, and `user_confirmed_*` are intentional schema contracts for later phases and are covered by tests.

## Threat Flags

None. The new filesystem trust boundaries were already covered in the plan threat model: YAML/JSON input validation and atomic JSONL writes.

## Verification

- `uv run pytest tests/test_index_models.py tests/test_index_storage.py tests/test_index_vocabulary.py -x` - 27 passed
- `uv run pytest -q` - 61 passed
- `uv run ruff check src/cpho_cli/models/index.py src/cpho_cli/core/index/ tests/test_index_*.py` - passed
- `uv run mypy src/cpho_cli/models/index.py src/cpho_cli/core/index/` - passed
- Manual schema audit with `rg` confirmed required D-07 / D-09 / D-10 / D-11 / D-14 models and reserved fields are present.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plans 02-02, 02-04, and 02-05 can import `IndexEntry`, `Vocabulary`, `IndexFingerprint`, `write_index`, `load_index`, and `load_merged_vocabulary` without redefining schemas or storage behavior.

## Self-Check: PASSED

- Created files exist on disk.
- Task commits `0ad32b6`, `0ec3b77`, and `a0ab883` exist in git history.
- Plan verification commands passed.

---
*Phase: 02-tag-indexing*
*Completed: 2026-05-23*
