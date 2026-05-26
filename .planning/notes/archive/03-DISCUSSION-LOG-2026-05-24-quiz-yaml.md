# Phase 3: Skill System + Core Skills - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-24
**Phase:** 3-skill-system-core-skills
**Areas discussed:** Skill Runtime 统一策略, SkillRuntime Step Kind 扩展, Skill 发现机制, CLI 命令模型, Explain 模式输出

---

## Skill Runtime 统一策略

| Option | Description | Selected |
|--------|-------------|----------|
| A. 全面统一 | 重构 solve 使其通过 SkillRuntime 执行，所有新 skill 也走 SkillRuntime | |
| B. 渐进式（基础） | solve 保持现状不动，explain 和 quiz 用 SkillRuntime 新写 | |
| C. 薄封装 | 每个 skill 仍是独立 Python 函数，共用 LLM/index/OCR 调用 | |

**User's choice:** B+（渐进式 + 共享层）
**Notes:** solve 已验证可用，Phase 3 核心交付是 explain/quiz 质量和 YAML 自动发现，不应变成"重构老功能 + 做新 skill"。但 B 不能变成简单重复代码——要求抽出共享 `ProblemContextBuilder` / `load_problem_context` 层，统一准备题目上下文（problem_id、OCR text、answer text、canonical tags、topic、source paper、related problems）。explain/quiz 不复制 solve 的 OCR/answer/index loading 逻辑。未来迁移 solve 到 SkillRuntime 也可复用。

---

## SkillRuntime Step Kind 扩展

| Option | Description | Selected |
|--------|-------------|----------|
| A. 只加必需的 | 新增 `index_query` kind，quiz 交互循环不走 DAG | ✓ |
| B. 扩展多种 kind | `index_query`、`user_prompt`、`condition_branch` 等 | |
| C. 用 python_tool 承载 | 所有非 LLM 操作用 python_tool + handler 注册 | |

**User's choice:** A
**Notes:** 索引检索是 cpho-cli skill 的核心能力，不应该隐藏在 python_tool handler 里。YAML skill 应能清晰表达"从索引加载题目 → LLM 分析 → 结构化输出"。`index_query` 最小支持 `get_problem_entry`、`query_index`、`find_related_problems`。quiz 的交互循环不应塞进 DAG——DAG 适合静态流程，quiz 的"提问 → 读回答 → 判断 → 追问"是 REPL 状态机，由薄 Python 主循环负责。quiz 内部可调用小型 DAG 或 LLM step，但不为此扩展 `user_prompt`、`condition_branch`、`loop` 等复杂 workflow 能力。

---

## Skill 发现机制

| Option | Description | Selected |
|--------|-------------|----------|
| A. 单一工作空间路径 | `<workspace>/.cpho/skills/` 唯一用户 skill 目录 | |
| B. 全局 + 工作空间双层 | `~/.cpho/skills/` + `<workspace>/.cpho/skills/` + builtin | ✓ |
| C. B + pip entry points | B + 第三方包通过 entry points 注册 | |

**User's choice:** B
**Notes:** 优先级 workspace > global > builtin。路径：`builtin_skills/`、`~/.cpho/skills/`、`<workspace>/.cpho/skills/`。常用 skill 跨 workspace 复用，项目特定 skill 覆盖全局同名 skill。Phase 3 不做 pip entry points（PLUGIN-04 属于 Phase 4）。同时实现 `cpho skills list`，显示 skill 名称、来源、路径、覆盖关系和加载错误。

---

## CLI 命令模型

| Option | Description | Selected |
|--------|-------------|----------|
| A. 每 skill 一个子命令 | `cpho explain`、`cpho quiz`，各自独立实现 | |
| B. 统一 cpho run | `cpho run <skill-name> <problem>` 通用入口 | |
| C. 混合模型（基础） | 内置核心有专属命令，用户 YAML skill 用 `cpho run` | |

**User's choice:** C+（混合 + 统一 registry）
**Notes:** `cpho explain` 和 `cpho quiz` 是高频核心价值入口，有专属子命令；`cpho run <skill-name>` 运行所有自动发现的 YAML skill。关键要求：explain 和 quiz 本身也必须注册进统一 skill registry，`cpho explain` 应该是 `cpho run explain` 的快捷封装——不出现两套执行逻辑。未来 REPL 的 `/explain` 和 `/run my_skill` 也从同一 registry 解析。

---

## Explain 模式输出

| Option | Description | Selected |
|--------|-------------|----------|
| A. 一次性完整报告（基础） | LLM 一次性输出完整推导 Markdown | |
| B. 分步交互式 | 输出第一步 → 用户回车看下一步 → 每步可追问 | |
| C. 混合 | 默认完整报告，每步标注追问标记 | |

**User's choice:** A+（结构化 step report）
**Notes:** Phase 3 MVP 默认输出一次性完整报告（最容易交付、最方便阅读、最适合 golden test 回归验证）。但不能是普通大段 Markdown——必须是结构化 step report，每步有 `step_id`、`derivation`、`why_this_step`、`possible_confusion`、`check_question`。既满足"逐步讲解"要求，又为 REPL 中按 step_id 追问预留入口。Phase 3 不做完全分步交互式 explain，交互追问等 Phase 02.2 REPL 和 quiz 模式稳定后再增强。

---

## Claude's Discretion

- `ProblemContextBuilder` 的具体 API 签名、返回类型
- `index_query` step kind 的 handler 注册方式和 skill.yml schema
- Skill registry 的内部数据结构
- quiz 交互循环的具体状态机设计

## Deferred Ideas

- solve 迁移到 SkillRuntime → 后续 phase
- `user_prompt` / `condition_branch` / `loop` step kind → 后续 phase
- pip entry points skill 发现 → Phase 4
- 分步交互式 explain（REPL 追问）→ Phase 02.2 + 后续增强
- 用户错题本编辑交互 → 后续 phase
- Review/refinement skill → 后续 phase
- Q&A 历史作为标签来源 → 后续 phase
