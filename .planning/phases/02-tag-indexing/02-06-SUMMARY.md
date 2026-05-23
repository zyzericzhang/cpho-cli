---
phase: 02
plan: 02-06
subsystem: builtin-vocabulary
status: complete
tags:
  - vocabulary
  - index
  - builtin-tags
key-files:
  created:
    - src/cpho_cli/vocabulary/builtin.yml
    - src/cpho_cli/vocabulary/builtin/01_optics_geometric.yml
    - src/cpho_cli/vocabulary/builtin/02_optics_wave_quantum.yml
    - src/cpho_cli/vocabulary/builtin/03_thermal_statistical.yml
    - src/cpho_cli/vocabulary/builtin/04_relativity_nuclear.yml
    - src/cpho_cli/vocabulary/builtin/05_mechanics_advanced.yml
    - src/cpho_cli/vocabulary/builtin/06_electrostatics_electromagnetism.yml
    - docs/builtin-vocabulary-manual.md
  modified:
    - src/cpho_cli/models/index.py
    - src/cpho_cli/core/index/vocabulary.py
    - pyproject.toml
    - tests/test_index_builtin_vocab.py
    - tests/test_index_models.py
    - tests/test_index_vocabulary.py
metrics:
  builtin_core_tags: 42
  builtin_loaded_tags: 837
  builtin_split_files: 6
completed_at: 2026-05-23T11:40:03.297447+00:00
---

# Plan 02-06 Summary: Starter Vocabulary Content and Package Data

## What Built

Plan 02-06 now ships a packaged builtin vocabulary with a small core file and multiple classified extension boards:

- `src/cpho_cli/vocabulary/builtin.yml` remains the 42-tag core starter vocabulary.
- `src/cpho_cli/vocabulary/builtin/*.yml` contains six classified boards derived from the user's `docs/builtinchanges.md`, `docs/bc2.md`, and `docs/bc3.md` files.
- `load_merged_vocabulary()` loads `builtin.yml` first, then sorted `builtin/*.yml`, then workspace and private layers.
- `TagCategory` now uses the redesigned five-category system: `physics_law`, `physics_model`, `math_technique`, `heuristic`, `approximation`.
- `system_selection` was folded into `heuristic`.
- `pyproject.toml` packages both `vocabulary/*.yml` and `vocabulary/builtin/*.yml`.
- `docs/builtin-vocabulary-manual.md` gives the requested Chinese manual for manual follow-up operations.

## Commits

Existing plan commits before checkpoint:

```text
51daf1a docs(02-06): add vocabulary review note
63c2f06 test(02-06): validate packaged builtin vocabulary
3f4efb8 feat(02-06): add starter builtin vocabulary
a16c265 docs(02): create phase plan with research, patterns, and 6 PLAN.md files
```

This summary is committed after the checkpoint feedback changes.

## Validation

- `uv run pytest tests/test_index_models.py tests/test_index_vocabulary.py tests/test_index_builtin_vocab.py -q` -> 29 passed.
- `uv run ruff check src/cpho_cli/models/index.py src/cpho_cli/core/index/vocabulary.py tests/test_index_models.py tests/test_index_vocabulary.py tests/test_index_builtin_vocab.py` -> passed.
- `uv run mypy src/cpho_cli/models/index.py src/cpho_cli/core/index/vocabulary.py` -> passed.
- `uv run python -c "from pathlib import Path; from cpho_cli.core.index.vocabulary import load_merged_vocabulary; v=load_merged_vocabulary(Path('.')); print(len(v.tags), v.version); assert 'fermat_principle' in v.tags; assert 'image_charge_method' in v.tags"` -> `837 v0.1+bt-d85ed2b1+ws-none+pv-none`.

## Deviations from Plan

1. The original plan expected one `builtin.yml` with 42 tags. User checkpoint feedback explicitly requested reviewing multiple candidate files and classifying tags into multiple builtin files by content board. The implementation keeps the 42-tag core and adds six packaged board files.
2. The original plan still referenced the old category system in places. User context and `.planning/notes/topic-hierarchy-design.md` redesigned the categories, so the implementation updates code and tests to the new five-category system.
3. `02-06-REVIEW-NOTE.md` was created before the human-review checkpoint so the user had the requested review artifact available during checkpoint review.

**Total deviations:** 3 user-directed scope refinements.
**Impact:** The vocabulary layer is larger and more realistic, while retaining deterministic load order and workspace/private override semantics.

## Issues Encountered

- Several candidate tags repeat across board files. The manual lists duplicates for human cleanup. Runtime behavior is deterministic: later sorted builtin board files override earlier builtin board files before workspace/private layers apply.

## Next Phase Readiness

- Plan 02-04 should use the new category rules: `selected_physics_models` should accept `physics_law` and `physics_model`; heuristic bucket should accept `heuristic` and `approximation`.
- Plan 02-07 should follow `.planning/notes/topic-hierarchy-design.md`: tags remain flat/multiple, topics are tree/single-path.

## Self-Check: PASSED

All key files exist, package data includes split vocabulary YAML files, the merged vocabulary loads 837 tags, and focused tests/ruff/mypy pass.
