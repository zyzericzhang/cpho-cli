# Roadmap: CPHO CLI

## Overview

CPHO CLI builds from a quality-first core pipeline through four phases: first establishing trustworthy physics derivations with answer-key grounding and OCR validation (Phase 1), then building the problem knowledge index infrastructure — the retrieval backbone and learning-memory foundation for all downstream skills (Phase 2), with an urgent Phase 02.1 insertion to fix a data-model mismatch by splitting multi-problem exam papers into individual ProblemEntries, layering on built-in Explanation and Quiz skills with a YAML skill loader extracted from real usage (Phase 3), and finally completing the knowledge network with cross-problem comparative analysis, exam PDF generation, Skill Creator, and community plugin ecosystem (Phase 4). Each phase delivers a coherent, verifiable capability that builds on the previous phase's foundation.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Core Foundation** — End-to-end analysis pipeline with verifiable output quality (Needs Review: verification gaps)
- [x] **Phase 2: Tag Indexing** — Problem knowledge index infrastructure: retrieval backbone + learning-memory foundation for all downstream skills (completed 2026-05-23)
- [x] **Phase 02.1: Paper Splitting** — 试卷切分：多题试卷拆分为独立题目条目，修复数据模型形状错配 (INSERTED — COMPLETE 2026-05-24)
- [x] **Phase 02.2: TUI REPL 骨架** — prompt_toolkit REPL 主循环、skill 注册机制、slash command 首批命令，为后续 phase 顺带扩展 TUI 打好基础 (INSERTED) (completed 2026-05-24)
- [ ] **Phase 02.3: Index 读写分离 + Solve 降级** — 移除 SolveReport→index 耦合与 golden_tests，index 标签层开放读写 API 供 skills 修改 (INSERTED)
- [ ] **Phase 3: Skill System + Core Skills** — Explanation mode, Quiz mode, and YAML skill extensibility
- [ ] **Phase 4: Knowledge Network + Ecosystem** — Comparative analysis, exam generation, knowledge graph, and community plugins

## Phase Details

### Phase 1: Core Foundation
**Goal**: Users can run `cpho solve <problem.pdf>` and receive trustworthy, step-by-step physics derivations cross-referenced against provided answer keys, with OCR errors detected and flagged rather than silently propagated.
**Depends on**: Nothing (first phase)
**Requirements**: CORE-01, CORE-02, CORE-03, CORE-04, CORE-05
**Success Criteria** (what must be TRUE):
  1. User configures OpenRouter API key once via environment variable or local config file and runs any command without inline key prompts; the key is never hardcoded or committed to git.
  2. User points `cpho` at a folder containing PDF exam papers and answer keys; the tool auto-discovers paper-to-answer pairings based on naming heuristics, then splits multi-problem papers into individual ProblemEntries (Phase 02.1).
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
**Goal**: 构建题目知识索引基础设施——将 workspace 中的试卷文件经 Phase 02.1 拆分为 ProblemEntry 后，连同 OCR 缓存、SolveReport 等整理成结构化索引，后续 skill 通过 Python API 检索而非重复读取原始文件。索引使用受控词表保证标签一致性，支持分层增量更新，并为用户错题本/学习记忆层预留数据边界。
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

### Phase 02.1: Paper Splitting — 试卷切分：将多题试卷 PDF 拆分为独立大题条目，修复 Phase 1/2 数据模型与真实工作空间之间的形状错配 (INSERTED — COMPLETE 2026-05-24)

**Goal:** 引入 PaperFile/ProblemEntry 分层数据模型，通过规则优先+LLM兜底切分器将多题试卷拆为独立题目条目，使 `cpho index` 的消费单位从「文件」升级为「题目」。
**Requirements**: 6 locked (see 02.1-SPEC.md)
**Depends on:** Phase 02
**Status:** Complete (5/5 plans executed, ready for verification)
**Plans:** 5/5 plans complete

Plans:
- [x] 02.1-01 — PaperFile + ProblemEntry 数据模型 (StrictModel)
- [x] 02.1-02 — 规则切分器 (regex + 页号定位)
- [x] 02.1-03 — LLM 兜底切分器 (Jinja2 prompt, 复用 core/llm.py)
- [x] 02.1-04 — 切分编排器 + discover_workspace 升级 + 答案卷配对
- [x] 02.1-05 — CLI 与索引集成 + golden 验收卷

### Phase 02.2: TUI REPL 骨架 — 打造 REPL 交互界面，后续新功能顺带扩展 TUI 零摩擦 (INSERTED)

**Goal:** 基于 prompt_toolkit 自建轻量 REPL 主循环和 `Command` registry，首批实现 `/search` + `/show` 斜杠命令。核心原则：加新功能 = 注册一个新 slash command + 补全规则，无需额外改动 TUI 布局。设计决策见 `.planning/notes/tui-design-decisions.md` 与 spike `.planning/spikes/02.2-repl-framework-comparison/COMPARISON.md`。
**Requirements**: TUI-01, TUI-02, TUI-03, TUI-04
**Depends on:** Phase 02.1
**Success Criteria** (what must be TRUE):
  1. 用户运行 `cpho repl` 进入 REPL 界面，看到 `cpho>` 提示符，输入 `/help` 列出所有可用命令。
  2. 用户输入 `/search 力学` 按标签搜索题目，REPL 输出匹配结果列表，搜索结果保存在会话上下文中。
  3. 用户在搜索后输入 `/show 3` 显示第 3 道题的全文内容（OCR 文本 + 标签 + 来源试卷），无需重新指定文件路径。
  4. 开发者在 Phase 3 中新增一个 skill（如 `/explain`）时，只需注册一个 Command 对象 + 补全规则，无需修改 REPL 主循环或任何 TUI 布局代码。
**Plans**: 6 plans
- Wave 1: `02.2-01` — prompt_toolkit/wcwidth 依赖 + cli/repl/ 包骨架 + Typer `cpho repl` 子命令
- Wave 2: `02.2-02` — Command registry + SessionState/IndexMeta + XDG persistence/history
- Wave 3: `02.2-03` — prompt_toolkit ReplApp 主循环 + display/completer/lexer + `/help` `/set` `/run` + Phase 3 stub
- Wave 4: `02.2-04` — workspace/index commands (`/workspace` `/status` `/config` `/index` `/reload-index` `/resume`)
- Wave 5: `02.2-05` — search/show commands (`/search` `/show`) + 标签补全缓存
- Wave 6: `02.2-06` — 端到端验收测试 (覆盖 4 项 Success Criteria + D-XX 决策)

Plans:
- [x] 02.2-01-deps-skeleton-PLAN.md — prompt_toolkit/wcwidth 依赖 + cli/repl/ 包骨架 + `cpho repl` Typer 入口
- [x] 02.2-02-core-abstractions-PLAN.md — Command registry + SessionState/IndexMeta + XDG persistence/history
- [x] 02.2-03-repl-runtime-display-PLAN.md — prompt_toolkit ReplApp 主循环 + display/completer/lexer + `/help` `/set` `/run`
- [x] 02.2-04-workspace-index-commands-PLAN.md — workspace/index commands：/workspace /status /config /index (D-20 dry-run) /reload-index /resume
- [x] 02.2-05-search-show-skill-PLAN.md — search/show commands：/search + /show + 标签补全缓存
- [x] 02.2-06-acceptance-PLAN.md — 4 项 Success Criteria + D-XX 决策端到端验收测试

### Phase 02.3: Index 读写分离 + Solve 降级 — 移除 SolveReport→index 耦合与 golden_tests，index 标签层开放读写 API 供 skills 修改 (INSERTED)

**Goal:** 将 solve 从 core 管线的一等公民降级为真正的 builtin skill；移除 index 管线对 SolveReport 标签的硬依赖（`TagSource.SOLVE_REPORT`）；删除未经验证的 golden_tests eval 框架；为 index 标签层提供读写 API，使 solve/explain 等 skills 和社区 skill 可以通过统一接口修改 index 条目标签。

**Depends on:** Phase 02.2

**Success Criteria** (what must be TRUE):
  1. `cpho index` 构建管线不再加载或依赖 `SolveReport`，标签归一化仅基于 OCR 文本 + vocabulary。
  2. `IndexEntry` 数据模型中移除 `solve_report_path` 字段，`TagSource` 枚举移除 `SOLVE_REPORT` 变体。
  3. `golden_tests/` 目录和 `cpho eval` 命令被移除；`core/eval.py` 不再存在。
  4. 提供 `cpho index tag-set` / `tag-add` / `tag-remove` CLI 子命令，skills 可以读写 index 标签。
  5. skill 写入的标签与 LLM 机打标签分离存储，`cpho index --force` 重建只覆盖机打标签，保留 skill 写入的标签。
  6. 标签写入记录出处（provenance）：哪个 skill、什么时间、基于什么推理。
  7. `cpho solve` 支持图片/PDF 多模态输入（通过 OpenRouter Universal PDF Support），模型不支持多模态时自动降级到 OCR 文本路径。
  8. `cpho index` 支持 `--vision` 选项启用多模态索引（默认仍用 OCR）。

**Plans**: TBD

### Phase 3: Skill System + Core Skills
**Goal**: Users can run Explanation and Quiz analysis modes on indexed problems (individual ProblemEntries split from exam papers), and extend the system with custom YAML-defined skills that are auto-discovered from a skills directory.
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
Phases execute in numeric order: 1 → 2 → 2.1 → 2.2 → 2.3 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Foundation | 5/5 | Needs Review | - |
| 2. Tag Indexing | 7/7 | Complete   | 2026-05-23 |
| 02.1. Paper Splitting | 5/5 | Complete | 2026-05-24 |
| 02.2. TUI REPL 骨架 | 6/6 | Complete   | 2026-05-24 |
| 02.3. Index 读写分离 + Solve 降级 | 0/TBD | Not started | - |
| 3. Skill System + Core Skills | 0/TBD | Not started | - |
| 4. Knowledge Network + Ecosystem | 0/TBD | Not started | - |
