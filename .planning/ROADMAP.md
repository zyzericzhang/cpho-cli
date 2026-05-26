# Roadmap: CPHO CLI

## Overview

CPHO CLI 从质量优先的核心管线起步（Phase 1：题解可信化 + OCR 验证），接着建立题目知识索引基础设施（Phase 2，作为下游所有 skill 的检索骨架与学习记忆地基），其中插入 Phase 02.1 用 PaperFile/ProblemEntry 修正"文件 ≠ 题目"的形状错配、Phase 02.2 搭起 prompt_toolkit REPL 骨架、Phase 02.3 把 solve 降级为 builtin skill 并打开 index 标签层读写 API；Phase 3 落地 skill 通用跨切面能力（Markdown 导出 / Follow-up 对话 / 运行过程进度显示）与三个核心讲解类 skill（重定位的 Solve = 给标答挑错并把错误以 tag 形式长期写回 index、增强的 Explain = 多 Tone × 分栏目 × 句子级 × 回写 Index、新增的"主动提问 Skill" = 连续对话寻找关键点 → markdown 输出）；Phase 4 在 Phase 3 之上交付"找同类题 skill"与基于编排文件的 PDF 组卷 skill，并系统性补齐异常边界处理；Phase 5 完成用户手册、README 与简化的 Python 扩展机制，为 GitHub 开源做准备。每个 phase 交付一组可验证的、向下游 skill 提供地基的能力。

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Core Foundation** — End-to-end analysis pipeline with verifiable output quality (Needs Review: verification gaps)
- [x] **Phase 2: Tag Indexing** — Problem knowledge index infrastructure: retrieval backbone + learning-memory foundation for all downstream skills (completed 2026-05-23)
- [x] **Phase 02.1: Paper Splitting** — 试卷切分：多题试卷拆分为独立题目条目，修复数据模型形状错配 (INSERTED — COMPLETE 2026-05-24)
- [x] **Phase 02.2: TUI REPL 骨架** — prompt_toolkit REPL 主循环、skill 注册机制、slash command 首批命令，为后续 phase 顺带扩展 TUI 打好基础 (INSERTED) (completed 2026-05-24)
- [x] **Phase 02.3: Index 读写分离 + Solve 降级** — 移除 SolveReport→index 耦合与 golden_tests，index 标签层开放读写 API 供 skills 修改 (INSERTED) (completed 2026-05-25)
- [ ] **Phase 3: Skill 跨切面 + 核心讲解 Skills** — 所有 skill 通用的 Markdown 导出 / Follow-up 对话 / 进度显示 + Solve 重定位（挑错 + tag 长期记录）+ Explain 增强（多 Tone / 分栏目 / 句子级 / 回写 Index）+ 主动提问 Skill
- [ ] **Phase 4: 找同类题 + 组卷 + 异常处理** — 找同类题 skill + 编排文件驱动的 PDF 组卷（一页一题，答案分卷）+ 工作流异常边界（中途退出 / 硬盘拔出 / 文件越界 / blackboard 落盘恢复）
- [ ] **Phase 5: 用户手册 + 开源准备** — README、`docs/user/` 延伸文档、简化的 Python 扩展机制，参考著名开源 repo 风格为 GitHub 开源做准备

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

**Status:** Complete (10/10 plans executed, verified 2026-05-25)

**Plans**: 10 plans

Plans:
- [x] 02.3-01-PLAN.md — Remove SolveReport from index schema and tag-normalization contract
- [x] 02.3-02-PLAN.md — Remove remaining SolveReport loading from build_index
- [x] 02.3-03-PLAN.md — Add index tag write API, provenance model, and CLI wrappers
- [x] 02.3-04-PLAN.md — Delete eval/golden_tests while preserving splitting fixture coverage
- [x] 02.3-05-PLAN.md — Route text-path solve through SkillRuntime handlers
- [x] 02.3-06-PLAN.md — Add neutral multimodal LLM helpers and solve multimodal routing
- [x] 02.3-07-PLAN.md — Align workspace suffix support and refresh REPL model capabilities
- [x] 02.3-08-PLAN.md — Add core index --vision behavior behind OCR-default fallback
- [x] 02.3-09-PLAN.md — Expose index vision in CLI/REPL and add phase acceptance gates
- [x] 02.3-10-PLAN.md — Run final real uv verification and write Chinese verification manual

### Phase 3: Skill 跨切面 + 核心讲解 Skills

**Goal:** 在 Phase 02.2 REPL 与 Phase 02.3 index 读写 API 基础上，搭建所有 skill 共用的跨切面能力，并交付三个核心讲解类 skill。跨切面能力包含：Markdown 导出（用户输入 path、每类文件有默认值、文件名包含题目名）、类似 Claude Code 的运行过程进度显示、所有 skill 结束后的 Follow-up 对话（像 ChatGPT 网页版一样继续聊）、异常基础（中途退出可恢复）。三个核心 skill：(1) **Solve 重定位** —— 不再去解题，而是给工作空间内已提供的标准答案逐步挑错，错误以受控 tag 形式长期写回 index 的 skill-tag 层（与 LLM 机打 tag 分离、含 provenance）；(2) **Explain 增强** —— 多 Tone（老师型 / 知识点密集型 / 简短型）可同时选多个生成多版输出，每版首段先描述整道题物理图像与思路再推导；分栏目（原答案推导 / 超越原答案的更清晰推导 / 句子级 explain），且可在讲解后基于新发现 tag 回写 Index（用户可手动增删）；(3) **主动提问 Skill** —— 连续对话寻找题目关键点和关键步骤，输出一份 markdown 文件（前半部分问题，后半部分解答）。Solve 优先于其他 skill 运行——其他 skill 在 Solve 校正过的标答基础上讲解。物理优先，数学为辅。

**Depends on:** Phase 02.3
**Requirements**: SKILL-SOLVE-REPOSITION, SKILL-EXPLAIN-NEW, SKILL-PROBE, CROSS-EXPORT, CROSS-FOLLOWUP, CROSS-PROGRESS（详见 REQUIREMENTS.md 更新）
**Success Criteria** (what must be TRUE):
  1. 用户运行 `cpho solve <题目>`，工具不返回新解法，而是对工作空间内匹配到的标准答案做逐步审查；发现的错误以受控 tag 形式写入 index 的 skill-tag 层（与 LLM 机打 tag 分离，含 skill 来源 / 时间 / 推理出处的 provenance），`cpho index --force` 重建只覆盖机打 tag、保留 skill 写入的 tag。
  2. 用户运行 Explain 并选择一个或多个 Tone（老师型 / 知识点密集型 / 简短型），工具同时生成对应版本的讲解；每个版本第一段都先用几句话陈述整道题的物理图像与解题思路，再开始推导。
  3. Explain 输出分栏目：「原答案逐步讲解」「超越原答案的更清晰推导（若有）」「句子级 explain」三栏内容像标准答案一样写出；讲解后用户可选择"基于本次发现的 tag 重新 index 这道题"，工具把新 tag 写入 index skill-tag 层（用户可手工增删），不动机打 tag。
  4. 用户运行"主动提问 Skill"，工具就同一道题展开连续对话寻找关键点 / 关键步骤 / 深挖处理；结束后生成一份 markdown 文件（路径用户输入、有默认值、文件名含题目名），文件前半为所有问题、后半为对应解答。
  5. 任意 skill 运行过程中都有类似 Claude Code 的进度显示（当前到第几步 / 正在做什么 / 已耗时）；任意 skill 结束都可一键导出 markdown，路径与文件名规则统一，用户可改默认值。
  6. 任意 skill 结束后用户进入 Follow-up 模式，可基于本次 skill 上下文像 ChatGPT 网页版那样继续追问，直至显式退出。

**Plans**: TBD（见 `/gsd:plan-phase 3` 拆分）

### Phase 4: 找同类题 + 组卷 + 异常处理

**Goal:** 在 Phase 3 核心 skill 已可用的基础上，落地"找同类题 skill"作为组卷前置，再交付 PDF 组卷 skill：用户准备一份"编排文件"（以题号顺序列出每个题位的填法 —— 题目 ID 或 pass，或仅填分类与大体要求），工具据此从原始 PDF 裁剪页面拼接成两份 PDF（题目卷一页一题、答案卷分开），不重渲染公式；用户也可让组卷 skill 完全自动选题。同时系统性补齐工作流的异常边界场景：中途退出、外接硬盘工作空间被拔出、选择的文件不在 workspace、blackboard 与 explain/index 等 skill 中间产物的落盘与恢复，做到"至少不卡机"。组卷输出格式与 PDF 拼接尽量复用 GitHub 开源库二次开发，不重写底层。

**Depends on:** Phase 3
**Requirements**: SKILL-RELATED, SKILL-COMPOSE, ROBUST-BOUNDARY（详见 REQUIREMENTS.md 更新）
**Success Criteria** (what must be TRUE):
  1. 用户对任意已索引题目运行"找同类题 skill"，工具基于 index 标签层返回按相似度排序的同类题列表；结果可作为下一个 skill（组卷 / Explain 对比等）的输入。
  2. 用户准备的编排文件（题号 → 题目 ID / pass / 分类与要求）可被组卷 skill 消费，工具生成两份 PDF：题目卷一页一题、答案卷分开；页面直接来自原始 PDF 裁剪，不做 LaTeX 重渲染。
  3. 用户也可让组卷 skill 自动选题（结合"找同类题"或标签筛选），无需手写编排文件即可产出一份 PDF。
  4. 工作空间挂在外接硬盘且中途拔出 / 用户中途 Ctrl+C / 用户选择的文件不在当前 workspace / OCR / LLM 调用失败：工具都有明确的失败提示而非卡死；任意 skill 的中间产物（blackboard、partial markdown、explain 中间版本）落盘到可恢复位置，下次运行同一 skill 可选择继续或丢弃。

**Plans**: TBD（见 `/gsd:plan-phase 4` 拆分）

### Phase 5: 用户手册 + 开源准备

**Goal:** 项目核心功能完成后，为 GitHub 开源做准备：写一份高质量 README（项目简介 / Demo 截图或 asciinema / 安装 / Quick Start / REPL 用法 / 所有内置 skill 列表与示例 / 配置 / 扩展指南 / License）；在 `docs/user/` 目录提供 README 的延伸文档（按模块/skill 分章）；开放一个简化的 Python 扩展机制（用户改代码加 skill，明确入口与复用底层路径，不像 v1 设想的 YAML 那样灵活）；版面风格参考著名 GitHub repo 的 README。

**Depends on:** Phase 4
**Requirements**: DOCS-README, DOCS-USER, PLUGIN-PY-SIMPLE（详见 REQUIREMENTS.md 更新；YAML skill loader / 自然语言生成 skill / pip 第三方包安装机制移入 Out of Scope）
**Success Criteria** (what must be TRUE):
  1. 仓库根目录 `README.md` 遵循著名开源项目的版面（简介 / 截图或 asciinema / 安装 / Quick Start / REPL 用法 / 所有内置 skill 列表与示例 / 配置 / 扩展指南 / License）；新用户从 clone 到运行第一个 skill 在 10 分钟内可完成。
  2. `docs/user/` 目录存在，按 skill / 模块分章提供 README 的延伸文档；至少覆盖 solve / explain（含 Tone 与回写 Index）/ 主动提问 / 找同类题 / 组卷 / index / REPL 每个 skill 的运行参数、典型用法与导出文件说明。
  3. 简化 Python 扩展机制有专门一章文档：明确要写哪个 Python 类 / 函数、如何复用 `core/llm.py` 与 index 读写 API、如何在 REPL 注册新 slash command；不再保留 YAML skill loader 或自然语言生成 skill 的承诺，明确写入 Out of Scope。
  4. README 至少包含一张运行截图或 asciinema（REPL 或 CLI 的实际运行画面）。

**Plans**: TBD（见 `/gsd:plan-phase 5` 拆分）

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 2.1 → 2.2 → 2.3 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Foundation | 5/5 | Needs Review | - |
| 2. Tag Indexing | 7/7 | Complete   | 2026-05-23 |
| 02.1. Paper Splitting | 5/5 | Complete | 2026-05-24 |
| 02.2. TUI REPL 骨架 | 6/6 | Complete   | 2026-05-24 |
| 02.3. Index 读写分离 + Solve 降级 | 10/10 | Complete | 2026-05-25 |
| 3. Skill 跨切面 + 核心讲解 Skills | 0/TBD | Not started | - |
| 4. 找同类题 + 组卷 + 异常处理 | 0/TBD | Not started | - |
| 5. 用户手册 + 开源准备 | 0/TBD | Not started | - |
