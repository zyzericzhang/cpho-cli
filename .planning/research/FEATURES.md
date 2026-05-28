# Feature Research

**Domain:** Local CLI tutor for physics-olympiad problem analysis (v1.1 additions to a shipped v1.0 CLI/REPL)
**Researched:** 2026-05-27
**Confidence:** MEDIUM (web verification unavailable this session; relies on training-data + project docs. Prior-art product names are HIGH-recognition; specific UI/API details are MEDIUM and flagged inline.)

> Scope: this file covers **only the six v1.1 feature clusters** asked about. v1.0 features (solve / explain-tone / probe / related / compose / index / repl / multimodal solve) are treated as already-shipped infrastructure that v1.1 must integrate with — not re-researched.

---

## 1. Knowledge Base Systems for Technical Tutoring

### Prior art surveyed

| Product | What's relevant |
|---|---|
| **Obsidian** | Markdown-file-as-source-of-truth; tag/link graph; vault = folder; community plugins for AI |
| **Logseq** | Block-level outliner; tag pages auto-aggregate references; markdown-on-disk |
| **Anki** | Note + card model; deck = collection; shared deck library; tag-based filtering |
| **RemNote** | Notes + spaced-repetition fused; concept tagging; "definition vs context" split |
| **NotebookLM** | Sources panel as first-class citizen; every AI claim cites a source |
| **Cursor / Continue / Cody (codebase Q&A)** | "Knowledge before generation": retrieve relevant files → inject into prompt → cite |

### Behaviors users expect (table stakes)

| Feature | Why Expected | Complexity | v1.0 Integration |
|---|---|---|---|
| Knowledge note as a **plain file on disk** (markdown / image / docx) | Obsidian/Logseq set the norm: "your notes are files, not a DB". Users hate lock-in. | LOW | New `knowledge/` dir alongside existing workspace folder |
| Notes are **tagged** (and tags are the join key to problems) | Anki + Obsidian + Logseq all use tags as the primary cross-cutting index | LOW | **Reuses v1.0 controlled-vocabulary tag index** — knowledge file's tags must come from the same vocabulary as problem tags |
| **List / browse** all notes from REPL | Mirror of `/search` for problems | LOW | New REPL slash command (e.g. `/kb list`, `/kb show <tag>`) |
| **Edit in your own editor** (not a built-in editor) | Obsidian/Logseq users want vim/VSCode; CLI users doubly so | LOW | Just print the file path; user opens it |
| **Surfacing relevant notes during AI generation** (the "knowledge before generation" loop) | NotebookLM, Cursor, Continue all do retrieve-then-generate; users expect AI to "know what I wrote" | MEDIUM | New retrieval step in Explain skill: for each problem tag, look up knowledge files with overlapping tags |
| **Citation / provenance in AI output** ("from notes/X.md") | NotebookLM normalized this expectation; users distrust un-cited AI | LOW | Append a `**Sources:**` section listing knowledge files consumed |
| **Draft → review → publish** for AI-normalized notes | Anki shared-deck culture, Obsidian "daily note inbox → permanent note", Zettelkasten "fleeting → literature → permanent" | MEDIUM | Two-step skill: generate to `knowledge/_draft/` → user reviews → promote to `knowledge/` |
| **Idempotent re-runs** of the normalization skill | If user tweaks a draft and re-runs, the skill should detect "already normalized, just clean up" not rewrite | MEDIUM | State detection on draft files (frontmatter marker or hash) |

### Differentiators (where CPHO can pull ahead)

| Feature | Value Proposition | Complexity | Notes |
|---|---|---|---|
| **Tag-driven retrieval instead of vector RAG** | More controllable, no hallucinated "relevance"; aligns with v1.0 "no vector search" decision | LOW–MED | Knowledge files inherit tags from controlled vocab → exact match join to problem tags. Cheaper, debuggable, no embedding store |
| **"Knowledge file is first-priority context"** (LM reads it *before* writing explanation) | NotebookLM cites sources but doesn't strongly prioritize one; CPHO promises "if a knowledge note exists for this tag, it dominates the explanation" | MEDIUM | Prompt ordering: knowledge file content → problem statement → answer → board-section instruction |
| **Preserve user's original phrasing** during normalization | Obsidian/RemNote AI plugins typically *rewrite* user prose; CPHO commits to "format only, keep原意" | MEDIUM | Explicit prompt constraint; diff displayed for user review |
| **Multimodal-direct knowledge ingestion** (image / docx / handwritten → multimodal LM, **not OCR**) | NotebookLM accepts images but treats them as opaque sources; CPHO treats handwritten model notes as first-class | MEDIUM | Leverages v1.0 OpenRouter multimodal pipeline already used for solve |
| **No explicit tag required from user when authoring** — skill infers from content | Obsidian forces `#tag`; Anki forces deck choice. Forcing tag choice on physics teachers writing about "高斯定理" is friction | MEDIUM | Normalization skill infers tags from controlled vocab during step 1 |

### Anti-features (decline these even if asked)

| Feature | Why Requested | Why Problematic | Alternative |
|---|---|---|---|
| **Graph visualization** of knowledge ↔ problems | Looks impressive (Obsidian graph view) | Already declared Out of Scope in v1.0; high effort, low decision value for a CLI tool | `/related` skill already answers "what's connected to what" on demand |
| **Vector/RAG over knowledge base** | "Industry standard" for AI knowledge retrieval | Conflicts with v1.0 controlled-vocab decision; harder to debug "why was this note retrieved?"; hallucinated relevance | Tag-overlap retrieval (exact, auditable) |
| **Built-in note editor** | Obsidian/Logseq have one | CPHO is a CLI tool; users have editors; maintaining one is a tar pit | Print path, let user `$EDITOR file` |
| **Auto-publish without review** | "Streamline the workflow" | Quality is the *core value*; un-reviewed AI normalization will drift the knowledge base | Mandatory two-step draft → review (designed-in) |
| **Versioning / history inside the tool** | "Track my edits" | Knowledge dir is on disk; git is right there | Recommend `git init` on the knowledge dir in docs |

---

## 2. Community Knowledge Libraries

### Prior art surveyed

| Product | Mechanism |
|---|---|
| **AnkiWeb shared decks** | Browse on web → click "Download" → `.apkg` file → import in app. Contribution = upload `.apkg` via account. Curation = popularity + star ratings |
| **Obsidian Hub / community vaults** | GitHub repos of markdown; users `git clone` into vault or copy folders manually |
| **awesome-* GitHub lists** | README with curated links; PRs to add entries; no in-app integration |
| **VSCode Marketplace / Cursor rules library** | Centralized registry + in-app install; high friction to publish |
| **Homebrew taps / nixpkgs** | Git-repo-as-package-registry; clone + install command |
| **dotfiles / chezmoi templates** | Just clone a public repo, run a setup command |

### Behaviors users expect (table stakes)

| Feature | Why Expected | Complexity | v1.0 Integration |
|---|---|---|---|
| **Browse what exists** before committing to download | Anki users browse the deck library before installing | LOW–MED | Either (a) point to a curated GitHub repo's README, or (b) `cpho kb browse` lists entries from a known index file in the repo |
| **One-command download to local KB** | Mirroring `brew install`, `pip install` | LOW | `cpho kb pull <pack>` → `git clone --depth=1` or `gh release download` into `knowledge/community/<pack>/` |
| **Local override wins** over community | Users edit community files and don't want next-pull to clobber | LOW | Community lives in a separate subdir (`knowledge/community/`); private in `knowledge/private/`; retrieval merges with private-wins |
| **Contribution path is documented & low-friction** | Anki's upload form vs awesome-list PR | LOW (docs) | GitHub PR workflow; CONTRIBUTING.md in the community repo |
| **Update / pull-latest** | `brew update`, `apt upgrade` analogy | LOW | `cpho kb update` → git pull on each installed pack |
| **Provenance visible in citations** | When Explain cites a knowledge file, user should see "this came from community pack X" | LOW | Path prefix already encodes it; cite full relative path |

### Differentiators

| Feature | Value Proposition | Complexity |
|---|---|---|
| **GitHub-repo-as-registry** (no separate platform) | Lowest infra cost; reuses developers' existing GitHub workflow; PR review = curation | LOW |
| **Tag-vocab-aligned packs** | Each community pack declares which controlled-vocab tags it covers → easy to evaluate "do I need this?" | LOW |
| **Per-pack enable/disable** | Users keep packs installed but disable for a session (e.g., focus on力学 only) | LOW–MED |
| **Pack manifest with author, license, version, tag coverage** | Anki shared decks rarely state license; CPHO ships an explicit manifest | LOW |

### Anti-features

| Feature | Why Requested | Why Problematic | Alternative |
|---|---|---|---|
| **In-app upload / publish** | "Anki has it" | Requires hosting, auth, moderation — none of which the project wants | GitHub PRs |
| **Ratings / stars / comments in-tool** | "Help me pick a good pack" | Social-platform tar pit | GitHub stars on the repo are sufficient |
| **Auto-pull-on-startup** | "Always up to date" | Network at startup = slow + breaks offline; surprise content changes mid-session | Explicit `cpho kb update` |
| **Single monolithic community repo** | Easier to find things | Hard to scale, no clear ownership per topic | Multiple packs (one repo per topic-area) with an index repo |

---

## 3. Per-Step Model Selection UI

### Prior art surveyed

| Product | Pattern |
|---|---|
| **LangChain / LangGraph UI / LangSmith** | DAG of nodes; each node has a `model` config field; per-node settings panel |
| **Flowise** | Drag-drop node editor; each "LLM node" has its own model dropdown; persisted as JSON |
| **n8n** (with AI nodes) | Workflow nodes; each AI node configures provider+model independently; node-level credentials |
| **Promptfoo** | YAML config; each test/provider combination explicit; CLI-first |
| **OpenAI Playground / Anthropic Workbench** | Single-model picker — not multi-step |
| **Cursor "models per feature"** | Settings page lists features (Chat / Cmd-K / Tab) with a model dropdown per feature — **closest analog to what CPHO needs** |
| **Continue.dev `config.json`** | Array of model entries with roles (`chat`, `edit`, `apply`, `autocomplete`) — file-based, declarative |

### Behaviors users expect (table stakes)

| Feature | Why Expected | Complexity | v1.0 Integration |
|---|---|---|---|
| **Visible list of steps** for each skill (DAG made legible) | Flowise/n8n made this normal; otherwise it's a black box | LOW | v1.0 skills are already deterministic DAGs — just need a `cpho skill show <name>` view |
| **Per-step model assignment** | Cursor, Continue, Flowise all do this | LOW–MED | New config layer: `skill_config.yml` mapping `(skill, step) → model_id` with fallback to default |
| **Persist user's choices** | No one wants to re-pick every session | LOW | YAML/JSON file in workspace; layered on top of `config.local.yml` |
| **Show the prompt file path** for each step (where the prompt template lives) | Promptfoo / Continue users expect transparency | LOW | v1.0 already stores prompts as files; just expose the path in the panel |
| **Defaults that work** out of the box | Users shouldn't *have* to configure | LOW | Ship sensible per-step defaults (e.g., cheap model for parsing, strong model for explanation) |
| **Reset to defaults** | Standard expectation | LOW | One command / single config key |

### Data model (recommended, derived from Continue.dev + Cursor patterns)

```yaml
# .cpho/skill_config.yml
skills:
  explain:
    steps:
      retrieve_knowledge: { model: "openrouter/google/gemini-2.0-flash" }
      generate_panel_thought_process: { model: "openrouter/anthropic/claude-3.5-sonnet" }
      generate_panel_answer_replacement: { model: "openrouter/anthropic/claude-3.5-sonnet" }
      generate_panel_alternative_method: { model: "openrouter/openai/gpt-4o" }
  solve:
    steps:
      parse: { model: "openrouter/google/gemini-2.0-flash" }
      critique: { model: "openrouter/anthropic/claude-3.5-sonnet" }
```

### Differentiators

| Feature | Value Proposition | Complexity |
|---|---|---|
| **In-REPL panel** (`/skill explain`) showing live status + each step's chosen model | Most prior art is web-UI; CPHO does it in a TUI | MEDIUM |
| **Cost / latency hints** next to each model option | n8n/Flowise don't surface this; very valuable for cost-conscious teachers | MEDIUM (depends on provider catalog data) |
| **"Why this step uses which model" rationale shown** | Pedagogical — teaches users when to upgrade a step's model | LOW (just doc strings) |

### Anti-features

| Feature | Why Requested | Why Problematic | Alternative |
|---|---|---|---|
| **Visual DAG editor** | "Like n8n / Flowise" | Out of scope (CLI only); skills are code, not user-edited workflows | Static `cpho skill show` rendering |
| **Per-call model override at the prompt** | "Just let me pick for this one call" | Surface area explodes; breaks reproducibility | Edit config, re-run — config is fast to edit |
| **AI-recommended model per step** | "Pick the best for me" | Vendors disagree, benchmarks lie | Document tradeoffs, let user choose |

---

## 4. Live Model List Discovery

### Prior art surveyed

| Product | Strategy |
|---|---|
| **LiteLLM proxy** | Hardcoded provider→model mapping in code; updated per release; `litellm.model_list` endpoint exposes it |
| **Open WebUI** | Calls each connected provider's "list models" endpoint at startup + manual refresh; caches in DB |
| **LM Studio** | Local model registry (downloaded GGUF files); listing is filesystem-driven |
| **Cursor / Continue** | Curated provider catalogs; periodic app updates ship new model IDs |
| **OpenRouter** | Exposes `GET /api/v1/models` returning live catalog (id, context length, pricing, modality flags) — **canonical case for live discovery** |
| **Google AI Studio** | `models.list` via Generative Language API |
| **Anthropic / OpenAI** | `GET /v1/models` standard endpoints |

(HIGH confidence on OpenRouter `/models` endpoint existence and shape from training data; MEDIUM on exact pricing field names.)

### Behaviors users expect (table stakes)

| Feature | Why Expected | Complexity | v1.0 Integration |
|---|---|---|---|
| **Live fetch from provider** when user opens the model picker | Open WebUI normalized this | LOW–MED | New module per provider: `providers/openrouter.py::list_models()`, `providers/google.py::list_models()` |
| **Cache with TTL** (default ~24h) so REPL is fast | Open WebUI caches; users hate startup latency | LOW | Cache file at `~/.cpho/cache/models_<provider>.json` with timestamp |
| **Manual refresh** command | Open WebUI has a refresh button | LOW | `cpho models refresh [--provider <p>]` |
| **Searchable picker** in REPL | Long lists are useless without search; `fzf`-style is the norm | LOW | `prompt_toolkit` already supports completer + fuzzy match |
| **Show modality / context-length / pricing** in the picker | OpenRouter exposes it; users want it | LOW | Surface fields from the catalog response |
| **Graceful offline mode** | API down ≠ tool broken | LOW | Fall back to last cached catalog, surface "stale since X" |

### Differentiators

| Feature | Value Proposition | Complexity |
|---|---|---|
| **Filter by capability** (multimodal? supports image input? long-context?) | Critical for CPHO since other-skill input strategy depends on multimodal support | LOW (providers expose flags) |
| **Auto-detect when chosen model lacks needed capability** and suggest swap | Avoids cryptic API errors mid-skill | MEDIUM |
| **Multi-provider unified picker** (OpenRouter + Google AI Studio + …) | Single search box across all connected providers | MEDIUM |

### Anti-features

| Feature | Why Requested | Why Problematic | Alternative |
|---|---|---|---|
| **Hardcoded model list shipped in releases** | Simple to implement | The whole reason users said "live, not hardcoded"; goes stale instantly | Live fetch + cache (designed-in) |
| **Auto-fetch on every command** | "Always fresh" | Slow, hits rate limits | TTL cache + manual refresh |
| **Scrape vendor websites** (vs API) | "Get docs/pricing too" | Brittle; APIs exist | Use official `/models` APIs only |
| **Sync provider catalogs to a CPHO-hosted registry** | "Faster" | Adds infrastructure; defeats "live from official source" | Direct provider calls |

---

## 5. Explain by Panel Selection (vs Tone)

### Prior art surveyed

| Product | Pattern |
|---|---|
| **Khan Academy / Khanmigo** | "Explain", "Give me a hint", "Quiz me" as discrete modes — **mode-as-action**, not tone |
| **Photomath / Mathpix Solver** | "Step-by-step" vs "Conceptual" toggles |
| **Brilliant.org** | Guided lessons with "alt explanation" / "another way to think about it" buttons |
| **ChatGPT custom GPTs for tutoring** | Often template prompts: "Explain the intuition", "Show me a different method", "Fill in the missing steps" — exactly CPHO's three panels |
| **Wolfram\|Alpha "Step-by-step solution"** | Has discrete view modes: outline / detailed / hints |
| **Cursor "Explain" vs "Fix" vs "Refactor"** | Mode = intent, not tone — closest software analog |

**Finding:** Mode-as-board-section (not tone) is the dominant pattern in *educational* AI. The v1.0 "Tone" design was an outlier vs the field. The v1.1 redesign (思路描述 / 标答替换 / 其他方法) aligns CPHO with the educational-AI mainstream. (MEDIUM confidence — based on training data, not live verification.)

### Behaviors users expect (table stakes)

| Feature | Why Expected | Complexity | v1.0 Integration |
|---|---|---|---|
| **Pick which panel(s)** to generate, not all-or-nothing | Khan/Brilliant let users pick the lens | LOW | Replace tone arg with `--panels` multi-select in CLI / checkbox in REPL |
| **Each panel has a clear, single purpose** | Mixing concerns ("explain *and* give alt method") confuses LMs and users | LOW | Three separate prompts, one per panel |
| **Output is structured & labeled** by panel | Users scan, don't read | LOW | Markdown headers per panel |
| **Knowledge files consumed first** (across all panels) | Required by project doc; matches NotebookLM expectation | MEDIUM | Retrieval step runs once before panels; result piped into each panel's prompt |
| **Source citations** in output | NotebookLM normalized this | LOW | Cite knowledge files + (optionally) the standard-answer reference |
| **Re-run a single panel** without redoing others | Users iterate on one section | LOW–MED | Per-panel cache or explicit `--only-panel` |

### Differentiators

| Feature | Value Proposition | Complexity |
|---|---|---|
| **"标答替换" as a first-class panel** | Unique to physics-olympiad pedagogy — "the answer skipped steps, fill them in" is the most-requested teacher need; nobody else has this exact panel | MEDIUM (depends on quality of step-gap detection) |
| **"其他方法" panel explicitly seeks methodological alternatives** | Most AI tutors give *one* explanation; this is a meta-pedagogy boost | MEDIUM |
| **Panel + knowledge-file fusion** | The combination — board sections + tag-driven knowledge retrieval + citations — is unique vs general tutors | MEDIUM (composition of pieces already designed) |
| **Per-panel model assignment** (from §3) | E.g., cheap model for 思路描述, strong for 其他方法 | LOW (falls out of §3 design) |

### Anti-features

| Feature | Why Requested | Why Problematic | Alternative |
|---|---|---|---|
| **Keep tone selector alongside panels** | "Don't break v1.0 users" | Doubles the prompt surface; the project doc explicitly says "去掉 tone" | Migration note in changelog; hard cut |
| **"All panels by default"** | "Just give me everything" | Expensive, noisy, defeats the point of panels | Default to a chosen subset (e.g., 思路描述 + 标答替换); 其他方法 opt-in |
| **Free-form "describe how you want it explained"** | "Maximum flexibility" | Hard to QA; defeats determinism; user can always edit the prompt template if they really want | Three fixed panels; users extend via the skill mechanism if needed |
| **Auto-pick panels based on problem type** | "Smart UX" | Adds an LM call upstream that often guesses wrong; users prefer to choose | Show recommendation, let user confirm |

---

## 6. Multimodal File Ingestion to LLM

### Prior art surveyed

| Product | Pattern |
|---|---|
| **NotebookLM** | Accepts PDF / GoogleDoc / TXT / images / YouTube → uploads to Gemini long-context. Images sometimes silently downsampled |
| **ChatGPT** | Drag-drop image / PDF / docx; PDF auto-extracted (text) or treated as vision (scanned). Docx → text extraction |
| **Claude.ai** | PDF native (vision + text); image native; docx via internal extraction |
| **OpenRouter Universal PDF Support** | Already used in v1.0 for solve; uniform interface across vision-capable models |
| **LM Studio / Ollama** | Local; only image input if model supports it; docx not supported natively |

### Behaviors users expect (table stakes)

| Feature | Why Expected | Complexity | v1.0 Integration |
|---|---|---|---|
| **Accept image / PDF / docx** | ChatGPT/Claude/NotebookLM all do | MEDIUM | v1.0 already handles PDF + image via OpenRouter; docx is new |
| **Use multimodal directly** (no OCR pre-step) when model supports it | The whole point of vision-capable LMs | LOW–MED | v1.0 multimodal solve pipeline extends to knowledge ingestion |
| **OCR fallback** when model lacks vision | Project doc explicitly requires this | MEDIUM | Existing RapidOCR pipeline; selector decides path based on §4 capability metadata |
| **Clear error when file type is unsupported** | Project doc requires "改哪里" error messages | LOW | Per-type handler with explicit "this needs a multimodal model — switch to …" message |
| **Size / page limits surfaced upfront** | Users hate "uploaded 200 pages, then it failed" | LOW | Pre-check page count / file size, warn before send |
| **Preserve original file** alongside any extraction | NotebookLM keeps source visible | LOW | Knowledge dir keeps original; extraction is sidecar |

### Known failure modes (from prior-art reports — MEDIUM confidence)

| Failure | Typical cause | Mitigation for CPHO |
|---|---|---|
| Handwriting misread | Vision model weak on dense math handwriting | Allow user to flag a file as "handwriting-heavy" → route to known-best vision model |
| Docx with embedded equations lost | python-docx loses MathML / OMML | Convert docx → PDF via LibreOffice headless, then route as PDF; document this fallback |
| Mixed-language docs (中英混排) | Some vision models drop Chinese | Choose Gemini / Claude variants known good on Chinese; surface in capability metadata |
| Silent image downscaling | Provider downsamples; fine detail lost | Pre-warn when image dimensions exceed provider's known limit |
| Token-limit overrun on large PDFs | PDFs explode token counts when rasterized | Page-range option; warn at threshold |
| Provider rejects unsupported MIME | Mis-routed via §4 capability check | Capability check before request, not retry-on-fail |
| OCR fallback produces garbage on diagrams | OCR can't read figures | When fallback engages, mark output "diagrams not captured" rather than pretending |

### Differentiators

| Feature | Value Proposition | Complexity |
|---|---|---|
| **Capability-aware routing** (§4 metadata → choose multimodal vs OCR per call) | Most tools have one path; CPHO chooses per request | MEDIUM |
| **Honest extraction-quality signaling** | Output tells user "this was OCR-fallback, expect figure gaps" rather than hiding the path used | LOW |
| **Knowledge-file ingestion uses the same pipeline as problem ingestion** | One pipeline, two callers — less code, more consistent behavior | LOW (already implied by architecture) |

### Anti-features

| Feature | Why Requested | Why Problematic | Alternative |
|---|---|---|---|
| **OCR everything for "consistency"** | Single code path simpler | Loses information that multimodal models would capture (diagrams, layout, handwriting context) | Multimodal-first, OCR-fallback (designed-in) |
| **Auto-convert everything to markdown before send** | "Normalize inputs" | Defeats vision; lossy for diagrams | Send native PDF/image to multimodal; convert only for OCR fallback |
| **Render docx ourselves with python-docx** | Pure-python, no external deps | Loses equations + layout | LibreOffice headless → PDF (already common pattern) |
| **Streaming partial extractions** while upload still running | "Feels faster" | Inconsistent state, harder error recovery | Atomic per-file ingestion with progress display (v1.0 already has progress) |

---

## Feature Dependencies

```
Live Model Catalog (§4)
    └──enables──> Per-Step Model Selection UI (§3)
                       └──enables──> Per-panel model assignment (§5)

Knowledge Base files-on-disk (§1)
    ├──requires──> v1.0 controlled-vocab tag index (already shipped)
    ├──enables──> Knowledge-first Explain panels (§5)
    └──enables──> Community Library pull (§2)
                       └──requires──> Knowledge Base dir layout (§1)

Multimodal Ingestion Pipeline (§6)
    ├──requires──> Capability metadata from Live Catalog (§4)
    ├──enables──> Knowledge ingestion of image/docx (§1)
    └──reuses────> v1.0 OpenRouter multimodal solve pipeline

Explain v2 Panels (§5)
    ├──requires──> Knowledge Base retrieval (§1)
    ├──benefits-from──> Per-step model selection (§3)
    └──replaces──> v1.0 Explain Tone design (hard cut)
```

### Dependency notes

- **§3 ← §4:** A per-step model UI is useless without a live, accurate model list. §4 must land in or before the same phase as §3.
- **§5 ← §1:** "Knowledge file as first priority" is meaningless without the KB. §1 must land before §5 ships.
- **§2 ← §1:** Community library is "more knowledge files via git"; layout must be stable first.
- **§6 ⇄ §4:** Multimodal routing depends on capability flags from §4; §4's "filter by capability" is more useful with §6 in place. They benefit from being adjacent in the roadmap.
- **§5 replaces v1.0 Tone:** Hard cut. The project doc explicitly says "不要妥协，不要想在现有架构下凑合 / jump out of the box."

---

## MVP Definition for v1.1

### Launch With (v1.1 must-have)

- [ ] **§1 Knowledge Base — file layout + tag join + draft/review skill** —核心新功能; everything else builds on it
- [ ] **§5 Explain v2 (3 panels, knowledge-first, with citations)** — promised hard cut; user expectation is set
- [ ] **§6 Multimodal ingestion routing (with capability check + OCR fallback)** — required to make §1 ingestion work for image/docx knowledge files
- [ ] **§4 Live model catalog (OpenRouter + one more provider, with TTL cache)** — required for §3 and §6 capability routing
- [ ] **§3 Per-step model selection (config-file driven, REPL panel viewer)** — promised in project doc

### Add After Validation (v1.1.x)

- [ ] **§2 Community library (browse + pull + update)** — high-value but works fine if shipped slightly later than §1; community content takes time to seed anyway
- [ ] **§4 advanced: multi-provider unified picker, capability filters in UI**
- [ ] **§5 advanced: per-panel re-run cache, recommendation hints**

### Future Consideration (v2+)

- [ ] **Cost/latency rollup dashboard across skills** — needs §3+§4 mature first
- [ ] **AI-suggested knowledge-note generation from clusters of solved problems** — needs §1 + KB at scale
- [ ] **Cross-pack conflict resolution UI for community library** — only matters once many packs exist

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---|---|---|---|
| §1 KB core (files + tags + retrieval) | HIGH | MEDIUM | **P1** |
| §1 KB normalization skill (draft→review) | HIGH | MEDIUM | **P1** |
| §1 Multimodal knowledge ingestion | HIGH | MEDIUM (rides on §6) | **P1** |
| §2 Community library pull/update | MEDIUM | LOW | **P2** |
| §2 Browse-in-REPL | LOW–MED | LOW | P2 |
| §2 In-app upload/publish | LOW | HIGH | **P3 (anti)** |
| §3 Skill panel viewer (`cpho skill show`) | MEDIUM | LOW | **P1** |
| §3 Per-step model config + persistence | HIGH | MEDIUM | **P1** |
| §3 Cost/latency hints in picker | MEDIUM | MEDIUM | P2 |
| §4 Live fetch + cache (OpenRouter) | HIGH | LOW–MED | **P1** |
| §4 Multi-provider unified picker | MEDIUM | MEDIUM | P2 |
| §4 Capability filtering | HIGH (for §6) | LOW | **P1** |
| §5 Three panels + selection | HIGH | MEDIUM | **P1** |
| §5 Knowledge-first prompt ordering + citations | HIGH | MEDIUM | **P1** |
| §5 Per-panel re-run cache | MEDIUM | MEDIUM | P2 |
| §6 Multimodal-first routing | HIGH | MEDIUM | **P1** |
| §6 OCR fallback path | HIGH | MEDIUM (mostly v1.0 reuse) | **P1** |
| §6 docx → PDF (LibreOffice) | MEDIUM | LOW–MED | **P2** |
| §6 Per-call capability mismatch detection | MEDIUM | LOW | **P1** (cheap; prevents support load) |

---

## Competitor Feature Analysis

| Feature | Obsidian + AI plugins | NotebookLM | Anki (shared decks) | Cursor / Continue | **CPHO v1.1 approach** |
|---|---|---|---|---|---|
| KB as files | ✓ markdown | ✗ opaque sources | ✗ DB-backed | n/a | ✓ markdown + image + docx on disk |
| Tag-driven retrieval | partial (manual) | ✗ (embedding) | ✓ tag filters | ✗ (embedding) | ✓ controlled-vocab tag join (deterministic) |
| Knowledge-before-generation | plugin-dependent | ✓ source-grounded | n/a | ✓ codebase context | ✓ knowledge file as first-priority context |
| Draft → review workflow | manual | ✗ | community curation only | n/a | ✓ explicit two-step skill |
| Community library | plugin gallery | ✗ | ✓ AnkiWeb upload | ✓ rule packs | ✓ GitHub-repo-as-registry |
| Per-step model selection | n/a | ✗ (single) | n/a | ✓ per-feature | ✓ per-skill-step config |
| Live model catalog | n/a | ✗ | n/a | curated catalog | ✓ live fetch + TTL cache |
| Explain modes (panels) | n/a | single | n/a | Explain/Fix/Refactor | ✓ 思路 / 标答替换 / 其他方法 |
| Multimodal ingestion | plugin-dependent | ✓ (PDF/image/YT) | ✗ | ✓ images | ✓ image/docx/PDF, capability-routed |
| Source citations in output | plugin-dependent | ✓ (signature feature) | n/a | partial | ✓ knowledge-file path + standard-answer cite |

---

## Risks / Open Questions for Roadmap

- **§1 + §5 tight coupling:** Designing the knowledge-file → Explain prompt-injection contract needs to happen *before* either ships independently. Recommend a small joint design spike at phase entry.
- **§6 docx route:** LibreOffice headless adds a non-Python system dep, which conflicts mildly with the "Python-only stack" constraint. May need a pure-Python fallback (mammoth → markdown, lossy) for environments without LibreOffice. Flag for **PITFALLS.md**.
- **§4 live fetch privacy/rate-limit:** Hitting OpenRouter `/models` from every user's machine is fine; hitting Google AI Studio's `models.list` requires auth — must use the user's API key, not a project-shared key. Flag for **PITFALLS.md**.
- **§2 governance:** Who reviews community PRs? Without a maintainer commitment, the community repo becomes a stale pile. Recommend deferring §2's community-repo creation until v1.1 main features ship.
- **v1.0 Explain Tone → §5 migration:** Existing users have Tone-based outputs in their workspaces. Need a migration note + tone→panel suggested mapping in changelog.

---

## Sources

Prior-art products referenced (training-data knowledge; not live-verified this session):

- Obsidian — obsidian.md
- Logseq — logseq.com
- Anki + AnkiWeb shared decks — ankiweb.net
- RemNote — remnote.com
- NotebookLM — notebooklm.google.com
- Cursor — cursor.com (per-feature model assignment in Settings)
- Continue.dev — continue.dev (`config.json` model roles)
- LangChain / LangGraph / LangSmith — langchain.com
- Flowise — flowiseai.com
- n8n — n8n.io (AI nodes)
- Promptfoo — promptfoo.dev
- LiteLLM — github.com/BerriAI/litellm
- Open WebUI — openwebui.com
- LM Studio — lmstudio.ai
- OpenRouter `/api/v1/models` — openrouter.ai/docs
- Google AI Studio Generative Language API `models.list` — ai.google.dev
- Khan Academy Khanmigo, Photomath, Brilliant, Wolfram Alpha — mode-based educational AI patterns

**Confidence caveats:**
- HIGH: product existence, broad UX patterns, OpenRouter `/models` endpoint existence
- MEDIUM: specific UI details, exact field names in catalog APIs, failure-mode frequency claims
- LOW: claims about how *common* a pattern is across the long tail of tutoring AIs (web verification unavailable this session)

Web search was unavailable during this research session (search tool returned model-availability errors). Recommend a follow-up verification pass before locking the roadmap on:
1. Exact shape of OpenRouter and Google AI Studio model-listing responses (for §4 implementation)
2. Current best-practice for docx→PDF in headless Python environments (for §6)
3. Anki shared-decks contribution UX details (for §2 — to confirm GitHub-repo-as-registry is the right choice vs an Anki-style upload portal)

---

*Feature research for: CPHO CLI v1.1 — Knowledge Base + Explain v2 + Model Panel + Multimodal Ingestion*
*Researched: 2026-05-27*
