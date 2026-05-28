# Architecture Patterns — CPHO CLI v1.1

**Domain:** Extending an existing 17K-LOC Python CLI (DAG skill pipeline + JSONL tag index + Typer/REPL) with a new shared Knowledge Base layer, a refactored Explain skill, and per-step model configuration.
**Researched:** 2026-05-27
**Confidence:** HIGH (recommendations derived from inspection of the actual v1.0 code under `src/cpho_cli/`).

This document answers the 7 integration questions in build-order, naming concrete modules / classes / signatures. New modules and modifications to existing files are clearly marked **[NEW]** or **[MODIFY]**.

---

## 1. Knowledge Base Layer — Storage & Module Layout

### Recommendation: a sibling module `core/knowledge/`, NOT an extension of `core/index/`

Rationale, in priority order:

1. **Different entity, different lifecycle.** `core/index/` indexes *problems* (one JSONL row per `ProblemEntry`). A knowledge file is a *first-class authored document* (markdown / LaTeX / image / docx) whose lifecycle is "user authors → standardize skill normalizes → committed to knowledge area". Coercing it into `IndexEntry` confuses provenance.
2. **Different source of truth.** Problems live in the user's workspace (`~/Desktop/物理竞赛资料/...`). Knowledge files live in `.cpho/knowledge/` (private) **and** a syncable community cache (`~/.cache/cpho/community-kb/`). The index is workspace-scoped; knowledge is cross-workspace.
3. **Decoupled rebuild semantics.** `cpho index --force` clobbers LLM tags; it must NOT touch knowledge files. Keeping the modules sibling avoids accidental cross-contamination.
4. **The link IS the tag.** Knowledge files are *joined* to problems via the shared canonical-tag vocabulary that already lives in `core/index/vocabulary.py`. The two modules share that vocabulary but nothing else.

### Module layout

```
src/cpho_cli/
├── core/
│   ├── index/                       # [UNCHANGED, lightly extended]
│   └── knowledge/                   # [NEW] parallel sibling
│       ├── __init__.py              # re-exports public API
│       ├── store.py                 # KnowledgeStore — read/write/list
│       ├── resolver.py              # tag → KnowledgeFile lookup
│       ├── ingest.py                # multimodal ingest (image/docx/md/LaTeX)
│       ├── standardize.py           # two-step standardization skill core
│       ├── sync.py                  # community pull/merge (§5)
│       ├── manifest.py              # JSONL manifest read/write
│       └── exceptions.py
├── models/
│   └── knowledge.py                 # [NEW] KnowledgeFile, KnowledgeManifestEntry, etc.
└── builtin_skills/
    └── knowledge_normalize/         # [NEW] standardize skill (two-step)
        ├── SKILL.md
        ├── skill.yml
        └── prompts/
```

### On-disk storage layout

```
<workspace>/.cpho/
  index.jsonl                         # existing problem index
  knowledge/                          # [NEW] knowledge area
    manifest.jsonl                    # one row per knowledge file (see below)
    files/
      <uuid>.md                       # normalized markdown content
      <uuid>.assets/                  # extracted images, original docx, etc.
    drafts/                           # standardize skill stage-1 output (pre-review)
      <uuid>.md
      <uuid>.source                   # symlink/copy of original user file
    community/                        # synced community library (read-only cache)
      <repo-name>/...                 # mirrors community repo structure
```

Why JSONL manifest instead of "directory scanning":

- Consistent with existing `index.jsonl` semantics (the codebase already has `core/index/builder.py` for JSONL).
- Enables fast tag→file lookup without re-reading every markdown file.
- Stores provenance (source: `private | community:<repo>`), tags, draft status, source-file hash.

### `KnowledgeManifestEntry` model — `models/knowledge.py` **[NEW]**

```python
class KnowledgeManifestEntry(BaseModel):
    knowledge_id: str                 # uuid
    title: str                        # extracted by normalize skill
    tags: list[CanonicalTag]          # canonical-tag refs (joins to vocabulary)
    source: Literal["private", "community"]
    source_repo: str | None           # set when source == community
    content_path: Path                # .cpho/knowledge/files/<uuid>.md
    original_path: Path | None        # user's original file (if available)
    original_format: Literal["markdown", "latex", "docx", "image", "handwritten_image"]
    content_hash: str                 # for sync conflict detection
    standardize_status: Literal["draft", "approved"]
    created_at: datetime
    updated_at: datetime
```

### `KnowledgeStore` API — `core/knowledge/store.py` **[NEW]**

```python
class KnowledgeStore:
    def __init__(self, workspace_path: Path) -> None: ...
    def list_all(self) -> list[KnowledgeManifestEntry]: ...
    def get(self, knowledge_id: str) -> KnowledgeFile: ...
    def add(self, file: KnowledgeFile, *, status: Literal["draft", "approved"]) -> KnowledgeManifestEntry: ...
    def update(self, knowledge_id: str, *, content: str | None = None,
               tags: list[CanonicalTag] | None = None,
               status: Literal["draft", "approved"] | None = None) -> KnowledgeManifestEntry: ...
    def find_drafts(self) -> list[KnowledgeManifestEntry]: ...
```

### `KnowledgeResolver` — `core/knowledge/resolver.py` **[NEW]**

The critical join API consumed by Explain v2:

```python
class KnowledgeResolver:
    """Tag → KnowledgeFile lookup, with priority (private > community)."""

    def __init__(self, store: KnowledgeStore) -> None: ...

    def find_for_problem(
        self,
        problem_entry: IndexEntry,
        *,
        include_community: bool = True,
        max_results: int = 8,
    ) -> list[ResolvedKnowledge]:
        """Return knowledge files whose tags overlap problem_entry.tags,
        sorted by (private_first, tag_overlap_score, recency)."""

    def find_for_tags(self, tags: list[CanonicalTag]) -> list[ResolvedKnowledge]: ...
```

`ResolvedKnowledge` carries the matched entry + the overlap reason + a citation block ready to be appended to skill output (satisfies §6 "输出标注来源").

---

## 2. Knowledge → Explain Integration (Data Flow)

### Current pipeline (v1.0)

`core/explain.py::run_explain` is monolithic — it iterates `tones`, runs two stages per tone (`_run_tone` → `stage1` + `sentence`), all glued by Jinja templates rendered inline. There is no extension point for injecting "first-priority context".

### v1.1 pipeline (after §3 refactor)

```
ExplainV2Skill.run(context)
  │
  ├─ Step 1: ContextResolveStep
  │     loads ProblemEntry from core/index, fetches problem_text + answer_text,
  │     normalizes image/PDF paths for multimodal routing (§6)
  │
  ├─ Step 2: KnowledgeInjectionStep          ⭐ NEW — guaranteed before any 板块
  │     knowledge_blocks = KnowledgeResolver(store).find_for_problem(entry)
  │     if knowledge_blocks: context["knowledge"] = knowledge_blocks
  │                          context["knowledge_citations"] = [...]
  │     else:               context["knowledge"] = []  (skill continues; no soft-fail)
  │
  ├─ Step 3..N: BoardStep (one per 板块 user selected)
  │     each Board (思路描述 / 标答替换 / 其他方法) is its own pipeline step
  │     each renders a prompt template that ALWAYS includes
  │     {{ knowledge_section }} above the problem statement
  │
  └─ Step N+1: CitationAttachStep
        appends "## 参考知识 (Knowledge sources)" markdown to final output,
        listing every KnowledgeManifestEntry referenced (id + title + path)
```

### Prompt pipeline change

Knowledge content is injected at the **system-prompt level**, not interleaved with user messages, so the LLM is instructed to read it before reasoning about the problem. Concretely, each Board's prompt template (`builtin_skills/explain/prompts/<board>.md.j2`) gains a fixed prelude:

```jinja
{% if knowledge %}
你必须先阅读以下知识总结，再开始本题讲解。讲解中如直接采用了这些知识，
请在结尾"参考知识"区列出对应的 knowledge_id。

{% for k in knowledge %}
---
# 知识 [{{ k.knowledge_id }}] {{ k.title }}
来源: {{ k.source }} ({{ k.original_path or k.content_path }})
{{ k.content }}
{% endfor %}
---
{% endif %}

# 题目
{{ problem_text }}
...
```

### Source attribution to user-visible output

`CitationAttachStep` appends a deterministic trailer to the markdown produced by `skill_outputs.write_markdown_atomic`:

```markdown
## 参考知识
- [k_3f1a...] 弹簧–小球共振模型（私有）— `.cpho/knowledge/files/3f1a....md`
- [k_b29c...] 张量展开通法（community/cpho-physics-kb）— `.cpho/knowledge/community/cpho-physics-kb/methods/tensor.md`
```

`knowledge_id` references are also embedded inline by the prompt instruction ("如直接采用…请列出对应的 knowledge_id"), giving paragraph-level traceability.

### What changes vs. what's new

| Concern | Status | Location |
|---|---|---|
| Knowledge resolution | **[NEW]** | `core/knowledge/resolver.py` |
| Pipeline-level injection step | **[NEW]** | `core/skills/steps/knowledge_injection.py` |
| Prompt templates with `{% if knowledge %}` prelude | **[MODIFY]** | `builtin_skills/explain/prompts/*.md.j2` (new files per 板块) |
| Citation trailer | **[NEW]** | `core/skills/steps/citation_attach.py` |
| Old `run_explain` monolith | **[DEPRECATE]** | `core/explain.py` — keep one release as fallback |

---

## 3. Skill Architecture Refactor — "Jump Out of the Box"

User mandate (§6.3): no compromise inside the existing pattern. Below is a concrete proposal that supports declared multi-step pipeline + per-step model selection + per-step prompt inspection + knowledge injection.

### Contrast: current monolithic pattern

```python
# core/explain.py (v1.0) — monolithic, opaque to the user
async def run_explain(*, provider, params, problem_text, answer_text, tones, ...):
    outputs = await asyncio.gather(*[_run_tone(...) for tone in tones])
    _extract_tags(...)
    write_markdown_atomic(...)
```

Problems:
- One `params: ModelParams` for the whole skill — can't pick a different model per step.
- Prompt rendering hidden inside `_render_prompt(...)` private helper — user can't introspect.
- Steps (`stage1`, `sentence`) hard-coded inside `_run_tone` — user can't see or reorder them.
- New steps (knowledge injection, citation) can only be added by editing `_run_tone` — fragile.

### v1.1 pattern: declarative `SkillPipeline`

```python
# core/skills/__init__.py [NEW]

class SkillStep(BaseModel, ABC):
    step_id: str                              # stable id, e.g. "explain.board.思路描述"
    title: str                                # human-readable for the panel
    prompt_template_path: Path | None         # for prompt-driven steps; None = code-only
    requires_multimodal: bool = False         # routes input strategy (§6)
    default_model: ModelRef                   # provider + model name

    @abstractmethod
    async def run(self, context: StepContext) -> StepResult: ...


class SkillPipeline(BaseModel):
    skill_id: str                             # "explain", "solve", "knowledge_normalize"
    steps: list[SkillStep]                    # ordered; rendered to the user pre-run

    def describe(self) -> SkillPanel:         # what the model-selection panel reads
        ...

    async def execute(
        self,
        context: StepContext,
        *,
        step_overrides: dict[str, ModelRef] | None = None,
        on_step_event: Callable[[StepEvent], None] | None = None,
    ) -> SkillResult:
        for step in self.steps:
            model_ref = (step_overrides or {}).get(step.step_id, step.default_model)
            provider = ProviderRegistry.get(model_ref)
            result = await step.run(context.with_model(provider, model_ref))
            context = context.advance(result)
            on_step_event(StepEvent.completed(step, result))
        return context.to_skill_result()
```

### What this unlocks

- **(a) Declared multi-step pipeline visible to user.** `pipeline.describe()` produces a tree the REPL can render *before* running:
  ```
  explain (v2)
    1. context_resolve         model: <default>            prompt: (code-only)
    2. knowledge_injection     model: <default>            prompt: (code-only)
    3. board:思路描述           model: anthropic/claude...   prompt: prompts/board_idea.md.j2
    4. board:标答替换           model: openai/gpt-...       prompt: prompts/board_replace.md.j2
    5. citation_attach         model: (none)               prompt: (code-only)
  ```
- **(b) Per-step model selection.** `step_overrides` dict is read from the panel store (§4). A user can run Explain with Gemini for 思路描述 and Claude for 标答替换 in the same invocation.
- **(c) Per-step prompt template inspection.** `step.prompt_template_path` is real on disk; `/skill panel explain` shows the path and `cpho skill show-prompt explain board:思路描述` prints it. No more hidden private helpers.
- **(d) Knowledge-injection step before any board step.** Encoded as the second step of every Explain pipeline; cannot be omitted because pipelines are immutable `BaseModel` declarations defined in the skill module.

### Concrete Explain v2 pipeline definition

```python
# builtin_skills/explain/pipeline.py [NEW]

def build_explain_pipeline(boards: list[ExplainBoard]) -> SkillPipeline:
    steps: list[SkillStep] = [
        ContextResolveStep(step_id="explain.context", ...),
        KnowledgeInjectionStep(step_id="explain.knowledge", ...),
    ]
    for board in boards:
        steps.append(
            BoardStep(
                step_id=f"explain.board.{board.value}",
                title=BOARD_TITLES[board],
                prompt_template_path=PROMPTS_DIR / f"board_{board.value}.md.j2",
                requires_multimodal=True,                       # §6
                default_model=DEFAULT_MODEL_PER_BOARD[board],
            )
        )
    steps.append(CitationAttachStep(step_id="explain.citations", ...))
    return SkillPipeline(skill_id="explain", steps=steps)
```

### Migration of Solve / Probe / Compose

To avoid an unbounded refactor, **only Explain is forced through the new pipeline in v1.1's Explain phase**. Other skills are migrated phase-by-phase once the framework is proven:

- Phase A: introduce `core/skills/` with `Explain v2` as the first consumer.
- Phase B: port `Solve` next (it's the next-most-complex skill).
- Phase C: port `Probe`, `Compose`, `Related` — they're simpler and benefit less.

The old `core/explain.py` stays as a transitional fallback for one release, then deletes.

---

## 4. Model Selection Panel — Storage

### Recommendation: extend SessionState **and** add a per-skill config file

The two needs are different:

| Need | Where it lives | Rationale |
|---|---|---|
| Session-scoped overrides (within one REPL invocation) | `SessionState` (in-memory) | User picks "use Gemini for 思路描述 this run only" |
| Persistent skill-wide defaults (across runs) | `.cpho/skills/<skill_id>.yml` (workspace) + `$XDG_CONFIG_HOME/cpho/skills/<skill_id>.yml` (user) | Survive REPL restart; workspace overrides user |
| Provider credentials / base URLs | **unchanged** — `config.local.yml` | Already battle-tested |

### Layered resolution (highest priority wins)

```
1. CLI flag / REPL one-shot override  (--step explain.board.思路描述=anthropic/claude-...)
2. SessionState.step_overrides         (set via /skill panel during this session)
3. .cpho/skills/<skill_id>.yml         (workspace project default)
4. ~/.config/cpho/skills/<skill_id>.yml (user global default)
5. SkillStep.default_model              (code default)
```

### Skill panel config format — `.cpho/skills/explain.yml` **[NEW]**

```yaml
skill: explain
version: 1
step_models:
  explain.context: { provider: openrouter, model: anthropic/claude-3.5-sonnet }
  explain.knowledge: { provider: openrouter, model: anthropic/claude-3.5-sonnet }
  explain.board.思路描述: { provider: openrouter, model: google/gemini-2.0-flash-thinking }
  explain.board.标答替换: { provider: openrouter, model: anthropic/claude-3.5-sonnet }
  explain.board.其他方法: { provider: openrouter, model: openai/o1 }
  explain.citations: { provider: none }
```

### Interaction with existing `--provider` and `config.local.yml`

- `config.local.yml` defines *available providers* (keys, base URLs). Unchanged.
- `--provider` flag selects a **default provider** for steps that don't specify one. Unchanged at the skill level but now interpreted as "fallback for steps lacking explicit assignment".
- `step_models[...].provider` keys must reference a provider name defined in `config.local.yml`; the loader raises `UnknownProviderError` with a "改哪里" pointer otherwise (§ error handling per §3 of new-understanding).

### Live model-list fetching

User explicitly demands the model list be scraped from the provider's API each time, not hard-coded (§2). Implementation:

```python
# core/skills/panel/model_catalog.py [NEW]

class ModelCatalog:
    """Live model-list fetcher with TTL cache."""

    def list_models(self, provider_kind: str, *, force_refresh: bool = False) -> list[ModelInfo]:
        """For 'openrouter': GET /api/v1/models (already partially used by
        fetch_openrouter_model_capabilities in core/llm.py).
        For 'google_ai_studio': GET https://generativelanguage.googleapis.com/v1beta/models.
        For 'deepseek': GET /models.
        Cached for 1h in $XDG_CACHE_HOME/cpho/model-catalog/<provider>.json."""
```

The REPL `/skill panel <skill>` command renders a selection box per step populated by `ModelCatalog.list_models(provider_kind=current_provider, force_refresh=False)`; `r` keypress triggers `force_refresh=True`.

---

## 5. Community Knowledge Sync (`cpho knowledge sync`)

### Recommendation: pull-only Git mirroring + manifest-driven merge

Constraints from user spec (§5.2):
- Source is a GitHub open-source library; users *download* community knowledge, optionally *upload* their own.
- Local-first remains paramount — no automatic uploads.

### Source

- **Primary upstream**: `https://github.com/<org>/cpho-physics-kb` (canonical community repo, to be created).
- **Optional additional upstreams**: configured in `~/.config/cpho/community.yml` as a list of git URLs (advanced users / forks).
- **Pulled via `git`** (sparse-clone, depth=1) — Python invokes `git` via subprocess. Falls back to a `tarball + GitHub API` path for users without git on PATH (Windows packaging concern, §7).

### Storage

```
~/.cache/cpho/community-kb/
  <repo-name>/
    .git/                    # full clone for `git pull` updates
    files/...                # mirrored markdown / images
    manifest.jsonl           # community-curated manifest (committed in the repo)
```

The community repo itself contains a top-level `manifest.jsonl` whose schema matches `KnowledgeManifestEntry` (with `source="community"`, `source_repo=<repo-name>`). This lets the local merger join community entries into the same `KnowledgeResolver` queries.

### Merge semantics

`cpho knowledge sync` performs:

```
1. git clone or git pull each upstream into ~/.cache/cpho/community-kb/<repo>/
2. Read upstream manifest.jsonl
3. Diff against last-synced manifest (stored in ~/.cache/cpho/community-kb/<repo>/.cpho-last-sync.json)
4. For each added/updated entry: ensure files/<uuid>.md is present; refresh local cache
5. Write a per-workspace symlink layer at <workspace>/.cpho/knowledge/community/<repo>/
   so KnowledgeStore.list_all() picks them up transparently
6. Never modify private files in <workspace>/.cpho/knowledge/files/
```

### Conflict resolution

- **Knowledge files are content-addressed by `knowledge_id` (uuid).** Private and community entries cannot collide on `knowledge_id`.
- **Tag-level overlap is fine and expected** — both private and community files may carry the same tag; `KnowledgeResolver` returns both, with private prioritized (§1 sort order).
- **If a user "promotes" their private file to community** (manual git PR flow, out of scope for the CLI in v1.1), they keep the same `knowledge_id` and the community version replaces the private one on next sync. Detected by manifest reconciliation; CLI prompts: "Private knowledge `<id>` now exists upstream; remove local copy? (y/N)".

### CLI surface

```
cpho knowledge sync                       # pull all configured upstreams
cpho knowledge sync --repo cpho-physics-kb
cpho knowledge sync --list                # show configured upstreams
cpho knowledge sync --add <git-url>       # adds to ~/.config/cpho/community.yml
```

REPL: `/knowledge sync`, `/knowledge list`, `/knowledge show <id>`.

---

## 6. Multimodal-First Input Routing

### Recommendation: skill-step capability declaration + runtime model-capability check + automatic OCR fallback

The infrastructure to do this *exists* in v1.0 (`detect_model_capabilities`, `fetch_openrouter_model_capabilities`, `ModelCapabilities.input_modalities`). v1.1 generalizes its application from "only Solve when `--vision`" to "every step that declares `requires_multimodal=True` automatically".

### Step declaration

```python
class BoardStep(SkillStep):
    requires_multimodal: bool = True
    fallback_to_ocr: bool = True             # if False, raise instead of OCR
```

### Runtime routing — `core/skills/input_router.py` **[NEW]**

```python
class InputRouter:
    def route_problem_input(
        self,
        problem_entry: IndexEntry,
        provider: LLMProvider,
        model_ref: ModelRef,
        *,
        require_multimodal: bool,
        allow_ocr_fallback: bool,
    ) -> RoutedInput:
        capabilities = detect_model_capabilities(provider, model_ref.model)
        wants_image = require_multimodal
        can_image = "image" in capabilities.input_modalities

        if wants_image and can_image:
            return RoutedInput.multimodal(
                image_paths=problem_entry.source_image_paths,
                pdf_path=problem_entry.source_pdf_path,
            )
        if wants_image and not can_image:
            if not allow_ocr_fallback:
                raise ModelCapabilityMismatch(...)
            # fallback path: use OCR + a verification subprompt (§1 of new-understanding)
            return RoutedInput.text_with_ocr_audit(
                text=problem_entry.problem_text,
                audit_prompt=OCR_AUDIT_PROMPT,
            )
        return RoutedInput.text(text=problem_entry.problem_text)
```

### Pipeline integration

`SkillStep.run` calls `InputRouter` before sending the user message. The decision is logged to `StepEvent` so `/skill panel` can show "Board:思路描述 ran in multimodal mode" or "fell back to OCR (model gemini-1.5-flash-text lacks image input)".

### Indexer remains OCR-only

`core/index/builder.py` is **not** touched — Index continues to use OCR + text per §1 of the new understanding. Only `core/skills/*` steps go multimodal.

---

## 7. Build Order Across the 6 v1.1 Modules

### Dependency graph

```
                       ┌──────────────────────────┐
                       │  Knowledge Base layer     │── independent foundation
                       │  (core/knowledge/)        │
                       └─────────────┬─────────────┘
                                     │ KnowledgeResolver
                                     ▼
   ┌─────────────────────────┐   ┌──────────────────────────┐
   │ Skill arch refactor      │   │ Explain v2 板块设计       │
   │ (core/skills/SkillPipe.) │──▶│  (uses pipeline + KB)    │
   └─────────────┬────────────┘   └──────────────────────────┘
                 │ SkillPipeline / SkillStep
                 ▼
   ┌─────────────────────────────┐
   │  Model selection panel       │── reads pipeline.describe()
   │  (core/skills/panel/)        │   needs ModelCatalog live-fetch
   └─────────────┬────────────────┘
                 │
                 ▼
   ┌─────────────────────────────┐
   │  Multimodal input routing    │── lifts existing capability
   │  (core/skills/input_router.)  │   detection; needs SkillStep flag
   └─────────────────────────────┘

   ┌─────────────────────────────┐
   │  Community sync              │── depends on KB store layout
   │  (core/knowledge/sync.py)    │   but otherwise standalone
   └─────────────────────────────┘

   ┌─────────────────────────────┐
   │  Error handling + docs       │── cross-cutting, parallel
   │  Cross-platform packaging    │── independent spike
   └─────────────────────────────┘
```

### Recommended phase order

| Phase | Module(s) | Why this order | Risk |
|---|---|---|---|
| **P1** | Knowledge Base layer (`core/knowledge/` store + resolver + models + private-only flow + standardize skill) | Blocks Explain v2. Standalone — produces user value as soon as ingest skill ships. | LOW. Storage layout is the only irreversible decision; document it. |
| **P2** | Skill architecture refactor (`core/skills/` pipeline framework, port Explain only) | Blocks per-step model panel and Explain v2's "knowledge injection step". User's explicit "jump out of the box" directive lives here. | MEDIUM. Touches a hot path; mitigate by keeping `core/explain.py` as a feature-flag fallback for one release. |
| **P3** | Explain v2 板块 design (build the three Board steps on top of P2 + use KnowledgeResolver from P1) | Now both prerequisites exist. | LOW once P1+P2 ship. |
| **P4** | Multimodal-first input routing (`InputRouter`, lift existing `detect_model_capabilities`) | Needs SkillStep declaration field from P2. Can land before or after P3, but is best done with P3 so 板块 outputs benefit immediately. | LOW. Infra exists; mostly wiring. |
| **P5** | Model selection panel (`core/skills/panel/`, `ModelCatalog`, `/skill panel` REPL command, `.cpho/skills/<id>.yml`) | Needs `SkillPipeline.describe()` from P2. Best done after P3 because Explain provides the most pipeline shape to display. | MEDIUM. Live model-list scraping is per-provider; budget for Google AI Studio quirks. |
| **P6** | Community knowledge sync (`core/knowledge/sync.py`, `cpho knowledge sync`) | Depends on P1 storage layout. Independent of skill refactor. | MEDIUM. Requires a community repo to exist; can ship empty-upstream-tolerant. |
| **P7 (parallel from P1)** | Error handling + docs (per-failure "改哪里" prompts, README/docs/user error tables) | Cross-cutting; each module above contributes its own error table as it ships. | LOW. |
| **P8 (independent spike)** | Cross-platform packaging (Windows + Mac one-click installer) | User flagged this as an open question. Run as a spike in parallel; do not block features on it. | HIGH but isolated. |

### Why P1 before P2

Even though §6.3 makes the skill refactor *psychologically* the headliner, the Knowledge Base storage decisions (manifest schema, on-disk layout, resolver semantics) inform the shape of `KnowledgeInjectionStep`. Shipping a refactor that immediately needs to be adjusted when the KB layout changes is wasteful. Ship the KB first as a standalone capability (private files via standardize skill produce immediate user value); then refactor skills with the KB as a stable dependency.

### Why P5 (model panel) after P3 (Explain v2)

The panel needs at least one *interesting* multi-step skill to demonstrate value. If we ship the panel against only `Solve` and `Probe` (still on the old monolithic pattern at that point), users see a one-line panel — uninteresting. Shipping the panel alongside Explain v2's 3-board pipeline immediately demonstrates the "per-step model" payoff.

---

## Anti-Patterns to Avoid

### A1: Stuffing knowledge files into `IndexEntry`
**What goes wrong:** You bolt a `knowledge_refs: list[str]` field onto `IndexEntry`. Soon you need rebuild semantics, sync semantics, draft/approved status — all of which collide with the index's invariants.
**Why bad:** Conflates "problem catalog" with "authored knowledge". `cpho index --force` will eventually clobber something it shouldn't.
**Instead:** Keep modules sibling (§1). The join key is the canonical-tag vocabulary, not direct foreign keys.

### A2: Reusing `core/explain.py::run_explain` and "just adding a knowledge step in the middle"
**What goes wrong:** You add an `if knowledge:` branch inside `_run_tone`, ship it, and call it done.
**Why bad:** Directly violates §6.3 "不要妥协". The user explicitly demanded a real refactor so that future skills inherit the new shape.
**Instead:** Introduce `core/skills/SkillPipeline` (§3) and make Explain v2 the first consumer. Treat `core/explain.py` as deprecated.

### A3: Caching the OpenRouter `/models` response forever
**What goes wrong:** ModelCatalog returns a snapshot; new models added by providers never appear.
**Why bad:** Violates "每次从官网扒下来" (§2). Users will not see new models.
**Instead:** TTL of 1 hour, with a manual `r` refresh in the panel and `--force-refresh` CLI flag.

### A4: Treating community knowledge as writeable
**What goes wrong:** Someone edits a file under `.cpho/knowledge/community/...`; next `sync` overwrites it.
**Why bad:** Silent data loss.
**Instead:** Community cache is read-only at the OS level (chmod 0444 after sync). Edits must go through a "fork to private" CLI command.

### A5: Coupling `InputRouter` to a specific provider
**What goes wrong:** `if provider_kind == 'openrouter': ...` branches.
**Why bad:** Adding Google AI Studio later doubles every conditional.
**Instead:** Route via `ModelCapabilities` (already an abstraction in `core/llm.py`). Each provider implements `get_model_capabilities`.

---

## Scalability Considerations

| Concern | At 10 knowledge files | At 200 knowledge files | At 2000 (community-merged) |
|---|---|---|---|
| Resolver lookup | Linear scan over manifest.jsonl is fine | Build in-memory `tag → [knowledge_id]` index on first call, cached per process | Add disk-side B-tree (`manifest.idx`) or migrate to sqlite-fts — re-evaluate at this size |
| `cpho knowledge sync` runtime | <1s | A few seconds (git pull + manifest diff) | Watch git pack size; consider partial-clone |
| `KnowledgeResolver.find_for_problem` | <1ms | <10ms with in-mem index | <50ms with disk index |
| Prompt token budget for injected knowledge | Send all matches | Truncate to top-K (default 8) | Re-rank with a cheap embedding step before truncation |

The "embedding re-rank" path is the only one that conflicts with the project's "no RAG / no vector retrieval" decision. If we hit the 2000-file regime, revisit that constraint; until then, tag-overlap scoring is sufficient.

---

## Sources

- v1.0 code inspection: `src/cpho_cli/core/llm.py`, `src/cpho_cli/core/index/__init__.py`, `src/cpho_cli/core/explain.py`, `src/cpho_cli/builtin_skills/explain/` (HIGH — direct read).
- User specification: `docs/new-understanding-2026-05-27.md` §§1–6 (HIGH — primary requirements doc).
- Project context: `.planning/PROJECT.md` (HIGH).
- OpenRouter `/models` endpoint usage already present in `fetch_openrouter_model_capabilities` (HIGH — verified in code).
