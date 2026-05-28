# Codebase Concerns

**Analysis Date:** 2026-05-28

## Tech Debt

**Strict typing is configured but not passing:**
- Issue: `pyproject.toml` enables `mypy` strict mode, but `uv run mypy src` reports 41 errors across 14 source files.
- Files: `pyproject.toml`, `src/cpho_cli/core/llm.py`, `src/cpho_cli/core/workspace.py`, `src/cpho_cli/core/skill_handlers.py`, `src/cpho_cli/core/index/builder.py`, `src/cpho_cli/cli/app.py`, `src/cpho_cli/cli/repl/commands/workspace.py`, `src/cpho_cli/cli/repl/commands/compose.py`
- Impact: Type drift is already visible at layer boundaries: `WorkspaceDiscoveryResult` accepts legacy `ProblemFile` unions while `build_index()` assumes `PaperFile`; `CompositionSlot(pass_slot=...)` works at runtime but mypy expects the alias field `pass`; `LLMProvider.complete()` generic inference collapses to `Never` for dynamic response models.
- Fix approach: Make the new paper/index models the only discovery return type, introduce typed wrappers for dynamic `response_model` calls, and add `uv run mypy src` to the same gate as tests before allowing strict mode to guide future edits.

**Large CLI shell module concentrates unrelated command behavior:**
- Issue: `src/cpho_cli/cli/app.py` is 670 lines and owns solve, index, topic, knowledge, compose, output formatting, retry prompts, and helper functions.
- Files: `src/cpho_cli/cli/app.py`, `src/cpho_cli/cli/repl/commands/workspace.py`, `src/cpho_cli/cli/repl/commands/compose.py`
- Impact: Small command changes risk coupling unrelated Typer behavior; index dry-run output, OCR-upgrade retry, composition path validation, and knowledge commands all share one module-level namespace.
- Fix approach: Keep Typer command registration in `src/cpho_cli/cli/app.py`, but move command bodies into focused modules matching the REPL command layout already used under `src/cpho_cli/cli/repl/commands/`.

**Legacy and current document models coexist:**
- Issue: `WorkspaceDiscoveryResult` still permits both `ProblemAnswerPair`/`ProblemFile` and `PaperAnswerPair`/`PaperFile`, while production discovery returns only paper-aware objects.
- Files: `src/cpho_cli/models/documents.py`, `src/cpho_cli/core/workspace.py`, `src/cpho_cli/core/index/builder.py`
- Impact: Consumers need defensive typing for paths, page counts, and answer fields even though runtime expects `PaperFile`; this causes mypy failures and increases the chance of accepting a partial legacy object in new indexing code.
- Fix approach: Remove legacy discovery model variants from `WorkspaceDiscoveryResult` or add a separate compatibility adapter at the CLI/API boundary.

**OCR cache semantics are not reflected in stats:**
- Issue: `CachedOCRProvider.last_was_cached` records cache hit/miss, but `build_index()` increments `ocr_reused` only for `re_tag_only` actions and `ocr_regenerated` for `re_ocr_and_re_tag`/`full_index`.
- Files: `src/cpho_cli/core/index/ocr_cache.py`, `src/cpho_cli/core/index/builder.py`
- Impact: CLI output can say OCR was regenerated even when the file-content cache served the OCR result; operators cannot distinguish cache efficiency from semantic index actions.
- Fix approach: Track cache hits/misses separately from index action names, then render both layers in `cpho index` output.

## Known Bugs

**Composed answer PDFs use the problem page range:**
- Symptoms: Answer documents are assembled with `entry.problem_page_range` instead of `entry.answer_page_range`, so answers are wrong whenever answer pages differ from problem pages.
- Files: `src/cpho_cli/core/compose_pdf.py:60`, `src/cpho_cli/models/index.py`, `tests/test_compose_pdf.py`
- Trigger: Build a composition where an `IndexEntry` has `problem_page_range=(1, 2)` and `answer_page_range=(3, 3)` or any non-identical answer range.
- Workaround: None in the current compose path; only source PDFs whose problem and answer page ranges align produce correct answer PDFs.

**Index dry-run prints a completion path for a file it does not write:**
- Symptoms: `cpho index <workspace> --dry-run` prints `完成. 索引: <workspace>/.cpho/index.jsonl` even though `build_index()` returns before writing the index.
- Files: `src/cpho_cli/core/index/builder.py:192`, `src/cpho_cli/cli/app.py:288`
- Trigger: Run `uv run cpho index "/Users/ericzhang/Desktop/物理竞赛资料" --dry-run --ocr-strategy reuse`.
- Workaround: Treat dry-run output as a discovery preview and check for `workspace/.cpho/index.jsonl` before relying on the printed path.

**MuPDF parser errors leak through discovery output:**
- Symptoms: Real workspace dry-run exits successfully but prints `MuPDF error: format error: corrupt object stream (...)` while page-count probing continues.
- Files: `src/cpho_cli/core/workspace.py:58`, `src/cpho_cli/core/documents.py:23`
- Trigger: Run discovery/dry-run over `/Users/ericzhang/Desktop/物理竞赛资料`, which includes at least one PDF that makes PyMuPDF emit a parser warning.
- Workaround: Use `--quiet` to suppress CLI progress, but PyMuPDF parser output can still appear because it is emitted below application logging.

**Indexing aborts the whole run on one file-level failure:**
- Symptoms: Any OCR, document loading, splitting, tagging, or topic-assignment error outside the explicitly non-blocking topic block raises and stops the full index build.
- Files: `src/cpho_cli/core/index/builder.py:254`, `src/cpho_cli/core/index/builder.py:273`, `src/cpho_cli/core/documents.py:10`
- Trigger: A single corrupt PDF that fails `load_document()`, an invalid cached OCR JSON file, or an LLM split failure during a run over a large workspace.
- Workaround: Use `cpho repl` `/index --path` to process smaller subtrees and isolate failing directories.

## Security Considerations

**Inline API keys are supported in local YAML config:**
- Risk: `ProviderConfig.openrouter_api_key`, `ProviderProfile.api_key`, and `CommunitySyncConfig.github_token` can hold secrets directly in YAML files.
- Files: `src/cpho_cli/models/config.py`, `src/cpho_cli/core/config.py`, `src/cpho_cli/models/community.py`, `.gitignore`, `docs/phase2-manual-operations-guide.md`, `docs/phase021-manual-acceptance-guide.md`
- Current mitigation: `.gitignore` excludes `*.local.yml`, `*.local.yaml`, `.env`, and `.cpho/`; runtime errors redact configured provider keys in several exception paths.
- Recommendations: Prefer `api_key_env` examples everywhere, avoid documentation commands that print `config.local.yml`, and add a secret-scan check for docs and committed fixtures.

**Vision mode uploads source files to the configured provider:**
- Risk: `--vision` passes source PDF/image content as base64 data URLs to the LLM provider; real workspace files are private teaching materials.
- Files: `src/cpho_cli/cli/app.py:156`, `src/cpho_cli/core/index/builder.py:201`, `src/cpho_cli/core/index/tagging.py:294`, `src/cpho_cli/core/multimodal.py:18`
- Current mitigation: CLI help says vision may upload PDFs/images, and capability detection can fall back to OCR text.
- Recommendations: Add an explicit confirmation gate for real workspace paths, size/count preview before upload, and per-run audit metadata recording whether OCR text or file upload was used.

**Community knowledge sync downloads and extracts release tarballs:**
- Risk: Pinned GitHub releases can still contain large archives, symlinks, or many files; the sync writes into a shared cache under `~/.cache/cpho/community-kb`.
- Files: `src/cpho_cli/core/community_sync.py:136`, `src/cpho_cli/core/community_sync.py:206`, `src/cpho_cli/core/community_sync.py:222`
- Current mitigation: Extraction validates member paths stay under the target directory, uses `tarfile.extractall(..., filter="data")`, validates knowledge frontmatter, and marks the final cache read-only.
- Recommendations: Add archive size, file count, and per-file byte limits before extraction and staging.

## Performance Bottlenecks

**PDF loading eagerly rasterizes every page:**
- Problem: `load_document()` renders every PDF page to PNG bytes and keeps all pages in memory before OCR or LLM routing.
- Files: `src/cpho_cli/core/documents.py:22`, `src/cpho_cli/core/ocr.py`, `src/cpho_cli/core/solve.py`, `src/cpho_cli/core/index/builder.py`
- Cause: `DocumentInput` is a full in-memory list of `DocumentPage` objects with `image_bytes`; there is no streaming page iterator or page-range loader.
- Improvement path: Add lazy page iteration for OCR/indexing, load only selected page ranges for compose/solve, and cap page count or rendered bytes per document.

**Workspace discovery opens every supported PDF for page counts:**
- Problem: `discover_workspace()` calls `_paper_total_pages()` for every supported problem and answer candidate.
- Files: `src/cpho_cli/core/workspace.py:58`, `src/cpho_cli/core/workspace.py:72`, `src/cpho_cli/core/workspace.py:76`
- Cause: `PaperFile.total_pages` is required during discovery rather than at the point where splitting needs it.
- Improvement path: Store page count lazily or tolerate unknown page counts until `load_document()` succeeds.

**Full real workspace indexing scales linearly with many LLM calls:**
- Problem: The real workspace shape sampled on 2026-05-28 contains 971 PDFs, 8 JPGs, 16 Word documents, archives/media, and deeply nested Chinese year/institution folders; discovery currently produces 670 paper inputs, 225 answer pairs, 445 unmatched papers, and 25 ambiguous matches.
- Files: `/Users/ericzhang/Desktop/物理竞赛资料`, `src/cpho_cli/core/workspace.py`, `src/cpho_cli/core/index/builder.py`, `src/cpho_cli/core/index/tagging.py`, `src/cpho_cli/core/index/topic_assignment.py`
- Cause: Indexing is sequential and can call LLM split/tag/topic logic per paper/problem.
- Improvement path: Add resumable per-file manifests, bounded concurrency, cost estimates, and a default subtree-first workflow for large real workspaces.

## Fragile Areas

**Real workspace naming heuristics skip or misclassify files:**
- Files: `src/cpho_cli/core/workspace.py`, `/Users/ericzhang/Desktop/物理竞赛资料`
- Why fragile: Answer detection is substring/marker based (`answer`, `solution`, `ans`, `key`, `答案`, `解析`), while the real workspace contains mixed Chinese institution folders, answer/problem files, unrelated PDFs, JPG scans, Word documents, archives, and media.
- Safe modification: Before changing pairing logic, run discovery against copied real-workspace samples and assert counts for pairs, unmatched papers, and ambiguous matches.
- Test coverage: `tests/test_workspace.py` covers simple English/Chinese pairs and generated-output ignores, but not the full real workspace distribution or corrupted PDF warnings.

**Problem splitting relies on first marker per page:**
- Files: `src/cpho_cli/core/splitting/rules.py`, `src/cpho_cli/core/splitting/__init__.py`, `tests/test_splitting_rules.py`, `tests/test_splitting_golden.py`
- Why fragile: `_find_markers()` records at most one problem marker per page, so multi-problem pages require LLM fallback unless the document is treated as a single image or single page.
- Safe modification: Keep rule split conservative, add fixtures for multi-problem pages from copied real PDFs, and treat LLM fallback failures as per-file failures rather than whole-run failures.
- Test coverage: Golden fixtures cover some split styles, but real PDFs are tested with fake OCR text rather than actual OCR output quality.

**Multimodal routing has no size budget:**
- Files: `src/cpho_cli/core/multimodal.py`, `src/cpho_cli/core/input_routing.py`, `src/cpho_cli/core/skill_handlers.py`, `src/cpho_cli/core/index/tagging.py`
- Why fragile: `_data_url()` reads whole files and base64-encodes them, which can produce very large requests for long PDFs or high-resolution scans.
- Safe modification: Add file-size and page-count guards before `build_multimodal_content()`, and preserve OCR fallback as the default route.
- Test coverage: `tests/test_llm.py` verifies multimodal content preservation, but not payload size limits or large real PDFs.

**Cache and checkpoint files are recoverable but not self-healing:**
- Files: `src/cpho_cli/core/index/ocr_cache.py`, `src/cpho_cli/core/runtime.py`, `src/cpho_cli/cli/repl/persistence.py`
- Why fragile: Invalid OCR cache JSON raises during `CachedOCRProvider.extract()`, and runtime checkpoints record keys/status but are not used to resume `build_index()`.
- Safe modification: Treat cache parse failures as cache misses, and add an index-run manifest that records completed file/problem IDs.
- Test coverage: `tests/test_index_ocr_cache.py` covers cache hit/miss and upgrade decisions, but not corrupted cache recovery.

## Scaling Limits

**Single-process sequential indexing:**
- Current capacity: Dry-run discovery over `/Users/ericzhang/Desktop/物理竞赛资料` reports 670 paper inputs.
- Limit: A single failing file aborts the run; a large workspace requires long uninterrupted execution and repeated provider calls.
- Scaling path: Add per-input result records under `.cpho/runs/`, retry/skip controls, and bounded worker pools for OCR while keeping LLM concurrency configurable.

**Unsupported real workspace file types are invisible to problem indexing:**
- Current capacity: `SUPPORTED_EXTENSIONS` covers PDFs and image formats only.
- Limit: The sampled real workspace contains `.doc`, `.docx`, `.pptx`, `.zip`, `.rar`, `.mp4`, `.mkv`, and `.downloading` files; 16 Word documents under the real workspace are not discoverable as problem inputs.
- Scaling path: Add explicit unsupported-file reporting in dry-run output, then choose whether `.docx` should use the existing `mammoth` path from knowledge normalization or remain out of scope.

**No CI workflow is present:**
- Current capacity: Local verification shows `uv run pytest -q` passes and `uv run ruff check .` passes.
- Limit: `.github/` contains issue templates and assets but no workflow enforcing tests, lint, type checks, docs checks, or secret scanning.
- Scaling path: Add a minimal GitHub Actions workflow for `uv run pytest -q`, `uv run ruff check .`, and, after fixing type errors, `uv run mypy src`.

## Dependencies at Risk

**PyMuPDF (`pymupdf`) handles both discovery and PDF rendering:**
- Risk: Parser warnings and corrupt-object handling surface during discovery; eager rendering drives memory usage.
- Impact: Real workspace scans can produce noisy output or fail at document-load time.
- Migration plan: Wrap PyMuPDF calls behind a document adapter that can suppress parser stderr where safe, report corrupt files, and support lazy page loading.

**RapidOCR version can be unknown:**
- Risk: `_rapidocr_version()` returns `"unknown"` when version metadata is unavailable, and the real workspace already contains an OCR cache file named with `rapidocr_unknown`.
- Impact: OCR upgrade detection and cache invalidation are less precise when the engine version is unknown.
- Migration plan: Record package version from installed metadata as a fallback and include OCR config hash in the cache filename, not only in index fingerprints.

**OpenAI-compatible provider assumptions are shared by OpenRouter and DeepSeek:**
- Risk: Structured output is implemented as forced tool calls with `parallel_tool_calls=False`; providers that prefer JSON schema or return structured content differently can fail validation.
- Impact: Skill runtime, solve, split fallback, tag refinement, and topic assignment all depend on this behavior.
- Migration plan: Add provider capability flags for structured-output mode and provider-specific payload adapters under `src/cpho_cli/core/llm.py`.

## Missing Critical Features

**Per-file failure isolation for real indexing:**
- Problem: Large real workspaces need skip-and-report behavior for corrupt PDFs, bad OCR cache records, and LLM failures.
- Blocks: Reliable first-pass indexing of `/Users/ericzhang/Desktop/物理竞赛资料` without manually narrowing subtrees.

**Answer page range preservation in composition:**
- Problem: `IndexEntry.answer_page_range` exists but is not used by PDF assembly.
- Blocks: Trustworthy generated answer PDFs when answer keys are consolidated or laid out differently from problem sheets.

**Unsupported-file visibility in dry-run:**
- Problem: Dry-run reports only supported paper inputs and not skipped `.doc`, `.docx`, archives, media, or ambiguous matches.
- Blocks: Coaches cannot tell from CLI output why some real workspace materials are absent from the index.

**Cost and upload preview before LLM-heavy operations:**
- Problem: Index and vision flows do not estimate file count, page count, multimodal bytes, or likely LLM calls before a non-dry run.
- Blocks: Safe operation over large private workspaces and expensive providers.

## Test Coverage Gaps

**Compose answer page ranges:**
- What's not tested: Assembly with `answer_page_range` different from `problem_page_range`.
- Files: `tests/test_compose_pdf.py`, `src/cpho_cli/core/compose_pdf.py`
- Risk: Incorrect answer PDFs pass current tests because fixtures use identical ranges.
- Priority: High

**Real corrupted PDF handling:**
- What's not tested: Discovery/load behavior for PDFs that make PyMuPDF emit parser errors or raise during full `load_document()`.
- Files: `tests/test_phase021_acceptance.py`, `tests/test_phase023_acceptance.py`, `src/cpho_cli/core/workspace.py`, `src/cpho_cli/core/documents.py`
- Risk: A single problematic source file can stop full indexing or produce confusing output.
- Priority: High

**Strict type check gate:**
- What's not tested: `uv run mypy src` in CI or local acceptance gates.
- Files: `pyproject.toml`, `.github/`, `src/cpho_cli`
- Risk: Runtime tests pass while type contracts keep drifting across command/core/model layers.
- Priority: Medium

**Real OCR quality and real LLM split fallback:**
- What's not tested: Actual RapidOCR text quality and real provider split/tag/topic behavior on copied samples from `/Users/ericzhang/Desktop/物理竞赛资料`.
- Files: `tests/test_phase021_acceptance.py`, `tests/test_phase023_acceptance.py`, `tests/test_splitting_golden.py`, `src/cpho_cli/core/splitting`
- Risk: Fake OCR providers assert pipeline shape but not the real data-shape failures that matter for coaches.
- Priority: Medium

**Large multimodal payload limits:**
- What's not tested: Maximum file size, PDF page count, base64 payload size, and provider rejection paths for `--vision`.
- Files: `tests/test_llm.py`, `src/cpho_cli/core/multimodal.py`, `src/cpho_cli/core/index/tagging.py`
- Risk: Private files may be uploaded in requests that are too large or costly, then silently fall back or fail late.
- Priority: Medium

---

*Concerns audit: 2026-05-28*
