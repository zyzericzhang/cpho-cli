# Phase 2: Tag Indexing - Context

**Gathered:** 2026-05-23
**Status:** Ready for planning

## Phase Boundary

Phase 2 交付题目标签索引系统——将本地 workspace 整理成后续 skill 可读取和复用的题目知识索引。它不是纯 OCR→LLM 自动标注管线，而是学习记忆/错题本层，保留每道题的关键知识点、难点推理步骤、用户识别的启发点，为跨题学习提供检索基础。

`cpho index` 不是解题命令，而是将题目相关多种信息（文件、OCR、SolveReport、Q&A 记录、用户笔记、卡点）组织成结构化索引。

## Implementation Decisions

### 索引架构

- **D-01:** 混合架构——核心模块（`cpho_cli/core/index.py`）拥有 schema、JSONL 存储、哈希/指纹、stale 检测、词表归一化、查询函数。LLM 打标签步骤复用既有 DAG/skill-runtime 约定（prompt 版本化、结构化输出校验、模型参数、traceability），但 index 不作为普通 built-in skill 注册。
- **D-02:** LLM 打标签必须使用既有 `cpho_cli/core/llm.py` provider 抽象，不走独立 LLM 路径。
- **D-03:** 索引模块必须导出 Python API：`query_index`、`get_problem_entry`、`find_related_problems`。下游 skill 通过这些 API 直接调用，不通过 CLI subprocess。

### 标签来源策略

- **D-04:** 索引定位为学习记忆/错题本层，不是纯自动标注管线。
- **D-05:** 来源优先级：(1) 用户添加的笔记/关键点/确认的难点 → (2) SolveReport 结构化分析和生成的标签 → (3) 用户-AI Q&A 历史（特别是重复提问或澄清过的误解）→ (4) 缓存的 OCR 文本作为兜底或补充上下文。
- **D-06:** 索引器运行专用归一化/精炼 pass，消费可用学习制品，产生受控词表索引字段——不是盲抄 SolveReport 标签。SolveReport 标签可能是自由格式，不符合受控词表要求。
- **D-07:** 索引字段：canonical knowledge/model tags、canonical math technique tags、heuristic/insight tags、user-confirmed key points、user-confirmed 卡点、source provenance（user_note / solve_report / qa_history / ocr_fallback）。
- **D-08:** 不使用 easy/medium/hard 通用难度标签。改为记录"难在哪里"——哪个概念、哪个过渡、哪个建模步骤、哪个近似、哪个守恒律选择、哪个坐标系选择、哪个数学处理造成了障碍。

### 受控词表体系

- **D-09:** 三层词汇体系，不把所有 tag 混平：
  - **内置基础词表** — 随 cpho-cli 项目发布，覆盖常见物理竞赛模型、数学技巧、推理过程。共享且稳定。
  - **workspace/团队词表** — 存在用户本地 workspace，可随项目增长，可含项目特定或教练/团队特定分类扩展。
  - **用户私有错题本词表** — 用户自己的学习语言、个人标签、错误原因、"卡点"、题目特定反思。默认不提交 git，不自动污染系统词表。
- **D-10:** 半开放受控词表——LLM 尽量复用已有 canonical tags；如果提议新系统标签，进入 candidate/pending 状态；用户或审核者确认后才正式生效。
- **D-11:** 每个 canonical tag 有中文展示名 + 英文内部 ID（stable snake_case）+ aliases。用户界面默认显示中文。内部 ID 用于存储稳定性、开发者可读性、跨环境迁移。
- **D-12:** Review skill 可从用户错题本语言建议映射到 canonical 系统标签（如 "我不会选系统" → "研究对象选择 / system_selection"），但映射必须进入 pending review，不得自动生效。用户确认后才写入 canonical/workspace 词表。
- **D-13:** Git commit 或导出工作流时，用户需明确选择哪些词汇层被包含（公开共享分类 / 团队 workspace 词表 / 私有个人学习笔记）。工具不得自动提交私有错题本内容。

### 增量更新与哈希策略

- **D-14:** 三层哈希/变更检测：
  - **文件层** — 题目 PDF/图片 + 答案文件是否变化。控制：是否重新读取源文件、是否重新 OCR、是否标记相关系统标签 stale。
  - **语义/系统索引层** — OCR 文本、SolveReport、标准答案 grounding、tag prompt version、schema version、model/prompt 设置、canonical vocabulary version 是否变化。控制：是否重新生成 canonical tags。
  - **用户学习/错题本/精炼层** — 用户错题本内容、个人标签、卡点记录、Q&A 衍生笔记是否变化。控制：是否触发 refinement/review pass（不触发 OCR 或完整 LLM tagging）。
- **D-15:** 分层存储：主系统索引、hash/fingerprint 状态文件、vocabulary 文件、用户错题本/私人笔记存储、OCR cache 各独立存储，不塞入单一文件。
- **D-16:** OCR 引擎升级策略：OCR engine name + version + config 进入 fingerprint。检测到变更后标记相关条目 stale，提示用户确认，允许选择：(a) 重建全部、(b) 只重建受影响条目、(c) 暂时跳过、(d) 只索引新增文件。
- **D-17:** `cpho index` 输出分层统计——文件层变化数、OCR 复用/重生成数、系统标签重生成/跳过数、用户笔记变化数、refinement mapping 建议数、pending review items 数。用户笔记变更不算 full re-index，单独统计为 refinement-layer change。

### Claude's Discretion

所有关键实现决策均由用户明确指定。具体实现细节（文件格式、API 签名、错误处理）由 planner 和 researcher 根据代码库既有模式决定。

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 架构与产品方向
- `docs/architecture-decisions.md` — 六项架构决策：纯本地 CLI、芯-壳分离、Python 生态、基座框架策略、配置文件驱动、用户策略
- `docs/product-spec.md` — 产品定位、典型用户场景、v1 范围

### 项目元信息
- `.planning/PROJECT.md` — 项目总览、约束条件、关键决策表（DAG 管线、三层 skill 系统、图片拼接 PDF）
- `.planning/REQUIREMENTS.md` — v1 18 项需求，Phase 2 分配 IDX-01/IDX-02/IDX-03
- `.planning/ROADMAP.md` — 四阶段路线图，Phase 2 成功标准（4 项）
- `.planning/phases/01-core-foundation/01-CONTEXT.md` — Phase 1 上下文，特别是 Integration Points 中关于 trace schema 作为 Phase 2 输入接口的说明

### 既有代码
- `src/cpho_cli/core/llm.py` — LLM provider 抽象（Phase 2 打标签必须复用）
- `src/cpho_cli/core/workspace.py` — workspace 发现和题目-答案配对（Phase 2 索引的输入入口）
- `src/cpho_cli/core/runtime.py` — DAG runtime、trace/checkpoint 机制（LLM 打标签步骤复用其约定）
- `src/cpho_cli/models/solve.py` — SolveReport schema（含 physics_model_tags、heuristic_insight_tags、math_technique_tags）
- `src/cpho_cli/models/documents.py` — ProblemFile、AnswerKeyFile、ProblemAnswerPair 模型

## Existing Code Insights

### Reusable Assets
- `workspace.py` 的 `discover_workspace()` 已有完整的文件发现和题目-答案配对逻辑——index 命令直接复用
- `llm.py` 的 provider 抽象和 `complete()` 方法——打标签 LLM 调用直接使用
- `runtime.py` 的 `SkillRuntime`、trace/checkpoint 机制——打标签步骤借鉴其 trace 写入模式
- `models/solve.py` 的 `SolveReport`——indexer 读取其 tag 字段作为标签来源之一

### Established Patterns
- **芯-壳分离**：索引逻辑 → `cpho_cli/core/index.py`，CLI 入口 → `cpho_cli/cli/app.py`
- **YAML 配置驱动**：index 相关配置（model params、vocabulary paths、hash settings）通过 config.local.yml 控制
- **Pydantic 模型**：所有数据结构使用 Pydantic BaseModel，JSON mode + schema 验证
- **中文 UX**：用户界面默认中文

### Integration Points
- **Phase 1 SolveReport** → Phase 2 读取作为标签来源之一（优先级 2）
- **Phase 1 workspace 发现** → Phase 2 索引入口（复用 discover_workspace；Phase 02.1 在 OCR 后插入 split 阶段，将 PaperFile 拆为 ProblemEntry 再进入索引）
- **Phase 3 Skill System** → 通过 `query_index`、`find_related_problems` API 检索题目（每条 IndexEntry 对应一个 ProblemEntry，非整份试卷）
- **Phase 4 Knowledge Network** → 基于索引标签相似度构建知识图谱

## Specific Ideas

- 用户错题本内容是题目级别的正常可编辑文本，不限于短 tag。具体交互形式（UI/TUI/CLI 编辑）在 Phase 3+ 设计，但 Phase 2 架构必须预留存储和 API
- `{problem_id}` 机制：用户可能自己命名题目（如"2019-IPhO-P1"），也可能自动生成（文件路径 hash）
- 参考 Obsidian 的笔记链接/反向链接思路——index 存储题目之间的关联关系，后续 phase 可视化或导航

## Phase 2 Scope Boundary

Phase 2 交付索引**基础设施**，不交付完整的错题本用户体验。具体边界：

### Phase 2 必做
- system-readable index：JSONL 主索引，canonical tags（中文展示名 + 英文内部 ID + aliases）
- LLM tagging pipeline：复用 `llm.py` provider，消费 SolveReport + OCR cache 产生 canonical tags
- 受控词表基础结构：内置基础词表（30-50 个标签，随项目发布）+ workspace 词表文件
- 半开放词表机制：LLM 复用已有 → 新 tag 标记 candidate → 数据模型预留确认流程（不含交互 UI）
- OCR cache 复用：OCR 输出缓存到 `.cpho/cache/`，solve 和 index 共享
- 分层哈希：文件层 + 语义层（第三层用户学习层预留字段但不完整实现）
- 增量索引：基于哈希跳过未变更文件
- OCR 引擎升级检测：OCR engine/version/config 进入 fingerprint，变更时提示用户（不静默重建）
- 分层输出统计：文件变化 / OCR 复用 / 标签重建 / 跳过
- 用户笔记存储数据模型：`problem_id → notes[]` 存储边界 + API stub（`get_problem_notes`、`set_problem_notes`），不做编辑器和交互
- vocabulary visibility 字段：`private / team / public` 枚举预留，不做 commit/export workflow
- Python API：`query_index`、`get_problem_entry`、`find_related_problems`（基于标签匹配，不做 embedding 或图算法）

### Deferred 到 Phase 3
- 用户错题本编辑交互（CLI / TUI / 外部编辑器）
- Review/refinement skill：user-note → canonical-tag mapping + pending review 流程
- Pending review CLI/UI
- 用户笔记变化触发 refinement 的完整链路
- Q&A 历史作为标签来源接入（Quiz 模式在 Phase 3 才存在）

### Deferred 到 Phase 4
- commit/export 可见性选择 workflow
- 知识图谱关联（KNOW-01）——Phase 2 的 `find_related_problems` 仅做相同标签匹配
- 相关题目上下文自动注入分析管线（KNOW-02）

### 数据源现实
Phase 2 实际运行时，可用数据源为 SolveReport + OCR cache。用户笔记和 Q&A 历史的数据模型和 API 在 Phase 2 预留，但完整消费链路依赖 Phase 3。

## Deferred Ideas

### 错题本完整体验 → Phase 3
- 用户可编辑的错题本笔记（支持长文本，不限于短 tag）
- 笔记与 canonical tag 的映射建议和确认流程
- 用户笔记变更触发的增量 refinement

### 复杂查询语法 → 后续 phase
- 布尔表达式查询（AND/OR/NOT）暂不在 Phase 2 实现
- Phase 2 提供简单标签匹配查询，复杂查询按需在 Phase 3/4 添加

### 完整物理学 taxonomy → 迭代构建
- Phase 2 内置词表以 30-50 个常见标签起步
- 不在 Phase 2 试图构建完整物理学分类体系

---

## Phase 2 Extension: Topic Hierarchy Classification (02-07)

*Added: 2026-05-23. Design session with gsd-explore.*

### Motivation

Phase 2 currently builds a flat tag system — tags describe what knowledge/techniques a problem uses. But for retrieval and exam composition, the user also needs a **hierarchical topic classification** — what subject area a problem belongs to.

### Two-System Model

Phase 2 now has two independent indexing dimensions:

| Dimension | Tags | Topics |
|-----------|------|--------|
| Structure | Flat | Hierarchical tree |
| Cardinality per problem | Multiple | Exactly one |
| Semantic | "What knowledge/techniques does this use?" | "What subject area is this?" |
| Example | `angular_momentum_conservation`, `binnet_equation` | 力学/天体运动/轨道理论 |
| Primary use | Knowledge search, cross-problem insight | Browsing, exam composition |

### Category System Redesign

The `TagCategory` enum has been redesigned (see `.planning/notes/topic-hierarchy-design.md` for full details):

| Old → New | Description |
|-----------|-------------|
| `physics_model` → `physics_law` | Specific physics laws (partition function, effective potential). Excludes textbook basics. |
| (new) `physics_model` | Concrete models from papers (e.g., rainbow scattering model) |
| `math_technique` | Kept. Exact differentials, series expansion, integration techniques. |
| `heuristic` | Kept + absorbs `system_selection`. Phase diagrams, optical-mechanical analogy. |
| `approximation` | Kept. Concrete approximation methods, not generic ones. |

Action required: sync `TagCategory` enum and `builtin.yml` to new values.

### Exam Paper Splitting

Source materials are exam papers (7-8 problems each). Per-problem tagging requires splitting:

- **Method:** LLM auto-split — read exam PDF, output problem boundaries
- **Atomic unit:** Individual problem = one `IndexEntry`
- **Splitting happens before indexing:** exam → split → per-problem files → normal index pipeline

### What 02-07 Covers

- `TopicNode` data model (tree, parent-child)
- Topic taxonomy YAML (builtin, shipped with project)
- `IndexEntry.topic_path` field (string path, e.g., "力学/天体运动/轨道理论")
- LLM-based topic assignment (classifies problem into single topic path)
- Query API: `find_problems_by_topic()`, `get_topic_tree()`
- CLI: `cpho topic list`, `cpho topic browse`
- MVP exam composition: `cpho compose --topic <path> --tags <tag1,tag2>`

### Scope Boundary

In scope for 02-07:
- Data model + taxonomy file + LLM assignment + query API + basic CLI
- MVP exam composition (output problem list, not full PDF generation)

Deferred beyond 02-07:
- Full exam PDF generation
- Topic conflict resolution UI
- Topic taxonomy editor/browser
- Auto-generation of taxonomy from corpus

### Related Documents

- `.planning/notes/topic-hierarchy-design.md` — Full design decisions and handoff notes for plan-writing agent
- `docs/vocabulary-extraction-prompt.md` — Agent prompt with new category values

---

*Phase: 2-Tag Indexing*
*Context gathered: 2026-05-23*
*Topic hierarchy supplement: 2026-05-23*
