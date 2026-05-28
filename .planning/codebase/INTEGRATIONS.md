<!-- refreshed: 2026-05-28 -->
# Integrations

**Analysis Date:** 2026-05-28

## Integration Overview

CPHO CLI is primarily a local filesystem application. It integrates with external
services only at specific boundaries:

- OpenAI-compatible LLM providers for solve, index tagging, topic assignment,
  paper splitting, explain, probe, and knowledge normalization.
- OpenRouter model catalog and model capability endpoints.
- GitHub release APIs for community knowledge base sync.
- Local OCR/PDF tooling through RapidOCR, ONNX Runtime, and PyMuPDF.
- The user's real local workspace at `/Users/ericzhang/Desktop/物理竞赛资料`, where
  generated `.cpho/` state sits beside nested PDF/image source material.

## LLM Providers

| Provider kind | Base URL default | Files |
|---------------|------------------|-------|
| `openrouter` | `https://openrouter.ai/api/v1` | `src/cpho_cli/core/config.py`, `src/cpho_cli/core/llm.py` |
| `deepseek` | `https://api.deepseek.com` | `src/cpho_cli/core/config.py`, `src/cpho_cli/core/llm.py` |

The provider abstraction is OpenAI-compatible:

- `create_llm_provider()` selects a provider class from `_PROVIDER_REGISTRY` in
  `src/cpho_cli/core/llm.py`.
- `_OpenAICompatibleProvider.complete()` posts to
  `<base_url>/chat/completions`.
- `_OpenAICompatibleProvider.stream()` uses the same endpoint with
  `"stream": true` and parses SSE `data:` lines.
- Structured output uses tool/function calling via `_tool_schema()` and forced
  `tool_choice`.
- Retries are limited to transient HTTP statuses `{429, 500, 502, 503, 504}` and
  transport errors.
- Error messages pass through `redact_secrets()` before surfacing provider
  failures.

## LLM Call Sites

| Workflow | Call site | Integration notes |
|----------|-----------|-------------------|
| Solve | `src/cpho_cli/core/solve.py` | Loads problem/answer documents, OCRs pages, executes packaged solve skill, writes JSON/Markdown report. |
| Index tagging | `src/cpho_cli/core/index/tagging.py` | Uses provider config for tag refinement; can use text-only OCR or vision payloads. |
| Topic assignment | `src/cpho_cli/core/index/topic_assignment.py` | Assigns indexed problems into topic taxonomy with provider calls. |
| Paper splitting fallback | `src/cpho_cli/core/splitting/llm.py` | Uses prompt templates to split PDFs when rule-based splitting is insufficient. |
| Skill runtime | `src/cpho_cli/core/skill_handlers.py` | Renders Jinja prompts and calls the selected provider for built-in skills. |
| Explain | `src/cpho_cli/core/explain.py` | Streams panel output and records `input_modality_used`. |
| Probe/follow-up | `src/cpho_cli/core/probe.py`, `src/cpho_cli/core/followup.py` | Generates follow-up questions and transcripts. |
| Knowledge normalization | `src/cpho_cli/core/knowledge/normalize.py` | Converts user notes into knowledge Markdown with structured metadata. |

## Provider Configuration and Secrets

Provider config is modeled by `src/cpho_cli/models/config.py` and loaded by
`src/cpho_cli/core/config.py`.

Supported config sources:

- `providers.<name>.api_key_env`: preferred; reads the secret from environment.
- `providers.<name>.api_key`: supported for local gitignored config only.
- `provider.openrouter_api_key`: legacy OpenRouter config path.
- `providers.<name>.base_url`: optional override for OpenAI-compatible endpoints.
- `providers.<name>.default_model`: provider-level model default.
- `skills.<skill>.model`: skill-level model override.

Security-relevant facts:

- `.gitignore` excludes `*.local.yml`, `*.local.yaml`, `.env`, and `.cpho/`.
- The local repo currently has a gitignored `config.local.yml`; mapping documents
  must describe key locations without copying secret values.
- `redact_secrets()` in `src/cpho_cli/core/runtime.py` is used by provider error
  paths and skill runtime traces.
- `err_config_missing_api_key()` in `src/cpho_cli/core/errors.py` points users to
  env vars or local config without exposing values.

## OpenRouter Model Catalog

Model selection is a separate integration from chat completions:

- `src/cpho_cli/core/model_catalog.py` fetches
  `GET <base_url>/models` with bearer auth for OpenRouter.
- Successful results are normalized into `ModelCatalog` and cached under
  `~/.cache/cpho/models/openrouter.json`.
- Cache freshness is controlled by `ttl_seconds`, defaulting to 3600 seconds.
- If live fetch fails and cache exists, stale cache is used.
- If no cache exists, `src/cpho_cli/data/model_catalog/openrouter_fallback.json`
  is used as package fallback.
- `OpenRouterProvider.get_model_capabilities()` in `src/cpho_cli/core/llm.py`
  also queries `/models` and caches capabilities in-process.

## GitHub Community Knowledge Sync

Community knowledge base sync is implemented in
`src/cpho_cli/core/community_sync.py`.

Flow:

1. Load `<workspace>/.cpho/community-kb.yml` into `CommunitySyncConfig`.
2. Parse each enabled GitHub repository URL.
3. Fetch `GET https://api.github.com/repos/<owner>/<repo>/releases/tags/<tag>`.
4. Download the returned `tarball_url`.
5. Extract into a temp directory with path traversal checks.
6. Stage supported knowledge files, validating each with
   `load_knowledge_document()`.
7. Replace `~/.cache/cpho/community-kb/<repo>/`.
8. Write `metadata.json` and mark the cache read-only.

Optional auth:

- `github_token` in `CommunitySyncConfig` adds `Authorization: Bearer ...` for
  GitHub release and tarball requests.
- Token values must not be written into generated docs or traces.

Safety controls:

- `_safe_extract_tarball()` verifies every member path stays within the extract
  root and uses `tarfile.extractall(..., filter="data")`.
- Frontmatter validation rejects invalid community knowledge files before they
  are moved into the final cache.
- `err_community_sync_failed()` produces user-facing remediation text.

## OCR and Document Processing Integrations

| Integration | Files | Notes |
|-------------|-------|-------|
| PyMuPDF / `fitz` | `src/cpho_cli/core/documents.py`, `src/cpho_cli/core/compose_pdf.py`, `src/cpho_cli/core/workspace.py` | Reads PDFs, counts pages, extracts embedded text, rasterizes pages, and assembles output PDFs. |
| RapidOCR | `src/cpho_cli/core/ocr.py` | Instantiated lazily inside `RapidOCRProvider.extract()` to avoid import-time cost. |
| ONNX Runtime | `pyproject.toml` | Runtime dependency backing RapidOCR. |
| Mammoth | `src/cpho_cli/core/knowledge/normalize.py` | Converts `.docx` knowledge source files to Markdown before LLM normalization. |

The real workspace contains many PDFs with Chinese filenames and separate
problem/answer naming patterns. Discovery and indexing should assume:

- nested directories several levels deep,
- mixed source file types,
- `.DS_Store` noise from macOS,
- workspace-local generated state in `.cpho/`,
- possible corrupt or warning-producing PDFs.

## Local Workspace Integration

The most important integration boundary is the user's own filesystem.

Primary paths:

- Source workspace: `/Users/ericzhang/Desktop/物理竞赛资料`.
- Generated workspace state: `<workspace>/.cpho/`.
- Index: `<workspace>/.cpho/index.jsonl`.
- OCR cache: `<workspace>/.cpho/cache/ocr/`.
- Run trace: `<workspace>/.cpho/run-trace.jsonl`.
- Vocabulary overrides: `<workspace>/.cpho/vocabulary/`.
- Topic overrides: `<workspace>/.cpho/topics/`.
- Compositions: `<workspace>/.cpho/compositions/`.
- Compose exports: `<workspace>/.cpho/exports/compose/`.
- Private knowledge: `<workspace>/.cpho/knowledge/files/`.

Discovery excludes generated directories in `src/cpho_cli/core/workspace.py`:

- `.cpho`
- `artifacts`
- `exports`
- `output`
- `outputs`

## REPL and CLI Integration Points

The same core functions are exposed through two user interfaces:

- Typer CLI in `src/cpho_cli/cli/app.py`.
- prompt_toolkit REPL in `src/cpho_cli/cli/repl/`.

Shared integration behavior:

- Both use `load_config()` and provider resolution.
- Both call core modules rather than shelling out to subprocesses.
- REPL session state tracks active workspace, index metadata, search context,
  selected problem, and model settings in `src/cpho_cli/cli/repl/session.py`.
- REPL model and skill commands write workspace-local skill model overrides under
  `.cpho/skills/*.yml`.

## Network Boundaries

Commands with potential network access:

- `cpho solve` and REPL `/solve` when not in dry-run mode.
- `cpho index` and REPL `/index` when tagging/topic assignment or LLM splitting
  is needed.
- REPL `/explain`, `/probe`, and follow-up flows.
- `cpho knowledge normalize` when normalizing with an LLM provider.
- `cpho knowledge sync` when fetching GitHub releases and tarballs.
- REPL model panel when refreshing live OpenRouter model catalog.

Commands that are primarily local:

- `cpho index --dry-run`.
- Topic/index read APIs over existing `.cpho/index.jsonl`.
- Composition file creation/building when all selected entries and PDFs are local.
- Knowledge publish/find over existing private and community caches.

## Integration Test Coverage

Representative tests:

- Provider and redaction: `tests/test_llm.py`, `tests/test_config.py`.
- Model catalog: `tests/test_model_catalog.py`.
- OCR and document flow: `tests/test_ocr.py`, `tests/test_documents.py`,
  `tests/test_index_ocr_cache.py`, `tests/test_index_ocr_upgrade.py`.
- Index build/API: `tests/test_index_builder.py`, `tests/test_index_api.py`,
  `tests/test_index_cli.py`.
- Community KB: `tests/test_community_sync.py`, `tests/test_knowledge_cli.py`.
- REPL model/commands: `tests/test_repl_model_panel.py`,
  `tests/test_repl_workspace_commands.py`, `tests/test_repl_search_commands.py`.
- Real API verification records: `docs/test-001-real-api-verification.md` and
  `docs/test-002-real-api-verification.md`.

## Integration Risks

- Inline API keys are valid config, so generated documentation and logs must avoid
  copying local config values.
- Vision mode can upload source PDFs/images; this is sensitive for the real
  physics-coach workspace.
- GitHub community KB sync trusts pinned release content after validation; archive
  size and file-count limits are not yet enforced.
- PDF parsing depends on PyMuPDF behavior and can surface parser warnings for
  real-world files.
- OpenAI-compatible providers differ in tool-call support; DeepSeek model choice
  is documented as important in `docs/index-tool-calling-design-note.md`.
