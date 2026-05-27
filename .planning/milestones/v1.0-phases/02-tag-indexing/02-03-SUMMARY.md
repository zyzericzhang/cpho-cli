---
phase: 02-tag-indexing
plan: "03"
subsystem: indexing
tags: [ocr-cache, engine-fingerprint, pydantic, pytest]
requires:
  - phase: 02-tag-indexing
    provides: "Index exceptions, storage.load_index/write_index, hashing.sha256_file/sha256_json, and IndexEntry fingerprints from Plans 02-01 and 02-02"
provides:
  - "CachedOCRProvider(inner, cache_dir, engine_name, engine_version) with OCRResult-returning extract()"
  - "OCR cache keys based on file content hash, OCR engine name, and OCR engine version"
  - "OcrEngineDelta, OcrUpgradeDecisionRequired, and detect_ocr_engine_upgrade() for D-16 CLI handoff"
affects: [phase-02-index-builder, cli-index-command, ocr-upgrade-strategy]
tech-stack:
  added: []
  patterns:
    - "OCRProvider-compatible wrapper with last_was_cached side channel"
    - "Core raises typed exception for CLI prompt handoff; core does not call input() or print()"
key-files:
  created:
    - src/cpho_cli/core/index/ocr_cache.py
    - tests/test_index_ocr_cache.py
    - tests/test_index_ocr_upgrade.py
  modified: []
key-decisions:
  - "Cache-hit reporting uses CachedOCRProvider.last_was_cached so extract() remains compatible with OCRProvider."
  - "OCR upgrade detection reports drift only; prompt/reuse/rebuild/new-only strategy resolution remains a CLI/builder concern."
  - "Phase 1 solve.py was not modified; solve cache sharing remains deferred by R4."
patterns-established:
  - "Cache key format: {file_sha256[:16]}__{ocr_engine}_{ocr_version}.json"
  - "OcrUpgradeDecisionRequired carries OcrEngineDelta for a later CLI prompt without recomputing index state."
requirements-completed: [IDX-02]
duration: 4min
completed: 2026-05-23
---

# Phase 02 Plan 03: OCR Cache Wrapper and Engine Upgrade Detection Summary

**Content-addressed OCR caching with engine-version invalidation and typed upgrade detection for the Phase 2 indexer**

## Performance

- **Duration:** 4 min
- **Started:** 2026-05-23T11:42:13Z
- **Completed:** 2026-05-23T11:46:14Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Added `CachedOCRProvider(inner: OCRProvider, cache_dir: Path, engine_name: str, engine_version: str)` with `extract(document) -> OCRResult`.
- Added `last_was_cached` as the cache-hit side channel so callers remain duck-type compatible with `OCRProvider`.
- Added runtime `_rapidocr_version()` fallback, `OCR_CACHE_DIRNAME`, `RAPIDOCR_ENGINE_NAME`, and `ocr_config_hash()`.
- Added `OcrEngineDelta` with `summary()` format: `OCR 引擎升级: {old_engine} {old_version} → {new_engine} {new_version}; 受影响条目 {affected_count}`.
- Added `OcrUpgradeDecisionRequired(delta)` for CLI/builder consumption and `detect_ocr_engine_upgrade()` for existing index fingerprint comparison.
- Confirmed `src/cpho_cli/core/solve.py` was not modified, preserving the R4 deferral.

## Task Commits

1. **Task 1: CachedOCRProvider wrapper class** - `c239a7e` (`feat`)
2. **Task 2: Engine upgrade detection** - `fa835dc` (`feat`)

## Files Created/Modified

- `src/cpho_cli/core/index/ocr_cache.py` - Cache wrapper, runtime RapidOCR version helper, OCR config hash helper, upgrade delta model, typed exception, and upgrade detector.
- `tests/test_index_ocr_cache.py` - Cache miss/hit, key format, content hash, version split, UTF-8, and lazy directory tests.
- `tests/test_index_ocr_upgrade.py` - No-index, matching fingerprint, version/config/engine drift, affected-only reporting, exception, and Chinese summary tests.

## Decisions Made

- Used `last_was_cached` instead of returning a tuple so `CachedOCRProvider.extract()` keeps the same return type as `OCRProvider.extract()`.
- Selected the most common stale OCR fingerprint among affected entries for `OcrEngineDelta.old_*` fields.
- Left all prompt/reuse/rebuild/new-only strategy behavior out of this module; this plan only detects and reports the delta.
- Did not update `.planning/STATE.md` or `.planning/ROADMAP.md` because the orchestrator prompt explicitly owns shared tracking.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed verification issues introduced during Task 1**
- **Found during:** Task 1 verification
- **Issue:** The initial test used a set containing unhashable `OCRResult` objects, and `_rapidocr_version()` had an unnecessary `type: ignore` that strict mypy rejected.
- **Fix:** Switched the test membership check to lists and removed the unused ignore.
- **Files modified:** `tests/test_index_ocr_cache.py`, `src/cpho_cli/core/index/ocr_cache.py`
- **Verification:** `uv run pytest tests/test_index_ocr_cache.py -x`, `uv run ruff check src/cpho_cli/core/index/ocr_cache.py tests/test_index_ocr_cache.py`, `uv run mypy src/cpho_cli/core/index/ocr_cache.py`
- **Committed in:** `c239a7e`

**Total deviations:** 1 auto-fixed (1 bug). **Impact:** Verification cleanup only; no scope change.

## Known Stubs

None.

## Threat Flags

None - the new cache-file read surface matches the plan threat model (`T-02-03`) and was documented in code as recoverable local cache data.

## Issues Encountered

- Task 1 RED failed as expected because `ocr_cache.py` did not exist yet.
- Task 2 RED failed as expected because upgrade-detection exports did not exist yet.

## Verification

- `uv run pytest tests/test_index_ocr_cache.py tests/test_index_ocr_upgrade.py -x` - 15 passed.
- `uv run ruff check src/cpho_cli/core/index/ocr_cache.py tests/test_index_ocr_*.py` - passed.
- `uv run mypy src/cpho_cli/core/index/ocr_cache.py` - passed.
- `git diff --name-only src/cpho_cli/core/solve.py` - empty.

## Next Phase Readiness

Plan 02-05 can wrap `RapidOCRProvider` with `CachedOCRProvider`, read `last_was_cached` for stats, call `ocr_config_hash()`, and use `detect_ocr_engine_upgrade()`/`OcrUpgradeDecisionRequired` for D-16 CLI handoff.

## Self-Check: PASSED

- Found created files: `src/cpho_cli/core/index/ocr_cache.py`, `tests/test_index_ocr_cache.py`, `tests/test_index_ocr_upgrade.py`.
- Found task commits: `c239a7e`, `fa835dc`.
- Verified final plan checks passed and `solve.py` remained untouched.

---
*Phase: 02-tag-indexing*
*Completed: 2026-05-23*
