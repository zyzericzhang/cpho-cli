# Feature Landscape

**Domain:** Physics Olympiad AI Analysis CLI Tool
**Researched:** 2026-05-20
**Analogous Products Surveyed:** Obsidian, Anki, Aider, Open Interpreter, PhysicsMinions, P1, 质心在线, NeoPi

## Feature Taxonomy: How to Read This

Features are organized into three strategic tiers based on competitive landscape analysis across knowledge management, AI tutoring, spaced repetition, and CLI developer tooling domains.

| Tier | Definition | Without It |
|------|-----------|------------|
| **Table Stakes** | The baseline. Users expect these and will abandon the product without them. | Product feels broken or incomplete. |
| **Differentiators** | The reason someone chooses CPHO CLI over alternatives. Not expected but highly valued when present. | Product is generic and undifferentiated. |
| **Anti-Features** | Features that would actively harm the product by adding complexity, violating constraints, or competing on the wrong axis. | Product stays focused and aligned. |

---

## Table Stakes

Features users expect. Missing = product feels incomplete. These are the non-negotiable baseline for any physics analysis CLI tool.

### 1. Problem Folder as Workspace (Zero Import Ceremony)

| Attribute | Detail |
|-----------|--------|
| **What it is** | Point the CLI at a folder of PDFs/images. The tool auto-discovers and indexes everything without a multi-step import flow. |
| **Why expected** | Obsidian established the "folder = vault" norm. Aider established "point at files, start working." Physics teachers have existing folder structures of scanned exams and handouts — they will reject anything that demands reorganization or explicit import. |
| **Complexity** | Medium |
| **Dependencies** | Tag-based indexing system (see Feature 2) |
| **Source** | Obsidian's local-first vault model; Aider's `aider <file1> <file2>` direct-add pattern |

### 2. Tag-Based Problem Indexing

| Attribute | Detail |
|-----------|--------|
| **What it is** | Every problem parsed from a folder gets auto-tagged and stored in a local JSON/JSONL index. Tags cover: physics model (e.g., "variable-mass system"), insight type (e.g., "symmetry exploitation"), difficulty (1-10), mathematical technique (e.g., "approximation"), cognitive skill (e.g., "deduction"). All subsequent operations query the index rather than re-reading raw files. |
| **Why expected** | Physics competition taxonomies are well-established (PhysicsEval dataset: 19 categories, difficulty tiers, soft labels; IPhO syllabus hierarchy; USAPhO topic taxonomy). Teachers already mentally organize problems this way. Without tagging, retrieval is ad-hoc file grepping — unacceptable for serious users. |
| **Complexity** | High |
| **Dependencies** | LLM-based tag generation |
| **Source** | PhysicsEval dataset tagging schema (category, difficulty, steps, soft_labels); Obsidian Dataview's SQL-like filtering model; Anki's tag-based cross-deck filtering |

### 3. LLM-Backed Analysis Output

| Attribute | Detail |
|-----------|--------|
| **What it is** | AI-generated analysis of physics problems. Minimum: identifies difficulty/insight points, verifies answer correctness against provided answer key, generates structured output (not freeform chat). |
| **Why expected** | P1, PhysicsMinions, and Physics Supernova have all demonstrated that LLMs can produce gold-medal-level physics reasoning. Users of CPHO CLI come specifically for AI analysis — if the output quality is poor, nothing else matters. |
| **Complexity** | High |
| **Dependencies** | OpenRouter API key management (Feature 4), anti-hallucination grounding against source text |
| **Source** | P1 model RL training on 5,065 Olympiad problems; PhysicsMinions multi-agent verification architecture; research showing Socratic/non-answer-giving behavior is critical for pedagogy |

### 4. API Key Management

| Attribute | Detail |
|-----------|--------|
| **What it is** | Users provide their own OpenRouter API key via environment variable (`OPENROUTER_API_KEY`) or local config file. Tool reads it on startup. Never prompts for inline entry (security). Clear error message if missing. |
| **Why expected** | Open Interpreter and Aider both standardized the pattern: user brings their own key, no baked-in API costs, no upload of user data to a service. In the physics competition community, many users are in Chinese schools with restricted internet — they need control over their API endpoint. |
| **Complexity** | Low |
| **Dependencies** | None |
| **Source** | Open Interpreter's `--api_key`, `--api_base` pattern; Aider's multi-provider model support |

### 5. Answer-Key Grounded Verification

| Attribute | Detail |
|-----------|--------|
| **What it is** | Every analysis mode cross-references the provided answer key. If the LLM produces a solution, it is checked against the official answer. Discrepancies are flagged explicitly. The tool refuses to hallucinate when no answer key is provided for verification-critical modes. |
| **Why expected** | Physics competition training demands correctness. The Stanford Socratic tutor research (2025) emphasizes that AI tutors must ground responses in teacher-provided documents and course-specific knowledge files. Korean physics educators (2025) identified hallucination as the #1 trust barrier. |
| **Complexity** | Medium |
| **Dependencies** | LLM-based answer comparison logic |
| **Source** | RAG-based Socratic tutor design (Tufino, 2025); PhysicsMinions dual-stage verifier (Physics-Verifier + General-Verifier) |

### 6. CLI-First Interaction

| Attribute | Detail |
|-----------|--------|
| **What it is** | All interaction happens via terminal. Slash-commands for mode switching. REPL-style chat for quiz mode. Clear, structured ASCII output (no raw JSON dumps). Progress indicators for long-running analyses. |
| **Why expected** | The project constraints explicitly rule out GUI/TUI/Web. Aider proved that CLI-native AI tools can have excellent UX through slash-commands, git-integrated safety, and iterative workflows. CPHO CLI competes on analysis quality, not interface chrome. |
| **Complexity** | Low (architecture) / Medium (UX polish) |
| **Dependencies** | None |
| **Source** | Aider's slash-command model (`/add`, `/drop`, `/undo`, `/diff`); Open Interpreter's terminal chat interface |

### 7. Input Format Support (PDF + Images)

| Attribute | Detail |
|-----------|--------|
| **What it is** | Parse physics problems from PDF files and common image formats (PNG, JPEG). OCR through abstract interface — implementation swappable. Handle multi-page PDFs with mixed text and diagrams. |
| **Why expected** | Real physics competition materials are overwhelmingly PDF (scanned exam papers) or photographs of handwritten work. A tool that can't read these is useless to physics teachers. The PhysicsMinions paper specifically highlights multi-modal support (text + diagrams + data figures) as essential for Olympiad problems. |
| **Complexity** | High (OCR quality is the hard part) |
| **Dependencies** | OCR abstraction layer |
| **Source** | PhysicsMinions Visual Studio (diagram parsing); IPhO multi-modal problem format (text + illustration + variable figures + data figures) |

---

## Differentiators

Features that set CPHO CLI apart from generic AI analysis tools. Not expected, but highly valued by the target audience of serious physics teachers and Olympiad coaches.

### 8. Multi-Mode Skill System

| Attribute | Detail |
|-----------|--------|
| **What it is** | Four built-in analysis modes, each as a discrete "skill": (1) **Quiz Mode** — Socratic interrogation: check answer, extract insights, ask probing questions via REPL; (2) **Explanation Mode** — step-by-step derivation with "why" for every transition; (3) **Comparative Mode** — select 2+ problems, find shared models/reasoning patterns, surface tag-linked related problems; (4) **Exam Generation** — assemble tagged problems into a print-ready problem sheet + answer sheet pair. |
| **Why differentiating** | No existing tool combines all four modes. 质心在线 provides a problem bank and mock exams but no AI-driven comparative analysis. P1/PhysicsMinions solve problems autonomously but lack teacher-facing explanation and exam assembly workflows. The quiz mode's Socratic approach addresses the core finding from 2024-2025 physics education research: teachers need AI that guides thinking, not just provides answers. |
| **Complexity** | High |
| **Dependencies** | Tag-based indexing (Feature 2), DAG pipeline (Feature 12), answer verification (Feature 5) |
| **Source** | Socratic AI tutor research (Tufino 2025, Gobert 2025); 质心在线 mock exam + problem bank model; Anki's active recall review flow |

### 9. Three-Tier Extensible Skill/Plugin System

| Attribute | Detail |
|-----------|--------|
| **What it is** | Users create custom analysis skills at three complexity levels: **Tier 1 (Prompt-only)** — a text file defining the system prompt and output schema, no code; **Tier 2 (YAML config)** — declarative pipeline config with input/output mapping, parameter binding, and conditional branching; **Tier 3 (Python script)** — full programmatic control via a `SkillPlugin` base class with lifecycle hooks (`initialize`, `analyze`, `post_process`). Skills are installed by dropping files into a `skills/` directory. |
| **Why differentiating** | Obsidian proved that a 1000+ community plugin ecosystem creates network effects and stickiness. Obsidian's plugin API (JavaScript, manifest.json, event bus) is the gold standard. CPHO CLI adapts this to a physics-specific domain with lower barrier to entry (prompt-only tier = anyone can contribute). No existing physics tool has an extensible analysis pipeline system. |
| **Complexity** | High (the framework itself) / Low (Tier 1 for users) |
| **Dependencies** | Skill loader infrastructure, lifecycle management, configuration injection |
| **Source** | Obsidian's plugin architecture (manifest.json, event bus, community marketplace); Claude Code's plugin/skills system (plugin.toml, install-enable-configure separation); Aider's Architect mode (two-step reasoning → execution) |

### 10. Skill Creator (Prompt-to-Skill Generator)

| Attribute | Detail |
|-----------|--------|
| **What it is** | User describes an analysis workflow in natural language (e.g., "For each problem, identify common student misconceptions and generate a 5-minute mini-lecture outline"). The Skill Creator generates a complete skill package — Tier 2 YAML config + refined prompt pipeline — ready to use. |
| **Why differentiating** | Lowers the bar from "write code" to "describe your teaching workflow." Physics coaches have domain expertise but limited programming time. This feature translates pedagogical intuition into reusable tooling. No analogous product in the education space offers this. |
| **Complexity** | Medium (meta-prompting over the skill config schema) |
| **Dependencies** | Skill system (Feature 9) must exist first |
| **Source** | Open Interpreter's natural-language-to-code execution model; Obsidian Claude PKM's prompt-chain automation |

### 11. Tag-Based Knowledge Graph Linking

| Attribute | Detail |
|-----------|--------|
| **What it is** | Beyond flat tag indexing, problems are linked by shared tags into a traversable knowledge graph. A problem tagged "energy conservation + rotating frame" is linked to all other problems with overlapping tags. Comparative mode uses this graph for "similar problems" suggestions. Explanation mode cites related problems as reinforcement. |
| **Why differentiating** | Obsidian's bidirectional links and Graph View are the killer knowledge management feature. 质心在线's problem bank is flat (filter by topic/difficulty only). A linked problem graph enables the kind of cross-domain reasoning that IPhO gold medalists use — recognizing that a thermodynamics problem is structurally identical to a mechanics problem. |
| **Complexity** | Medium (graph construction is algorithmic; the value comes from tag quality) |
| **Dependencies** | Tag-based indexing (Feature 2) with high-quality tag generation |
| **Source** | Obsidian's bidirectional linking + Graph View; Obsidian Dataview's SQL-like query over metadata; IPhO cross-domain problem style (mechanics + E&M combinations) |

### 12. DAG Step-by-Step Pipeline for Long Problems

| Attribute | Detail |
|-----------|--------|
| **What it is** | Long Olympiad problems (multiple sub-questions, 30+ minute solve time) are split into steps. Each step gets only the context it needs (problem statement + relevant previous results). The LLM processes one step at a time rather than tackling the whole problem in one prompt. Results flow through a directed acyclic graph where Step 3 depends on Step 2 but not Step 4. |
| **Why differentiating** | A key finding from the PhysicsMinions paper and the P1 research: LLM attention dilution on long problems causes skipped intermediate reasoning. By narrowing context per step, the model stays focused. This mirrors how human Olympiad contestants work — sub-question at a time. No existing educational AI tool implements context-isolated step pipelines. |
| **Complexity** | High |
| **Dependencies** | Problem structure parsing (identifying sub-question boundaries) |
| **Source** | PhysicsMinions multi-agent architecture (Visual Studio → Logic Studio → Review Studio); Aider's surgical precision philosophy (small, focused changes); cognitive load theory in physics education research |

### 13. PDF Exam Assembly from Tagged Problems

| Attribute | Detail |
|-----------|--------|
| **What it is** | User queries the tag index (e.g., "mechanics problems, difficulty 5-7, involving energy conservation"). The tool assembles matching problems into a PDF problem sheet and a separate PDF answer sheet. Uses image stitching from original PDFs — not LaTeX re-rendering. |
| **Why differentiating** | Physics teachers spend hours assembling practice exams from disparate PDFs. 质心在线 provides premade mock exams but no custom assembly from the user's own problem collection. The image-stitching approach (vs LaTeX rendering) is a pragmatic tradeoff that respects the project constraint of avoiding heavy rendering infrastructure. |
| **Complexity** | Medium |
| **Dependencies** | Tag-based indexing (Feature 2), PDF manipulation libraries |
| **Source** | 质心在线 mock exam feature; Queryfy's PDF export from curated content; project constraints (no LaTeX rendering, use image stitching) |

### 14. Predictable DAG Pipelines (Not Autonomous Agents)

| Attribute | Detail |
|-----------|--------|
| **What it is** | Every analysis mode follows a deterministic step sequence. The LLM is called at specific pipeline nodes with specific prompts. The tool never asks the LLM to "figure out what to do next." Pipeline traces are logged for debugging. |
| **Why differentiating** | This is an intentional anti-Agent stance. Physics competition coaches need reproducibility — if they run the same problem through Explanation Mode twice, they expect the same structure. Autonomous ReAct agents (the standard in AI coding tools) are unpredictable and skip steps on long problems. The project Key Decisions doc explicitly calls this out. |
| **Complexity** | Medium (pipeline orchestration) |
| **Dependencies** | Pipeline framework |
| **Source** | Project Key Decisions: "DAG 管线而非自主 Agent"; PhysicsMinions hard-coded workflow stages; research showing autonomous agents skip intermediate reasoning on long Olympiad problems |

### 15. Scaffolded Verification for Students

| Attribute | Detail |
|-----------|--------|
| **What it is** | In Quiz Mode, the system does not immediately reveal answers. It uses Socratic questioning: "What is conserved in this collision?" not "The answer is X because Y." When a student is stuck, it offers progressive hints (concept hint → method hint → equation hint) before revealing the solution. Optional mode flag to enforce this strictly. |
| **Why differentiating** | The 2024-2025 physics education research consensus is unambiguous: AI tutors must be Socratic, not answer-giving. NotebookLM as a Socratic physics tutor (Tufino, 2025) demonstrates this approach. The gap between "teachers want instant answers" and "students need guided discovery" is the key tension — CPHO CLI can serve both audiences by making the mode explicit and selectable. |
| **Complexity** | Medium |
| **Dependencies** | Quiz Mode (part of Feature 8) |
| **Source** | Tufino (2025) "NotebookLM as a Socratic physics tutor"; Gobert (2025) "AI as pedagogical guide not solution provider"; Korean physics educators study (2025) |

---

## Anti-Features

Features to explicitly NOT build. These are deliberate exclusions based on project constraints, competitive strategy, and physics domain realities.

### Anti-Feature 1: GUI / TUI / Web Interface

| Attribute | Detail |
|-----------|--------|
| **Why avoid** | Adds 6-12 months to v1 timeline. Competes on the wrong axis — teachers who want a polished UI already have 质心在线, Anki, or web-based platforms. CPHO CLI's advantage is power-user CLI workflows (like Aider vs Cursor). |
| **What to do instead** | Clean ASCII output, structured tables, color-coded results in terminal. REPL for interactive modes. |

### Anti-Feature 2: Database Storage (SQLite, PostgreSQL, etc.)

| Attribute | Detail |
|-----------|--------|
| **Why avoid** | Introduces schema migrations, query complexity, and operational burden. Physics teachers' problem collections are file-based by nature. A database adds friction to the "folder = workspace" model. |
| **What to do instead** | JSON/JSONL flat files in the problem folder. Git-friendly. Human-readable for debugging. Obsidian proved this model scales to thousands of notes. |

### Anti-Feature 3: Multi-User / Authentication / Login

| Attribute | Detail |
|-----------|--------|
| **Why avoid** | Local-first tool. No server to authenticate against. Adding auth would require a backend, user database, session management — all out of scope for v1 and antithetical to the local-first philosophy. |
| **What to do instead** | Nothing. A single-user local tool needs no identity system. |

### Anti-Feature 4: LaTeX Rendering Engine

| Attribute | Detail |
|-----------|--------|
| **Why avoid** | Physics problems contain complex formulas, diagrams, and mixed notation. Re-rendering existing problems in LaTeX requires parsing unstructured PDFs into structured math — a research-grade problem, not a v1 feature. |
| **What to do instead** | Image clipping/stitching from original PDFs for exam assembly. LaTeX rendering may make sense as a v2 feature once the core analysis quality is proven. |

### Anti-Feature 5: Autonomous ReAct-Style Agent

| Attribute | Detail |
|-----------|--------|
| **Why avoid** | LLM agents are unpredictable. On long Olympiad problems, they skip intermediate reasoning steps. Physics competition analysis is high-stakes (correctness matters); the analysis pipeline steps are known and deterministic. |
| **What to do instead** | DAG pipelines with explicit nodes and fixed prompt schedules. Each node does one thing, verified before proceeding. |

### Anti-Feature 6: Spaced Repetition Scheduling (SRS)

| Attribute | Detail |
|-----------|--------|
| **Why avoid** | Anki owns this space. Building an SRS engine (SM-2, FSRS) with scheduling, due-dates, and review intervals is a product unto itself. CPHO CLI's value is analysis depth, not memory scheduling. Adding SRS would split focus and delay the analysis pipeline work that is the core differentiator. |
| **What to do instead** | If a user wants spaced repetition, they can export problem data and import into Anki. Tag metadata makes this feasible. Consider as v3 integration. |

### Anti-Feature 7: Cloud Sync / Multi-Device

| Attribute | Detail |
|-----------|--------|
| **Why avoid** | Introduces server infrastructure, conflict resolution, and privacy concerns (uploading problem files). Violates the "local-first, API calls only" constraint. |
| **What to do instead** | Users manage sync themselves (rsync, git, Dropbox). The file-based index is sync-friendly by design. |

### Anti-Feature 8: Automated Problem Solving (Answer Generation Without Answer Key)

| Attribute | Detail |
|-----------|--------|
| **Why avoid** | The core value proposition is analysis quality grounded in provided answer keys. Generating answers from scratch without verification is unreliable for Olympiad-level physics (even P1 and PhysicsMinions, state-of-the-art systems, achieve only ~70-80% on IPhO problems). Shipping a feature that produces wrong answers damages trust irreparably. |
| **What to do instead** | Require answer keys for all analysis modes. Flag missing answer keys explicitly. If a mode can operate without one (e.g., initial problem exploration), label outputs "UNVERIFIED — no answer key provided." |

### Anti-Feature 9: Mobile Support

| Attribute | Detail |
|-----------|--------|
| **Why avoid** | CLI tool. Physics problem analysis requires reading PDFs and typing analysis commands — inherently desktop/terminal workflow. Adding mobile support (PWA, app) is a different product. |
| **What to do instead** | Optimize for terminal width, support piping to other tools, ensure output is readable when SSH'd from a tablet. |

---

## Feature Dependency Graph

```
Tag-Based Indexing (2)
    ├── Multi-Mode Skill System (8)
    │       ├── Quiz Mode (Socratic REPL)
    │       ├── Explanation Mode (step-by-step)
    │       ├── Comparative Mode ── requires ── Tag Knowledge Graph (11)
    │       └── Exam Generation (13)
    ├── DAG Pipeline (12)
    │       └── used by all Skill System modes
    └── Scaffolded Verification (15)
            └── part of Quiz Mode

Skill/Plugin System (9)
    └── Skill Creator (10) ── requires Skill System (9)

Problem Folder Workspace (1)
    └── Input Format Support (7)
            └── Tag-Based Indexing (2)

API Key Management (4)
    └── used by everything that calls LLM

Answer-Key Grounded Verification (5)
    └── used by all Skill System modes
```

---

## MVP Recommendation

Based on the research, the v1 MVP should ship these features:

**Phase 1: Core Pipeline (Must Ship First)**
1. **Problem Folder as Workspace** — the entry point; nothing else works without it
2. **Input Format Support (PDF + Images)** — hard prerequisite for any analysis
3. **API Key Management** — unblocks all LLM functionality
4. **CLI-First Interaction** — the interface everything else is delivered through

**Phase 2: The Engine**
5. **Tag-Based Problem Indexing** — unlocks retrieval, comparison, exam generation
6. **Answer-Key Grounded Verification** — quality guarantee for all analysis output
7. **DAG Step-by-Step Pipeline** — the execution model for all skills
8. **Predictable DAG Pipelines** — the architectural pattern (not autonomous)

**Phase 3: Skills + Ecosystem**
9. **Multi-Mode Skill System** — initially just Explanation Mode (highest value-to-complexity ratio)
10. **Scaffolded Verification** — ships with Quiz Mode
11. **Three-Tier Extensible Skill System** — unblocks community contributions
12. **Skill Creator** — lowers barrier to skill creation

**Phase 4: Knowledge Network**
13. **Tag-Based Knowledge Graph Linking** — powers Comparative Mode
14. **PDF Exam Assembly** — the "output artifact" differentiator for teachers

**Deferred to v2+:**
- Comparative Mode (requires knowledge graph maturity)
- Full Quiz Mode REPL (until Explanation Mode quality is proven)
- Spaced repetition integration (separate product decision)

### Ordering Rationale

1. **Pipeline first, skills second.** The DAG engine and indexing are prerequisites for every skill. Building skills before the engine means rewriting them later.
2. **Quality over breadth.** Ship Explanation Mode at high quality before adding Quiz and Comparative modes. Physics teachers will forgive missing features but not wrong answers.
3. **Plugin system as a v1 differentiator, not a v1 requirement.** The three-tier skill system and Skill Creator are CPHO CLI's strongest differentiator against existing tools. Ship it early enough to gather community skills, but only after the core pipeline proves the value hypothesis.

---

## Feature Complexity Reference

| Complexity | Definition | Example |
|-----------|------------|---------|
| **Low** | Copy established pattern, minimal unknowns | API Key Management, CLI interaction |
| **Medium** | Known domain, moderate integration work | Tag Knowledge Graph, PDF assembly, Skill Creator |
| **High** | Significant unknowns, quality-critical, or novel | OCR parsing, DAG pipeline, tag generation quality, 3-tier plugin framework |

---

## Sources

- PhysicsEval Dataset: `IUTVanguard/PhysicsEval` on Hugging Face — 19,609 annotated problems, 19 categories, difficulty + soft labels schema
- Obsidian Plugin Ecosystem: 1,000+ community plugins, Dataview query language, manifest.json-based plugin discovery
- Aider: Git-integrated CLI AI tool, slash-command UX, surgical edit philosophy — [GitHub](https://github.com/Aider-AI/aider)
- Open Interpreter: Local LLM execution, `exec()` function model, LiteLLM integration — [GitHub](https://github.com/OpenInterpreter/open-interpreter)
- PhysicsMinions: Coevolutionary multi-agent Olympiad solver, Visual-Logic-Review Studio pipeline — [arXiv:2509.24855](https://arxiv.org/abs/2509.24855)
- P1: RL-trained Olympiad physics model, 5,065 problem training set — [arXiv:2511.13612](https://arxiv.org/abs/2511.13612)
- Tufino (2025): "NotebookLM as a Socratic physics tutor" — [arXiv:2504.09720](https://arxiv.org/abs/2504.09720)
- Mohammadipour (2025): "Strategic Integration of AI Chatbots in Physics Teacher Preparation" — [arXiv:2507.14860](https://arxiv.org/abs/2507.14860)
- Gobert (2025): IPN presentation on AI-based teacher/student support in science education
- 质心在线 (ZhiXin Online): Chinese physics Olympiad training platform — problem bank, mock exams, live courses
- AEQG-MCQ-Distractors-Physics: LLM + Concept Map + RAG for question generation — [GitHub](https://github.com/nicyscaria/AEQG-MCQ-Distractors-Physics)
- Collection of Solved Problems in Physics (Charles University): Cognitive skill taxonomy — [physicstasks.eu](http://physicstasks.eu)
- Anki: SM-2/FSRS spaced repetition, notes/cards/templates model — [Wikipedia](https://en.wikipedia.org/wiki/Anki_(software))
