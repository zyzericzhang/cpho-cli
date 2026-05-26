---
title: 最小 REPL 骨架
trigger_condition: Phase 02.1 完成，用户执行 /gsd:quick 启动
planted_date: 2026-05-24
---

## 做什么

在 Phase 02.1 完成后，搭一个最小 REPL 骨架，包含：

- 基于 `prompt_toolkit` 的 REPL 主循环（`cpho repl` 入口）
- 两个 skill: `/search`（按标签/关键词查题）和 `/show`（显示题目详情）
- 有状态会话（搜索结果上下文跨命令共享）
- Skill 注册机制（新 skill = 新命令 + 补全规则，无 UI 改动）

## 为什么是最小骨架而不是完整 TUI

- 早期验证 REPL 架构方向
- 让后续每个 phase 可以顺带注册新 skill，自然积累
- 避免在主体功能完成前过度投入 TUI

## 不在范围内

- 完整的 skill 系统
- Dashboard 或 Wizard 模式
- 美观的主题/TUI 样式

## 关联

- 设计决策见 [[tui-design-decisions]]
- 完整 TUI phase 见 ROADMAP Phase 02.2
- 参考设计见 `docs/tui-repl-pattern.md`
