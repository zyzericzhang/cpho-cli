<!-- refreshed: 2026-05-28 -->
# Architecture

**Analysis Date:** 2026-05-28

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                         CLI Surface                          │
├──────────────────┬──────────────────┬───────────────────────┤
│  Typer Commands  │ prompt_toolkit    │  Built-in Commands    │
│ `src/cpho_cli/`  │ REPL             │ `src/cpho_cli/cli/`    │
│ `cli/app.py`     │ `cli/repl/app.py`│ `repl/commands/`       │
└────────┬─────────┴────────┬─────────┴──────────┬────────────┘
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      Core Application Layer                  │
│ `src/cpho_cli/core/`                                        │
│ index, solve, explain, probe, compose, knowledge, config     │
└────────┬─────────────────────────┬──────────────────────────┘
         │                         │
         ▼                         ▼
┌─────────────────────────────┐   ┌───────────────────────────┐
│       Domain Models          │   │      Adapter Protocols     │
│ `src/cpho_cli/models/`       │   │ `core/llm.py`, `core/ocr.py`│
│ Pydantic schemas             │   │ OpenAI-compatible LLM, OCR │
└────────┬────────────────────┘   └─────────────┬─────────────┘
         │                                      │
         ▼                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Local Workspace + Package Data             │
│ workspace `.cpho/`, XDG config/cache/data, builtin skills,   │
│ builtin vocabulary, PDFs/images, JSONL/YAML/Markdown outputs │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| CLI root | Defines `cpho` Typer commands for solve, index, topic, compose, knowledge, and REPL startup. | `src/cpho_cli/cli/app.py` |
| REPL runtime | Owns prompt_toolkit loop, command dispatch, session initialization, and REPL error logging. | `src/cpho_cli/cli/repl/app.py` |
| REPL commands | Register slash commands and adapt user input into core service calls. | `src/cpho_cli/cli/repl/commands/__init__.py` |
| Session state | Carries active workspace, config, index metadata, search context, solve context, and REPL settings. | `src/cpho_cli/cli/repl/session.py` |
| Workspace discovery | Scans PDF/image trees, ignores generated directories, classifies problem and answer files, and pairs by filename markers. | `src/cpho_cli/core/workspace.py` |
| Document loader | Converts images and PDFs into `DocumentInput` pages with embedded text and PNG page images. | `src/cpho_cli/core/documents.py` |
| OCR adapter | Defines `OCRProvider` and implements RapidOCR-backed extraction with embedded-text shortcut. | `src/cpho_cli/core/ocr.py` |
| Index builder | Orchestrates discovery, OCR cache, splitting, fingerprints, tag refinement, topic assignment, and index writes. | `src/cpho_cli/core/index/builder.py` |
| Index storage/API | Reads and writes `.cpho/index.jsonl`, queries entries, mutates user tags, and finds related problems. | `src/cpho_cli/core/index/storage.py`, `src/cpho_cli/core/index/api.py` |
| Vocabulary loaders | Merge builtin, workspace, and private vocabulary/topic layers into canonical lookup structures. | `src/cpho_cli/core/index/vocabulary.py`, `src/cpho_cli/core/index/topic_vocabulary.py` |
| Skill runtime | Executes skill DAGs, validates step inputs/outputs, writes optional traces/checkpoints, and redacts secrets. | `src/cpho_cli/core/runtime.py` |
| Skill loader/handlers | Load package skill folders and render Jinja prompts into LLM calls or Python-tool steps. | `src/cpho_cli/core/skills.py`, `src/cpho_cli/core/skill_handlers.py` |
| Solve service | Runs the packaged solve skill over OCR text and writes JSON/Markdown reports. | `src/cpho_cli/core/solve.py` |
| Explain service | Streams panel explanations, resolves knowledge references, extracts candidate tags, and writes Markdown. | `src/cpho_cli/core/explain.py` |
| Probe service | Runs an interactive follow-up loop and stores a Markdown transcript. | `src/cpho_cli/core/probe.py` |
| Composition service | Resolves composition slots from index entries and assembles problem/answer PDFs. | `src/cpho_cli/core/composition.py`, `src/cpho_cli/core/compose_pdf.py` |
| Knowledge service | Normalizes, publishes, resolves, and syncs knowledge documents. | `src/cpho_cli/core/knowledge/` |
| Data models | Define strict Pydantic contracts for documents, index entries, config, skills, runtime, solve, explain, probe, topics, and knowledge. | `src/cpho_cli/models/` |
| Builtin assets | Package built-in skills, prompt templates, vocabulary, topics, and model catalog data. | `src/cpho_cli/builtin_skills/`, `src/cpho_cli/vocabulary/`, `src/cpho_cli/data/` |

## Pattern Overview

**Overall:** Layered local CLI with a functional core, strict Pydantic domain models, filesystem-backed workspace state, and adapter protocols for LLM/OCR providers.

**Key Characteristics:**
- Keep UI adapters thin: `src/cpho_cli/cli/app.py` and `src/cpho_cli/cli/repl/commands/` should parse arguments, handle interactive confirmation, and call `src/cpho_cli/core/` functions.
- Put business rules in `src/cpho_cli/core/` and represent all cross-module payloads with `src/cpho_cli/models/`.
- Store user/workspace state in local files rather than a database: `.cpho/index.jsonl`, `.cpho/vocabulary/*.yml`, `.cpho/topics/*.yml`, `.cpho/compositions/*.yml`, `.cpho/exports/`, XDG session/history/log files, and `output/`.
- Use package data for built-in skill and taxonomy assets: `src/cpho_cli/builtin_skills/` and `src/cpho_cli/vocabulary/` are shipped through `pyproject.toml`.
- Treat the real user workspace shape as nested, Chinese-named folders with mixed `.pdf`, image files, and separate problem/answer naming markers; design discovery changes around `src/cpho_cli/core/workspace.py`.

## Layers

**Command Layer:**
- Purpose: Expose user workflows through command-line subcommands and REPL slash commands.
- Location: `src/cpho_cli/cli/`
- Contains: Typer commands, prompt_toolkit app, command registry, display helpers, completers, REPL persistence adapters.
- Depends on: `src/cpho_cli/core/`, `src/cpho_cli/models/`, Typer, click, prompt_toolkit.
- Used by: Console script `cpho` configured in `pyproject.toml`.

**Core Services Layer:**
- Purpose: Implement application use cases independently from CLI parsing.
- Location: `src/cpho_cli/core/`
- Contains: `build_index`, `solve_problem`, `run_explain`, `run_probe`, `resolve_composition_slots`, `assemble_composition_pdfs`, `KnowledgeResolver`, config resolution, LLM/OCR adapters, boundary checks.
- Depends on: Pydantic models in `src/cpho_cli/models/`, package assets, PyMuPDF, RapidOCR, httpx, Jinja2, PyYAML.
- Used by: CLI commands, REPL commands, tests.

**Index Subsystem:**
- Purpose: Build and query a structured physics-problem index for local workspaces.
- Location: `src/cpho_cli/core/index/`
- Contains: Orchestrator, storage, API, hashing, OCR cache, tag refinement, topic assignment, vocabulary loaders, notebooks, composition search.
- Depends on: `src/cpho_cli/core/workspace.py`, `src/cpho_cli/core/documents.py`, `src/cpho_cli/core/ocr.py`, `src/cpho_cli/core/splitting/`, `src/cpho_cli/core/llm.py`, `src/cpho_cli/models/index.py`.
- Used by: `cpho index`, `/index`, `/search`, `/show`, `/search-related`, compose, knowledge resolver, solve tag persistence.

**Skill Runtime Layer:**
- Purpose: Execute packaged skill DAGs with reproducible prompts and strict output validation.
- Location: `src/cpho_cli/core/runtime.py`, `src/cpho_cli/core/skills.py`, `src/cpho_cli/core/skill_handlers.py`
- Contains: `SkillRuntime`, `SkillSpec`, `SkillStep`, prompt rendering, LLM JSON parsing, Python tool handler, trace/checkpoint writers.
- Depends on: `src/cpho_cli/models/skills.py`, `src/cpho_cli/models/runtime.py`, `src/cpho_cli/core/llm.py`, Jinja2.
- Used by: `src/cpho_cli/core/solve.py` and debug/model-panel REPL tools.

**Domain Model Layer:**
- Purpose: Provide typed, validated contracts for all major data exchanged between layers.
- Location: `src/cpho_cli/models/`
- Contains: Strict Pydantic models for documents, OCR, index, topics, config, LLM, skill specs, runtime traces, solve reports, explain panels, probe transcripts, composition files, knowledge docs, community sync.
- Depends on: Pydantic and standard library only.
- Used by: All `src/cpho_cli/core/` and `src/cpho_cli/cli/` modules.

**Asset/Data Layer:**
- Purpose: Ship built-in prompts, vocabulary, topic taxonomy, model catalog, and sample files.
- Location: `src/cpho_cli/builtin_skills/`, `src/cpho_cli/vocabulary/`, `src/cpho_cli/data/`, `examples/`
- Contains: `SKILL.md`, `skill.yml`, Jinja templates, YAML vocabularies, OpenRouter fallback catalog, sample problem/answer Markdown.
- Depends on: Package data inclusion in `pyproject.toml`.
- Used by: Skill loader, index vocabulary loaders, model catalog, documentation/tests.

**Workspace Persistence Layer:**
- Purpose: Persist user-specific and workspace-specific state without a server.
- Location: User workspaces, XDG directories, and local output dirs.
- Contains: `.cpho/index.jsonl`, `.cpho/cache/`, `.cpho/vocabulary/`, `.cpho/topics/`, `.cpho/compositions/`, `.cpho/exports/`, `.cpho/knowledge/`, `.cpho/community-kb.yml`, `~/.config/cpho/session.json`, `~/.config/cpho/history.txt`, `~/.cache/cpho/repl.log`, `~/.local/share/cpho/`.
- Depends on: Filesystem access and boundary checks in `src/cpho_cli/core/boundary.py`.
- Used by: REPL, index, compose, knowledge, output writing.

## Data Flow

### Primary Index Build Path

1. User invokes `cpho index` or `/index`; Typer calls `build_index(...)` from `index_command` (`src/cpho_cli/cli/app.py:204`) and REPL calls the same core function (`src/cpho_cli/cli/repl/commands/workspace.py:271`).
2. `build_index` resolves `workspace_root`, optional `target_subpath`, and calls `discover_workspace` (`src/cpho_cli/core/index/builder.py:170`, `src/cpho_cli/core/index/builder.py:178`).
3. `discover_workspace` recursively collects supported files, skips generated directories, classifies answer-like paths, and creates pairs/unmatched lists (`src/cpho_cli/core/workspace.py:76`).
4. Each paper and answer file is loaded into `DocumentInput` pages (`src/cpho_cli/core/index/builder.py:258`, `src/cpho_cli/core/documents.py:10`).
5. `CachedOCRProvider` wraps `RapidOCRProvider`; OCR extraction uses embedded PDF text when available and image OCR otherwise (`src/cpho_cli/core/index/builder.py:242`, `src/cpho_cli/core/ocr.py:39`).
6. `split_paper` uses image/single-file handling, rules, or LLM fallback depending on document type and diagnostics (`src/cpho_cli/core/index/builder.py:274`, `src/cpho_cli/core/splitting/__init__.py:20`).
7. Fingerprints combine file, OCR, prompt, model, vocabulary, and user-note versions to decide skip, refinement-only, re-tag, or full indexing (`src/cpho_cli/core/index/builder.py:311`, `src/cpho_cli/core/index/builder.py:326`).
8. `refine_tags` maps OCR text to canonical tags and pending candidates; `assign_topic` adds a topic path when topic taxonomy is available (`src/cpho_cli/core/index/builder.py:384`, `src/cpho_cli/core/index/builder.py:402`).
9. The builder creates `IndexEntry` objects with relative workspace paths and writes `.cpho/index.jsonl` atomically through `write_index` (`src/cpho_cli/core/index/builder.py:419`, `src/cpho_cli/core/index/builder.py:467`, `src/cpho_cli/core/index/storage.py:13`).

### Solve Skill Path

1. User invokes `cpho solve` or `/solve`; CLI calls `solve_problem` (`src/cpho_cli/cli/app.py:72`) and REPL calls it after resolving an indexed problem (`src/cpho_cli/cli/repl/commands/builtin_skills.py:70`).
2. `solve_problem` validates problem/answer file existence and loads both documents (`src/cpho_cli/core/solve.py:79`, `src/cpho_cli/core/solve.py:90`).
3. OCR runs over problem and answer documents, producing warnings for low-confidence blocks (`src/cpho_cli/core/solve.py:92`, `src/cpho_cli/core/solve.py:95`).
4. Config resolution creates an LLM provider and model params for the `solve` skill (`src/cpho_cli/core/solve.py:88`, `src/cpho_cli/core/solve.py:101`, `src/cpho_cli/core/solve.py:107`).
5. `load_skill` loads `src/cpho_cli/builtin_skills/solve/`, and `SkillRuntime` executes steps with Python-tool and LLM handlers (`src/cpho_cli/core/solve.py:108`, `src/cpho_cli/core/solve.py:115`, `src/cpho_cli/core/runtime.py:78`).
6. A validated `SolveReport` is written as JSON and Markdown in the output directory (`src/cpho_cli/core/solve.py:132`, `src/cpho_cli/core/solve.py:29`).
7. Optional discrepancy confirmation persists accepted user tags into `.cpho/index.jsonl` through `add_problem_tags` (`src/cpho_cli/cli/app.py:90`, `src/cpho_cli/core/index/api.py:146`).

### REPL Session Path

1. `cpho repl` imports and runs `run_repl` (`src/cpho_cli/cli/app.py:655`, `src/cpho_cli/cli/app.py:670`).
2. `ReplApp` loads config, installs command modules, creates a prompt session, and initializes `SessionState` with workspace and index metadata (`src/cpho_cli/cli/repl/app.py:61`, `src/cpho_cli/cli/repl/app.py:66`, `src/cpho_cli/cli/repl/app.py:74`).
3. User input is parsed with `shlex`, dispatched through the command registry, and errors are logged to `~/.cache/cpho/repl.log` (`src/cpho_cli/cli/repl/app.py:85`, `src/cpho_cli/cli/repl/app.py:97`, `src/cpho_cli/cli/repl/app.py:101`).
4. On exit, `write_session` persists workspace/search/output preferences to XDG config (`src/cpho_cli/cli/repl/app.py:116`, `src/cpho_cli/cli/repl/persistence.py:46`).

### Explain/Probe Path

1. `/explain` resolves an indexed problem and creates provider/model params with `provider_and_params` (`src/cpho_cli/cli/repl/commands/builtin_skills.py:118`, `src/cpho_cli/cli/repl/adapters/skill_command.py:26`).
2. `run_explain` resolves related knowledge, runs selected panels concurrently, extracts candidate tags, and writes Markdown (`src/cpho_cli/core/explain.py:29`, `src/cpho_cli/core/explain.py:46`, `src/cpho_cli/core/explain.py:61`, `src/cpho_cli/core/explain.py:72`).
3. `/probe` resolves the same problem context and calls `run_probe`, which loops over LLM-generated questions and user answers until exit/max rounds (`src/cpho_cli/cli/repl/commands/builtin_skills.py:167`, `src/cpho_cli/core/probe.py:25`, `src/cpho_cli/core/probe.py:48`).

### Compose Path

1. User creates or loads a composition YAML through `cpho compose new/build/auto` or `/compose` (`src/cpho_cli/cli/app.py:583`, `src/cpho_cli/cli/app.py:596`, `src/cpho_cli/cli/app.py:621`).
2. `resolve_composition_slots` uses explicit problem IDs or index search candidates while preventing duplicate problem selection (`src/cpho_cli/core/composition.py:63`, `src/cpho_cli/core/composition.py:81`, `src/cpho_cli/core/composition.py:98`).
3. `assemble_composition_pdfs` copies selected page ranges into separate problem and answer PDFs under `.cpho/exports/compose/` or a workspace-contained output directory (`src/cpho_cli/core/compose_pdf.py:19`, `src/cpho_cli/core/compose_pdf.py:26`, `src/cpho_cli/core/compose_pdf.py:77`).

**State Management:**
- Workspace index state lives in `.cpho/index.jsonl`; all index storage should go through `src/cpho_cli/core/index/storage.py`.
- Workspace taxonomies and vocabularies are layered from package builtins plus `.cpho/vocabulary/` and `.cpho/topics/`.
- REPL state lives in `SessionState` during runtime and is persisted through `src/cpho_cli/cli/repl/persistence.py`.
- Global process state is limited to `_CAPABILITY_CACHE` in `src/cpho_cli/core/llm.py`; treat it as an in-memory provider/model metadata cache.

## Key Abstractions

**Strict Pydantic Models:**
- Purpose: Enforce stable data contracts across CLI, core services, storage, and LLM JSON output.
- Examples: `src/cpho_cli/models/config.py`, `src/cpho_cli/models/index.py`, `src/cpho_cli/models/documents.py`, `src/cpho_cli/models/skills.py`, `src/cpho_cli/models/runtime.py`.
- Pattern: Use `StrictModel` or Pydantic `BaseModel` with validators for persisted or cross-layer payloads.

**Workspace Discovery Result:**
- Purpose: Convert arbitrary local folder trees into problem/answer pairs that the index builder can process.
- Examples: `src/cpho_cli/core/workspace.py`, `src/cpho_cli/models/documents.py`.
- Pattern: Supported extensions, answer/problem filename markers, ignored generated dirs, page counting through PyMuPDF.

**IndexEntry:**
- Purpose: Persist searchable problem metadata, source paths, page ranges, tags, topic, fingerprints, user tags, and OCR metadata.
- Examples: `src/cpho_cli/models/index.py`, `src/cpho_cli/core/index/storage.py`, `src/cpho_cli/core/index/api.py`.
- Pattern: JSONL line-per-entry storage with atomic temp-file replacement.

**SkillSpec and SkillRuntime:**
- Purpose: Model built-in skills as DAGs with declarative steps, inputs, outputs, prompts, and handlers.
- Examples: `src/cpho_cli/models/skills.py`, `src/cpho_cli/core/runtime.py`, `src/cpho_cli/builtin_skills/solve/skill.yml`.
- Pattern: Topological execution, blackboard state, strict output-key validation, optional checkpoint/trace files.

**LLMProvider:**
- Purpose: Abstract OpenAI-compatible complete/stream APIs and model capability detection.
- Examples: `src/cpho_cli/core/llm.py`, `src/cpho_cli/core/config.py`, `src/cpho_cli/core/skill_handlers.py`.
- Pattern: Protocol plus provider registry; add provider kinds by extending `_PROVIDER_REGISTRY` and config support.

**OCRProvider:**
- Purpose: Allow OCR substitution in tests and future providers without changing index/solve flows.
- Examples: `src/cpho_cli/core/ocr.py`, `src/cpho_cli/core/index/builder.py`, `src/cpho_cli/core/solve.py`.
- Pattern: Protocol with `extract(DocumentInput) -> OCRResult`.

**Boundary Checks:**
- Purpose: Keep generated composition output and file access inside the selected workspace.
- Examples: `src/cpho_cli/core/boundary.py`, `src/cpho_cli/cli/app.py`, `src/cpho_cli/cli/repl/commands/workspace.py`.
- Pattern: Resolve paths and require `relative_to(workspace)`.

## Entry Points

**Console Script:**
- Location: `pyproject.toml`
- Triggers: `cpho` installed by package metadata.
- Responsibilities: Maps the command to `cpho_cli.cli.app:app`.

**Typer App:**
- Location: `src/cpho_cli/cli/app.py`
- Triggers: `cpho solve`, `cpho index`, `cpho topic`, `cpho compose`, `cpho knowledge`, `cpho repl`.
- Responsibilities: Parse arguments, print CLI output, translate core exceptions into Typer errors, invoke core services.

**REPL App:**
- Location: `src/cpho_cli/cli/repl/app.py`
- Triggers: `cpho repl`.
- Responsibilities: Manage prompt_toolkit loop, load session/config/index metadata, dispatch slash commands, persist session on exit.

**REPL Command Registry:**
- Location: `src/cpho_cli/cli/repl/commands/__init__.py`
- Triggers: `ReplApp.__init__`.
- Responsibilities: Install `/search`, `/show`, `/workspace`, `/index`, `/solve`, `/explain`, `/probe`, `/compose`, `/related`, `/model`, `/skill`, and help/config commands from command modules.

**Builtin Skill Folders:**
- Location: `src/cpho_cli/builtin_skills/solve/`, `src/cpho_cli/builtin_skills/explain/`, `src/cpho_cli/builtin_skills/probe/`
- Triggers: `load_skill` or direct prompt rendering from core services.
- Responsibilities: Store skill documentation, `skill.yml`, and prompt templates as package data.

## Architectural Constraints

- **Threading:** The Typer CLI is synchronous; REPL command handlers are async and call synchronous core functions where needed. `run_explain` uses `asyncio.gather` to run selected panels concurrently, but provider streaming itself is synchronous inside each panel.
- **Global state:** `_CAPABILITY_CACHE` in `src/cpho_cli/core/llm.py` caches provider/model capability metadata. REPL command registry `registry` in `src/cpho_cli/cli/repl/commands/__init__.py` is module-level but copied per `ReplApp`.
- **Circular imports:** `src/cpho_cli/core/index/__init__.py` exposes a broad re-export surface and imports submodules after declaring exceptions. Prefer importing concrete submodules inside core code when adding new internals, and use `cpho_cli.core.index` only for public API surfaces.
- **Secrets:** `config.local.yml`, `config.local.yaml`, `.env`, `*.local.yml`, and `*.local.yaml` are ignored by `.gitignore`; never read, quote, or persist secret values. Pass secret values only into provider construction and `SkillRuntime(secrets=[...])` redaction.
- **Workspace boundary:** User-chosen output paths must remain under the active workspace. Use `ensure_in_workspace` for composition and any future file-writing features.
- **Real workspace shape:** `/Users/ericzhang/Desktop/物理竞赛资料` contains year/provider/topic nested folders, Chinese filenames, PDFs, images, and existing `.cpho/` state. Discovery logic must preserve Unicode paths, nested traversal, answer markers like `答案`/`解析`, and ignored generated dirs.

## Anti-Patterns

### Fat CLI Logic

**What happens:** Implementing business behavior directly in `src/cpho_cli/cli/app.py` or `src/cpho_cli/cli/repl/commands/*.py`.
**Why it's wrong:** The same use case usually exists in both Typer and REPL flows; duplicating core behavior creates drift and makes tests target UI adapters instead of reusable services.
**Do this instead:** Put behavior in `src/cpho_cli/core/` and call it from CLI/REPL modules, following `build_index` in `src/cpho_cli/core/index/builder.py` and `solve_problem` in `src/cpho_cli/core/solve.py`.

### Raw Dict Storage For Domain Objects

**What happens:** Passing unvalidated dictionaries between index, skill, or knowledge code.
**Why it's wrong:** Core flows depend on stable JSON/YAML contracts, and persisted files are later reloaded into Pydantic models.
**Do this instead:** Define or reuse Pydantic models in `src/cpho_cli/models/`, then validate at module boundaries, following `IndexEntry` in `src/cpho_cli/models/index.py` and `SkillSpec` in `src/cpho_cli/models/skills.py`.

### Path Writes Without Boundary Checks

**What happens:** Writing output to a user-provided path without resolving it under the active workspace.
**Why it's wrong:** The app operates on local physics-workspace folders and must not accidentally write outside the workspace when users pass absolute paths.
**Do this instead:** Use `ensure_in_workspace` from `src/cpho_cli/core/boundary.py`, following `_compose_output_dir` in `src/cpho_cli/cli/app.py` and `_insert_entry_pages` in `src/cpho_cli/core/compose_pdf.py`.

### Reading Secret Configs For Documentation Or Diagnostics

**What happens:** Inspecting `config.local.yml`, `.env`, or other ignored local config content to infer provider details.
**Why it's wrong:** These files can contain API keys and should never be copied into committed docs or logs.
**Do this instead:** Document supported config key names from `src/cpho_cli/models/config.py` and `src/cpho_cli/core/config.py`; note only the existence of local config files.

## Error Handling

**Strategy:** Core modules raise typed `RuntimeError`/`ValueError` subclasses for domain failures; CLI and REPL adapters catch them and render user-facing messages.

**Patterns:**
- Convert core config/index/solve errors into `typer.BadParameter` in `src/cpho_cli/cli/app.py`.
- REPL dispatch catches handler exceptions, writes stack traces to `~/.cache/cpho/repl.log`, and prints concise errors in `src/cpho_cli/cli/repl/app.py`.
- LLM calls wrap HTTP/provider failures in `LLMProviderError` and redact API keys with `redact_secrets` in `src/cpho_cli/core/llm.py`.
- Skill runtime records failed step traces/checkpoints when paths are configured and redacts configured secrets in `src/cpho_cli/core/runtime.py`.
- Index topic assignment is non-blocking; failures log a warning and continue without `topic_path` in `src/cpho_cli/core/index/builder.py`.

## Cross-Cutting Concerns

**Logging:** REPL errors are logged to `~/.cache/cpho/repl.log` through `src/cpho_cli/cli/repl/app.py`; index/tag/topic modules use Python `logging` for non-blocking warnings.
**Validation:** Pydantic models in `src/cpho_cli/models/` validate persisted schemas; PyYAML inputs are validated after parsing; CLI path and option validation occurs in Typer/argparse adapters.
**Authentication:** LLM provider credentials resolve from explicit provider profile keys or environment variable names through `src/cpho_cli/core/config.py`; do not persist resolved secret values.
**Internationalization:** User-facing CLI/REPL text is largely Chinese, and workspace/file handling must preserve Unicode paths and filenames.
**Generated Artifacts:** Generated workspace artifacts belong under `.cpho/`, `output/`, or XDG paths and are excluded from repository source by `.gitignore`.

---

*Architecture analysis: 2026-05-28*
