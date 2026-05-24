---
title: TUI 设计决策
date: 2026-05-24
context: /gsd-explore 讨论 cpho TUI 方向后记录
---

## 背景

用户希望在主体功能完成后为 cpho 打造 TUI 界面，核心诉求是加新功能时 TUI 维护成本尽量低。

## 决策

### D1: REPL + 斜杠命令模式

**选型:** 类似 Claude Code 的 REPL 交互（`> /search 力学`），而非 Dashboard 面板或 Wizard 向导。

**理由:** 用户的日常工作流是"查题 + 解析"，REPL 模式加功能 = 注册命令 + 注册补全规则，无需改布局——TUI 维护成本最低。

**参考文件:** `docs/tui-repl-pattern.md`

### D2: Skill 即意图层

**选型:** REPL 中的 `/` 命令是高层意图抽象（如 `/analyze`），自动编排底层步骤（OCR → LLM → 标签 → 入库），不是 CLI 子命令的简单搬运。

**理由:** 用户已有 `split`、`ocr`、`tag`、`index` 等底层命令。REPL skill 应该组合这些步骤，让用户表达"做什么"而非"怎么做"。

### D3: 有状态会话

**选型:** REPL 会话内搜索结果、当前题目等上下文跨命令共享。

**理由:** 支持自然交互流——先 `/search` 找到 5 道题，然后直接说 `/show 第3题`，不需要重复指定 ID。

### D4: 时机

**选型:** Phase 02.1 完成后，用 `/gsd:quick` 搭最小 REPL 骨架（`/search` + `/show`），后续每个 phase 顺带加对应的 skill 命令。

**理由:** 不需要等全部主体功能完成，早期骨架出来能及时验证 TUI 架构方向是否正确。
