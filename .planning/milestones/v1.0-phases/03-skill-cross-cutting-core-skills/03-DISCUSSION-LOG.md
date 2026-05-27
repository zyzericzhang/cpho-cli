# Phase 3: Skill 跨切面 + 核心讲解 Skills — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-26
**Phase:** 03-skill-cross-cutting-core-skills
**Areas discussed:** A. 跨切面三件套, B. Solve 重定位, C. Explain 增强, D. 主动提问 Skill (Probe), E. SkillRuntime 架构

---

## A. 跨切面三件套（导出 / Follow-up / 进度）

### A1. Markdown 导出默认存放位置

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) workspace 内 `outputs/` | 与题目共存，跟 workspace 一起备份 | |
| (b) XDG `~/.local/share/cpho/outputs/...` | 不污染题库；与 Phase 02.2 XDG 持久化一致 | ✓ |
| (c) CWD 下 `./cpho-out/` | 最容易看到 | |

**用户选择：** (b) 推荐
**备注：** 用户可通过 `/set out.dir` 覆盖。

---

### A2. Follow-up 对话模式实现

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) REPL inline 子模式（提示符变 `cpho:followup>`） | 复用现有 prompt_toolkit，无新依赖 | ✓ |
| (b) 独立 PromptSession，历史不留 | 干净但上下文不持久 | |
| (c) LangChain/litellm 现成框架 | 多轮 memory 现成 | |

**用户选择：** (a) inline 子模式
**备注：** 用户主动要求深度分析 (c) 的弊端后，确认选 (a)。核心原因：LangChain 引入 30+ 传递依赖、与现有 `core/llm.py` 冲突、Follow-up 需求只是 8 行 Python，无需大框架。

---

### A3. 进度显示实现

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) 引入 `rich` 库（Spinner/Live） | Claude Code 同款；非 TTY 自动降级 | ✓ |
| (b) 手写 ANSI（复用 `make_index_progress_printer`） | 零新依赖 | |
| (c) 极简纯文本 `[2/7] step_name (3.1s)` | 最简单但效果打折 | |

**用户选择：** (a) 推荐

---

## B. Solve 重定位

### B1. 标答错误 tag 词表来源

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) 复用现有 heuristic_tags | 零新结构 | |
| (b) 新建 `error_taxonomy.yml` + `skill_error_tags` bucket | 独立命名空间，语义清晰 | |
| (c) 不进受控词表，存自由文本 discrepancies 列表 | 最灵活 | ✓ |

**用户选择：** (c) 自由文本
**备注：** 用户选择不强制受控词表，保持灵活性。与 new-understanding §二"错误以 tag 形式记录"的措辞有出入，但用户明确选 (c)。

---

### B2. Solve 写 tag 的时机

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) 直接写（无人值守） | 简单；批量友好 | |
| (b) 展示候选 → 用户 confirm 后写入 | 质量可控；与 Explain 回写模式一致 | ✓ |
| (c) 写 pending 暂存层，独立 review 命令审核 | 解耦但复杂 | |

**用户选择：** (b) 推荐，支持 `--auto-confirm` flag

---

### B3. Solve 执行入口与 DAG 改造

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) 替换 `cpho solve`，同名入口，行为改变 | 入口干净 | ✓（与 c 组合） |
| (b) 保留旧 `cpho solve`，新建 `cpho solve-check` | 渐进式迁移 | |
| (c) 保留入口名，重写 DAG steps 为挑错向 | 一步到位 | ✓（与 a 组合） |

**用户选择：** (a)+(c) 推荐组合

---

## C. Explain 增强

### C1. 多 Tone 并发策略 + 输出文件组织

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) 串行调用 N 次 | 最简单 | |
| (b) asyncio 并行 | 3 Tone 几乎同耗时出完 | ✓ |
| (c) 串行流式 | 打字机效果但仍串行 | |

**用户选择：** (b) asyncio 并行，**且要求各自独立流式输出**（用户主动补充，在推荐基础上加了流式需求）

| 文件组织 | 选中 |
|---------|------|
| (d) 每 Tone 独立文件 | |
| (e) 合并单文件（每 Tone 一个 section） | ✓ |

**用户选择：** (e) 合并单文件

---

### C2. 分栏目 × 句子级 explain 执行模型

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) 每栏单独 LLM 调用（3 个步骤） | 质量高，可并行 | |
| (b) 单次大 prompt 一次出三栏 | 调用次数少 | |
| (c) 两阶段：主推导+超越 → 句子级 | 质量平衡，句子级有前文上下文 | ✓ |

**用户选择：** (c) 推荐

---

### C3. 回写 Index 交互方式

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) confirm 列表 + 用户可自写 tag | 质量可控；与 B2 一致 | ✓ |
| (b) 直接写入不 confirm | 无摩擦但违背用户原话 | |
| (c) pending 层批量审核 | 解耦但复杂 | |

**用户选择：** (a) 推荐

---

## D. 主动提问 Skill (Probe)

### D1. 对话深度控制

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) 固定 N 轮（默认 5） | 可预期 | |
| (b) 用户显式退出 + 软上限 10 轮 | 用户驱动 + 防呆 | ✓ |
| (c) LLM 自评覆盖度 + 上限 | 质量驱动 | |

**用户选择：** (b) 推荐（全部按推荐）

---

### D2. Markdown 输出时机

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) 每轮增量 append | 可恢复；防丢失 | ✓ |
| (b) 结束时一次性 dump | 文件始终完整 | |
| (c) 增量 append 问题，结束后回填解答 | 结构完整 + 可恢复 | |

**用户选择：** (a) 推荐

---

### D3. Probe 触发方式

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) 独立 `/probe` 命令 | 边界清晰 | |
| (b) 仅作为 Explain 后续 | 强化推荐流程 | |
| (c) 双入口：独立 `/probe` + Explain 后提示 | 最灵活 | ✓ |

**用户选择：** (c) 推荐

---

## E. SkillRuntime 架构调整

### E1. Tone 参数化与 runtime 扩展

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) 调用层 asyncio.gather，不改 runtime | 最小侵入 | ✓ |
| (b) Runtime 加 fan_out/fan_in step 类型 | 原生并行支持 | |
| (c) Explain 完全跳过 SkillRuntime | 自由但失去 trace | |

**用户选择：** (a)

---

### E2. Skill 间共享 context

| 选项 | 描述 | 选中 |
|------|------|------|
| (a) 通过 index skill-tag 层传递 | 持久化；跨会话可用 | |
| (b) SessionState 热路径（同会话）| 最简单 | |
| (c) SessionState 热路径 + 可选持久化到 index | 最灵活 | ✓ |

**用户选择：** (c)

---

## Claude's Discretion

- Explain DAG 内每个 Tone 的 trace 文件命名规则（`03-explain-teacher-trace.jsonl` 等）
- Solve confirm UI 与 Explain 回写 confirm UI 的具体组件接口设计（`display.confirm_list(…)` 参数）
- rich Live 面板的并排布局 vs 顺序布局（多 Tone 同时流式时）

## Deferred Ideas

- 批量 solve 跨题目模式 → Phase 4
- Explain 跨会话历史（Tone 缓存）→ Phase 4
- Probe 导出 Anki/Obsidian 格式 → 超出范围
- `provider.stream()` 非 OpenRouter 实现 → Phase 4+
