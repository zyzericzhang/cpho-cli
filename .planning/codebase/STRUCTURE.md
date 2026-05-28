# Codebase Structure

**Analysis Date:** 2026-05-28

## Directory Layout

```text
cpho-cli/
├── src/cpho_cli/                 # Python package source
│   ├── cli/                      # Typer CLI and prompt_toolkit REPL adapters
│   │   └── repl/                 # REPL app, session, persistence, display, commands
│   ├── core/                     # Application services and integrations
│   │   ├── index/                # Index build/query/storage/tag/topic subsystem
│   │   ├── knowledge/            # Private/community knowledge normalization and lookup
│   │   └── splitting/            # Rule and LLM paper-splitting logic
│   ├── models/                   # Pydantic domain models
│   ├── builtin_skills/           # Packaged skills and prompt templates
│   ├── vocabulary/               # Built-in tag/topic YAML assets
│   └── data/                     # Packaged data such as model catalog fallback
├── tests/                        # Pytest suite and fixtures
│   └── fixtures/                 # Golden workspaces, PDFs, images, JSON fixtures
├── docs/                         # Product, architecture decision, verification, and user docs
│   └── user/                     # Published user-facing docs and error references
├── examples/                     # Sample problem/answer Markdown
├── .planning/                    # GSD project plans, phases, research, and codebase maps
│   └── codebase/                 # Generated codebase mapping documents
├── .github/                      # Issue templates and README demo asset
├── pyproject.toml                # Package metadata, dependencies, tooling config
├── uv.lock                       # uv lockfile
├── README.md                     # Product overview and quick start
├── AGENTS.md                     # Repository agent instructions
├── CLAUDE.md                     # Claude-oriented repository instructions
├── LICENSE                      # MIT license
└── .gitignore                    # Local secrets/cache/output exclusions
```

## Directory Purposes

**`src/cpho_cli/`:**
- Purpose: The installable Python package.
- Contains: CLI adapters, core services, Pydantic models, built-in skill assets, vocabulary assets, and packaged data.
- Key files: `src/cpho_cli/__init__.py`, `src/cpho_cli/cli/app.py`, `src/cpho_cli/core/`, `src/cpho_cli/models/`.

**`src/cpho_cli/cli/`:**
- Purpose: User interface adapters for command-line execution.
- Contains: Typer app root and REPL package.
- Key files: `src/cpho_cli/cli/app.py`, `src/cpho_cli/cli/__init__.py`.

**`src/cpho_cli/cli/repl/`:**
- Purpose: Interactive prompt_toolkit application.
- Contains: `ReplApp`, session state, persistence, display helpers, completers, command registry, command modules, skill command adapters.
- Key files: `src/cpho_cli/cli/repl/app.py`, `src/cpho_cli/cli/repl/session.py`, `src/cpho_cli/cli/repl/persistence.py`, `src/cpho_cli/cli/repl/commands/__init__.py`.

**`src/cpho_cli/cli/repl/commands/`:**
- Purpose: Slash command implementations for REPL workflows.
- Contains: Workspace/index commands, search/show commands, solve/explain/probe commands, compose commands, related-problem commands, model/skill commands, help/debug/settings commands.
- Key files: `src/cpho_cli/cli/repl/commands/workspace.py`, `src/cpho_cli/cli/repl/commands/search.py`, `src/cpho_cli/cli/repl/commands/builtin_skills.py`, `src/cpho_cli/cli/repl/commands/compose.py`.

**`src/cpho_cli/core/`:**
- Purpose: UI-independent application services and provider adapters.
- Contains: Config, LLM, OCR, document loading, workspace discovery, skill runtime, solve/explain/probe workflows, index, knowledge, composition, related search, boundary checks, output helpers.
- Key files: `src/cpho_cli/core/config.py`, `src/cpho_cli/core/llm.py`, `src/cpho_cli/core/runtime.py`, `src/cpho_cli/core/solve.py`, `src/cpho_cli/core/explain.py`, `src/cpho_cli/core/probe.py`.

**`src/cpho_cli/core/index/`:**
- Purpose: Build and query the local problem index.
- Contains: Builder, JSONL storage, public API, hashing/fingerprint logic, OCR cache, tag refinement, topic assignment, vocabulary/topic loaders, notebook user-learning inputs, prompt templates.
- Key files: `src/cpho_cli/core/index/builder.py`, `src/cpho_cli/core/index/storage.py`, `src/cpho_cli/core/index/api.py`, `src/cpho_cli/core/index/tagging.py`, `src/cpho_cli/core/index/topic_assignment.py`, `src/cpho_cli/core/index/vocabulary.py`.

**`src/cpho_cli/core/splitting/`:**
- Purpose: Split multi-problem papers into indexed problem entries.
- Contains: Rule splitter, LLM fallback splitter, prompt templates, package exports.
- Key files: `src/cpho_cli/core/splitting/__init__.py`, `src/cpho_cli/core/splitting/rules.py`, `src/cpho_cli/core/splitting/llm.py`, `src/cpho_cli/core/splitting/prompts/split_paper.md.j2`.

**`src/cpho_cli/core/knowledge/`:**
- Purpose: Normalize, publish, resolve, and load private/community knowledge documents.
- Contains: Knowledge resolver, store/frontmatter loader, normalization flow, prompt templates.
- Key files: `src/cpho_cli/core/knowledge/resolver.py`, `src/cpho_cli/core/knowledge/store.py`, `src/cpho_cli/core/knowledge/normalize.py`, `src/cpho_cli/core/knowledge/prompts/normalize_knowledge.md.j2`.

**`src/cpho_cli/models/`:**
- Purpose: Domain and persistence schemas.
- Contains: Pydantic models for config, documents, OCR, index, topics, LLM messages, skill specs, runtime traces, solve reports, explain outputs, probe transcripts, composition files, knowledge docs, community sync.
- Key files: `src/cpho_cli/models/config.py`, `src/cpho_cli/models/documents.py`, `src/cpho_cli/models/index.py`, `src/cpho_cli/models/skills.py`, `src/cpho_cli/models/runtime.py`.

**`src/cpho_cli/builtin_skills/`:**
- Purpose: Built-in skill package data consumed by core workflows.
- Contains: `solve`, `explain`, and `probe` folders with `SKILL.md`, `skill.yml`, and Jinja prompt templates.
- Key files: `src/cpho_cli/builtin_skills/solve/skill.yml`, `src/cpho_cli/builtin_skills/explain/prompts/approach.md.j2`, `src/cpho_cli/builtin_skills/probe/prompts/next_turn.md.j2`.

**`src/cpho_cli/vocabulary/`:**
- Purpose: Built-in canonical tags and topic taxonomy.
- Contains: Root vocabulary YAML, thematic vocabulary shards, and builtin topic tree.
- Key files: `src/cpho_cli/vocabulary/builtin.yml`, `src/cpho_cli/vocabulary/builtin/05_mechanics_advanced.yml`, `src/cpho_cli/vocabulary/topics/builtin_topics.yml`.

**`src/cpho_cli/data/`:**
- Purpose: Package data that is not code or prompts.
- Contains: Model catalog fallback JSON.
- Key files: `src/cpho_cli/data/model_catalog/openrouter_fallback.json`.

**`tests/`:**
- Purpose: Pytest tests for CLI, REPL, core services, models, docs, and acceptance flows.
- Contains: `test_*.py` modules and fixtures for documents, splitting, index workspaces, and JSON expectations.
- Key files: `tests/test_index_builder.py`, `tests/test_repl_runtime.py`, `tests/test_solve.py`, `tests/test_compose_pdf.py`, `tests/conftest.py`.

**`tests/fixtures/`:**
- Purpose: Reusable test assets.
- Contains: Golden index workspace with paired images, splitting PDFs and expected JSON, sample multi-problem JSON.
- Key files: `tests/fixtures/golden_index_workspace/problem_a.png`, `tests/fixtures/golden_index_workspace/problem_a-answer.png`, `tests/fixtures/splitting/ipho_style_multi_problem.pdf`.

**`docs/`:**
- Purpose: Product docs, decisions, verification records, and research notes.
- Contains: Phase decision docs, verification docs, user docs, error docs, vocabulary notes, REPL/TUI patterns.
- Key files: `docs/product-spec.md`, `docs/architecture-decisions.md`, `docs/user/README.md`, `docs/user/errors/README.md`.

**`.planning/`:**
- Purpose: GSD planning state and generated project intelligence.
- Contains: Milestones, roadmap, phases, research, notes, quick tasks, verification artifacts, and codebase maps.
- Key files: `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/PROJECT.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`.

**`examples/`:**
- Purpose: Small sample inputs for users and tests/docs.
- Contains: Markdown problem and answer examples.
- Key files: `examples/sample-problem.md`, `examples/sample-answer.md`, `examples/README.md`.

**`.github/`:**
- Purpose: Repository metadata for GitHub.
- Contains: Issue templates and README demo SVG.
- Key files: `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/feature_request.md`, `.github/assets/cpho-demo.svg`.

## Key File Locations

**Entry Points:**
- `pyproject.toml`: Defines package metadata, dependencies, tool config, package data, and `cpho = "cpho_cli.cli.app:app"`.
- `src/cpho_cli/cli/app.py`: Main Typer application and subcommand definitions.
- `src/cpho_cli/cli/repl/app.py`: Interactive REPL startup, loop, dispatch, and shutdown persistence.
- `src/cpho_cli/cli/repl/commands/__init__.py`: REPL command registry and installer.

**Configuration:**
- `pyproject.toml`: Project dependencies, pytest, mypy, ruff, package data.
- `AGENTS.md`: Repository coding and real-workspace-reference instructions.
- `.gitignore`: Excludes `.env`, local configs, `.cpho/`, outputs, traces, caches, `.venv/`, and `.claude/`.
- `config.local.yml`: Local config file present in working tree and ignored by `.gitignore`; do not read or commit contents.
- `src/cpho_cli/core/config.py`: Runtime config loading and provider/model resolution.
- `src/cpho_cli/models/config.py`: Config schemas and supported key names.

**Core Logic:**
- `src/cpho_cli/core/workspace.py`: Workspace discovery and problem/answer pairing.
- `src/cpho_cli/core/documents.py`: PDF/image loading.
- `src/cpho_cli/core/ocr.py`: OCR protocol and RapidOCR adapter.
- `src/cpho_cli/core/index/builder.py`: End-to-end index build orchestrator.
- `src/cpho_cli/core/index/storage.py`: Atomic JSONL index persistence.
- `src/cpho_cli/core/index/api.py`: Query/mutation API over the index.
- `src/cpho_cli/core/runtime.py`: Skill DAG runtime.
- `src/cpho_cli/core/skills.py`: Skill folder loader.
- `src/cpho_cli/core/skill_handlers.py`: LLM/Python step handlers.
- `src/cpho_cli/core/solve.py`: Solve skill orchestration.
- `src/cpho_cli/core/explain.py`: Explain panel orchestration.
- `src/cpho_cli/core/probe.py`: Probe loop orchestration.
- `src/cpho_cli/core/composition.py`: Composition YAML resolution.
- `src/cpho_cli/core/compose_pdf.py`: PDF assembly.
- `src/cpho_cli/core/knowledge/`: Knowledge file workflows.

**Models:**
- `src/cpho_cli/models/documents.py`: Document, paper, splitting, and workspace discovery models.
- `src/cpho_cli/models/index.py`: Tag, vocabulary, fingerprint, index entry, and stats models.
- `src/cpho_cli/models/skills.py`: Skill pipeline and DAG descriptions.
- `src/cpho_cli/models/runtime.py`: Trace, checkpoint, resume, and result models.
- `src/cpho_cli/models/llm.py`: LLM response/message/capability models.
- `src/cpho_cli/models/composition.py`: Composition file and slot models.

**Assets:**
- `src/cpho_cli/builtin_skills/solve/`: Solve skill docs, spec, and prompts.
- `src/cpho_cli/builtin_skills/explain/`: Explain skill docs, spec, and prompts.
- `src/cpho_cli/builtin_skills/probe/`: Probe skill docs, spec, and prompts.
- `src/cpho_cli/vocabulary/builtin.yml`: Root built-in tag vocabulary.
- `src/cpho_cli/vocabulary/builtin/*.yml`: Thematic built-in vocabulary shards.
- `src/cpho_cli/vocabulary/topics/builtin_topics.yml`: Built-in topic taxonomy.
- `src/cpho_cli/data/model_catalog/openrouter_fallback.json`: Packaged fallback model catalog.

**Testing:**
- `tests/test_cli.py`: CLI command surface tests.
- `tests/test_repl_runtime.py`: REPL app/runtime tests.
- `tests/test_index_builder.py`: Index builder flow tests.
- `tests/test_splitting_*.py`: Rule/LLM/integration/golden splitting tests.
- `tests/test_knowledge*.py`: Knowledge workflow tests.
- `tests/test_compose*.py`: Composition and PDF assembly tests.
- `tests/fixtures/golden_index_workspace/`: Image-based golden workspace.
- `tests/fixtures/splitting/`: PDF splitting fixtures.

## Naming Conventions

**Files:**
- Python modules use lowercase snake_case: `src/cpho_cli/core/model_catalog.py`, `src/cpho_cli/core/skill_outputs.py`.
- Test modules use `test_<area>.py`: `tests/test_index_builder.py`, `tests/test_repl_workspace_commands.py`.
- REPL command modules use command-area names: `src/cpho_cli/cli/repl/commands/workspace.py`, `src/cpho_cli/cli/repl/commands/model_panel.py`.
- Built-in skill folders use skill names: `src/cpho_cli/builtin_skills/solve/`, `src/cpho_cli/builtin_skills/explain/`.
- Prompt templates use descriptive `.md.j2` names: `src/cpho_cli/core/index/prompts/topic_assignment.md.j2`, `src/cpho_cli/builtin_skills/solve/prompts/final_report.md.j2`.
- YAML package data uses domain names: `src/cpho_cli/vocabulary/builtin.yml`, `src/cpho_cli/vocabulary/topics/builtin_topics.yml`.

**Directories:**
- Source code is under `src/cpho_cli/` using a `src/` package layout.
- Core subpackages group domains: `src/cpho_cli/core/index/`, `src/cpho_cli/core/knowledge/`, `src/cpho_cli/core/splitting/`.
- REPL subpackages separate adapters from command modules: `src/cpho_cli/cli/repl/adapters/`, `src/cpho_cli/cli/repl/commands/`.
- Package data lives next to the package under `src/cpho_cli/builtin_skills/`, `src/cpho_cli/vocabulary/`, and `src/cpho_cli/data/`.
- Test fixtures live under `tests/fixtures/<fixture-area>/`.

## Where to Add New Code

**New CLI Subcommand:**
- Primary code: `src/cpho_cli/cli/app.py` for Typer wiring only.
- Core behavior: Add or extend a module under `src/cpho_cli/core/`.
- Models: Add schemas under `src/cpho_cli/models/` when data crosses module or persistence boundaries.
- Tests: Add command tests under `tests/test_cli.py` or a focused `tests/test_<feature>_cli.py`.

**New REPL Command:**
- Implementation: Add a module or extend an existing module under `src/cpho_cli/cli/repl/commands/`.
- Registration: Register the command in that module's `register(registry)` function and install the module from `src/cpho_cli/cli/repl/commands/__init__.py`.
- Shared helpers: Put cross-command adaptation helpers in `src/cpho_cli/cli/repl/adapters/`.
- Tests: Add focused tests under `tests/test_repl_<feature>_commands.py`.

**New Core Feature:**
- Primary code: `src/cpho_cli/core/<feature>.py` for a narrow service, or `src/cpho_cli/core/<feature>/` for a multi-file subsystem.
- Models: `src/cpho_cli/models/<feature>.py`.
- CLI/REPL adapters: `src/cpho_cli/cli/app.py` and/or `src/cpho_cli/cli/repl/commands/<feature>.py`.
- Tests: `tests/test_<feature>.py`, with fixtures under `tests/fixtures/<feature>/` when file assets are needed.

**New Index Behavior:**
- Implementation: Use `src/cpho_cli/core/index/`.
- Builder orchestration: `src/cpho_cli/core/index/builder.py`.
- Query/mutation surface: `src/cpho_cli/core/index/api.py`.
- Persistence changes: `src/cpho_cli/core/index/storage.py` and `src/cpho_cli/models/index.py`.
- Prompt changes: `src/cpho_cli/core/index/prompts/`.
- Tests: `tests/test_index_<feature>.py`.

**New Skill:**
- Skill assets: Add `src/cpho_cli/builtin_skills/<skill>/SKILL.md`, `src/cpho_cli/builtin_skills/<skill>/skill.yml`, and prompt templates under `src/cpho_cli/builtin_skills/<skill>/prompts/`.
- Loader/runtime reuse: Use `src/cpho_cli/core/skills.py`, `src/cpho_cli/core/runtime.py`, and `src/cpho_cli/core/skill_handlers.py`.
- Workflow wrapper: Add `src/cpho_cli/core/<skill>.py` if the skill has a public use case.
- Package data: Ensure `pyproject.toml` includes the new package data pattern if the existing glob is insufficient.
- Tests: Add `tests/test_<skill>.py` and fixture prompts/files as needed.

**New Vocabulary Or Topic Data:**
- Built-in vocabulary: Add or update YAML in `src/cpho_cli/vocabulary/builtin/` or `src/cpho_cli/vocabulary/builtin.yml`.
- Built-in topics: Update `src/cpho_cli/vocabulary/topics/builtin_topics.yml`.
- Loader behavior: Use `src/cpho_cli/core/index/vocabulary.py` and `src/cpho_cli/core/index/topic_vocabulary.py`.
- Tests: Add or update `tests/test_index_vocabulary.py`, `tests/test_topic_vocabulary.py`, and integration tests when index output changes.

**New Workspace File Output:**
- Output code: Put writer logic in `src/cpho_cli/core/`.
- Boundary checks: Use `src/cpho_cli/core/boundary.py` for user-provided paths.
- Default generated paths: Prefer workspace `.cpho/<feature>/`, `.cpho/exports/<feature>/`, or `output/` depending on whether the artifact is workspace state or user-visible output.
- Tests: Include workspace-boundary tests under `tests/test_boundary.py` or a feature-specific test file.

**Utilities:**
- Shared file/output helpers: `src/cpho_cli/core/skill_outputs.py`.
- JSON parsing helpers: `src/cpho_cli/core/json_utils.py`.
- Provider/config helpers: `src/cpho_cli/core/config.py`, `src/cpho_cli/core/llm.py`.
- Keep one-off helpers private in the feature module until reused by another module.

## Special Directories

**`src/cpho_cli/builtin_skills/`:**
- Purpose: Packaged prompt/skill assets.
- Generated: No.
- Committed: Yes.

**`src/cpho_cli/vocabulary/`:**
- Purpose: Packaged tag/topic taxonomy data.
- Generated: No.
- Committed: Yes.

**`src/cpho_cli.egg-info/`:**
- Purpose: Local package metadata from editable/build operations.
- Generated: Yes.
- Committed: No.

**`.planning/`:**
- Purpose: GSD project planning and generated codebase intelligence.
- Generated: Mixed; many files are workflow-generated project artifacts.
- Committed: Project-dependent, but codebase map documents are intended to be written here.

**`.venv/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `__pycache__/`:**
- Purpose: Local environment and tool caches.
- Generated: Yes.
- Committed: No.

**`eval-output/`:**
- Purpose: Local evaluation report output.
- Generated: Yes.
- Committed: No.

**`output/`:**
- Purpose: Default solve/report output directory when running CLI workflows.
- Generated: Yes.
- Committed: No.

**Workspace `.cpho/`:**
- Purpose: User workspace state, including index JSONL, OCR/cache data, vocabulary/topic overlays, compositions, exports, knowledge drafts, and community KB config.
- Generated: Mixed user-managed and app-generated.
- Committed: No for real user workspaces.

**`/Users/ericzhang/Desktop/物理竞赛资料`:**
- Purpose: Real physics competition coach workspace used to validate architecture assumptions.
- Generated: No; user-owned source data plus app-generated `.cpho/` state.
- Committed: No.
- Architecture relevance: Contains nested year/provider/topic directories, Unicode names, PDFs, images, answer files, and existing `.cpho/`; discovery and file-output code should be tested against this shape when designing workspace features.

---

*Structure analysis: 2026-05-28*
