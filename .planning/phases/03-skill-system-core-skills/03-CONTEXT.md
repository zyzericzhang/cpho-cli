# Phase 3: Skill System + Core Skills - Context

**Gathered:** 2026-05-24
**Status:** Ready for planning

## Phase Boundary

Phase 3 在 Phase 1/2 的索引基础设施上构建统一的 Skill 执行框架和两个内置分析 skill。交付物包括：(1) 共享 `ProblemContextBuilder` 上下文准备层，(2) 逐步讲解（explain）skill 的完整 prompt pipeline，(3) 主动提问（quiz）skill 的交互主循环，(4) YAML skill 自动发现与加载机制（双层路径 + builtin），(5) 统一 skill registry 和 CLI 命令模型。不做 solve 重构，不做完整 workflow engine。

## Implementation Decisions

### Skill Runtime 统一策略

- **D-01:** 渐进式统一——`solve_problem()` 保持现状不动，不在 Phase 3 迁移到 SkillRuntime。solve 是已验证路径，全面重构回归风险过高。
- **D-02:** 抽出共享 `ProblemContextBuilder` / `load_problem_context` 层，统一准备题目上下文：`problem_id`、OCR text、answer text、canonical tags、topic path、source paper、related problems（通过 `find_related_problems`）。explain 和 quiz 复用此层，不复制 solve 的 OCR/answer/index loading 逻辑。未来迁移 solve 到 SkillRuntime 时也可复用。

### SkillRuntime Step Kind 扩展

- **D-03:** 只新增 `index_query` step kind，最小支持三个操作：`get_problem_entry`、`query_index`、`find_related_problems`。YAML skill 应能清晰表达"从索引加载题目 → 调用 LLM 分析 → 输出结构化结果"。
- **D-04:** quiz 的交互循环不走 DAG。DAG 适合静态流程（检索题目、生成问题梯度、生成讲解）；quiz 的"提问 → 读用户回答 → 判断 → 追问/提示/揭示答案"是 REPL 状态机，由薄 Python 主循环负责。quiz 内部可以调用小型 DAG 或 LLM step，但不为此扩展 `user_prompt`、`condition_branch`、`loop` 等复杂 workflow 能力。

### Skill 发现机制

- **D-05:** 双层 + builtin 发现路径。优先级：`<workspace>/.cpho/skills/` > `~/.cpho/skills/` > `builtin_skills/`。同名 skill 按优先级覆盖。
- **D-06:** 实现 `cpho skills list` 命令，显示每个 skill 的名称、来源路径、优先级（是否被覆盖）、加载状态（正常/错误+原因）。
- **D-07:** Phase 3 不做 pip entry points 发现（PLUGIN-04 属于 Phase 4）。只做 YAML skill 的目录扫描和加载。

### CLI 命令模型与 Skill Registry

- **D-08:** 混合命令模型。内置核心 skill 有专属子命令（`cpho explain`、`cpho quiz`），用户 YAML skill 通过 `cpho run <skill-name>` 运行。
- **D-09:** 所有 skill（内置 + 用户）注册进统一的 skill registry。`cpho explain` 是 `cpho run explain` 的快捷封装——共用同一套 SkillSpec 解析和执行逻辑，不出现两套执行路径。
- **D-10:** 未来 Phase 02.2 REPL 的 `/explain` 和 `/run my_skill` 也从同一 registry 解析，不重复实现发现逻辑。

### Explain 模式输出

- **D-11:** Phase 3 MVP 输出一次性完整报告，但必须是结构化 step report。每个推导步骤包含字段：`step_id`、`step_title`、`derivation`（推导内容）、`why_this_step`（为什么想到这一步——核心要求）、`possible_confusion`（学生可能困惑的点）、`check_question`（检验理解的追问，为 REPL 追问预留入口）。
- **D-12:** 不做分步交互式 explain（依赖 Phase 02.2 REPL）。但数据结构中的 `step_id` 和 `check_question` 为后续 REPL 按步追问预留升级空间。

### Claude's Discretion

- `ProblemContextBuilder` 的具体 API 签名、返回类型由 planner/researcher 根据既有 `workspace.py` 和 `index/` 模块的 API 风格决定
- `index_query` step kind 的 handler 注册方式和 skill.yml 中的 exact schema 由 planner 决定
- Skill registry 的内部数据结构（dict / dataclass / Pydantic model）由 planner 根据既有模式决定
- quiz 交互循环的具体状态机设计由 planner 决定

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 架构与产品方向
- `docs/architecture-decisions.md` — 六项架构决策：纯本地 CLI、芯-壳分离、Python 生态、基座框架策略、配置文件驱动、用户策略
- `docs/product-spec.md` — 产品定位、典型用户场景、v1 范围

### 项目元信息
- `.planning/PROJECT.md` — 项目总览、约束条件、关键决策表（DAG 管线、三层 skill 系统、图片拼接 PDF）
- `.planning/REQUIREMENTS.md` — v1 需求，Phase 3 分配 SKILL-01/SKILL-02/PLUGIN-01
- `.planning/ROADMAP.md` — Phase 3 成功标准（4 项）、Phase 02.2 依赖关系

### 前序 Phase 上下文
- `.planning/phases/01-core-foundation/01-CONTEXT.md` — Phase 1 决策：uv/pyproject scaffold、skill-based 架构、blackboard DAG、Jinja2 prompt 模板、JSON mode + Pydantic、manual-first eval loop、芯-壳分离
- `.planning/phases/02-tag-indexing/02-CONTEXT.md` — Phase 2 决策：混合索引架构、受控词表三层体系、半开放词表、增量哈希、Python API（query_index / get_problem_entry / find_related_problems）、Phase 3 deferred 项

### 既有代码（Phase 3 直接依赖）
- `src/cpho_cli/core/skills.py` — Skill loader（读取 skill.yml + SKILL.md，返回 LoadedSkill）
- `src/cpho_cli/core/runtime.py` — SkillRuntime（DAG 拓扑排序、blackboard 数据传递、trace/checkpoint）
- `src/cpho_cli/core/solve.py` — 当前 solve 硬编码路径（OCR → LLM → validation），Phase 3 不动此文件
- `src/cpho_cli/models/skills.py` — SkillSpec / SkillStep Pydantic 模型
- `src/cpho_cli/models/runtime.py` — TraceRecord / CheckpointRecord / SkillRunResult 模型
- `src/cpho_cli/core/llm.py` — LLM provider 抽象（explain/quiz 复用）
- `src/cpho_cli/core/index/` — 索引模块，提供 query_index / get_problem_entry / find_related_problems API
- `src/cpho_cli/core/workspace.py` — Workspace 发现（ProblemContextBuilder 复用的入口）
- `src/cpho_cli/cli/app.py` — 当前 Typer CLI 命令结构

## Existing Code Insights

### Reusable Assets
- `SkillRuntime`（`core/runtime.py`）已是通用 DAG 执行器——拓扑排序、blackboard key 验证、trace/checkpoint 写入。explain skill 的 DAG 定义直接复用。
- `load_skill()`（`core/skills.py`）已实现 skill.yml + SKILL.md 加载和 `SkillSpec` 验证。skill 发现只需在此基础上加目录扫描。
- `SkillSpec` / `SkillStep`（`models/skills.py`）模型已就位，`SkillStep.kind` 字段天然支持新增 `index_query` kind。
- `core/llm.py` 的 provider 抽象和 `complete()` 方法——explain/quiz 的所有 LLM 调用直接复用。
- `core/index/` 的 `query_index`、`get_problem_entry`、`find_related_problems`——`ProblemContextBuilder` 和 `index_query` handler 的直接依赖。
- `builtin_skills/solve/` 的 skill 文件夹结构——explain/quiz 的 skill 目录参照此模板。

### Established Patterns
- **芯-壳分离**：skill 逻辑 → `cpho_cli/core/`，CLI 入口 → `cpho_cli/cli/app.py`
- **YAML + Pydantic 配置驱动**：skill 元数据在 skill.yml，Pydantic `BaseModel` 验证，`ConfigDict(extra="forbid")`
- **Jinja2 prompt 模板**：`prompts/*.md.j2`，skill.yml 中 `prompt_template` 字段引用
- **中文 UX**：用户界面默认中文
- **handler 注册模式**：`SkillRuntime` 通过 `handlers: Mapping[str, StepHandler]` 注入 step kind 实现

### Integration Points
- **Phase 2 Index API** → Phase 3 `ProblemContextBuilder` 读取题目上下文和关联题目
- **Phase 2 IndexEntry** → explain/quiz 通过 `problem_id` 检索索引条目
- **Phase 02.2 TUI REPL** → Phase 3 skill registry 被 REPL 复用（`/explain`、`/run` 命令从同一 registry 解析）
- **Phase 4 Knowledge Network** → explain 输出的 `related_problems` 字段为知识图谱关联提供数据

## Specific Ideas

- `ProblemContextBuilder` 应该返回一个 `ProblemContext` Pydantic model，包含所有下游 skill 需要的字段，避免 skill 各自拼凑上下文
- explain skill 的 prompt 管线参考现有 solve skill 的 step 分解粒度（normalize → derive → cross-check → report），但核心差异在 derive 步骤的 prompt 设计要求"每一步推导解释为什么想到这一步"
- quiz skill 的状态机设计参考经典 Socratic 教学法：concept hint → method hint → equation hint → reveal step，每层给用户一次回答机会
- `cpho skills list` 输出表格格式：名称 | 来源(builtin/global/workspace) | 路径 | 状态 | 备注（覆盖/错误原因）
- YAML skill 的最小合法定义：`name` + 至少一个 `step`。SKILL.md 可选但推荐

## Deferred Ideas

### 确认推迟到后续 Phase
- solve 迁移到 SkillRuntime → 后续 phase（solve 是已验证路径，等 explain/quiz 在 SkillRuntime 上跑稳后再迁移）
- `user_prompt` / `condition_branch` / `loop` step kind → 后续 phase（quiz 交互走 Python 状态机，不做通用 workflow engine）
- pip entry points skill 发现 → Phase 4（PLUGIN-04，需要包管理、版本冲突、安全边界）
- 分步交互式 explain（REPL 中按 step_id 追问）→ Phase 02.2 + 后续增强

### 讨论中提及但不在 Phase 3 范围
- 用户错题本编辑交互 → Phase 2 已 defer 到 Phase 3，但 Phase 3 scope 为 explain/quiz/YAML loader，错题本完整编辑体验仍需后续 phase
- Review/refinement skill（user-note → canonical-tag mapping）→ Phase 2 deferred，Phase 3 不做
- Q&A 历史作为标签来源接入 → Phase 2 deferred，Phase 3 不做（quiz 历史记录可作为数据源但非本 phase 交付物）

---

*Phase: 3-Skill System + Core Skills*
*Context gathered: 2026-05-24*
