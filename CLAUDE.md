# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

<!-- GSD:project-start source:PROJECT.md -->
## Project

**CPHO CLI**

CPHO CLI 是一个本地命令行工具，帮助物理竞赛教练和深度学习者对题目文件夹进行 AI 驱动的结构化分析。用户在自己本地的题目文件夹（PDF/图片 + 答案）中工作，通过可扩展的 Skill 插件系统运行多种分析模式——包括主动提问、逐步讲解、多题对比分析、组卷输出。它是物理竞赛领域的 Obsidian + AI agent：文件夹即知识库，标签索引驱动高效检索，解析质量优先于一切。

**Core Value:** **生成质量**——真正找到题目的难点、启发点，讲清楚每一步推导的"为什么"，关联到相关题目形成知识网络。这是系统内置 skill 需要反复打磨的核心。

### Constraints

- **技术栈**: Python only，不引入 Node.js/TypeScript 依赖
- **本地优先**: 除 LLM API 调用外，所有处理在本地完成，不上传题目文件到任何远程服务
- **安全**: API Key 只能从环境变量或本地配置文件读取，严禁硬编码或提交到 git
- **开源协议**: MIT License，面向物理竞赛社区
- **解析质量**: 严谨防幻觉，解析结果必须基于题目原文和标准答案
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

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
### Skill / Plugin System
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| pluggy | 1.6.0 | Hook-based plugin system | Born from pytest, battle-tested by thousands of projects. MIT license. Separates hook specs (declared by core) from hook implementations (provided by plugins). Supports `tryfirst`/`trylast` ordering and `hookwrapper` pattern. |
| importlib.metadata | stdlib (3.12) | Plugin discovery via entry points | Python standard since 3.8. Plugins declare `[project.entry-points."cpho.skills"]` in pyproject.toml. Core discovers them at runtime without import magic. |
- **Level 1 (Prompt template):** `.md` or `.yaml` file with frontmatter metadata. Core reads, interpolates variables, sends to LLM. No pluggy needed — pure file-based.
- **Level 2 (Declarative YAML):** YAML config specifying prompt templates, parameters, output schema. Core interprets the YAML as a pipeline definition.
- **Level 3 (Python script):** Full pluggy plugin implementing `cpho.skills` hook specs. Can define custom DAG steps, preprocessing, postprocessing.
### Task Pipeline / DAG Orchestration
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Custom lightweight DAG | (in core/) | Deterministic multi-step LLM pipeline | No existing framework fits our exact need. LangGraph is designed for agentic loops (not our use case). Haystack is RAG-focused. Our DAG is simple: OCR output passes through ordered steps (chunking → Q1 deduction → Q2 deduction → synthesis). Each step = LiteLLM call with a curated prompt template + context window. |
| asyncio | stdlib (3.12) | Concurrent step execution | When DAG steps are independent (e.g., parallel sub-question deduction), `asyncio.gather()` runs them concurrently. Python's TaskGroup (3.11+) for structured concurrency. |
### OCR
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| RapidOCR | latest | Primary OCR engine (Chinese + formula) | ONNX Runtime backend — no PaddlePaddle dependency. Cross-platform (Win/Mac/Linux). Models <5MB. CPU performance >30 FPS. Apache 2.0 license. |
| RapidLaTeXOCR | latest | LaTeX formula recognition | Specialized fork for math formula → LaTeX conversion. ONNX Runtime based. Handles inline `$...$` and display `$$...$$` formulas. |
| PaddleOCR | 3.2.x | Optional high-accuracy fallback | Higher accuracy for complex layouts, but requires PaddlePaddle framework (heavier install). Recommended as optional dependency behind an OCR abstraction interface. |
# core defines the interface
# Two implementations
### PDF Processing
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| pikepdf | latest | Primary PDF manipulation | C++ (QPDF) backend — 15x faster than pure Python on large files. Handles corrupted PDFs. MPL 2.0 license. Perfect for merging/splitting problem PDFs and answer PDFs. |
| pypdf | 5.x | Simple PDF operations | Pure Python, zero external dependencies. Use for metadata reading, basic splitting when pikepdf heavy install is not needed. |
| pdf2image | latest | PDF page → image conversion | Wraps poppler. Needed to feed PDF pages into OCR pipeline. |
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
# Core dependencies
# CLI layer
# OCR (primary — lightweight ONNX Runtime path)
# OCR (optional — high accuracy upgrade)
# pip install paddlepaddle paddleocr  # heavier install
# PDF processing
# Dev dependencies
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
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
