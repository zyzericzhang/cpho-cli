---
phase: 02-tag-indexing
plan: "02"
subsystem: indexing
tags: [hashing, fingerprints, deterministic-cache, pytest, pydantic]

requires:
  - phase: 02-tag-indexing
    provides: "Plan 02-01 index schema models used by the hashing module"
provides:
  - "Deterministic sha256_file and sha256_json primitives"
  - "File, semantic, user-learning, and aggregate IndexFingerprint composers"
  - "IndexAction Literal contract and D-14 decide_action dispatcher"
affects: [index-builder, ocr-cache, tag-indexing]

tech-stack:
  added: []
  patterns:
    - "Small pure functions in core/index/hashing.py"
    - "Hash-based incremental indexing decisions"

key-files:
  created:
    - src/cpho_cli/core/index/hashing.py
    - tests/test_index_hashing.py
  modified: []

key-decisions:
  - "TAG_SCHEMA_VERSION is pinned to v1 in hashing.py."
  - "IndexAction strings are full_index, re_ocr_and_re_tag, re_tag_only, refinement_only, and skip."
  - "User-learning qa_history_sha256 remains None in Phase 2."

patterns-established:
  - "sha256_json uses sorted JSON with ensure_ascii=False and default=str."
  - "decide_action precedence is file > semantic > user_learning."

requirements-completed: [IDX-02]

duration: 5min
completed: 2026-05-23
---

# Phase 02 Plan 02: Three-Tier Hashing Summary

**Deterministic three-layer index fingerprints with D-14 action dispatch for cached incremental indexing**

## Performance

- **Duration:** 5 min
- **Started:** 2026-05-23T09:25:57Z
- **Completed:** 2026-05-23T09:31:05Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- Added pure hash primitives: `sha256_file(path)` and canonical `sha256_json(obj)`.
- Added composers for `FileFingerprint`, `SemanticFingerprint`, `UserLearningFingerprint`, and `IndexFingerprint`.
- Added `IndexAction` and `decide_action` covering all five D-14 rebuild branches.
- Added 23 focused unit tests for determinism, semantic invalidation inputs, Phase 2 notebook hashing, and dispatcher precedence.

## Task Commits

1. **Task 1: Pure hash primitives** - `94ffb76` (`feat(02-02): add deterministic hash primitives`)
2. **Task 2: Compose three-layer fingerprints** - `48ba471` (`feat(02-02): compose index fingerprints`)
3. **Task 3: decide_action dispatcher** - `f13fc2a` (`feat(02-02): add index action dispatcher`)

## Files Created/Modified

- `src/cpho_cli/core/index/hashing.py` - Pure hashing, fingerprint composition, `TAG_SCHEMA_VERSION`, `IndexAction`, and `decide_action`.
- `tests/test_index_hashing.py` - Unit coverage for all exported behavior in this plan.

## Exported Contract

- `TAG_SCHEMA_VERSION = "v1"`
- `IndexAction = Literal["full_index", "re_ocr_and_re_tag", "re_tag_only", "refinement_only", "skip"]`
- `decide_action(old, new_fp)` returns:
  - `full_index` when no prior entry exists
  - `re_ocr_and_re_tag` when file fingerprint changes
  - `re_tag_only` when semantic fingerprint changes
  - `refinement_only` when only user-learning fingerprint changes
  - `skip` when all three layers match

## Decisions Made

- Followed the plan's D-14 ordering exactly: file changes dominate semantic changes, and semantic changes dominate user-learning changes.
- Used `file_fp.problem_sha256[:16]` for semantic dependency linkage, matching the plan's short hash requirement.
- Kept `qa_history_sha256=None` for Phase 2 even when notebook content exists; Phase 3 will populate QA history.

## Deviations from Plan

None - plan behavior executed as written.

## Issues Encountered

- Initial test patch landed outside the requested worktree because the patch tool used the caller cwd. The unintended untracked file was removed before any commit, then all subsequent edits used verified absolute worktree paths under `/Users/ericzhang/Desktop/cpho-cli-wt-02-02`.

## Known Stubs

None. `qa_history_sha256=None` is intentional Phase 2 reserved behavior, covered by `test_user_learning_fp_qa_history_phase2_none`.

## Verification

- `uv run pytest tests/test_index_hashing.py -x` - 23 passed.
- `uv run ruff check src/cpho_cli/core/index/hashing.py tests/test_index_hashing.py` - passed.
- `uv run mypy src/cpho_cli/core/index/hashing.py` - passed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 02-05 can consume `compose_index_fingerprint`, `decide_action`, and the `IndexAction` string contract for builder dispatch without introducing LLM or index-storage dependencies into hashing.

## Self-Check: PASSED

- Found `src/cpho_cli/core/index/hashing.py`.
- Found `tests/test_index_hashing.py`.
- Found `.planning/phases/02-tag-indexing/02-02-SUMMARY.md`.
- Found task commits `94ffb76`, `48ba471`, and `f13fc2a`.

---
*Phase: 02-tag-indexing*
*Completed: 2026-05-23*
