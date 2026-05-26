# Phase 3: Skill 跨切面 + 核心讲解 Skills — Context

**Gathered:** 2026-05-26
**Status:** Ready for planning

<domain>
## Phase Boundary

在 Phase 02.2 REPL + Phase 02.3 Index 读写 API 基础上，交付：

1. **跨切面三件套**（所有 skill 共用）：Markdown 导出 / Follow-up 对话 / 运行过程进度显示
2. **Solve 重定位**：不再返回新解法，而是给工作空间内已提供的标准答案做逐步审查；发现的问题以自由文本形式写入 SessionState 并可选持久化到 index
3. **Explain 增强**：多 Tone（老师型/密集型/简短型）asyncio 并行生成，各自流式输出，合并单文件；分两阶段（主推导+超越原答案 → 句子级 explain）；完成后 confirm 回写 Index skill-tag 层
4. **主动提问 Skill (Probe)**：连续对话寻找关键点，增量落盘，双入口

本 Phase **不包含**：找同类题、PDF 组卷、异常边界（Phase 4）；用户手册、开源准备（Phase 5）。

</domain>

<decisions>
## Implementation Decisions

### A. 跨切面三件套

- **D-01 Markdown 导出默认路径**：XDG `~/.local/share/cpho/outputs/<workspace_hash>/<skill>/<problem_name>.md`；用户可通过 `/set out.dir <path>` 覆盖为任意目录（包括 workspace 内或 CWD）。每类 skill 有各自默认子目录名。文件名必须含题目名（problem_id / 题目标题）。
- **D-02 Follow-up 模式实现**：REPL inline 子模式。Skill 结束后提示符变为 `cpho:followup>`；输入 `/exit` 或连续两次空行退出，返回主 REPL。Follow-up 历史可选 append 到当次 skill 的 markdown 导出文件末尾。不引入 LangChain / litellm——follow-up 本质是"在 skill 输出上下文上多轮 `provider.complete` 调用"，用现有 `core/llm.py` 自建即可。
- **D-03 进度显示**：引入 `rich` 库（仅用于 `Spinner` + `Live`）。非 TTY 环境 rich 自动降级为纯文本。显示内容：当前 step 名 / 正在做什么 / 已耗时。风格类似 Claude Code。

### B. Solve 重定位

- **D-04 错误记录方式**：不进受控词表，用自由文本 `discrepancies` 列表记录每处发现的问题（数值错误/符号错误/物理图像错误/单位错误等 LLM 自由描述）。与 B1 决定一致：不强制受控 tag，保持灵活。
- **D-05 写入时机**：Solve 跑完后展示候选 discrepancies 列表，用户 `[y]/[n]/[edit]` 逐项 confirm 后才写入 SessionState（热路径）；支持 `--auto-confirm` flag 供批量场景跳过确认。
- **D-06 执行入口与 DAG**：保留 `cpho solve` 命令名 + REPL `/solve`，但 DAG steps 全面重写为"挑错向"。新 DAG 参考结构：`extract_official_steps → check_each_step → classify_error_types → propose_discrepancies → assemble_solve_report`。旧 prompt 文件（`normalize.md.j2` 等）可参考但需按新语义重写。

### C. Explain 增强

- **D-07 多 Tone 并发 + 流式输出**：调用层用 `asyncio.gather` 对每个选中的 Tone 各跑一次完整 `SkillRuntime.run()`（不改 runtime 核心）。每个 Tone 独立流式输出（`provider.stream()`）；rich Live 面板同时渲染 N 个 Tone 的打字机效果（并排或顺序渲染）。所有 Tone 完成后合并进单一 `.explain.md` 文件（每 Tone 一个 `## Tone: 老师型` section）。
- **D-08 分栏目执行模型（两阶段）**：
  - 阶段一（每 Tone 1 次 LLM 调用）：同时输出"原答案逐步讲解" + "超越原答案的更清晰推导（若有）"
  - 阶段二（每 Tone 1 次 LLM 调用，依赖阶段一输出）：专门做句子级 explain（输入：阶段一全文 + 原题）
  - 每 Tone 共 2 次调用；多 Tone 并行时总调用数 = 2 × N
- **D-09 Explain prompt 原则（来自 new-understanding 锁定）**：
  - 首段固定：整道题物理图像 + 解题思路描述
  - 总是先物理图像/架构描述 → 再推导逻辑 → 再完整推导
  - 物理为主，数学为辅
  - 三种 Tone 的 prompt 各写一版：老师型（引导性/"我们看"/设问自答）、知识点密集型（完整物理思维+详细数学推导）、简短型（最短最重要的物理过程和推导逻辑）
- **D-10 回写 Index 交互**：Explain 完成后展示候选 tag（LLM 从讲解中提取），用户逐项 `[y]/[n]` confirm；支持用户在 confirm 时输入 `+<tag_name>` 追加自写 tag。最终调用 `add_problem_tags(source="explain", provenance=…)`，走现有 Phase 02.3 `skill_tags` 路径。

### D. 主动提问 Skill (Probe)

- **D-11 对话深度控制**：用户显式退出（`/exit` 或连续两次空行）；软上限默认 10 轮，到上限后提示"已达最大轮次，是否继续？"而非强制截断；上限可通过 `/set probe.max_rounds N` 配置。
- **D-12 Markdown 输出时机**：每轮 Q+A 完成后立即 append 到文件（增量落盘，防崩溃丢失）。对话结束后生成最终版文件：前半部分为所有问题、后半部分为对应解答（重新排版）。
- **D-13 触发入口（双入口）**：
  - 独立 `/probe <problem_id>` 注册为正式 REPL 命令（与 `/solve` `/explain` 并列）
  - Explain 完成后提示一行："→ 进入 Probe 模式？(`/probe` 或 Enter 跳过)"

### E. SkillRuntime 架构

- **D-14 Tone 并行不改 runtime**：`asyncio.gather` 在 Explain 调用层管理，`SkillRuntime` 不感知 Tone。每个 Tone 有独立 trace 文件（便于单 Tone 重试）。不引入 `fan_out/fan_in` 概念，Phase 3 不需要。
- **D-15 Skill 间共享 context（两层）**：
  - **热路径**（同会话）：Solve 跑完后把 `SolveReport`（含 discrepancies）存入 `SessionState`；同一 REPL 会话内 Explain/Probe 直接从 `session.current_solve_report` 读取
  - **可选持久化**：Solve confirm 结束后提示"是否把本次发现持久化到 index？"，用户选择后调 `add_problem_tags(source="solve", provenance=…)` 写入；下次跨会话 Explain 可从 index 读取历史 solve 发现
  - Solve discrepancies（自由文本）存 SessionState 字段，不强制进 tag 词表

### 运行顺序（已锁定）

- **D-16** Solve 优先于其他 skill——其他 skill（Explain/Probe）默认在 Solve 校正过的标答基础上工作。REPL 如果检测到当前题目没有 solve 记录，在 `/explain` `/probe` 启动时给出提示（非强制阻断）。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 核心需求与设计原则
- `docs/new-understanding-2026-05-26.md` — Phase 3 全部功能的原始设计意图（确定设计 / 大致思路 / 公开提问 三分类）；**必读**，尤其 §二（Solve）§三（Explain）§四（Follow-up）§五（Probe）§九（导出/进度/依赖库）§十（runtime 架构）
- `.planning/REQUIREMENTS.md` §Phase 3 — SKILL-SOLVE-REPOSITION / SKILL-EXPLAIN-NEW / SKILL-PROBE / CROSS-EXPORT / CROSS-FOLLOWUP / CROSS-PROGRESS / CROSS-ORDER 6 项需求定义
- `.planning/ROADMAP.md` §Phase 3 — 6 项 Success Criteria（验收门槛）

### 现有 Index 读写 API（Solve/Explain 回写依赖）
- `src/cpho_cli/core/index/api.py` — `add_problem_tags` / `update_problem_tags` / `remove_problem_tags` / `find_related_problems`；skill-tag 与 LLM 机打 tag 分离的 provenance 模型
- `src/cpho_cli/models/index.py` — `IndexEntry` / `UserTagEntry` 数据模型；skill_tags bucket 结构

### SkillRuntime（DAG 执行引擎）
- `src/cpho_cli/core/runtime.py` — `SkillRuntime`（DAG 拓扑排序 + trace + checkpoint）；Phase 3 不改此文件
- `src/cpho_cli/core/skill_handlers.py` — `make_llm_handler`（Jinja2 prompt + multimodal + pydantic response）；Explain/Probe/Solve 新 skill 的 handler 工厂

### REPL 基础设施
- `src/cpho_cli/cli/repl/commands/builtin_skills.py` — Phase 3 placeholder（当前存 `/explain` `/quiz` stub），Phase 3 实现替换此文件
- `src/cpho_cli/cli/repl/session.py` — `SessionState`；D-15 要求在此加 `current_solve_report` 字段
- `src/cpho_cli/cli/repl/display.py` — 现有 `make_index_progress_printer`（ANSI 模式）；Phase 3 改用 rich Live 替代

### 现有 Solve Skill（重写参考）
- `src/cpho_cli/builtin_skills/solve/skill.yml` — 当前 7 步 DAG；Phase 3 重写为挑错向 5 步，参考结构但语义全换
- `src/cpho_cli/builtin_skills/solve/prompts/` — 旧 prompt 文件参考；新 prompt 按 D-06 新 DAG 重写

### 依赖说明
- `pyproject.toml` — 当前生产依赖列表；Phase 3 新增 `rich>=13.0`（D-03）；`asyncio` 标准库无需新增

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/cpho_cli/core/index/api.py:add_problem_tags` — Solve confirm 写 discrepancies / Explain 回写 tag 的统一入口；已支持 `source` + `provenance` 参数
- `src/cpho_cli/cli/repl/commands/builtin_skills.py` — Phase 3 skill 命令在此注册；`/explain` `/quiz` 占位符直接替换
- `src/cpho_cli/cli/repl/display.py:make_index_progress_printer` — 进度打印思路参考（ANSI 多行刷新）；Phase 3 用 rich Live 实现同效果
- `src/cpho_cli/core/skill_handlers.py:make_llm_handler` — Jinja2 + pydantic + multimodal 的 LLM handler 工厂；Explain/Probe/新 Solve 的 handler 直接复用此工厂
- `src/cpho_cli/cli/repl/persistence.py` — XDG 路径管理（与 D-01 markdown 导出路径逻辑复用）

### Established Patterns
- **DAG skill 结构**：每个 skill 是 `skill.yml`（step 定义）+ `prompts/*.md.j2`（Jinja2 模板）+ `SKILL.md`（说明）+ `skill_handlers.make_llm_handler` 执行。Phase 3 三个新 skill 沿用此模式。
- **REPL command 注册**：`Command(name, help, usage, handler, category)` + `register(registry)` 函数。`/solve` `/explain` `/probe` 按此注册。
- **Async handler**：REPL command handler 已是 `async def do_xxx(session, args)`，asyncio.gather 可直接在 handler 内使用。
- **XDG 持久化**：Phase 02.2 的 session history / IndexMeta 用 `~/.local/share/cpho/` 路径；D-01 markdown 导出复用同前缀。

### Integration Points
- `SessionState`（`session.py`）加 `current_solve_report: SolveReport | None` 字段（D-15 热路径）
- `provider.stream()` 方法需要在 `core/llm.py` 的 `LLMProvider` 接口上新增（C1 流式输出要求）
- `rich` 依赖加入 `pyproject.toml`；`display.py` 引入 `rich.live.Live` + `rich.spinner.Spinner`
- Explain skill 的 `asyncio.gather` 调用在 REPL command handler 层（非 runtime 层）

</code_context>

<specifics>
## Specific Ideas

- **Explain 分栏目输出样式**（来自 new-understanding §三）：每个 Tone 版本的 markdown 文件内，栏目固定为：① 整道题物理图像与思路（首段，所有 Tone 必有）② 原答案逐步讲解 ③ 超越原答案的更清晰推导（若无则注明"原答案推导已足够清晰"）④ 句子级 explain（逐句解释关键推导句）
- **Probe 文件结构**（来自 new-understanding §五）：markdown 文件前半为所有问题列表（`## 问题`），后半为对应解答（`## 解答`），一一对应编号
- **Explain Tone 提示风格**：老师型用"我们看"/"大家思考一下"类引导语 + 设问自答；密集型直接陈述物理思维链 + 详细数学推导；简短型只陈述最关键物理过程，省去数学推导展开
- **Follow-up 提示符**：主 REPL = `cpho> `，Follow-up 子模式 = `cpho:followup> `，退出方式：`/exit` 或连续两次空行
- **Solve confirm UI**：与 Explain 回写 tag confirm UI 共用同一套交互组件（`display.confirm_list(items, allow_edit=True, allow_append=True)`），Phase 3 统一实现

</specifics>

<deferred>
## Deferred Ideas

- **批量 solve 跨题目模式**（连续对多道题目运行 solve）— 属于 Phase 4 工作流范畴
- **Explain 跨会话历史（Tone 缓存/增量更新）** — Phase 4 边界处理阶段考虑
- **Probe 对话导出到 Anki/Obsidian 格式** — 超出当前 Phase 范围
- **provider.stream() 的非 OpenRouter 实现** — Phase 3 仅需 OpenRouter 路径，其他 provider 流式支持留 Phase 4+
- **已废弃旧 Phase 3 思路（Quiz/YAML）** — 归档于 `.planning/notes/archive/03-CONTEXT-2026-05-24-quiz-yaml.md`

</deferred>

---

*Phase: 3-skill-cross-cutting-core-skills*
*Context gathered: 2026-05-26*
