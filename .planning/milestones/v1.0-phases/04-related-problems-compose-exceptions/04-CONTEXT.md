# Phase 4: 找同类题 + 组卷 + 异常处理 - Context

**Gathered:** 2026-05-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 4 在 Phase 3 核心讲解 skill 已可用的基础上，交付三项能力：

1. **SKILL-RELATED**：将现有 `find_related_problems()` API 包装成完整 skill（进度显示 / Follow-up / Markdown 导出跨切面均继承 Phase 3 已定方案）。
2. **SKILL-COMPOSE**：用户写"编排文件"（YAML）描述每个题位（题目 ID / pass / 自动填 spec），skill 用 pymupdf 从原始 PDF 裁页拼装出两份 PDF（题目卷各题整数页、答案卷分开），不重渲染 LaTeX；同时支持全自动选题模式。
3. **ROBUST-BOUNDARY**：Ctrl+C 中断 / 外接硬盘拔出 / 文件越界 / OCR/LLM 调用失败的系统性边界处理，做到"至少不卡机"，blackboard 中间产物落盘可恢复。

跨切面三件套（CROSS-EXPORT / CROSS-FOLLOWUP / CROSS-PROGRESS）在 Phase 3 已定，Phase 4 两个 skill 直接继承，本 CONTEXT 不再重复。

</domain>

<decisions>
## Implementation Decisions

### 找同类题 Skill（SKILL-RELATED）

- **D-01：输出去向** — CLI 表格 + REPL session `last_related` 同时支持。CLI 模式将结果以表格打印；REPL `/search-related <problem_id>` 同时存入 `SessionState.last_related`。
- **D-02：下游链路** — 显式串联：组卷 skill 通过 `--from last-related` 读取 `last_related`，不做隐式自动注入（与 Phase 02.3 "provenance 显式记录" 原则一致）。
- **D-03：打分权重** — 沿用现有 `find_related_problems()` 算法，调整默认权重优先级：`physics_model_tags` 同类 → `math_technique_tags` 同类 → `heuristic_tags` 同类 > 跨分类 tag（cross_category × 0.5）。不引入用户可选 `--mode`（v1 保持简单）。
- **D-04：默认参数** — `max_results=10, min_shared_tags=1`。REPL 通过 `/set related.max` 可持久化修改 max_results。

### 组卷编排文件（SKILL-COMPOSE）

- **D-05：编排文件格式** — YAML，与项目其它 `skill.yml` 使用同一 PyYAML loader，格式校验用 Pydantic StrictModel。
- **D-06：存放位置** — 默认 `.cpho/compositions/<name>.yml`；用户可在 CLI/REPL 调用时通过路径参数覆盖。`cpho compose new --count N --name <name>` 生成 stub 模板。
- **D-07：题位 schema** — 每个 slot 用 `slot: <int>` 作键，内容三选一：
  ```yaml
  slots:
    1:
      problem_id: "prob_abc123"   # 显式指定
    2:
      pass: true                  # 跳过此题位（输出留空）
    3:
      spec:                       # 自动填充
        topic: "力学/天体运动"
        tags: ["牛顿定律"]
        requirement: "中等难度"   # 可选，自然语言
  ```
  Pydantic 强校验，不符合三选一即报错。

### PDF 拼接与布局（SKILL-COMPOSE）

- **D-08：拼接库** — pymupdf（fitz），已在 `pyproject.toml` 依赖中，使用 `Document.insert_pdf(src, from_page, to_page)` 做页面裁剪拼装，零额外依赖。
- **D-09："一页一题"** — 每题各占整数页，若原题跨多页则原样保留多页，不做缩放或拼接到单页。符合"不重渲染"原则，忠实原版式。
- **D-10：题号呈现** — 不在页面加水印，在输出 PDF 的 **outline（书签）** 中写 `第 N 题`，方便 PDF 阅读器跳转，保持页面原版式。
- **D-11：输出位置** — `.cpho/exports/compose/<编排名>-题目.pdf` 和 `.cpho/exports/compose/<编排名>-答案.pdf`（隐藏目录，因为是工具中间/输出产物，对齐 `.cpho/traces/` 等已有约定）。用户可通过 `--output <dir>` 覆盖。

### 自动选题策略

- **D-12：触发方式** — 两种都支持：编排文件每个 slot 写 `spec` 按需自动填；`cpho compose auto --count N --topic <X>` 全自动（等价于所有 slot 均为 `spec`）。
- **D-13：多样性** — v1 只做去重：同一 `problem_id` 在同一张试卷中不出现两次；不强制 `physics_model_tag` 数量上限（保持简单，等用户反馈再加）。
- **D-14：选不到题** — 报错并列出实际可选题目数，不自动放宽过滤，不静默跳过，让用户修改 spec。

### 异常边界（ROBUST-BOUNDARY）

- **D-15：Checkpoint 粒度** — step 级：每个 DAG step 完成后立即落盘 blackboard checkpoint，Ctrl+C 在 `finally` 块保证最后一次 checkpoint 写完再退出。
- **D-16：Checkpoint 位置** — `.cpho/runs/<skill>/<problem_id>/<run_id>.json`，与现有 `.cpho/traces/` 同层。下次运行同 skill 同 problem 时，若发现未完成 run，提示"发现未完成的 run（<run_id>），继续/丢弃"。
- **D-17：LLM/OCR 失败重试** — 自动 3 次指数退避（1s/2s/4s），三次均失败后透传原始错误并把当前 blackboard 落盘（含失败 step 信息），用户可通过 resume 重入。
- **D-18：文件越界 / 挂载丢失** — 在 SkillRuntime 入口 + REPL command 入口统一调用 `_ensure_in_workspace(path)` 工具函数（比较 `path.resolve()` 是否在 `workspace.resolve()` 子树）；每次重 IO 操作前调 `path.exists()` 探测挂载状态；两类错误均以中文提示，不让 OS 原生异常裸冒泡。

### Claude's Discretion

- `run_id` 的生成策略（UUID / 时间戳 / 哈希）由 planner 根据现有 trace 命名约定决定。
- 软链接路径在 `_ensure_in_workspace` 中的处理方式（`resolve()` 后再比较，还是拒绝软链接）由 planner 决定。
- REPL `/search-related` 命令的参数设计（是否支持 `--top N` 覆盖 max_results）由 planner 按现有命令风格决定。
- `cpho compose new` stub 模板的具体 YAML 内容格式由 planner 决定，须满足 D-07 schema。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 需求与路线图
- `.planning/ROADMAP.md` — Phase 4 Goal + Success Criteria（4 项）；Phase 3 跨切面能力（CROSS-EXPORT / CROSS-FOLLOWUP / CROSS-PROGRESS，Phase 4 skill 直接继承）
- `.planning/REQUIREMENTS.md` — SKILL-RELATED, SKILL-COMPOSE, ROBUST-BOUNDARY 完整描述
- `.planning/PROJECT.md` — 项目约束（Python only、本地优先、芯-壳分离、优先复用开源库）
- `docs/new-understanding-2026-05-26.md` — 用户对组卷、找同类题、异常边界的原始设计意图（MUST READ）

### 前期阶段上下文
- `.planning/phases/02.3-index-solve-solvereport-index-golden-tests-index-api-skills/02.3-CONTEXT.md` — D-03~D-09 标签读写 API + user_tags 分离存储 + provenance；D-12~D-14 SkillRuntime / llm / python_tool handler 模式
- `.planning/phases/02.2-tui-repl-repl-tui-inserted/02.2-CONTEXT.md` — D-02/D-03 命令注册架构（REPL skill 命令遵循同一模式）；D-07 芯-壳分离目录结构

### 核心 API（必读）
- `src/cpho_cli/core/index/api.py` — `find_related_problems(workspace, problem_id, *, min_shared_tags, max_results, same_category_weight)` 现有实现；`add_problem_tags()` / `remove_problem_tags()`
- `src/cpho_cli/core/index/compose.py` — `compose_problem_list(workspace, *, topic_path, tag_ids)` 现有过滤器（Phase 4 组卷 spec 填充在此基础上扩展）
- `src/cpho_cli/core/index/topic_api.py` — `find_problems_by_topic()` / `get_topic_tree()`

### 数据模型
- `src/cpho_cli/models/documents.py` — `ProblemEntry.problem_page_range / answer_page_range`（组卷裁页的页码来源）；`PaperFile`
- `src/cpho_cli/models/index.py` — `IndexEntry`（`physics_model_tags / math_technique_tags / heuristic_tags / user_tags`）

### SkillRuntime
- `src/cpho_cli/core/runtime.py` — DAG 执行引擎；Ctrl+C 在 `finally` 块落盘 checkpoint 的扩展点
- `src/cpho_cli/core/skill_handlers.py` — llm / python_tool handler 实现（Phase 4 skill 复用）
- `src/cpho_cli/core/workspace.py` — `discover_workspace()`；`_paper_total_pages()` pymupdf 读页数逻辑（组卷可复用）

### CLI / REPL 结构
- `src/cpho_cli/cli/app.py` — 现有 `compose` 命令（Phase 4 重写/扩展）；`topic browse`
- `src/cpho_cli/cli/repl/commands/` — REPL 命令注册模式（找同类题 `/search-related` 遵循同一模式）

### 依赖
- `pyproject.toml` — pymupdf（fitz）已在依赖中，无需新增即可做页裁剪拼装

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `core/index/api.py:find_related_problems()` — 已实现 tag overlap 打分，Phase 4 只需调整 physics_model 权重并包装成 skill
- `core/index/compose.py:compose_problem_list()` — 已实现 topic + tag 交集过滤，组卷 spec 自动选题在此基础上扩展
- `core/workspace.py:_paper_total_pages()` — 用 fitz 读 PDF 页数，组卷拼接可复用同一 fitz 使用模式
- `core/runtime.py:SkillRuntime` — DAG 引擎，Phase 4 两个 skill 直接在 `builtin_skills/` 下用 YAML 定义步骤
- `core/skill_handlers.py` — llm / python_tool handler，Phase 4 skill 步骤复用

### Established Patterns
- **芯-壳分离**：组卷 PDF 生成逻辑在 `core/compose_pdf.py`（新建），CLI/REPL 做薄包装
- **Pydantic StrictModel**：编排文件 schema（`CompositionFile / SlotSpec`）用 StrictModel 校验
- **handler 注册**：找同类题 / 组卷 skill 的 DAG 步骤都注册为 SkillRuntime handler，不写硬编码逻辑
- **中文 UX**：所有用户提示、错误信息默认中文

### Integration Points
- **Phase 3 跨切面**：CROSS-EXPORT / CROSS-FOLLOWUP / CROSS-PROGRESS 已在 Phase 3 落地，Phase 4 skill 注册时直接挂载跨切面 wrapper，不重复实现
- **REPL SessionState**：`SessionState.last_related` 新增字段，存储最近一次找同类题结果，供 `/compose --from last-related` 读取
- **`.cpho/runs/` checkpoint 目录**：新建，与 `.cpho/traces/` 同层，SkillRuntime 的 `finally` 块写入
- **`_ensure_in_workspace(path)`**：新建工具函数，在 `core/workspace.py` 或独立 `core/boundary.py`，SkillRuntime 入口 + 每个 REPL command handler 都调用

</code_context>

<specifics>
## Specific Ideas

- 找同类题输出表格列：题目 ID / 相似度分数 / physics_model_tags（前 2 个）/ topic_path / 来源文件，对齐 `/search` 命令的现有表格风格。
- 编排文件 stub 模板由 `cpho compose new --count N --name <name>` 生成，每个 slot 预填 `spec: {}` + 注释示例，让用户改 problem_id 或保留 spec。
- 组卷 PDF 书签命名：`第 N 题`（题目卷）/ `第 N 题 答案`（答案卷），嵌套在 `cpho compose` 输出日志里打印最终文件路径。
- 异常提示风格：与现有中文提示对齐，例如 `错误：文件不在当前工作空间（{workspace}）：{path}`；`工作空间不可用，请检查外接硬盘连接：{workspace}`。
- 恢复 prompt 风格：`发现未完成的 <skill> 运行（{run_id}，已完成 {n}/{total} 步）。[继续] [丢弃]`。

</specifics>

<deferred>
## Deferred Ideas

- **难度控制**（v1 不做）：按 `difficulty_aspects` 标签或编排文件 `difficulty: easy/mid/hard` 字段筛选，等用户反馈再加入 Phase 4 迭代或独立 phase。
- **physics_model_tag 数量上限**（多样性 v2）：组卷自动选题时同一物理模型题目数量上限，v1 只去重 problem_id，v2 根据反馈加入。
- **软链接 workspace 支持**：`_ensure_in_workspace` 对软链接目录的完整处理，v1 用 `resolve()` 后比较，如有软链接跨 workspace 场景再专门设计。
- **`unverified` 标签提升为 canonical 的 UI**：遗留自 Phase 02.3，Phase 4 不做，留待后续 phase。
- **找同类题 `--mode strict/loose` preset**：用户按相似度精细调整的需求，v1 不做，v2 按反馈加入。

</deferred>

---

*Phase: 04-找同类题 + 组卷 + 异常处理*
*Context gathered: 2026-05-26*
