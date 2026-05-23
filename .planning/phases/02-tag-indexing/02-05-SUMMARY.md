---
phase: 02
plan: "02-05"
subsystem: core/index
tags: [builder, cli, api, determinism, notebook, golden-fixture]
dependency_graph:
  requires: ["02-01", "02-02", "02-03", "02-04"]
  provides: [build_index, query_index, get_problem_entry, find_related_problems, get_problem_notes, set_problem_notes, cpho-index-cli]
  affects: [cli/app.py, core/index/__init__.py]
tech_stack:
  added: []
  patterns: [atomic-write, fake-llm-testing, golden-fixture-determinism]
key_files:
  created:
    - src/cpho_cli/core/index/builder.py
    - src/cpho_cli/core/index/notebook.py
    - src/cpho_cli/core/index/api.py
    - tests/test_index_api.py
    - tests/test_index_builder.py
    - tests/test_index_stats.py
    - tests/test_index_determinism.py
    - tests/test_index_cli.py
    - tests/conftest.py
    - tests/fixtures/golden_index_workspace/
  modified:
    - src/cpho_cli/core/index/__init__.py
    - src/cpho_cli/cli/app.py
decisions:
  - "Golden fixture uses PNG images (not .txt) because discover_workspace only scans SUPPORTED_EXTENSIONS"
  - "dimensional_analysis resolves as heuristic (not math_technique) due to override in builtin/05_mechanics_advanced.yml; golden fixture uses calculus_integral for math bucket"
  - "FakeLLM matches problem_id via substring in user prompt content"
metrics:
  duration: "11m"
  completed: "2026-05-23"
  tasks: 4
  tests_added: 50
  files_created: 10
  files_modified: 2
---

# Phase 2 Plan 5: build_index Orchestration, cpho index CLI, Python Query API, Golden Integration Summary

End-to-end indexer wiring: build_index orchestrates discover -> fingerprint -> decide -> OCR -> tag -> write with five action dispatches; Python query API for Phase 3 skills; cpho index CLI with Chinese UX and D-16/D-17 features; golden fixture proves determinism.

## What Was Built

### build_index Orchestrator (builder.py)

Signature: `build_index(workspace_root, config_path=None, provider_name=None, *, force=False, only_new=False, dry_run=False, ocr_strategy="prompt", ocr_provider=None, llm_provider=None) -> IndexRunStats`

Five dispatch actions from `decide_action`:
- **skip**: fingerprint match, no work
- **refinement_only**: user notebook changed, no OCR/LLM
- **re_tag_only**: semantic config changed, OCR cache hit, LLM re-run
- **re_ocr_and_re_tag**: file content changed (or --force), OCR + LLM
- **full_index**: new problem, OCR + LLM

OCR strategy handling:
- `prompt`: detects engine upgrade, raises `OcrUpgradeDecisionRequired`
- `reuse`: skip upgrade detection
- `rebuild`: force re-OCR on version-mismatched entries
- `new-only`: only index new problems

Candidate merging: `_merge_candidates` deduplicates by `normalize_alias(display_zh_suggestion)` and increments occurrences.

### Python Query API (api.py)

- `query_index(ws, *, physics_model_ids, math_technique_ids, heuristic_ids, match_mode)`: within-bucket any/all, across-bucket conjunction
- `get_problem_entry(ws, problem_id)`: single entry lookup
- `find_related_problems(ws, problem_id, *, min_shared_tags, max_results, same_category_weight)`: weighted overlap scoring (+1.0 same-category, +0.5 cross-category)

### User Notebook (notebook.py)

- `get_problem_notes(ws, problem_id)`: returns None if missing
- `set_problem_notes(ws, notes)`: atomic .tmp+replace write, path traversal guard via `PROBLEM_ID_PATTERN`

### CLI (cli/app.py)

`cpho index` command with Chinese help:
- `--force`, `--only-new`, `--dry-run`, `--ocr-strategy`, `--list-candidates`, `--quiet`
- Interactive OCR upgrade prompt (a/b/c/d) via `typer.prompt`
- D-17 layered stats rendering

### Public Re-exports (__init__.py)

Full surface: `build_index`, `query_index`, `get_problem_entry`, `find_related_problems`, `get_problem_notes`, `set_problem_notes`, `load_vocabulary`, `list_pending_candidates`, all exception types, all model types.

## Test Breakdown

| File | Tests | Description |
|------|-------|-------------|
| test_index_api.py | 17 | Query API, notebook CRUD, path traversal guard |
| test_index_builder.py | 17 | Builder orchestration, OCR strategies, notebook refinement, SolveReport consumption |
| test_index_stats.py | 5 | Stats counter accuracy |
| test_index_determinism.py | 3 | Golden fixture: first indexing, reindex identical output, skip on rerun |
| test_index_cli.py | 8 | CLI help, dry-run, OCR upgrade interactive, stats rendering, quiet mode |
| **Total** | **50** | |

Full suite: 180 tests pass (50 new + 130 existing from plans 01-xx through 02-04 + 02-06).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Golden fixture expected_canonical_tags.json used wrong categories**
- **Found during:** Task 2 (determinism test)
- **Issue:** `dimensional_analysis` is overridden from `math_technique` to `heuristic` by `builtin/05_mechanics_advanced.yml`. The plan assumed it remained `math_technique`.
- **Fix:** Replaced with `calculus_integral` (confirmed `math_technique` after merge) in expected_canonical_tags.json.
- **Files modified:** tests/fixtures/golden_index_workspace/expected_canonical_tags.json

**2. [Rule 1 - Bug] Golden fixture used .txt files but workspace discovery only supports PDF/images**
- **Found during:** Task 2 (fixture design)
- **Issue:** Plan specified `.txt` problem files but `discover_workspace` only scans `SUPPORTED_EXTENSIONS` (PDF, PNG, JPG, etc.)
- **Fix:** Created minimal valid PNG files as fixtures instead of text files.
- **Files modified:** tests/fixtures/golden_index_workspace/*.png

## Confirmation

- **R4 deferral honored**: `git diff --name-only src/cpho_cli/core/solve.py` is empty.
- **Source files pass mypy strict**: `mypy src/` reports 0 errors.
- **Ruff clean**: `ruff check .` reports 0 errors.
- **Python API surface operational**: `from cpho_cli.core.index import query_index, find_related_problems, ...` succeeds.

## Commits

| Task | Hash | Message |
|------|------|---------|
| T1 | 9ca60d1 | feat(02-05): add Python query API, notebook data layer, and index re-exports |
| T2 | fa7c7ac | feat(02-05): add build_index orchestrator, golden fixture, and determinism tests |
| T3 | 1f9d0bd | feat(02-05): add cpho index CLI command with Chinese help and layered stats |
| T4 | fb54643 | chore(02-05): clean unused imports in test conftest |

## Self-Check: PASSED

All created files verified to exist on disk. All commit hashes verified in git log.
