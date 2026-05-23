# Roadmap: CPHO CLI

## Overview

CPHO CLI builds from a quality-first core pipeline through four phases: first establishing trustworthy physics derivations with answer-key grounding and OCR validation (Phase 1), then building the problem knowledge index infrastructure — the retrieval backbone and learning-memory foundation for all downstream skills (Phase 2), layering on built-in Explanation and Quiz skills with a YAML skill loader extracted from real usage (Phase 3), and finally completing the knowledge network with cross-problem comparative analysis, exam PDF generation, Skill Creator, and community plugin ecosystem (Phase 4). Each phase delivers a coherent, verifiable capability that builds on the previous phase's foundation.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Core Foundation** — End-to-end analysis pipeline with verifiable output quality (Needs Review: verification gaps)
- [x] **Phase 2: Tag Indexing** — Problem knowledge index infrastructure: retrieval backbone + learning-memory foundation for all downstream skills (completed 2026-05-23)
- [ ] **Phase 3: Skill System + Core Skills** — Explanation mode, Quiz mode, and YAML skill extensibility
- [ ] **Phase 4: Knowledge Network + Ecosystem** — Comparative analysis, exam generation, knowledge graph, and community plugins

## Phase Details

### Phase 1: Core Foundation
**Goal**: Users can run `cpho solve <problem.pdf>` and receive trustworthy, step-by-step physics derivations cross-referenced against provided answer keys, with OCR errors detected and flagged rather than silently propagated.
**Depends on**: Nothing (first phase)
**Requirements**: CORE-01, CORE-02, CORE-03, CORE-04, CORE-05
**Success Criteria** (what must be TRUE):
  1. User configures OpenRouter API key once via environment variable or local config file and runs any command without inline key prompts; the key is never hardcoded or committed to git.
  2. User points `cpho` at a folder containing PDF problem files and answer keys; the tool auto-discovers all problems with correct problem-to-answer pairings based on naming heuristics.
  3. User runs `cpho solve <problem.pdf>` and receives structured LLM analysis where each derivation step is explicitly cross-referenced against the provided answer key; discrepancies are flagged.
  4. OCR-extracted text from Chinese-language physics PDFs preserves core mathematical notation (subscripts, Greek letters, fractions); low-confidence OCR regions are surfaced in output rather than silently fed to the LLM.
  5. Developer runs the golden test suite (20-30 physics problems with known correct derivations) with a single command and receives a per-problem pass/fail report; all problems pass before Phase 1 is declared complete.
**Plans**:
- Wave 1: `01-01` — uv project scaffold, CLI shell, config/API-key foundation, and quality gates
- Wave 2: `01-02` — workspace discovery, answer pairing, document loading, and RapidOCR abstraction
- Wave 2: `01-03` — skill folder loader, blackboard DAG runtime, trace/checkpoint/resume contracts
- Wave 3: `01-04` — OpenRouter provider, built-in solve skill, answer cross-check, and `cpho solve`
- Wave 4: `01-05` — golden evaluation runner, `cpho eval golden_tests/`, and Phase 1 E2E regression

### Phase 2: Tag Indexing
**Goal**: 构建题目知识索引基础设施——将 workspace 中的题目文件、OCR 缓存、SolveReport 等整理成结构化索引，后续 skill 通过 Python API 检索而非重复读取原始文件。索引使用受控词表保证标签一致性，支持分层增量更新，并为用户错题本/学习记忆层预留数据边界。
**Depends on**: Phase 1
**Requirements**: IDX-01, IDX-02, IDX-03
**Success Criteria** (what must be TRUE):
  1. User runs `cpho index` on a workspace and receives a JSONL index file where every problem has canonical tags (physics model, insight/heuristic, math technique) with Chinese display names and stable internal IDs, generated via a controlled vocabulary.
  2. User modifies, adds, or removes PDF files and re-runs `cpho index`; only files with content-hash changes are re-indexed. Output shows layered statistics: file changes, OCR cache reuse/regeneration, and tag regeneration counts.
  3. User queries problems by tag via Python API (`query_index`, `get_problem_entry`, `find_related_problems`) and receives results with zero OCR or LLM re-processing — all served from the JSONL index.
  4. The same problem re-indexed produces identical canonical tag values; tags across all problems use a consistent controlled vocabulary with no synonymous or variant labels.
**Plans**: 7 plans
- Wave 1: `02-01` — Index data models (Pydantic StrictModel), JSONL atomic storage, three-layer vocabulary loader + alias normalization
- Wave 1: `02-02` — Three-tier hashing (file/semantic/user-learning), fingerprint composition, decide_action dispatcher
- Wave 1: `02-06` — Starter vocabulary content (42 canonical tags in builtin.yml), pyproject package-data, R8 review checkpoint
- Wave 2: `02-03` — OCR cache wrapper (CachedOCRProvider) + engine-upgrade detection (D-16); solve.py untouched (R4)
- Wave 2: `02-04` — LLM tagging pipeline via core/llm.py (D-02), Jinja2 prompt template, canonical-mapping pass (M3 determinism), trace JSONL
- Wave 3: `02-05` — build_index orchestration, `cpho index` CLI with layered stats (D-17), Python API (query_index/get_problem_entry/find_related_problems), notebook stubs, golden determinism test
- Wave 4: `02-07` — Topic hierarchy classification (TopicNode tree model, builtin taxonomy YAML, LLM topic assignment, topic query API, CLI topic/compose commands, MVP exam composition)

### Phase 3: Skill System + Core Skills
**Goal**: Users can run Explanation and Quiz analysis modes on indexed problems, and extend the system with custom YAML-defined skills that are auto-discovered from a skills directory.
**Depends on**: Phase 2
**Requirements**: SKILL-01, SKILL-02, PLUGIN-01
**Success Criteria** (what must be TRUE):
  1. User runs explanation mode on a problem and receives a complete derivation where every step explicitly states the reasoning logic for the transition (为什么想到这一步), not just the mathematical calculation.
  2. User runs quiz mode and engages in a REPL-based Socratic dialogue; the tool asks scaffolded questions (concept hint → method hint → equation hint) before revealing any solution step, and adapts follow-up questions based on user responses.
  3. User creates a custom skill by writing a single YAML file (defining inputs, DAG step sequence, prompt template references, and output format), placing it in the skills directory; the skill is auto-discovered and immediately executable without restarting the CLI.
  4. All CLI output — error messages, help text, skill descriptions, and prompt instructions to the LLM — is in Chinese by default, matching the target audience's primary language.
**Plans**: TBD

### Phase 4: Knowledge Network + Ecosystem
**Goal**: Users can compare problems, generate exam PDFs, explore knowledge-graph connections, install community skills via pip, and create new skills from natural language descriptions.
**Depends on**: Phase 3
**Requirements**: SKILL-03, SKILL-04, PLUGIN-02, PLUGIN-03, PLUGIN-04, KNOW-01, KNOW-02
**Success Criteria** (what must be TRUE):
  1. User selects two or more problems for comparative analysis; output identifies shared physics models and common solution strategies, and automatically pulls additional related problems from the tag-based knowledge graph for extended comparison.
  2. User queries problems by tags and generates two PDF files (problem sheet + answer sheet) where pages are extracted and stitched directly from source PDFs — no LaTeX re-rendering, preserving original formatting.
  3. User describes a desired analysis workflow in natural Chinese language; Skill Creator produces a complete, functional YAML skill configuration with prompt templates that executes correctly on first run.
  4. User runs `pip install <some-cpho-skill-package>` and the installed skill is automatically discovered via Python entry points and available for execution without any manual registration step.
  5. When analyzing any problem with any skill, related-problem context from the knowledge graph (tag-similar problems from the workspace) is automatically injected into the analysis pipeline as supplementary context.
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Foundation | 5/5 | Needs Review | - |
| 2. Tag Indexing | 7/7 | Complete   | 2026-05-23 |
| 3. Skill System + Core Skills | 0/TBD | Not started | - |
| 4. Knowledge Network + Ecosystem | 0/TBD | Not started | - |
