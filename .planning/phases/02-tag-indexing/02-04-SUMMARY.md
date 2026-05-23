---
phase: 02-tag-indexing
plan: "04"
subsystem: indexing
tags: [llm, tagging, jinja2, pydantic, trace, vocabulary]
requires:
  - phase: 02-01
    provides: "Index models, Vocabulary, CanonicalTag, CandidateTag, TagCategory"
  - phase: 02-06
    provides: "Split builtin vocabulary and redesigned tag categories"
provides:
  - "Versioned tag refinement prompt template and manifest"
  - "TagRefinementOutput and CanonicalMappingResult schemas"
  - "Deterministic canonical_mapping_pass with candidate downgrade guard"
  - "refine_tags provider path using LLMProvider.complete(response_model=)"
  - "Redacted JSONL trace helper for index tagging"
affects: [02-05-index-builder, 02-07-topic-hierarchy, semantic-fingerprint]
tech-stack:
  added: []
  patterns:
    - "Jinja2 FileSystemLoader with strict undefined variables for index prompts"
    - "LLM output is validated as StrictModel JSON before deterministic mapping"
    - "TraceRecord append mirrors core/runtime.py with redact_secrets"
key-files:
  created:
    - src/cpho_cli/core/index/prompts/__init__.py
    - src/cpho_cli/core/index/prompts/MANIFEST.yml
    - src/cpho_cli/core/index/prompts/tag_refinement.md.j2
    - src/cpho_cli/core/index/tagging.py
    - tests/test_index_canonical_mapping.py
    - tests/test_index_tagging.py
  modified:
    - pyproject.toml
    - src/cpho_cli/models/index.py
key-decisions:
  - "selected_physics_models accepts both physics_law and physics_model for compatibility with the existing IndexEntry field name."
  - "selected_heuristics accepts heuristic and approximation after system_selection was folded into heuristic."
  - "CandidateTag now carries status=TagStatus.CANDIDATE by default to support the D-10 candidate lifecycle."
patterns-established:
  - "Index prompts live under core/index/prompts with MANIFEST.yml versioning."
  - "Unknown, aliased-to-wrong-category, or fabricated LLM ids are candidates, never canonical IndexEntry references."
requirements-completed: [IDX-01]
duration: 8min
completed: 2026-05-23
---

# Phase 02 Plan 04: LLM Tagging Pipeline Summary

**Versioned LLM tag refinement with strict JSON output, deterministic vocabulary mapping, and redacted index trace records**

## Performance

- **Duration:** 8 min
- **Started:** 2026-05-23T11:42:08Z
- **Completed:** 2026-05-23T11:50:15Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Added `tag_refinement.md.j2` and `MANIFEST.yml` version `v1`; `load_tag_prompt_version()` now exposes this for semantic fingerprint invalidation.
- Added `TagRefinementOutput`, `CandidateTagSuggestion`, and `CanonicalMappingResult` strict schemas.
- Implemented `canonical_mapping_pass()` as a pure deterministic guard: direct ids and aliases resolve to canonical tags, unknown or wrong-category ids become `CandidateTag`s.
- Implemented `refine_tags()` using `LLMProvider.complete(messages=, params=, response_model=TagRefinementOutput)` with Jinja2 rendering and no direct HTTP client.
- Added `append_trace()` with `TraceRecord` JSONL append and `redact_secrets()` on success/failure paths.

## Task Commits

1. **Task 1: Versioned prompt template** - `e099ca0` (`feat(02-04): add versioned tag refinement prompt`)
2. **Task 2: Canonical-mapping pass** - `de41ff7` (`feat(02-04): implement canonical tag mapping pass`)
3. **Task 3: LLM invocation and trace path** - `c96a8da` (`feat(02-04): add refine tags provider path`)

## Files Created/Modified

- `src/cpho_cli/core/index/prompts/__init__.py` - Packages index prompt templates.
- `src/cpho_cli/core/index/prompts/MANIFEST.yml` - Declares prompt version `v1` and template mapping.
- `src/cpho_cli/core/index/prompts/tag_refinement.md.j2` - Chinese Jinja2 prompt with controlled vocabulary injection and prompt-injection warning.
- `src/cpho_cli/core/index/tagging.py` - Tagging schemas, canonical mapping, prompt rendering, provider call, prompt version loading, and trace append helper.
- `src/cpho_cli/models/index.py` - Adds default candidate status for candidate lifecycle tracking.
- `pyproject.toml` - Ships `core/index/prompts/*` as package data while preserving vocabulary package data.
- `tests/test_index_canonical_mapping.py` - Covers aliases, fabricated ids, category misassignment, determinism, and source propagation.
- `tests/test_index_tagging.py` - Covers provider schema calls, model params, trace redaction, validation failure, truncation, and prompt version loading.

## Decisions Made

- Kept topic hierarchy out of scope for 02-04; tagging remains flat and multi-tag as required by the handoff note.
- Applied the updated category redesign over stale plan text: `physics_law` and `physics_model` both map into the existing `physics_model_tags` output bucket.
- Kept `SYSTEM_PROMPT` as a Python constant and the long user prompt in Jinja2, matching the plan’s simpler option.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added `CandidateTag.status` default**
- **Found during:** Task 2
- **Issue:** The plan requires candidate lifecycle metadata with `TagStatus.CANDIDATE`, but `CandidateTag` had no `status` field.
- **Fix:** Added `status: TagStatus = TagStatus.CANDIDATE` to `CandidateTag`.
- **Files modified:** `src/cpho_cli/models/index.py`
- **Verification:** `uv run pytest tests/test_index_canonical_mapping.py -x`, full suite `uv run pytest -q`.
- **Committed in:** `de41ff7`

**2. [Rule 2 - Category handoff] Accepted `physics_law` in the physics bucket**
- **Found during:** Task 2
- **Issue:** The original plan allowed only `physics_model`; user feedback and Wave 1 category redesign require `physics_law` plus `physics_model`.
- **Fix:** `canonical_mapping_pass()` uses `{TagCategory.PHYSICS_LAW, TagCategory.PHYSICS_MODEL}` for `selected_physics_models`.
- **Files modified:** `src/cpho_cli/core/index/tagging.py`, `tests/test_index_canonical_mapping.py`
- **Verification:** `test_physics_bucket_accepts_law_and_model_categories`, plan-level pytest.
- **Committed in:** `de41ff7`

**3. [Rule 3 - Acceptance consistency] Avoided literal `StrictUndefined` in the template**
- **Found during:** Task 1
- **Issue:** The plan’s template block mentioned `StrictUndefined`, while acceptance required `grep -c "StrictUndefined" tag_refinement.md.j2` to return 0.
- **Fix:** Kept the strict-undefined contract in wording without that literal token; Python config contains the actual `jinja2.StrictUndefined` guard.
- **Files modified:** `src/cpho_cli/core/index/prompts/tag_refinement.md.j2`, `src/cpho_cli/core/index/tagging.py`
- **Verification:** Template grep returned 0; `tagging.py` grep returned 1.
- **Committed in:** `e099ca0`, `c96a8da`

**Total deviations:** 3 auto-fixed (2 missing critical/category correctness, 1 blocking acceptance consistency)
**Impact on plan:** All deviations are required for the updated category design or for meeting the plan’s own acceptance gates. No topic hierarchy work was added.

## Issues Encountered

- The local shell does not expose `python`; verification commands were run with `uv run python`, matching the project toolchain.
- A relative patch initially targeted the original checkout; those accidental prompt/pyproject edits were removed before any commit. All committed work is in `/Users/ericzhang/Desktop/cpho-cli-wt-02-04`.

## Known Stubs

None. Stub scan found only normal optional/default model fields and test assertions.

## Verification

- `uv run pytest tests/test_index_tagging.py tests/test_index_canonical_mapping.py -x` -> 23 passed.
- `uv run ruff check src/cpho_cli/core/index/tagging.py src/cpho_cli/core/index/prompts/__init__.py tests/test_index_tagging.py tests/test_index_canonical_mapping.py` -> passed.
- `uv run mypy src/cpho_cli/core/index/tagging.py` -> passed.
- `grep -v '^#' src/cpho_cli/core/index/tagging.py | grep -c httpx` -> 0.
- `grep -c 'tag_refinement.md.j2' src/cpho_cli/core/index/tagging.py` -> 1.
- `uv run python -c "from cpho_cli.core.index.tagging import load_tag_prompt_version; print(load_tag_prompt_version())"` -> `v1`.
- `uv run pytest -q` -> 115 passed.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/02-tag-indexing/02-04-SUMMARY.md`.
- Task commits present: `e099ca0`, `de41ff7`, `c96a8da`.
- Key created files exist under `src/cpho_cli/core/index/prompts/`, `src/cpho_cli/core/index/tagging.py`, and `tests/`.

## User Setup Required

None - no external service configuration required for this plan. Real provider calls still use the project’s existing provider configuration path.

## Next Phase Readiness

Plan 02-05 can call `refine_tags()` and `load_tag_prompt_version()` while composing semantic fingerprints and building `IndexEntry` records. Candidate review remains deferred to later lifecycle work, and topic hierarchy remains deferred to 02-07.

---
*Phase: 02-tag-indexing*
*Completed: 2026-05-23*
