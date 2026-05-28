<!-- refreshed: 2026-05-28 -->
# Technology Stack

**Analysis Date:** 2026-05-28

## Project Identity

- Package: `cpho-cli`
- Purpose: local command-line workbench for Chinese Physics Olympiad problem
  indexing, official-answer review, explanation generation, follow-up probing,
  related-problem search, knowledge management, and PDF composition.
- Runtime entry point: `cpho = "cpho_cli.cli.app:app"` in `pyproject.toml`.
- Source layout: Python package under `src/cpho_cli/`, tests under `tests/`.
- Primary user workspace shape: nested Chinese-named directories containing PDF
  papers, answer PDFs, image problems, and a workspace-local `.cpho/` data folder,
  as seen under `/Users/ericzhang/Desktop/物理竞赛资料`.

## Languages and Runtime

| Layer | Technology | Evidence |
|-------|------------|----------|
| Application language | Python 3.11+ | `pyproject.toml` declares `requires-python = ">=3.11"` |
| Package manager | uv | `uv.lock`, README quick start, `[tool.uv] package = true` |
| CLI framework | Typer + Click | `src/cpho_cli/cli/app.py`, `pyproject.toml` |
| Interactive shell | prompt_toolkit | `src/cpho_cli/cli/repl/app.py`, `src/cpho_cli/cli/repl/` |
| Terminal rendering | Rich with plain fallback | `src/cpho_cli/core/skill_progress.py`, README dependency table |
| Data models | Pydantic v2 strict models | `src/cpho_cli/models/config.py`, `src/cpho_cli/models/index.py` |
| YAML parsing | PyYAML | `src/cpho_cli/core/config.py`, `src/cpho_cli/core/index/vocabulary.py` |
| Prompt templates | Jinja2 | `src/cpho_cli/core/skill_handlers.py`, prompt `*.md.j2` files |

## Core Dependencies

| Dependency | Role | Primary files |
|------------|------|---------------|
| `httpx>=0.27` | OpenAI-compatible chat completions, model catalog fetches, GitHub release API, tarball downloads | `src/cpho_cli/core/llm.py`, `src/cpho_cli/core/model_catalog.py`, `src/cpho_cli/core/community_sync.py` |
| `pymupdf>=1.24` | PDF page loading, text extraction, page rasterization, PDF composition | `src/cpho_cli/core/documents.py`, `src/cpho_cli/core/compose_pdf.py`, `src/cpho_cli/core/workspace.py` |
| `rapidocr>=3.0` | OCR engine for image/PDF pages without embedded text | `src/cpho_cli/core/ocr.py` |
| `onnxruntime>=1.18` | Runtime used by RapidOCR models | `pyproject.toml` |
| `mammoth>=1.12.0` | Word `.docx` to Markdown conversion for knowledge normalization | `src/cpho_cli/core/knowledge/normalize.py` |
| `wcwidth>=0.2.13` | Terminal width handling for CJK display | `pyproject.toml`, REPL/display usage |
| `rich>=13.0` | Progress spinner and terminal formatting | `src/cpho_cli/core/skill_progress.py` |

## Development Tooling

| Tool | Configuration | Notes |
|------|---------------|-------|
| pytest | `[tool.pytest.ini_options] testpaths = ["tests"]` | Large test suite covers CLI, REPL, index, OCR, solve, explain, knowledge, compose, and docs. |
| pytest-asyncio | dev dependency | Used for async REPL command tests. |
| ruff | `[tool.ruff] line-length = 100`, `target-version = "py311"` | Formatting/linting authority. |
| mypy | strict mode in `pyproject.toml` | Strict typing is configured; `CONCERNS.md` notes current strict failures. |
| setuptools package data | `[tool.setuptools.package-data]` | Ships built-in skills, vocabularies, topic taxonomies, prompt manifests, and model fallback data. |

## Configuration Stack

Configuration is local-first and file/env based:

- Default filenames: `config.local.yml`, `config.local.yaml` in `src/cpho_cli/core/config.py`.
- Discovery: `find_default_config_path()` walks from the current directory upward.
- Schema: `AppConfig`, `ProviderProfile`, `ModelParams`, and `SkillConfig` in
  `src/cpho_cli/models/config.py`.
- Active provider: `active_provider` defaults to `openrouter`.
- Legacy provider support: `provider.openrouter_api_key` and `provider.base_url`
  are still converted into an OpenRouter profile by `_legacy_openrouter_profile()`.
- Preferred secret handling: `api_key_env` such as `OPENROUTER_API_KEY` or
  `DEEPSEEK_API_KEY`; inline `api_key` is supported but should remain gitignored.
- Timeout override: provider-level `timeout`, otherwise `LLM_TIMEOUT`, otherwise
  120 seconds.
- Per-skill model override: `config.skills.<skill>.model` merged by
  `resolve_model_params()`.

## Package Data and Built-In Assets

The package ships domain assets rather than downloading them at runtime:

- Built-in skill specifications and prompts: `src/cpho_cli/builtin_skills/**/*`.
- Built-in vocabulary: `src/cpho_cli/vocabulary/builtin.yml` and
  `src/cpho_cli/vocabulary/builtin/*.yml`.
- Built-in topic taxonomy: `src/cpho_cli/vocabulary/topics/builtin_topics.yml`.
- Index prompt templates: `src/cpho_cli/core/index/prompts/*`.
- Splitting prompt templates: `src/cpho_cli/core/splitting/prompts/*`.
- Knowledge prompt templates: `src/cpho_cli/core/knowledge/prompts/*`.
- Fallback model catalog: `src/cpho_cli/data/model_catalog/openrouter_fallback.json`.

These paths are included in `pyproject.toml` under `[tool.setuptools.package-data]`.

## Local Storage Technologies

| Storage | Format | Location |
|---------|--------|----------|
| Main index | JSON Lines | `<workspace>/.cpho/index.jsonl` |
| OCR cache | JSON/cache files | `<workspace>/.cpho/cache/ocr/` |
| Run trace | JSON Lines | `<workspace>/.cpho/run-trace.jsonl` |
| User vocabulary | YAML | `<workspace>/.cpho/vocabulary/*.yml` |
| Topic taxonomy overrides | YAML | `<workspace>/.cpho/topics/*.yml` |
| Notebook notes | JSON | `<workspace>/.cpho/notebook/<problem_id>.json` |
| Compositions | YAML | `<workspace>/.cpho/compositions/*.yml` |
| Compose exports | PDF | `<workspace>/.cpho/exports/compose/` |
| Knowledge drafts/published files | Markdown with YAML frontmatter | `<workspace>/.cpho/knowledge/` |
| Community KB cache | Markdown + metadata JSON | `~/.cache/cpho/community-kb/<repo>/` |
| Model catalog cache | JSON | `~/.cache/cpho/models/<provider>.json` |

## Runtime Architecture by Dependency

**CLI and REPL**

- Typer commands live in `src/cpho_cli/cli/app.py`.
- The REPL is prompt_toolkit-based and split into session, display, persistence,
  completers, adapters, and slash command modules under `src/cpho_cli/cli/repl/`.
- CLI command bodies convert domain exceptions into `typer.BadParameter`; core
  modules do not depend on terminal UI.

**LLM and structured outputs**

- `src/cpho_cli/core/llm.py` implements a shared OpenAI-compatible provider for
  `/chat/completions`.
- Structured output is implemented with forced function/tool calling, not JSON
  schema response format.
- Streaming consumes server-sent event lines and returns text deltas.
- Provider metadata fetches model capabilities from `/models` when supported.

**Document processing**

- `src/cpho_cli/core/documents.py` loads images directly and PDFs via PyMuPDF.
- PDF pages retain embedded text and are rasterized to PNG bytes for OCR or
  multimodal upload.
- `src/cpho_cli/core/ocr.py` prefers embedded text and falls back to RapidOCR for
  page images.
- `src/cpho_cli/core/compose_pdf.py` assembles source PDF pages with PyMuPDF.

**Knowledge processing**

- `src/cpho_cli/core/knowledge/normalize.py` supports text-like sources and uses
  Mammoth for Word documents.
- `src/cpho_cli/core/knowledge/store.py` validates Markdown frontmatter and loads
  private/community knowledge documents.
- `src/cpho_cli/core/knowledge/resolver.py` resolves private knowledge before
  community cache entries.

## External Runtime Requirements

- Python 3.11 or newer.
- `uv` for the documented development and execution workflow.
- Network access only when a command calls an LLM provider, fetches a model
  catalog, or syncs community KB from GitHub.
- Provider credentials supplied by environment variables or gitignored local YAML.
- For realistic acceptance testing, a workspace shaped like
  `/Users/ericzhang/Desktop/物理竞赛资料`, including nested folders, PDF papers,
  answer files, images, and `.cpho/` state.

## Build and Distribution Status

- Project is packageable as a Python package through setuptools and uv.
- No compiled extension modules are authored in this repository.
- No frontend build system, database server, web server, Dockerfile, or CI workflow
  is present in the mapped repo snapshot.
- `.github/` contains issue templates and a demo SVG asset, not an automated CI
  pipeline.
