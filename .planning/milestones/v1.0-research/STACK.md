# Technology Stack

**Project:** CPHO CLI
**Researched:** 2026-05-20
**Overall confidence:** HIGH

## Recommended Stack

### Language Runtime

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.12 | Runtime | Current stable CPython with mature typing, match statements, and best async support. Python 3.13 has GIL-removal but ecosystem not fully there yet. |

### LLM Abstraction

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| LiteLLM | 1.85.x | Unified LLM API interface | Proven by Aider and Open Interpreter in production. Native OpenRouter support (`openrouter/` prefix). Supports 50+ providers with single API. Handles cost tracking, retries, fallbacks. No LangChain dependency. |

### CLI Layer

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Typer | latest | CLI argument parsing, subcommands | Builds on Click's maturity but adds type-hint-driven DX. `solve`, `batch`, `index`, `tag` commands defined as typed Python functions. Same author as FastAPI — consistent philosophy. |
| prompt-toolkit | 3.0.52 | REPL interactive mode | Gold standard for Python REPLs (powers IPython, pgcli, mycli). Provides `PromptSession` with history, autocomplete, Vi/Emacs keybindings, multi-line input, bottom toolbar for contextual help. |
| Rich | 15.0.0 | Terminal markdown rendering, tables, syntax highlighting | Best-in-class terminal output. `rich.markdown.Markdown` renders LLM responses (headings, lists, code blocks with syntax highlighting). `rich.live.Live` for streaming output. `rich.table.Table` for result comparison. |

**Why prompt-toolkit + Rich, not Textual:**
Textual is a full-screen TUI framework (widgets, CSS layout, mouse support). Our v1 needs a command-driven REPL, not a dashboard. prompt-toolkit excels at the REPL pattern. The Aider project uses exactly this combo: prompt-toolkit for input, Rich for output.

### Skill / Plugin System

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| pluggy | 1.6.0 | Hook-based plugin system | Born from pytest, battle-tested by thousands of projects. MIT license. Separates hook specs (declared by core) from hook implementations (provided by plugins). Supports `tryfirst`/`trylast` ordering and `hookwrapper` pattern. |
| importlib.metadata | stdlib (3.12) | Plugin discovery via entry points | Python standard since 3.8. Plugins declare `[project.entry-points."cpho.skills"]` in pyproject.toml. Core discovers them at runtime without import magic. |

**Skill system layering:**
- **Level 1 (Prompt template):** `.md` or `.yaml` file with frontmatter metadata. Core reads, interpolates variables, sends to LLM. No pluggy needed — pure file-based.
- **Level 2 (Declarative YAML):** YAML config specifying prompt templates, parameters, output schema. Core interprets the YAML as a pipeline definition.
- **Level 3 (Python script):** Full pluggy plugin implementing `cpho.skills` hook specs. Can define custom DAG steps, preprocessing, postprocessing.

### Task Pipeline / DAG Orchestration

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Custom lightweight DAG | (in core/) | Deterministic multi-step LLM pipeline | No existing framework fits our exact need. LangGraph is designed for agentic loops (not our use case). Haystack is RAG-focused. Our DAG is simple: OCR output passes through ordered steps (chunking → Q1 deduction → Q2 deduction → synthesis). Each step = LiteLLM call with a curated prompt template + context window. |
| asyncio | stdlib (3.12) | Concurrent step execution | When DAG steps are independent (e.g., parallel sub-question deduction), `asyncio.gather()` runs them concurrently. Python's TaskGroup (3.11+) for structured concurrency. |

**Why NOT LangChain/LangGraph:**
1. Their core value prop (agentic loops, tool use, memory management) is what we explicitly avoid — we use deterministic DAG pipelines.
2. Dependency footprint is massive (~200+ transitive dependencies).
3. LangChain's abstraction layers (Chain, Agent, Tool) add complexity without benefit for our linear/branching prompt pipelines.
4. Aider (the most mature Python AI CLI) intentionally avoids LangChain — uses LiteLLM directly. Open Interpreter does the same.
5. For a local CLI tool, startup time and install size matter. LangChain adds significant weight.

**Why NOT Prefect/Dagster/Airflow:**
These are production data pipeline schedulers with servers, databases, and UI dashboards. Our DAG runs in-process during a single CLI session — no scheduling, no persistence, no distributed workers needed.

### OCR

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| RapidOCR | latest | Primary OCR engine (Chinese + formula) | ONNX Runtime backend — no PaddlePaddle dependency. Cross-platform (Win/Mac/Linux). Models <5MB. CPU performance >30 FPS. Apache 2.0 license. |
| RapidLaTeXOCR | latest | LaTeX formula recognition | Specialized fork for math formula → LaTeX conversion. ONNX Runtime based. Handles inline `$...$` and display `$$...$$` formulas. |
| PaddleOCR | 3.2.x | Optional high-accuracy fallback | Higher accuracy for complex layouts, but requires PaddlePaddle framework (heavier install). Recommended as optional dependency behind an OCR abstraction interface. |

**OCR abstraction pattern:**
```python
# core defines the interface
class OcrEngine(Protocol):
    async def recognize(self, image_path: Path) -> OcrResult: ...

# Two implementations
class RapidOcrEngine: ...   # Default, fast, lightweight
class PaddleOcrEngine: ...   # Optional, higher accuracy
```

User chooses at config time. Default is RapidOCR for quick setup.

### PDF Processing

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| pikepdf | latest | Primary PDF manipulation | C++ (QPDF) backend — 15x faster than pure Python on large files. Handles corrupted PDFs. MPL 2.0 license. Perfect for merging/splitting problem PDFs and answer PDFs. |
| pypdf | 5.x | Simple PDF operations | Pure Python, zero external dependencies. Use for metadata reading, basic splitting when pikepdf heavy install is not needed. |
| pdf2image | latest | PDF page → image conversion | Wraps poppler. Needed to feed PDF pages into OCR pipeline. |

**PDF output strategy (confirmed):**
The "image stitching" approach is validated. For "组卷输出" (compilation output), we:
1. Extract relevant pages from source PDFs using pikepdf
2. Concatenate into problem set PDF and answer set PDF
3. No LaTeX re-rendering needed — cuts cost and preserves original formatting

### Configuration

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| pydantic-settings | 2.x | Typed configuration management | Loads from env vars, `.env` files, YAML files, CLI args with clear priority. Built-in validation (e.g., `OPENROUTER_API_KEY` must be non-empty string). `SettingsConfigDict` for declarative config. |
| PyYAML | 6.x | YAML parsing for skill configs | Standard YAML library. Used for skill definitions (Level 2) and batch experiment configs. |

### Data Storage

| Technology | Format | Purpose | Why |
|------------|--------|---------|-----|
| JSON | `.cpho/index.jsonl` | Tag index (one JSON object per line per problem) | Append-only, grep-friendly, human-readable. Each line = one problem's metadata (file path, tags, physics models, heuristics, difficulty). No database needed. |
| YAML | `.cpho/config.yaml` | Project configuration | User edits directly. Model settings, OCR engine choice, skill registry, API key reference (points to env var, never stores the key itself). |

### Utilities

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| httpx | latest | Async HTTP client | Modern async HTTP with HTTP/2 support. Used by LiteLLM internally, also for any direct API calls. |
| structlog | latest | Structured logging | Key-value logging to JSONL files. Enables `grep` / `jq` analysis of pipeline execution traces. Standard in Python CLI tools. |
| pydantic | 2.x | Data validation and serialization | Already pulled in by pydantic-settings. Used for skill output schemas, OCR result structures, pipeline intermediate data. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| LLM framework | LiteLLM (direct) | LangChain / LangGraph | Agentic-loop design conflicts with deterministic DAG requirement. Massive dependency tree. Aider and Open Interpreter both avoid it. |
| LLM framework | LiteLLM (direct) | Haystack | RAG-focused architecture. Pipeline model is document-centric, not problem-solving-centric. |
| CLI framework | Typer | Click (directly) | Typer IS Click under the hood but adds type-hint-driven API. Same capabilities, better DX. |
| CLI framework | Typer | argparse | Too low-level. Manual help text, no type coercion, verbose code. Standard library but wrong tool for multi-command CLI. |
| REPL/TUI | prompt-toolkit + Rich | Textual | Full-screen TUI framework for dashboards, not command-driven REPLs. Too heavy for v1. |
| OCR | RapidOCR | PaddleOCR (as primary) | Requires PaddlePaddle framework install — heavy for quick local setup. Use as optional upgrade path. |
| OCR | RapidOCR | Tesseract | Poor Chinese + LaTeX mixed content accuracy. Not designed for this use case. |
| Plugin system | pluggy | Custom decorator registry | pluggy provides hook ordering (tryfirst/trylast), hookwrapper, and multimethod dispatch for free. Standard pattern, less to maintain. |
| Plugin system | pluggy | setuptools entry points (alone) | Entry points handle discovery but don't provide hook semantics. pluggy + entry points is the standard combo. |
| PDF | pikepdf | PyMuPDF (fitz) | AGPL license — incompatible with project's MIT license. Stronger text extraction but license is a blocker. |
| PDF | pikepdf | pdfplumber | Good for table extraction but slower and heavier. Not needed for our image-stitching PDF output approach. |
| Pipeline | Custom DAG | Prefect / Dagster | Production orchestrators with servers and databases. Overkill for in-process pipeline execution during a CLI session. |
| Pipeline | Custom DAG | Dask | Distributed computing framework. We don't need cluster scheduling for single-machine LLM API calls. |

## Installation

```bash
# Core dependencies
pip install litellm>=1.80
pip install pluggy>=1.6.0
pip install pydantic-settings>=2.0
pip install pydantic>=2.0
pip install pyyaml>=6.0
pip install httpx

# CLI layer
pip install typer
pip install prompt-toolkit>=3.0.50
pip install rich>=15.0.0  # (likely 14.x on Python 3.12; 15.0 requires Python 3.9+)

# OCR (primary — lightweight ONNX Runtime path)
pip install rapidocr
pip install rapid-latex-ocr

# OCR (optional — high accuracy upgrade)
# pip install paddlepaddle paddleocr  # heavier install

# PDF processing
pip install pikepdf
pip install pypdf>=5.0
pip install pdf2image  # requires poppler system install (brew install poppler on macOS)

# Dev dependencies
pip install pytest>=8.0
pip install pytest-asyncio
pip install mypy>=1.0
pip install ruff  # linter + formatter (replaces flake8 + isort + black)
```

## Source References

- **LiteLLM + OpenRouter**: [litellm GitHub Issues](https://github.com/BerriAI/litellm) — OpenRouter provider confirmed as first-class support. Verified via ContextAgent, CIRISProxy production usage.
- **Aider architecture**: [DeepWiki — Aider Core System](https://deepwiki.com/helloandworlder/aider/2-core-system) and [Architecture Overview](https://deepwiki.com/helloandworlder/aider/1.2-architecture-overview). Confirms LiteLLM + Rich + prompt-toolkit pattern. Apache 2.0.
- **Open Interpreter architecture**: [DeepWiki — Core Architecture](https://deepwiki.com/OpenInterpreter/open-interpreter/3-core-architecture). Confirms same LiteLLM pattern. AGPL-3.0 (note license incompatibility — reference patterns only, not code).
- **prompt-toolkit 3.0.52**: [PyPI](https://pypi.org/project/prompt-toolkit/) — latest release Aug 27, 2025. Verified features: `PromptSession`, `NestedCompleter`, `FileHistory`.
- **Rich 15.0.0**: [PyPI](https://pypi.org/project/rich/) — latest release Apr 12, 2026. Python ≥3.9. Verified `rich.markdown.Markdown` class for terminal rendering.
- **pluggy 1.6.0**: [Changelog](https://pluggy.readthedocs.io/en/stable/changelog.html) — May 15, 2025 release. Python 3.9–3.14 support. MIT license.
- **RapidOCR**: [DeepWiki](https://deepwiki.com/RapidAI/RapidOCR/1-overview) and [Key Features](https://deepwiki.com/RapidAI/RapidOCR/1.2-key-features). ONNX Runtime backend, <5MB models, Apache 2.0.
- **PaddleOCR 3.2.0**: [官方更新页](http://www.paddleocr.ai/main/update/update.html) — Aug 21, 2025 release. PP-FormulaNet for LaTeX formula recognition.
- **pikepdf**: Feature matrix via [PyMuPDF docs](https://pymupdf.readthedocs.io/en/latest/about.html#about-feature-matrix) benchmark: 15x faster than pypdf on 7,031-page merge test. MPL 2.0.
- **LangGraph vs Haystack 2025**: [aimug.org analysis](https://aimug.org/docs/jun-2025/lightning-talks/ai-ecosystem-2025/research-guide/) and [dev.to competitive analysis](https://dev.to/yeahiasarker/executive-competitive-analysis-graphbit-vs-langchain-llamaindex-haystack-and-workflow-4lad). Confirms LangGraph is agentic-loop focused.

## Confidence Assessment

| Area | Confidence | Reason |
|------|------------|--------|
| LLM abstraction (LiteLLM) | HIGH | Verified in production by Aider and Open Interpreter. OpenRouter support confirmed in LiteLLM issues. |
| CLI layer (Typer + prompt-toolkit + Rich) | HIGH | This exact combo is used by Aider (the most mature Python AI CLI). All libraries have current PyPI releases verified. |
| Plugin system (pluggy) | HIGH | v1.6.0 released May 2025. pytest ecosystem standard. MIT license. Mature API. |
| OCR (RapidOCR) | MEDIUM | Strong community adoption for Chinese OCR. LaTeX formula recognition via RapidLaTeXOCR is promising but needs validation on physics competition problem scans specifically. Recommend spike test with 10 real problems. |
| DAG (custom) | MEDIUM | Rationale to avoid LangChain/LangGraph is solid, but custom DAG is untested. Recommend modeling after Hamilton's function-name-based wiring or Aider's sequential coder pipeline. |
| PDF (pikepdf) | HIGH | Benchmarks confirm 15x speed advantage. MPL 2.0 license is compatible. Mature library. |
