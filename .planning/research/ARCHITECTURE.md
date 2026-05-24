# Architecture Patterns

**Domain:** Physics Olympiad AI Analysis CLI Tool
**Researched:** 2026-05-20

## Recommended Architecture

### High-Level Structure

```
cpho/
├── core/                          # Pure library — zero I/O, zero framework dependencies
│   ├── models/                    # Domain entities: Problem, TagSet, PipelineStep, SkillDef
│   ├── indexing/                  # Tag schema, index writer/reader, query engine
│   ├── pipeline/                  # DAG engine, context injector, blackboard
│   ├── skills/                    # Skill discovery interface, loader, validator
│   ├── llm/                       # LLM gateway interface (abstract)
│   ├── ocr/                       # OCR interface (abstract)
│   └── output/                    # PDF stitching logic, report generation
│
├── cli/                           # Thin shell — Typer commands, output formatting
│   ├── commands/                  # solve, batch, index, skill, repl
│   ├── formatters/                # Terminal output (Rich), JSON output, Markdown
│   └── repl/                      # REPL session management
│
├── adapters/                      # Concrete implementations of core interfaces
│   ├── openrouter_client.py       # LLM Gateway: OpenRouter API
│   ├── ocr_tesseract.py           # OCR: Tesseract wrapper
│   ├── ocr_rapid.py               # OCR: RapidOCR (Chinese+formula optimized)
│   └── file_index.py              # Index: JSONL-backed tag index
│
└── skills_builtin/                # Shipped skill definitions (YAML + prompt files)
    ├── question_mode/
    ├── step_by_step/
    ├── comparative/
    └── exam_compose/
```

**Dependency rule:** `core/` never imports from `cli/` or `adapters/`. `cli/` imports from `core/` and `adapters/`. `adapters/` implements interfaces defined in `core/`.

### Why This Structure

The core-shell separation (aka "Functional Core / Imperative Shell") is the dominant pattern in Python CLI tools as of 2025. Projects like `gpt-engineer`, `profile_engine`, and `renku-python` all converged on this pattern independently. The key property: every function in `core/` is a pure transformation that can be tested without mocking any I/O. The `cli/` layer contains no business logic — it only parses arguments, calls core functions, and formats output.

This is not over-engineering for a CLI tool. The project spec explicitly calls for future online platform integration. If core and CLI are coupled, the web port requires a rewrite. With this separation, the web layer becomes just another shell around the same core.

---

## Component Boundaries

### 1. CLI Layer (`cli/`)

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| `commands/solve.py` | Parse `solve` args, orchestrate single-problem pipeline | WorkspaceManager, PipelineEngine, OutputFormatter |
| `commands/batch.py` | Parse `batch` args, fan-out multiple solves | solve command (reused), ProgressDisplay |
| `commands/index.py` | Parse `index` args, build/query tag index | IndexWriter, IndexReader |
| `commands/skill.py` | Parse `skill` args, install/create/list skills | SkillLoader, SkillCreator |
| `commands/repl.py` | Interactive REPL with session state | PipelineEngine, SessionState |
| `formatters/terminal.py` | Rich-formatted console output | (reads core model objects) |
| `formatters/json_out.py` | JSON/JSONL file output | (reads core model objects) |
| `formatters/markdown.py` | Markdown report output | (reads core model objects) |
| `repl/session.py` | REPL state, history, context persistence | commands/repl.py, PipelineEngine |

**Technology:** `Typer` (modern, type-hinted, built on Click) for command definitions. `Rich` for terminal formatting. `prompt_toolkit` for REPL input handling.

**Rationale:** Typer is the 2025 standard for new Python CLIs — it leverages type hints for argument validation and generates `--help` automatically. Rich provides tables, panels, Markdown rendering, and progress bars without the user installing anything beyond `pip`. prompt_toolkit handles the REPL interaction loop (history, completion, multi-line input).

### 2. Pipeline Engine (`core/pipeline/`)

The most architecturally significant component. This is where the DAG-based step execution lives.

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| `dag.py` | DAG definition (nodes, edges), topological sort, parallel scheduling | Blackboard, ContextInjector |
| `step.py` | Single step execution: render prompt, call LLM, parse output, store in blackboard | LLMGateway, ContextInjector, Blackboard |
| `blackboard.py` | Mutable shared state across steps (key-value store with typed access) | PipelineEngine (all steps read/write) |
| `context_injector.py` | Jinja2 template rendering for prompt context injection | PipelineStep (renders its prompt template) |

**DAG Execution Model:**

The pipeline engine uses dependency-driven scheduling, not explicit graph wiring. Each step declares `depends_on: [step_ids]`. The engine performs topological sort and executes steps as soon as all dependencies are satisfied. Independent steps run in parallel via `concurrent.futures.ThreadPoolExecutor` (sufficient since LLM calls are I/O-bound, not CPU-bound).

```
Step A ──┐
          ├──→ Step C ──→ Step D
Step B ──┘

Execution: A and B start in parallel → C starts when both complete → D starts when C completes
```

**Why DAG not autonomous agent:** The project spec explicitly rejects autonomous ReAct-style agents because they skip intermediate derivation steps in long physics problems. The DAG model enforces deterministic step execution — the pipeline author (skill creator) defines the exact sequence, and the engine guarantees every step runs. Quality trumps flexibility here.

**Why not LangGraph/Griptape:** These frameworks carry significant dependency weight and abstraction overhead. The pipeline DAG for this project is straightforward — topological sort + parallel execution + template rendering with context injection. Approximately 300-400 lines of core code. Bringing in a 100K+ line framework for this scope is premature. The project can adopt DSPy later for prompt optimization (the library integrates at a module level, not framework level), but the execution engine should remain minimal and transparent.

### 3. Skill System (`core/skills/`)

Three-tier architecture as specified in project requirements. The skill system interfaces with the pipeline engine by producing `PipelineDefinition` objects (list of steps with dependencies).

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| `interface.py` | Abstract Skill base class / Protocol — what every skill must provide | (defines contract) |
| `discovery.py` | Find installed skills via Python entry points + filesystem scanning | SkillLoader |
| `loader.py` | Load and validate skill from directory (YAML spec + prompt files + optional Python) | SkillValidator |
| `validator.py` | Validate skill structure, required fields, prompt template syntax | (reads skill directory) |
| `creator.py` | Generate skill skeleton from natural language description via LLM | LLMGateway |
| `registry.py` | In-memory registry of loaded skills (name → SkillDefinition) | CLI commands, PipelineEngine |

**Three Tiers (implemented via polymorphism):**

```
Tier 1 (Pure Prompt):  Skill directory contains only prompt.md files.
                       Loader wraps them in a default sequential pipeline.
                       User edits markdown — no code touched.

Tier 2 (YAML Declarative): Skill directory contains skill.yaml with step
                           definitions, dependencies, and prompt file references.
                           Loader parses YAML into PipelineDefinition.
                           User edits YAML — no Python required.

Tier 3 (Python Script): Skill directory contains skill.py with a class
                        implementing the Skill Protocol.
                        Full control: custom DAG construction, pre/post-processing.
                        User writes Python.
```

**Skill Discovery Pattern:**

Discovery uses a two-tier strategy, inspired by the pluggy/pytest model:

1. **Installed plugins (entry points):** Skills distributed as pip packages register under the `cpho.skills` entry point group in `pyproject.toml`. Discovered via `importlib.metadata.entry_points()`.

2. **Local skills (filesystem):** Skills in `~/.cpho/skills/` or `./cpho-skills/` (project-local) are discovered by scanning directories for `skill.yaml` or `skill.py`.

This supports both third-party skill distribution (pip install cpho-skill-thermodynamics) and quick prototyping (drop a YAML file in a directory).

**Skill Creator Flow:**

```
User: cpho skill create "analyze rotational dynamics problems, check conservation laws"
  → SkillCreator sends description to LLM (with structured output schema)
  → LLM returns: skill name, step definitions, dependency graph, prompt templates
  → Creator writes skill.yaml + prompt/ directory to ~/.cpho/skills/<name>/
  → User can edit generated files before use
```

### 4. Indexing Layer (`core/indexing/`)

Tag-based indexing is the retrieval backbone. Problems are pre-analyzed once, and all subsequent queries operate on the index, not raw files.

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| `schema.py` | TagSet model (physical models, insights, difficulties, math techniques) | All index components |
| `writer.py` | Scan papers, split into problems (Phase 02.1), call LLM for tag generation, write JSONL index | LLMGateway, WorkspaceManager |
| `reader.py` | Query index by tag combinations, return matching problem references | (reads JSONL file) |
| `query.py` | Tag query parser (AND/OR/NOT operations on tag fields) | IndexReader |

**Index Format (JSONL — one JSON object per problem entry, split from exam papers):**

```jsonl
{"problem_id": "abc123:1", "paper_path": "papers/2024-mechanics.pdf", "problem_page_range": [2, 3], "problem_number": 1, "tags": {"physics_model": ["rigid_body", "angular_momentum"], "heuristic": ["conservation_law_selection", "reference_frame_choice"], "math_technique": ["vector_cross_product", "differential_equation"]}, "answer_paper_path": "answers/2024-mechanics-ans.pdf", "answer_page_range": [1, 2], "indexed_at": "2026-05-20T10:30:00Z"}
```

**Why JSONL not SQLite:** The project constraints say no database. JSONL is append-only, grep-friendly, version-controllable, and trivially mergeable. For the expected scale (hundreds to low thousands of problems), JSONL scanning with in-memory filtering is fast enough (sub-10ms for 1000 records). If the problem set grows to 10K+, a SQLite FTS layer can be added behind the same `IndexReader` interface without changing any consumer code.

**Pre-Compute Pattern:** The index is the canonical example of the pre-compute pattern. Tag generation is expensive (LLM call per problem). By computing tags once and storing them, every subsequent query (comparative analysis, exam composition, tag-based retrieval) is a fast local read with no LLM cost.

### 5. LLM Gateway (`core/llm/` + `adapters/openrouter_client.py`)

Abstract interface in core, concrete OpenRouter implementation in adapters.

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| `gateway.py` (core) | Abstract interface: `complete(prompt, schema) -> StructuredOutput` | (defines contract) |
| `openrouter_client.py` (adapters) | OpenRouter API calls, structured output, retry logic | OpenRouter API |

**Structured Output Strategy (3-layer defense):**

1. **Schema injection via `extra_body`:** OpenRouter's LiteLLM wrapper strips `response_format` from some models. The workaround is passing `json_schema` via `extra_body`, which OpenRouter forwards to the underlying provider. This is the canonical approach as of 2025.

2. **Response Healing:** OpenRouter's free Response Healing plugin auto-fixes JSON syntax errors (trailing commas, unescaped chars, missing brackets). Enabled by default in API calls. Reduces parse failures by 80-99% depending on model.

3. **Provider routing:** Requests include `provider: {require_parameters: true}` to ensure OpenRouter only routes to providers that support structured output. Prevents silent fallback to `json_object` mode or plain text.

4. **Retry with degradation:** If structured output fails after 2 retries, fall back to free-text + regex extraction with a warning. Never silently return partial results.

### 6. Workspace Manager (`core/workspace/`)

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| `discovery.py` | Scan paper folder, identify PDF/image files, associate answer files at paper level | (filesystem via adapter interface) |
| `paper.py` | PaperFile model: file path, paper kind, total pages + answer pairing | Phase 02.1 splitter, PipelineEngine |
| `problem.py` | ProblemEntry model: problem_id, paper_path, page_range, text (split from paper) | IndexWriter, PipelineEngine |
| `file_io.py` (adapters) | File system operations (abstracted for testability) | WorkspaceManager |

**Paper-Answer Association:** The workspace manager uses naming heuristics to match exam papers with answer files at the paper level (e.g., `模拟试卷七.pdf` pairs with `模拟试卷七解析.pdf`). After Phase 02.1 splitting, individual ProblemEntries from the question paper are paired with corresponding ProblemEntries from the answer paper by problem number.

### 7. OCR Adapter (`core/ocr/` interface + adapter implementations)

Abstract interface only in v1. The OCR strategy is not yet decided (research question #2 remains open). The architecture isolates this behind an interface so the implementation can change without affecting any other component.

```python
class OcrBackend(Protocol):
    def extract_text(self, file_path: Path, pages: list[int] | None = None) -> str: ...
    def supports_latex(self) -> bool: ...
    def supports_chinese(self) -> bool: ...
```

### 8. Output Pipeline (`core/output/`)

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| `pdf_stitch.py` | Extract pages from source PDFs, concatenate into output PDF | (file system, PyPDF2/pikepdf) |
| `report.py` | Generate structured Markdown report from pipeline results | (reads Blackboard output) |
| `json_writer.py` | Write pipeline results as JSON/JSONL | (reads Blackboard output) |

**PDF Output Strategy:** As decided in project spec — no LaTeX rendering. Output PDFs are assembled by extracting relevant pages from source PDFs and stitching them together. For "exam compose" skill: problem pages extracted from individual problem PDFs, concatenated into a single problem-set PDF. Same for answer pages.

---

## Data Flow

### Primary Flow: `cpho solve problem.pdf`

> **Note:** This flow represents pre-Phase-02.1 design. In the current codebase, exam papers are split into ProblemEntries during `cpho index`. `cpho solve` currently works on individual PDF files; Phase 3 will upgrade solve to consume ProblemEntry from the index.

```
User invokes: cpho solve "2024-mechanics-q3.pdf" --skill step-by-step

  1. CLI (commands/solve.py)
     └─ Parses args, resolves paths

  2. WorkspaceManager
     └─ Discovers problem file + answer file
     └─ Returns Problem object

  3. OCR Adapter (if PDF/image)
     └─ Extracts text content
     └─ Caches result in Problem.text

  4. IndexWriter (incremental)
     └─ Checks if problem already indexed
     └─ If not: calls LLM for tag generation
     └─ Appends tag record to index.jsonl

  5. SkillLoader
     └─ Loads "step-by-step" skill definition
     └─ Returns PipelineDefinition (DAG of steps)

  6. PipelineEngine.run(pipeline_def, problem, answer)
     │
     ├─ Blackboard initialized with {problem_text, answer_text}
     │
     ├─ Topological sort of steps
     │
     ├─ For each step in dependency order:
     │   │
     │   ├─ ContextInjector renders step prompt
     │   │   Template: "Given the problem: {{ blackboard.problem_text }}
     │   │              And previous results: {{ blackboard.step_2_output }}
     │   │              Now: {{ step.prompt }}"
     │   │
     │   ├─ LLMGateway.complete(rendered_prompt, output_schema)
     │   │   └─ OpenRouter API call with structured output
     │   │
     │   └─ Blackboard[step.id] = parsed_output
     │
     └─ Returns final Blackboard state

  7. OutputFormatter
     └─ Renders result to terminal (Rich Markdown)
     └─ Writes result to output/2024-mechanics-q3_result.json
```

### Index Build Flow: `cpho index ./papers/`

```
  1. WorkspaceManager scans ./papers/ recursively
     └─ Returns list of PaperFile objects (exam papers)

  2. Phase 02.1 Paper Splitting:
     ├─ Rules-based splitter (regex + page markers)
     ├─ LLM fallback for ambiguous cases
     └─ Produces list of ProblemEntry objects (one per problem)

  3. For each unindexed ProblemEntry:
     │
     ├─ OCR Adapter extracts text from the paper's relevant pages
     │
     ├─ LLMGateway.complete(
     │     "Analyze this physics problem and generate tags...",
     │     output_schema=TagSetSchema
     │   )
     │
     └─ IndexWriter appends record to index.jsonl

  4. IndexReader verifies: count of indexed == count of problems
```

### REPL Session Flow: `cpho repl`

```
  1. REPL Session starts
     └─ Loads workspace context (folder path, index state)

  2. User enters: "compare problems 3 and 7 on rotational dynamics"

  3. REPL parses intent (natural language → command)
     └─ Extracts: action=compare, problem_refs=[3,7], topic=rotational_dynamics

  4. IndexReader queries tags for problems 3 and 7
     └─ Returns tag sets for context

  5. PipelineEngine runs comparative skill
     └─ Injects both problem texts + tag overlap as context

  6. Result displayed in REPL
     └─ Session state updated (last_result, problem_context)

  7. User follow-up: "now add problem 12 to the comparison"
     └─ REPL uses session state (knows current comparison)
     └─ Re-runs with expanded problem set
```

### State Management Strategy

**REPL sessions** require mutable state that persists across commands. This is the key architectural difference from batch commands (which are stateless).

```
SessionState:
  workspace_path: Path
  last_result: PipelineResult | None
  active_comparison: ComparisonState | None
  problem_context: dict[problem_id, ProblemContext]
  history: list[CommandRecord]
```

The session state lives in the REPL process memory (single-user, local CLI — no persistence needed between sessions initially). If the user wants to save a session, it serializes to `~/.cpho/sessions/<timestamp>.json`.

**Batch commands** are stateless. Each `solve` or `batch` invocation is self-contained. The index file provides the only shared state across invocations.

---

## Patterns to Follow

### Pattern 1: Abstract Interface + Adapter Injection

**What:** Core defines a Protocol/ABC. Adapters implement it. CLI composes them at startup (manual DI — no framework needed at this scale).

**Example:**
```python
# core/llm/gateway.py
from typing import Protocol

class LLMGateway(Protocol):
    def complete(self, prompt: str, schema: dict) -> dict: ...

# adapters/openrouter_client.py
class OpenRouterClient:
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self._key = api_key
        self._base = base_url

    def complete(self, prompt: str, schema: dict) -> dict:
        # OpenRouter API call with extra_body for json_schema
        ...

# cli/commands/solve.py
def solve_command(problem_path: str, skill: str, model: str):
    llm = OpenRouterClient(api_key=get_api_key())
    engine = PipelineEngine(llm_gateway=llm)
    result = engine.run(problem, skill)
    # format and output
```

### Pattern 2: Blackboard Pattern for Step Context

**What:** A shared typed key-value store that all pipeline steps read from and write to. Steps reference prior step outputs by key. The blackboard is the single source of truth for context injection.

**When:** Any multi-step pipeline where later steps need context from earlier steps. This is the standard pattern in LLM pipeline frameworks (Griptape, Flock, LangGraph).

**Example:**
```python
# core/pipeline/blackboard.py
class Blackboard:
    def __init__(self, initial: dict[str, Any]):
        self._store: dict[str, Any] = dict(initial)

    def put(self, key: str, value: Any) -> None:
        self._store[key] = value

    def get(self, key: str) -> Any:
        return self._store[key]

    def snapshot(self) -> dict[str, Any]:
        return dict(self._store)

# In PipelineEngine:
bb = Blackboard({"problem_text": problem.text, "answer_text": answer.text})

for step in dag.topological_order():
    # Context injector renders template with blackboard access
    prompt = ContextInjector.render(step.prompt_template, bb.snapshot())

    output = llm.complete(prompt, step.output_schema)
    bb.put(step.id, output)
```

### Pattern 3: Pre-Compute Metadata Pattern

**What:** Expensive computations (tag generation via LLM) run once at index time. All subsequent operations query the pre-computed index for instant results.

**When:** Any analysis that needs semantic understanding of problems. Tag-based similarity, comparative analysis, exam composition all depend on the index.

### Pattern 4: Producer-Consumer Pipeline (Batch Command)

**What:** `cpho batch` is a producer-consumer queue. The producer scans the workspace for problems. Workers (configurable concurrency) process problems through the pipeline. Results stream to output files.

**Example:**
```python
# cli/commands/batch.py
def batch_command(folder: str, skill: str, concurrency: int = 3):
    problems = workspace.discover_problems(folder)

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(engine.run, p, skill): p for p in problems}
        for future in as_completed(futures):
            result = future.result()
            output.write_result(result)
            progress.update()
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Pipeline Steps That Call Other Pipelines
**What:** A step in a DAG that itself invokes a sub-pipeline.
**Why bad:** Creates hidden dependencies, complicates context injection, makes debugging intractable.
**Instead:** Flatten the pipeline. If a sub-problem needs its own analysis, it should be a separate pipeline invocation with a clear boundary. The parent pipeline step can reference the sub-result by path/ID, not by nesting.

### Anti-Pattern 2: LLM Call in CLI Command Handler
**What:** Putting an `openai.chat.completions.create()` call directly in a Typer command function.
**Why bad:** Couples I/O to shell layer, makes testing impossible without mocking, prevents reuse for batch/web.
**Instead:** CLI command function only parses args and calls `core` functions. All LLM calls go through the LLMGateway interface.

### Anti-Pattern 3: Raw Dict Passing for Domain Data
**What:** Passing `dict` objects for tags, problem data, pipeline results between components.
**Why bad:** No type safety, no IDE support, silent key errors.
**Instead:** Use frozen dataclasses or Pydantic models at component boundaries. `TagSet`, `Problem`, `PipelineStep`, `StepResult` should all be typed models.

### Anti-Pattern 4: Skill Directory Contains Only Python Code
**What:** A skill that requires the user to write Python without offering a YAML or pure-prompt alternative.
**Why bad:** Violates the three-tier accessibility promise. Physics coaches should not need to write Python.
**Instead:** Every skill should have at minimum a `skill.yaml` definition. Python code is an optional escape hatch for advanced users, not the default path.

---

## Scalability Considerations

| Concern | At 100 problems | At 1K problems | At 10K problems |
|---------|----------------|---------------|-----------------|
| **Indexing time** | ~5 min (sequential LLM calls) | ~50 min (sequential) / ~10 min (parallel=5) | ~8 hours (sequential) — needs batch + caching |
| **Index query** | In-memory scan of JSONL: <1ms | In-memory scan: ~5ms | SQLite FTS behind same IndexReader interface |
| **Pipeline execution** | Single thread: fine | Thread pool (5 workers): fine | Thread pool (10+ workers) with rate limiting |
| **Output storage** | JSON files in output dir | JSON files in output dir | Sharded by date/batch |
| **REPL state** | In-memory: trivial | In-memory: still fine | Save/load session files |

**Key insight:** For the v1 target audience (individual coaches, <1000 problems), JSONL + in-memory indexing is more than sufficient. The architecture isolates the index storage behind `IndexReader`/`IndexWriter` interfaces, so migrating to SQLite or a vector store later requires zero changes to consumers.

---

## Build Order Implications

Based on dependency analysis of the component graph:

```
LLMGateway ← WorkspaceManager ← IndexingLayer ← PipelineEngine ← SkillSystem ← CLI commands
     ↑                                                          ↑
  OCR Adapter                                              Output Pipeline
```

**Suggested phase ordering:**

1. **Phase: Foundation** — LLM Gateway + Workspace Manager + CLI scaffold
   - These have zero internal dependencies. Everything else depends on them.
   - A working `cpho solve` that calls OpenRouter and returns raw LLM output proves the chain works end-to-end.

2. **Phase: Indexing** — Tag schema + Index writer/reader + OCR adapter interface
   - Depends on: LLM Gateway, Workspace Manager
   - Unlocks: tag-based queries, incremental indexing, comparative analysis foundation
   - The index format (JSONL schema) must stabilize before any skill that depends on tag queries can be built.

3. **Phase: Pipeline Engine** — DAG scheduler + Blackboard + Context injector
   - Depends on: LLM Gateway (for step execution)
   - Unlocks: multi-step analysis, step-by-step derivation, quality verification
   - This is the most architecturally significant component. Getting the DAG model right here determines whether skills are composable.

4. **Phase: Skill System** — Skill discovery + Loader + Built-in skills
   - Depends on: Pipeline Engine (skills produce pipeline definitions)
   - Unlocks: user-extensible analysis modes, skill creator, community skills
   - Built-in skills (question mode, step-by-step, comparative) are built on this framework — they are the first clients of the skill system.

5. **Phase: Output + REPL + Batch** — PDF stitching + REPL sessions + batch processing
   - Depends on: Everything above
   - Unlocks: polished user experience, exam composition output, interactive analysis

**Rationale:** Each phase builds on the previous. The LLM Gateway must work before anything else (it is the foundation). The pipeline engine must stabilize before skills are written (skills are pipeline definitions). Output formatting is last because it is the least risky — format changes do not cascade backward.

---

## Sources

- Python core-shell / hexagonal architecture patterns: [gpt-engineer core/cli separation discussion](https://github.com/AntonOsika/gpt-engineer/issues/718), [profile_engine refactor](https://github.com/szmyty/profile/issues/150)
- Python plugin discovery: [importlib.metadata entry points](https://docs.python.org/3/library/importlib.metadata.html#entry-points), [pluggy hook system](https://pluggy.readthedocs.io/)
- DAG pipeline patterns: [Griptape Workflow documentation](https://github.com/griptape-ai/griptape), [LangGraph StateGraph](https://python.langchain.com/docs/langgraph/)
- Blackboard architecture: [Flock declarative multi-agent system](https://github.com/whiteducksoftware/flock), [Microsoft UFO Blackboard](https://microsoft.github.io/UFO/)
- OpenRouter structured output: [extra_body workaround](https://github.com/BerriAI/litellm/discussions/11652), [Response Healing announcement](https://openrouter.ai/announcements/response-healing-reduce-json-defects-by-80percent)
- CLI tooling standards: [Typer](https://typer.tiangolo.com/), [Rich](https://rich.readthedocs.io/), [prompt_toolkit](https://python-prompt-toolkit.readthedocs.io/)
- Agent framework comparison: [LangWatch 2025 comparison](https://langwatch.ai/blog/best-ai-agent-frameworks-in-2025-comparing-langgraph-dspy-crewai-agno-and-more)
