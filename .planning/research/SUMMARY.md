# Project Research Summary

**Project:** CPHO CLI
**Domain:** Physics Olympiad AI Analysis CLI Tool
**Researched:** 2026-05-20
**Confidence:** HIGH

## Executive Summary

CPHO CLI is a local-first command-line tool for physics competition coaches to run AI-driven structured analysis on problem folders (PDFs of exam questions paired with answer keys). It is best understood as a physics-specific Obsidian-like knowledge base where the folder IS the workspace, a JSONL tag index powers fast retrieval, and deterministic DAG pipelines -- not autonomous agents -- drive multi-step LLM analysis. The core value proposition is analysis quality: finding genuine difficulty points in problems, explaining the "why" behind every derivation step, and linking related problems through a tag-based knowledge graph.

The recommended approach, validated across multiple research domains, is Python 3.12 with a core-shell architecture. The `core/` package contains pure business logic with zero I/O dependencies, while `cli/` is a thin Typer shell. LLM calls flow through LiteLLM to OpenRouter (the same pattern used by Aider and Open Interpreter in production). The pipeline engine must be a custom lightweight DAG -- not LangChain, not LangGraph, not a production orchestrator -- because the domain requires deterministic step execution with pruned context per node, not agentic loops. OCR uses RapidOCR (ONNX Runtime, lightweight) with PaddleOCR as an optional high-accuracy fallback behind an abstract interface. The plugin system uses pluggy for hook semantics, not a custom decorator registry.

The primary risk is that analysis output quality is everything, and three failure modes can destroy it before anyone sees the tool's value: (1) hallucinated physics reasoning that erodes teacher trust, (2) OCR errors that silently corrupt inputs before the LLM even sees them, and (3) context window dilution on long problems that causes the model to skip the intermediate reasoning the product exists to provide. All three must be addressed in Phase 1 through answer-key grounding, OCR validation steps, and aggressive DAG-based problem decomposition. A secondary risk is building the skill/plugin ecosystem before proving the core analysis pipeline works on real physics problems -- the temptation is real, and the research is unambiguous: plugin systems designed before real usage patterns are known become liabilities, not assets.

## Key Findings

### Recommended Stack

Python 3.12 with a deliberately minimal dependency tree. The guiding principle is that best-in-class Python AI CLI tools (Aider, Open Interpreter) avoid heavy frameworks and compose small, focused libraries instead. Every dependency was chosen by verifying it is used in production by analogous projects.

**Core technologies:**
- **LiteLLM (1.85.x)** -- Unified LLM API for OpenRouter -- Proven by Aider and Open Interpreter in production. Supports 50+ providers, cost tracking, retries, fallbacks. No LangChain dependency.
- **Typer + prompt-toolkit + Rich** -- CLI framework, REPL input, terminal output -- Same combo used by Aider. Typer adds type-hint-driven DX on top of Click. prompt-toolkit powers the REPL. Rich renders LLM markdown output in terminal.
- **pluggy (1.6.0) + importlib.metadata** -- Hook-based plugin system + entry point discovery -- Born from pytest, battle-tested. Separates hook specs from implementations with tryfirst/trylast ordering.
- **Custom lightweight DAG + asyncio** -- Deterministic multi-step LLM pipeline -- Intentionally NOT LangChain/LangGraph (agentic loops conflict with deterministic requirement) and NOT Prefect/Dagster (production schedulers are overkill for in-process CLI sessions).
- **RapidOCR + RapidLaTeXOCR** -- Primary OCR (Chinese + formulas) -- ONNX Runtime backend, models <5MB, no PaddlePaddle dependency. PaddleOCR kept as optional high-accuracy fallback behind an abstract interface.
- **pikepdf + pypdf + pdf2image** -- PDF manipulation -- pikepdf (C++ backend, 15x faster than pure Python) for merging/splitting. pypdf for simple reads. pdf2image for OCR pipeline feeding.
- **pydantic-settings + PyYAML** -- Typed configuration + YAML parsing -- Config from env vars, .env, YAML with clear priority. Skill definitions and batch configs in YAML.
- **JSONL files** -- Tag index storage -- Append-only, grep-friendly, git-friendly, human-readable. One JSON object per line per problem. No database needed for v1 scale (<1000 problems).

Full details and alternatives considered in [STACK.md](STACK.md).

### Expected Features

**Table stakes (must ship -- product is incomplete without them):**
1. **Problem Folder as Workspace** -- Point CLI at folder, auto-discover PDFs/images. Zero import ceremony. Modeled on Obsidian's vault and Aider's direct-add patterns.
2. **Tag-Based Problem Indexing** -- Auto-tag each problem with physics model, insight type, difficulty, math technique, cognitive skill. Stored in JSONL. All subsequent operations query the index. Based on PhysicsEval dataset's 19-category tagging schema.
3. **LLM-Backed Analysis Output** -- Structured AI analysis: difficulty identification, insight extraction, answer verification. Not freeform chat.
4. **API Key Management** -- Users provide their own OpenRouter key via env var or config file. Never prompts for inline entry. Modeled on Aider/Open Interpreter patterns.
5. **Answer-Key Grounded Verification** -- Every analysis cross-references the provided answer key. Discrepancies flagged. Refuses to operate in verification-critical modes without an answer key.
6. **CLI-First Interaction** -- Terminal-only. Slash-commands, REPL for quiz mode, structured ASCII output. No GUI/TUI/Web.
7. **Input Format Support (PDF + Images)** -- Parse from PDF files and common image formats. OCR through swappable implementation.

**Differentiators (reason to choose CPHO CLI over alternatives):**
8. **Multi-Mode Skill System** -- Four built-in skills: Quiz (Socratic REPL), Explanation (step-by-step with "why"), Comparative (cross-problem analysis), Exam Generation (PDF assembly).
9. **Three-Tier Extensible Skill System** -- Tier 1: prompt-only (.md file). Tier 2: YAML declarative config. Tier 3: Python script (full control). Modeled on Obsidian's plugin architecture.
10. **Skill Creator** -- Describe a workflow in natural language, get a complete skill package. Lowers barrier from "write code" to "describe your teaching workflow."
11. **Tag-Based Knowledge Graph Linking** -- Problems linked by shared tags into traversable graph. Powers Comparative Mode and Explanation Mode reinforcement.
12. **DAG Step-by-Step Pipeline** -- Long Olympiad problems split into isolated-context steps. Each node gets only: base setup + specific sub-question + relevant prior results. Prevents attention dilution.
13. **PDF Exam Assembly from Tagged Problems** -- Query tags, assemble matching problems into problem sheet + answer sheet PDF via image stitching (not LaTeX re-rendering).
14. **Predictable DAG Pipelines (Not Autonomous Agents)** -- Deterministic step sequence. Same problem + same mode = same structure. Pipeline traces logged. Explicitly rejects agentic loops.
15. **Scaffolded Verification for Students** -- Socratic questioning in Quiz Mode. Progressive hints (concept -> method -> equation) before revealing solutions.

**Deferred to v2+:**
- Comparative Mode (requires knowledge graph maturity)
- Full Quiz Mode REPL (until Explanation Mode quality is proven)
- Spaced Repetition Scheduling (Anki owns this space; export compatibility instead)
- LaTeX Rendering Engine (image stitching is v1 pragmatism)
- TUI Dashboard (Textual-based, after CLI core is stable)

Full feature taxonomy, dependency graph, and competitive analysis in [FEATURES.md](FEATURES.md).

### Architecture Approach

Core-shell separation (Functional Core / Imperative Shell) with strict dependency rules. The `core/` package is a pure library -- zero I/O, zero framework dependencies, fully testable without mocks. The `cli/` layer is a thin shell that parses arguments, calls core functions, and formats output. The `adapters/` layer implements interfaces defined in core (OpenRouter client, OCR backends, file index). This separation is not over-engineering: the project spec explicitly calls for future online platform integration, and with this architecture the web layer becomes just another shell around the same core.

**Major components (in dependency order):**
1. **LLM Gateway (`core/llm/` + `adapters/openrouter_client.py`)** -- Abstract interface for LLM calls. Concrete OpenRouter implementation with 4-layer structured output defense (extra_body schema injection, Response Healing, provider routing, retry-with-degradation). Everything depends on this.
2. **Workspace Manager (`core/workspace/`)** -- Scans problem folders, discovers PDFs/images, associates answer files via naming heuristics. Produces `Problem` domain objects.
3. **OCR Adapter (`core/ocr/` + adapter implementations)** -- Abstract `OcrBackend` Protocol. RapidOCR is default, PaddleOCR is optional upgrade. Isolates OCR quality concerns from the rest of the system.
4. **Indexing Layer (`core/indexing/`)** -- Tag schema, JSONL writer/reader, tag query parser (AND/OR/NOT). Pre-compute pattern: expensive LLM tag generation runs once at index time, all subsequent queries are fast local reads.
5. **Pipeline Engine (`core/pipeline/`)** -- DAG definition, topological sort, parallel scheduling, blackboard (shared typed key-value store), context injector (Jinja2 template rendering). The most architecturally significant component. Step decomposition is mandatory for every sub-question.
6. **Skill System (`core/skills/`)** -- Three-tier architecture via polymorphism. Discovery via entry points (pip packages) + filesystem scanning (local skills). Produces `PipelineDefinition` objects consumed by the pipeline engine.
7. **Output Pipeline (`core/output/`)** -- PDF stitching (extract + concatenate pages from source PDFs), Markdown report generation, JSON result writing.

**Key patterns:**
- **Abstract Interface + Adapter Injection** -- Core defines Protocols, adapters implement them, CLI composes at startup (manual DI for this scale).
- **Blackboard Pattern** -- Shared typed key-value store for pipeline step context. Steps read prior results by key. Single source of truth for context injection.
- **Pre-Compute Metadata** -- Expensive LLM operations (tagging) run once. All queries hit the pre-computed index.
- **Producer-Consumer (Batch)** -- `cpho batch` uses thread pool for parallel problem processing with configurable concurrency.

Full component boundaries, data flows, anti-patterns, and scalability analysis in [ARCHITECTURE.md](ARCHITECTURE.md).

### Critical Pitfalls

1. **Hallucinated Physics Reasoning** -- The LLM generates plausible but incorrect derivations. A single bad step corrupts everything downstream. Prevention: ground every step in the provided answer (the anchor truth), run multi-pass verification in the DAG, use anti-agreeability prompting, maintain a regression test suite of 20-30 physics problems with known correct derivations.

2. **Context Window Pressure Causing Skipped Reasoning** -- Long problems stuffed into a single context window cause the model to skip intermediate derivations -- exactly what the product exists to provide. Prevention: aggressive DAG decomposition (every sub-question is its own node), pruned context per node (base setup + specific question + prior conclusions only), intermediate result compression between nodes.

3. **Over-Engineering the Skill System Before Core Quality Is Validated** -- Building the 3-tier plugin system, Skill Creator, and marketplace infrastructure before proving the analysis pipeline works on real physics problems. Prevention: Phase 1 has zero plugin system. Hardcode 1-2 analysis modes. Validate on 50+ real problems first. Extract plugin boundaries only where actual variation exists.

4. **OCR Accuracy as Silent Quality Ceiling** -- Chinese+LaTeX mixed content OCR introduces subtle errors (misrecognized subscripts, Greek letters) that the LLM treats as ground truth. The output looks plausible but is wrong. Prevention: OCR validation step in the DAG, human-in-the-loop for low confidence, maintain a test corpus of representative problems, support multiple OCR backends behind the abstraction.

5. **File-Based Index Staleness and Corruption** -- The JSONL index drifts out of sync with source files. Tag searches return ghost entries or miss real problems. Prevention: content-hash-based change detection (not existence checks), index as rebuildable derived artifact, SQLite migration path planned behind same interface, validate index integrity on every read.

All 13 pitfalls with phase-specific warnings and prevention strategies in [PITFALLS.md](PITFALLS.md).

## Implications for Roadmap

Based on combined architecture dependency analysis, feature MVP recommendation, and pitfall phase warnings, the suggested phase structure is:

### Phase 1: Core Foundation

**Rationale:** Everything depends on the LLM Gateway and Workspace Manager. Getting a working `cpho solve problem.pdf` end-to-end -- even if the output is raw LLM text -- proves the entire chain works. This phase addresses the three critical quality pitfalls (hallucination, context dilution, OCR errors) before any feature work begins.

**Delivers:**
- LLM Gateway with OpenRouter integration (structured output, retry, circuit breaker)
- Workspace Manager (folder scanning, problem-answer association, PDF type detection)
- OCR adapter interface + RapidOCR implementation + OCR validation DAG step
- CLI scaffold (Typer commands: `solve`, `index`, `config`)
- API Key Management (env var + config file)
- Answer-key grounded verification (cross-reference pass in pipeline)
- Basic DAG pipeline with aggressive sub-question decomposition
- Regression test suite (20-30 physics problems with known derivations)

**Addresses features:** Table Stakes #3 (LLM Analysis), #4 (API Key), #6 (CLI), #7 (Input Format)

**Avoids pitfalls:** #1 (hallucination) via answer grounding and regression tests, #2 (context dilution) via DAG decomposition from day one, #4 (OCR ceiling) via OCR validation step, #6 (OpenRouter reliability) via retry/circuit-breaker, #12 (PDF type handling) via auto-detection

**Must validate:** Analysis quality on 50+ real physics problems before declaring Phase 1 complete. Golden test suite must pass.

### Phase 2: Tag Indexing + Pipeline Maturation

**Rationale:** The index is the retrieval backbone. Every subsequent feature (comparative analysis, exam generation, knowledge graph) depends on tag-based queries working reliably. The pipeline engine matures here with the blackboard pattern and parallel execution. Doing these together makes sense because index building exercises the pipeline engine heavily.

**Delivers:**
- Tag schema with controlled vocabulary (YAML-defined, LLM maps to it)
- Index writer (content-hash-based change detection, incremental and full rebuild)
- Index reader (tag query parser with AND/OR/NOT, in-memory filtering for v1 scale)
- DAG engine maturation (topological sort, parallel scheduling, blackboard, context injector)
- Intermediate result compression between pipeline nodes
- `cpho batch` command (thread pool, configurable concurrency, progress display)
- Batch problem indexing (`cpho index ./problems/`)

**Addresses features:** Table Stakes #1 (Problem Folder Workspace), #2 (Tag-Based Indexing), Differentiator #12 (DAG Pipeline), #14 (Predictable DAG)

**Avoids pitfalls:** #5 (index staleness) via content-hash detection and rebuild capability, #13 (tag drift) via controlled vocabulary, #7 (prompt rot) via prompt versioning in YAML with model pinning

**Must validate:** Index query accuracy on 100+ problems. Tag consistency across re-indexing. Pipeline trace reproducibility (same problem, same output structure).

### Phase 3: Skill System + Built-in Skills

**Rationale:** With the pipeline engine stable and the index populated, skills can be built as pipeline definitions. The skill system itself is a Phase 3 concern -- not Phase 1 or 2 -- because the extension points can only be designed correctly after real usage patterns emerge from built-in skills. Start with the simplest extensibility tier (prompt override) and add YAML/Python tiers only when needed.

**Delivers:**
- Skill discovery and loader (entry points + filesystem scanning)
- Skill registry (name -> SkillDefinition)
- Prompt-only skill tier (Tier 1)
- Built-in Explanation Mode (step-by-step derivation with "why")
- Built-in Quiz Mode (Socratic questioning with scaffolded verification)
- Skill YAML definition format (Tier 2)
- Output pipeline: Markdown reports, JSON result files, terminal rendering (Rich)
- Chinese-language error messages, help text, and tutorial walkthrough

**Addresses features:** Table Stakes #5 (Answer Verification -- refined), Differentiators #8 (Multi-Mode Skills -- Explanation + Quiz), #9 (Skill System -- Tiers 1+2), #15 (Scaffolded Verification)

**Avoids pitfalls:** #3 (over-engineering) by deferring Tier 3 and Skill Creator to Phase 4, #9 (Python security) by not shipping Python tier, #10 (CLI complexity) by investing in Chinese UX, #8 (Obsidian envy) by keeping scope physics-specific

**Must validate:** Explanation Mode quality vs. human-written derivations on 30+ problems. Quiz Mode Socratic flow with real students/coaches. Skill creation UX for non-programmer physics teachers.

### Phase 4: Knowledge Network + Ecosystem + REPL

**Rationale:** The knowledge graph, comparative mode, exam generation, and REPL all depend on a mature index and stable skill system. The Skill Creator (a meta-tool that generates skills) can only work once the skill architecture is proven. The REPL ties everything together for interactive workflows. This phase also handles PDF output assembly and distribution readiness.

**Delivers:**
- Tag-based knowledge graph (problems linked by shared tags)
- Comparative Mode (compare 2+ problems, find shared models/patterns)
- PDF Exam Assembly (query tags, stitch problem + answer PDFs)
- REPL interactive mode (prompt-toolkit, session state, slash-commands)
- Skill Creator (natural language -> skill package generation)
- YAML declarative skill tier refinement
- Python script skill tier (Tier 3) -- gated behind explicit user opt-in with security warnings
- Distribution packaging (pip install, documentation, tutorial video)

**Addresses features:** Differentiators #10 (Skill Creator), #11 (Knowledge Graph), #13 (PDF Exam Assembly), Comparative Mode (from #8), Tier 3 Python skills (from #9)

**Avoids pitfalls:** #7 (prompt rot) via expanded golden test suite (30+ problems per skill), #8 (scope creep) by explicit physics-only boundary, #10 (CLI complexity) by REPL as the primary interaction mode for less technical users

**Must validate:** Knowledge graph linking quality. Exam assembly output fidelity. Skill Creator output quality (does it generate useful skills?). REPL usability with physics teacher testers.

### Phase Ordering Rationale

1. **Quality pipeline first, features second.** The research is unanimous: if the analysis isn't correct, nothing else matters. Phase 1 invests entirely in getting the LLM pipeline to produce trustworthy physics derivations. The DAG architecture, OCR validation, and answer grounding are not Phase 1 "features" -- they are quality infrastructure.

2. **Index before skills.** Skills depend on the tag index for retrieval, comparative analysis, and knowledge graph linking. The index data model (JSONL schema, controlled vocabulary, tag semantics) stabilizes in Phase 2 so skills in Phase 3 are built against a stable contract.

3. **Built-in skills before plugin system.** The skill framework is extracted from real usage, not designed in a vacuum. Phase 3 builds two concrete skills (Explanation, Quiz) as hardcoded pipeline definitions first. The loader, registry, and YAML format emerge as refactorings of what already works. This is the opposite of designing the plugin system and then building skills on top of it.

4. **REPL and ecosystem last.** The REPL is the most user-facing component and benefits from a stable core. Comparative Mode and Exam Generation are the features that differentiate CPHO CLI from a single-problem analysis tool, but they require the index and skill system to be production-ready. The Skill Creator is explicitly deferred to the final phase because it is building a tool-generating-tool -- it needs the skill architecture to be battle-tested.

### Research Flags

**Phases likely needing deeper research during planning (`/gsd:plan-phase --research-phase <N>`):**

- **Phase 1:** OCR quality validation on real physics competition problem scans (RapidOCR Chinese+LaTeX accuracy is the highest-uncertainty area in the entire stack). Prompt engineering for anti-hallucination physics derivations (this is the core quality problem and has no off-the-shelf solution). Regression test suite design (what makes a good golden problem set?).
- **Phase 3:** Skill definition format design -- the YAML schema for declarative skills needs exploration of what pipeline authors actually need vs. what's theoretically possible. Socratic questioning prompt design for Quiz Mode (this is a specialized pedagogy domain with research literature but no production implementations).
- **Phase 4:** Knowledge graph traversal algorithms for comparative analysis (graph similarity metrics for physics problems). REPL session state management patterns (what state to persist, how to handle context window across turns).

**Phases with standard patterns (skip research-phase):**

- **Phase 1 (CLI scaffold, API Key, Workspace Manager):** Well-established patterns from Aider, Open Interpreter, and dozens of Python CLI tools. Typer, Rich, and prompt-toolkit all have mature APIs.
- **Phase 2 (DAG engine, JSONL index, thread pool batch):** Standard computer science patterns. Topological sort, thread pools, and JSONL are well-understood. The novelty is in the context pruning strategy, not the execution model.
- **Phase 3 (Skill loader, entry point discovery):** pluggy and importlib.metadata are battle-tested in the pytest ecosystem. The discovery and loading patterns are standard.
- **Phase 4 (PDF stitching, Markdown reports):** pikepdf and Rich have straightforward APIs. PDF assembly via page extraction and concatenation is a well-documented operation.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | LiteLLM verified in production by Aider/Open Interpreter. Typer+Rich+prompt-toolkit is Aider's exact combo. pluggy v1.6.0 released May 2025 with mature API. pikepdf benchmarks confirmed. All versions checked against PyPI. |
| Features | HIGH | Competitive analysis spans 6+ analogous products across knowledge management, AI tutoring, and CLI tooling. Feature taxonomy validated against 2024-2025 physics education research (Tufino, Gobert, Mohammadipour, et al.). Anti-features derived from explicit project constraints. |
| Architecture | HIGH | Core-shell pattern verified in gpt-engineer, profile_engine, renku-python. Blackboard pattern confirmed in Flock, UFO, Griptape. DAG approach validated by PhysicsMinions paper. Structured output strategy confirmed in OpenRouter docs and LiteLLM GitHub issues. |
| Pitfalls | HIGH | Multiple verified sources: Nikolic et al. (hallucination), Syal et al. (multimodal interference), arXiv:2603.04474 (DAG error cascades), OpenRouter production incident reports (rate limiting), Chinese+LaTeX OCR research (MinerU, Mathpix evaluations). |

**Overall confidence:** HIGH

All four research domains produced confident findings backed by verified sources, production usage evidence, and current (2025-2026) literature. The only medium-confidence areas are OCR accuracy on our specific problem domain (needs spike validation with real problems) and prompt quality for physics derivations (inherently requires iteration -- no amount of research replaces testing).

### Gaps to Address

- **RapidOCR LaTeX formula accuracy on physics competition scans:** Research confidence is MEDIUM in STACK.md. The RapidLaTeXOCR fork is promising but unproven on IPhO-style problems (dense notation, multi-line equations, mixed Chinese/English/LaTeX). Mitigation: first Phase 1 task is a spike test with 10-20 real scanned physics problems. If accuracy is below threshold, PaddleOCR becomes the primary OCR path and the install-weight tradeoff is accepted.

- **Optimal DAG decomposition granularity for physics problems:** Research shows decomposition is necessary, but the optimal split point (one node per sub-question? per equation? per conceptual step?) is not determined by existing literature. Mitigation: start with one-node-per-sub-question, measure output quality on golden test set, adjust based on results.

- **Chinese-language LLM output quality:** Most physics education LLM research (P1, PhysicsMinions, Tufino) evaluates English-language models. Chinese-language physics terminology and derivation style may produce different error patterns. Mitigation: golden test set must include Chinese-language problems. Evaluate separately from English problems.

- **Physics teacher CLI tolerance threshold:** Research identifies this as a pitfall (#10) but lacks quantitative data on the target audience's CLI comfort. Mitigation: Phase 1 users are developers and technically-inclined coaches. Do not distribute to general physics teachers until after Phase 3 REPL investment. Measure onboarding time and abandonment rate with early users.

## Sources

### Primary (HIGH confidence)
- **Aider architecture** ([DeepWiki](https://deepwiki.com/helloandworlder/aider/2-core-system)) -- Confirmed LiteLLM + Rich + prompt-toolkit pattern. Slash-command UX model. Apache 2.0.
- **Open Interpreter architecture** ([DeepWiki](https://deepwiki.com/OpenInterpreter/open-interpreter/3-core-architecture)) -- Confirmed LiteLLM integration. API key management pattern.
- **LiteLLM OpenRouter issues** ([GitHub](https://github.com/BerriAI/litellm)) -- OpenRouter provider confirmed as first-class. `extra_body` structured output workaround verified.
- **pluggy 1.6.0** ([Changelog](https://pluggy.readthedocs.io/en/stable/changelog.html)) -- May 2025 release. Python 3.9-3.14 support. MIT license.
- **RapidOCR** ([DeepWiki](https://deepwiki.com/RapidAI/RapidOCR/1-overview)) -- ONNX Runtime backend, <5MB models, Apache 2.0.
- **pikepdf benchmarks** ([PyMuPDF docs](https://pymupdf.readthedocs.io/en/latest/about.html#about-feature-matrix)) -- 15x faster than pypdf on 7,031-page merge test. MPL 2.0.
- **PhysicsMinions** ([arXiv:2509.24855](https://arxiv.org/abs/2509.24855)) -- Multi-agent Olympiad solver architecture. Visual-Logic-Review pipeline. Hard-coded workflow stages.
- **P1 model** ([arXiv:2511.13612](https://arxiv.org/abs/2511.13612)) -- RL-trained Olympiad physics model. 5,065 problem training set.
- **PhysicsEval Dataset** ([Hugging Face](https://huggingface.co/IUTVanguard/PhysicsEval)) -- 19,609 annotated problems, 19 categories, difficulty + soft labels schema.
- **Tufino (2025)** ([arXiv:2504.09720](https://arxiv.org/abs/2504.09720)) -- "NotebookLM as a Socratic physics tutor." Socratic questioning design.
- **Gobert (2025)** -- IPN presentation on AI-based teacher/student support in science education.
- **OpenRouter Response Healing** ([announcement](https://openrouter.ai/announcements/response-healing-reduce-json-defects-by-80percent)) -- Auto-fixes JSON syntax errors, reduces parse failures by 80-99%.

### Secondary (MEDIUM confidence)
- **Korean physics educators study (2025)** -- Identified hallucination as #1 trust barrier for AI tutoring.
- **Mohammadipour (2025)** ([arXiv:2507.14860](https://arxiv.org/abs/2507.14860)) -- Strategic integration of AI chatbots in physics teacher preparation.
- **arXiv:2603.04474** -- Error cascades in multi-agent DAGs; genealogy-graph defense.
- **Syal et al. (2026)** ([arXiv:2605.04131](https://arxiv.org/abs/2605.04131)) -- Multimodal Interference Effect: 96% text-only vs. significant drop on image-based physics problems.
- **Chevalier, Mizera & Annala (2024)** -- "Can AI Teach Science?" Agreeability problem in LLM tutoring.
- **Mok et al. (2024, UCL)** -- LLM grading of undergraduate physics solutions; mathematical error prevalence.
- **Obsidian plugin ecosystem analysis** ([arXiv:2602.17018](https://arxiv.org/abs/2602.17018)) -- 6 functional clusters, plugin discovery patterns.
- **质心在线 (ZhiXin Online)** -- Chinese physics Olympiad training platform. Problem bank, mock exams, live courses.
- **OpenRouter production incidents** -- Rate-limit failures (99.5%), provider cooldown issues, silent failover to wrong models.

### Tertiary (LOW confidence)
- **gpt-engineer core/cli separation** ([GitHub issue #718](https://github.com/AntonOsika/gpt-engineer/issues/718)) -- Architecture pattern reference only.
- **Griptape Workflow documentation** -- DAG pipeline pattern reference. Agentic-framework approach, not adopted.
- **LangGraph StateGraph** -- Reference for DAG design patterns. Not adopted (agentic-loop design conflict).
- **AEQG-MCQ-Distractors-Physics** -- LLM + Concept Map + RAG for question generation. Reference for future question generation feature.
- **Charles University physics problem collection** ([physicstasks.eu](http://physicstasks.eu)) -- Cognitive skill taxonomy reference.

---
*Research completed: 2026-05-20*
*Ready for roadmap: yes*
