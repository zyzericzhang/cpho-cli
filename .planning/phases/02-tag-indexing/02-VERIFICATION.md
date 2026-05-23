---
phase: 02-tag-indexing
verified: 2026-05-23T00:00:00Z
status: passed
score: 4/4 success criteria verified (plus 7/7 plans' must_haves verified)
overrides_applied: 0
re_verification:
  previous_status: none
  previous_score: n/a
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 2: Tag Indexing Verification Report

**Phase Goal:** 构建题目知识索引基础设施——将 workspace 中的题目文件、OCR 缓存、SolveReport 等整理成结构化索引，后续 skill 通过 Python API 检索而非重复读取原始文件。索引使用受控词表保证标签一致性，支持分层增量更新，并为用户错题本/学习记忆层预留数据边界。

**Verified:** 2026-05-23
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (from ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC1 | `cpho index` produces JSONL with canonical tags (physics_model, insight/heuristic, math technique) with Chinese display names + stable internal IDs from a controlled vocabulary | ✓ VERIFIED | `cpho index --help` exposes the command with Chinese help text. `IndexEntry` has `physics_model_tags`, `math_technique_tags`, `heuristic_tags` of `TaggedReference` (with `internal_id` referencing `Vocabulary.tags`). `builtin.yml` provides version v0.1 with 42 starter tags; extension `builtin/*.yml` files add 795 more (total 837 canonical tags, all with `display_zh` + snake_case `internal_id`). `canonical_mapping_pass` enforces vocabulary lookup. `test_golden_workspace_first_indexing` PASSES |
| SC2 | Re-running on a workspace re-indexes only files with content-hash changes; layered stats show file/OCR/tag changes | ✓ VERIFIED | `decide_action` in `hashing.py` returns 5 actions keyed off sha256-based 3-layer fingerprints. `build_index` dispatches per-action and accumulates `IndexRunStats` (total_problems, file_changed/unchanged, ocr_reused/regenerated, ocr_engine_upgrade_detected, tags_regenerated/skipped, refinement_only, candidate_tags_proposed, pending_review_items, forced_regenerations). CLI `cpho index` renders the layered stats in Chinese (`索引统计`, `OCR 复用`, `标签层`, `候选词表`). `test_build_index_skip_on_rerun`, `test_stats_file_changed_counter`, `test_stats_ocr_reused_vs_regenerated`, `test_index_layered_stats_rendered` all PASS |
| SC3 | Python API (`query_index`, `get_problem_entry`, `find_related_problems`) retrieves problems from JSONL with no OCR/LLM re-processing | ✓ VERIFIED | `from cpho_cli.core.index import query_index, get_problem_entry, find_related_problems, get_problem_notes, set_problem_notes, load_vocabulary, list_pending_candidates` works (verified via Python import). All three call `load_index(workspace_root)` only — no OCR/LLM dependency in `api.py`. 17 tests in `test_index_api.py` PASS |
| SC4 | Re-indexing the same problem produces identical canonical tag values; vocabulary is consistent across problems | ✓ VERIFIED | `test_golden_workspace_reindex_identical_output` PASSES (asserts byte-level equality of index.jsonl across re-runs, modulo `indexed_at`). Determinism stack: M1 (fingerprint-cached skip, `decide_action`), M2 (strict vocabulary enum in prompt), M3 (`canonical_mapping_pass` deterministic), M4 (temperature configurable, defaults applied via `resolve_model_params(config, "index")`). `test_canonical_mapping_pass_deterministic` PASSES |

**Score:** 4/4 ROADMAP Success Criteria verified

### Plan-Level Must-Haves (from PLAN frontmatter)

| Plan | Must-Have Truth | Status |
|------|-----------------|--------|
| 02-01 | StrictModel inheritance + JSON round-trip + vocabulary 3-layer merge + alias normalization + atomic writes + reserved Phase 3 fields | ✓ VERIFIED — 16 model classes in `models/index.py` (all StrictModel), `storage.py` uses `tmp.replace(path)`, `vocabulary.py` implements 3-layer merge with `_short_sha8` version composition |
| 02-02 | sha256 deterministic + 3-layer fingerprint composition + `decide_action` 5-branch dispatcher + user-learning fingerprint reserves qa_history | ✓ VERIFIED — `hashing.py` exports `sha256_file`, `sha256_json`, `compose_file_fingerprint`, `compose_semantic_fingerprint`, `compose_user_learning_fingerprint`, `compose_index_fingerprint`, `decide_action` (IndexAction Literal) |
| 02-03 | `CachedOCRProvider` wraps `OCRProvider` returning `OCRResult` (not tuple) with `last_was_cached` side-channel + engine-upgrade detection (R4 solve.py untouched) | ✓ VERIFIED — `ocr_cache.py` defines `CachedOCRProvider`, `OcrEngineDelta` (StrictModel), `OcrUpgradeDecisionRequired` (IndexBuildError), `detect_ocr_engine_upgrade`. `git log -- src/cpho_cli/core/solve.py` shows no commit since `7c6e5ef fix(01-04)` — R4 deferred |
| 02-04 | `refine_tags` via core/llm.py (no httpx) + Jinja2 StrictUndefined + canonical-mapping pass + trace with redaction + tag_prompt_version flows | ✓ VERIFIED — `tagging.py`: 0 `httpx` occurrences, 1 `StrictUndefined` use, 3 `redact_secrets` references, `load_tag_prompt_version()` reads MANIFEST.yml v1. `test_refine_tags_uses_llm_provider_module_not_direct_httpx`, `test_trace_redacts_api_key` PASS |
| 02-05 | `build_index` + `cpho index` CLI with all flags + Python API exports + OcrUpgradeDecisionRequired flow + golden determinism test | ✓ VERIFIED — `builder.py:build_index`, `cli/app.py:index_command` with `--force`, `--only-new`, `--dry-run`, `--ocr-strategy`, `--list-candidates`, `--quiet`. Chinese help text confirmed via `cpho index --help`. `test_index_ocr_upgrade_prompt_interactive` PASSES |
| 02-06 | builtin.yml ships 42 canonical tags with `category` ∈ {physics_law, physics_model, math_technique, heuristic, approximation}; pyproject ships `vocabulary/*.yml` | ✓ VERIFIED — `builtin.yml` loads to 42 tags v0.1; `pyproject.toml` lists `vocabulary/*.yml`, `vocabulary/builtin/*.yml`, `vocabulary/topics/*.yml`, `core/index/prompts/*` in package-data. Total live vocabulary expanded to 837 tags via `builtin/*.yml` extension files |
| 02-07 | TopicNode tree + builtin_topics.yml + 3-layer topic loader + assign_topic LLM pipeline + IndexEntry.topic_path + cpho topic list/browse + cpho compose + build_index integration | ✓ VERIFIED — `models/topic.py:TopicNode/TopicTaxonomy`, `vocabulary/topics/builtin_topics.yml` (5 roots), `topic_vocabulary.py:load_merged_topic_taxonomy`, `topic_assignment.py:assign_topic` validates against taxonomy, `topic_api.py:find_problems_by_topic/get_topic_tree`, `compose.py:compose_problem_list`. CLI commands `cpho topic list` / `cpho topic browse` / `cpho compose` all functional with Chinese help. `test_build_index_assigns_topic_path` PASSES |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/cpho_cli/models/index.py` | 16 StrictModel classes incl. IndexEntry, IndexFingerprint, IndexRunStats, Vocabulary, CanonicalTag, CandidateTag, UserNotebookEntry, TaggedReference + topic_path field | ✓ VERIFIED | 16 classes confirmed. `topic_path: str \| None = None` field on IndexEntry (line 137) |
| `src/cpho_cli/models/topic.py` | TopicNode + TopicTaxonomy with flatten_paths/find_node_by_path | ✓ VERIFIED | Both classes present |
| `src/cpho_cli/core/index/__init__.py` | Exception hierarchy + full re-export surface | ✓ VERIFIED | `IndexBuildError`, `IndexNotFoundError`, `ProblemNotIndexedError`, `VocabularyError` + re-exports of all public API (query_index, find_related_problems, get_problem_notes, set_problem_notes, build_index, find_problems_by_topic, get_topic_tree, assign_topic, compose_problem_list) |
| `src/cpho_cli/core/index/storage.py` | Atomic JSONL read/write | ✓ VERIFIED | `write_index` uses `tmp.replace(path)`; `load_index` raises `IndexNotFoundError` |
| `src/cpho_cli/core/index/vocabulary.py` | 3-layer vocab loader + alias normalization | ✓ VERIFIED | `load_merged_vocabulary`, `normalize_alias`, `load_yaml_vocab`, `list_pending_candidates` present. NFKC + casefold + punctuation strip implemented |
| `src/cpho_cli/core/index/hashing.py` | sha256 primitives + 3-layer fingerprint + decide_action | ✓ VERIFIED | All 7 functions present, `TAG_SCHEMA_VERSION = "v1"` constant, `IndexAction` Literal |
| `src/cpho_cli/core/index/ocr_cache.py` | CachedOCRProvider + engine upgrade detection | ✓ VERIFIED | Class + `OcrEngineDelta` + `OcrUpgradeDecisionRequired` + `detect_ocr_engine_upgrade` |
| `src/cpho_cli/core/index/tagging.py` | TagRefinementOutput + canonical_mapping_pass + refine_tags + append_trace + load_tag_prompt_version | ✓ VERIFIED | All functions/classes present. Jinja2 with StrictUndefined |
| `src/cpho_cli/core/index/topic_assignment.py` | assign_topic + TopicAssignmentOutput | ✓ VERIFIED | Both present, validates against taxonomy via find_node_by_path |
| `src/cpho_cli/core/index/topic_vocabulary.py` | load_merged_topic_taxonomy + 3-layer merge | ✓ VERIFIED | Builtin + workspace + private layers; version string format `v0.1+bt-{sha8}+ws-{sha8}+pv-{sha8}` |
| `src/cpho_cli/core/index/api.py` | query_index + get_problem_entry + find_related_problems | ✓ VERIFIED | All three functions present |
| `src/cpho_cli/core/index/topic_api.py` | find_problems_by_topic + get_topic_tree | ✓ VERIFIED | Both functions; prefix matching via `startswith(topic_path + "/")` |
| `src/cpho_cli/core/index/compose.py` | compose_problem_list (topic + tag intersection) | ✓ VERIFIED | Function present, supports topic-only / tag-only / both / neither |
| `src/cpho_cli/core/index/notebook.py` | get_problem_notes + set_problem_notes + problem_id sanitization | ✓ VERIFIED | `PROBLEM_ID_PATTERN` enforced. Atomic .tmp+replace write |
| `src/cpho_cli/core/index/builder.py` | build_index orchestrator wiring all of the above + topic assignment | ✓ VERIFIED | `build_index` + `_problem_id_for` + `_load_solve_report` + `_solve_report_tag_dict` + `_ocr_config` + `_merge_candidates`. `assign_topic` and `load_merged_topic_taxonomy` imported and called |
| `src/cpho_cli/core/index/prompts/MANIFEST.yml` | Version + templates manifest | ✓ VERIFIED | Lists `tag_refinement` and `topic_assignment` |
| `src/cpho_cli/core/index/prompts/tag_refinement.md.j2` | Jinja2 prompt template | ✓ VERIFIED | Uses controlled_vocabulary loop, Chinese instructions |
| `src/cpho_cli/core/index/prompts/topic_assignment.md.j2` | Jinja2 topic prompt | ✓ VERIFIED | Lists valid_paths, anti-injection footer |
| `src/cpho_cli/vocabulary/builtin.yml` | 42 canonical tags v0.1 | ✓ VERIFIED | Loads to 42 tags via yaml.safe_load; categories present |
| `src/cpho_cli/vocabulary/builtin/*.yml` | Extension vocabulary (scope expansion beyond original plan) | ⚠️ NOTE | 6 extension files add ~795 more tags (total 837). Documented as a `_builtin_vocab_paths()` plural-loader extension; not blocking but worth noting for Phase 3 |
| `src/cpho_cli/vocabulary/topics/builtin_topics.yml` | Topic taxonomy YAML | ✓ VERIFIED | 5 roots (力学, 热学, 电磁学, 光学, 近代物理), 2-3 deep |
| `src/cpho_cli/cli/app.py` | `cpho index`, `cpho topic list`, `cpho topic browse`, `cpho compose` | ✓ VERIFIED | All 4 commands present with Chinese help text |
| `tests/fixtures/golden_index_workspace/` | Reproducible E2E fixture for determinism test | ✓ VERIFIED | PNG-based fixture (deviation noted in 02-05 SUMMARY); 3 determinism tests PASS |
| `pyproject.toml` | Package-data ships YAML + prompts | ✓ VERIFIED | Includes `vocabulary/*.yml`, `vocabulary/builtin/*.yml`, `vocabulary/topics/*.yml`, `core/index/prompts/*` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| storage.py | models/index.py | `IndexEntry`, `IndexBuildError` | ✓ WIRED | Imports confirmed |
| vocabulary.py | models/config.py | `StrictModel` | ✓ WIRED | Import present |
| hashing.py | models/index.py | All fingerprint models | ✓ WIRED | Imports + instantiations confirmed |
| ocr_cache.py | core/ocr.py | `OCRProvider` Protocol | ✓ WIRED | CachedOCRProvider conforms to Protocol (return type OCRResult, not tuple) |
| ocr_cache.py | core/index/__init__.py | `IndexBuildError` | ✓ WIRED | OcrUpgradeDecisionRequired subclasses it |
| tagging.py | core/llm.py | `LLMProvider` (D-02 lockdown) | ✓ WIRED | 0 `httpx` references in tagging.py |
| tagging.py | core/runtime.py | `redact_secrets`, `TraceRecord` | ✓ WIRED | 3 redact_secrets references |
| tagging.py | prompts/tag_refinement.md.j2 | Jinja2 FileSystemLoader | ✓ WIRED | StrictUndefined enforced |
| topic_assignment.py | tagging.py | `_build_jinja_env`, `append_trace` | ✓ WIRED | Reuses shared env (inherits StrictUndefined config) |
| topic_assignment.py | core/llm.py | LLMProvider | ✓ WIRED | 0 httpx references |
| builder.py | workspace.py | `discover_workspace` | ✓ WIRED | Iterates pairs + unmatched_problems |
| builder.py | tagging.py | `refine_tags`, `load_tag_prompt_version`, `append_trace` | ✓ WIRED | All three called |
| builder.py | topic_assignment.py | `assign_topic` (non-blocking) | ✓ WIRED | Called after refine_tags; failure sets topic_path=None |
| builder.py | hashing.py | All composers + `decide_action` + TAG_SCHEMA_VERSION | ✓ WIRED | Full fingerprint pipeline |
| builder.py | ocr_cache.py | `CachedOCRProvider`, `detect_ocr_engine_upgrade` | ✓ WIRED | OCR upgrade detection wired |
| cli/app.py | core/index | `build_index`, `IndexBuildError`, `OcrUpgradeDecisionRequired`, `find_problems_by_topic`, `get_topic_tree`, `compose_problem_list`, `list_pending_candidates` | ✓ WIRED | Imports + call sites confirmed |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `cpho index` CLI | `stats: IndexRunStats` | `build_index()` return value | Yes — populated by actual file fingerprint + LLM tagging pipeline | ✓ FLOWING |
| `query_index` | `entries: list[IndexEntry]` | `load_index(workspace_root)` reads JSONL from disk | Yes — JSONL written by `build_index` | ✓ FLOWING |
| `find_problems_by_topic` | `entries.topic_path` | `assign_topic` LLM call writes into IndexEntry | Yes — topic_path validated against TopicTaxonomy | ✓ FLOWING |
| `compose_problem_list` | filtered entries | Intersects load_index output with topic + tag filters | Yes | ✓ FLOWING |
| `IndexEntry.physics_model_tags` | `mapping.physics_model_tags` from `canonical_mapping_pass` | LLM `TagRefinementOutput` → vocabulary lookup → `TaggedReference` | Yes — canonical_mapping_pass returns vocabulary-validated tags | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `cpho index --help` lists all flags with Chinese text | `uv run cpho index --help` | Shows all 6 flags + Chinese description | ✓ PASS |
| `cpho topic list --help` shows Chinese | `uv run cpho topic list --help` | "显示完整主题分类树" + workspace arg | ✓ PASS |
| `cpho compose --help` shows --topic/--tags | `uv run cpho compose --help` | Both options present with Chinese help | ✓ PASS |
| Python API importable | `python -c "from cpho_cli.core.index import query_index, ..."` | "all imports ok" | ✓ PASS |
| builtin.yml loads with 42 tags | `python -c "yaml.safe_load(...)"` | version v0.1, 42 tags | ✓ PASS |
| Full test suite | `uv run pytest -q` | 216 passed in 6.73s | ✓ PASS |
| Key determinism + builder tests | `pytest tests/test_index_determinism.py tests/test_index_builder.py tests/test_topic_builder_integration.py` | 24/24 PASS | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| IDX-01 | 02-01, 02-04, 02-05, 02-06, 02-07 | `cpho index` 自动生成标签，标签存入 JSONL 索引文件 | ✓ SATISFIED | `cpho index` command, `IndexEntry` with physics_model_tags/math_technique_tags/heuristic_tags, JSONL via storage.py, 837 canonical tags, golden determinism test |
| IDX-02 | 02-02, 02-03, 02-05 | 内容哈希检测变更，仅对变更文件重新索引 | ✓ SATISFIED | `hashing.py` sha256-based fingerprints, `decide_action` 5-branch dispatch, `test_build_index_skip_on_rerun` PASSES |
| IDX-03 | 02-01, 02-05, 02-07 | 通过标签索引检索题目而非重读原始文件，受控词汇表保证一致性 | ✓ SATISFIED | `query_index`/`find_related_problems`/`get_problem_entry` API serves from JSONL only; `canonical_mapping_pass` enforces vocabulary; `test_index_api.py` 17 tests PASS |

**REQUIREMENTS.md status note:** REQUIREMENTS.md still lists IDX-01/02/03 as "Pending" — this is a documentation lag (ROADMAP.md correctly marks Phase 2 as Complete on 2026-05-23). Not a blocker; recommend updating REQUIREMENTS.md traceability table on phase close.

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| (none in phase 2 files) | — | — | — |

Scans for `TODO`/`FIXME`/`TBD`/`HACK`/`PLACEHOLDER` across phase 2 source files: none flagged. `input()` and `print()` calls absent from core modules (芯-壳 boundary respected: 0 in tagging.py / ocr_cache.py / builder.py / topic_assignment.py). `httpx` absent from tagging.py and topic_assignment.py (D-02 lockdown verified). `solve.py` unchanged since Phase 1 (R4 deferral verified via `git log -- src/cpho_cli/core/solve.py`).

### Notable Scope Expansions (Informational)

1. **Vocabulary expanded from 42 → 837 tags** via `src/cpho_cli/vocabulary/builtin/*.yml` (6 extension files). This is beyond what 02-06 PLAN scoped (which specified exactly 42 tags). The expansion is loaded via a new helper `_builtin_vocab_paths()` (plural) in `vocabulary.py`. Tests in `test_index_builtin_vocab.py` still pass against the expanded set. This may have downstream implications for Phase 3 prompt token budgets (larger vocabulary → longer prompts). Not a blocker; recommended that Phase 3 review prompt size impact.

2. **Golden fixture uses PNG instead of .txt** — documented in 02-05 SUMMARY as a deviation: `discover_workspace` only scans SUPPORTED_EXTENSIONS (PDF/images), so the fixture was rebuilt with minimal valid PNGs. Tests pass; no behavioral impact.

3. **`dimensional_analysis` reclassified from math_technique → heuristic** in `builtin/05_mechanics_advanced.yml` override — documented in 02-05 SUMMARY. Golden fixture uses `calculus_integral` instead. Not a blocker.

### Gaps Summary

None. All ROADMAP success criteria for Phase 2 are demonstrably satisfied in the codebase. The full test suite (216 tests) passes, including the canonical determinism test `test_golden_workspace_reindex_identical_output` (SC4 regression guard) and the layered-stats E2E test (SC2). The Python query API surface is operational and re-exported from `cpho_cli.core.index`, satisfying SC3's "zero OCR or LLM re-processing" guarantee. The CLI `cpho index` ships with all D-17 layered stats and the D-16 interactive OCR upgrade flow.

The user has already marked Phase 2 as "Complete (2026-05-23)" in ROADMAP.md, consistent with this verification.

---

_Verified: 2026-05-23_
_Verifier: Claude (gsd-verifier)_
