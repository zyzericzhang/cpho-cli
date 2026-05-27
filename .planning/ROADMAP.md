# Roadmap: CPHO CLI

## Overview

CPHO CLI 从质量优先的核心管线起步，经过 8 个 phase、51 个计划，完成了 v1.0 MVP。v1.1 将引入知识记录系统、Explain v2 板块设计、模型选择面板和跨平台安装包。

## Milestones

- ✅ **v1.0 MVP** — Phases 1–5 (shipped 2026-05-27)
- 🚧 **v1.1** — Phases 6+ (planning)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1, 2, 02.1, 02.2, 02.3, 3, 4, 5) — SHIPPED 2026-05-27</summary>

**Phase Numbering:**
- Integer phases (1, 2, 3, 4, 5): Planned milestone work
- Decimal phases (02.1, 02.2, 02.3): Urgent insertions

- [x] **Phase 1: Core Foundation** — End-to-end OCR + DAG pipeline with OpenRouter solve (5/5 plans) — completed 2026-05-22
- [x] **Phase 2: Tag Indexing** — Problem knowledge index: retrieval backbone + learning-memory foundation (7/7 plans) — completed 2026-05-23
- [x] **Phase 02.1: Paper Splitting** (INSERTED) — 试卷切分：多题试卷拆分为独立题目条目，修复数据模型形状错配 (5/5 plans) — completed 2026-05-24
- [x] **Phase 02.2: TUI REPL 骨架** (INSERTED) — prompt_toolkit REPL 主循环、skill 注册机制、/search /show (6/6 plans) — completed 2026-05-24
- [x] **Phase 02.3: Index 读写分离 + Solve 降级** (INSERTED) — 移除 SolveReport→index 耦合，index 标签层开放读写 API (10/10 plans) — completed 2026-05-25
- [x] **Phase 3: Skill 跨切面 + 核心讲解 Skills** — Explain / Solve 重定位 / Probe + 跨切面能力 (8/8 plans) — completed 2026-05-26
- [x] **Phase 4: 找同类题 + 组卷 + 异常处理** — 找同类题 skill + PDF 组卷 + 异常边界 (6/6 plans) — completed 2026-05-26
- [x] **Phase 5: 用户手册 + 开源准备** — README / docs/user/ / Python 扩展机制 (4/4 plans) — completed 2026-05-26

Full details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

### 🚧 v1.1 (Planning)

Phases TBD — see `/gsd:new-milestone` to kick off v1.1 planning.

Key themes from `docs/new-understanding-2026-05-27.md`:
- Phase 6: 知识记录系统 (Knowledge Base + 社区库 + 两步标准化 skill + Explain 联动)
- Phase 7: Explain v2 重构 (板块选择替代 Tone + 架构重构)
- Phase 8: 模型选择与 Skill 配置面板 (每步独立模型 + 实时官网抓取)
- Phase 9: 输入策略 + 错误处理打磨 (多模态优先 + 全链路错误诊断)
- Phase 10: 跨平台 + 安装包 (Windows 兼容 + 一键安装)

## Progress

**Execution Order:** 1 → 2 → 02.1 → 02.2 → 02.3 → 3 → 4 → 5 → (v1.1 phases TBD)

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Core Foundation | v1.0 | 5/5 | Complete | 2026-05-22 |
| 2. Tag Indexing | v1.0 | 7/7 | Complete | 2026-05-23 |
| 02.1. Paper Splitting | v1.0 | 5/5 | Complete | 2026-05-24 |
| 02.2. TUI REPL 骨架 | v1.0 | 6/6 | Complete | 2026-05-24 |
| 02.3. Index 读写分离 + Solve 降级 | v1.0 | 10/10 | Complete | 2026-05-25 |
| 3. Skill 跨切面 + 核心讲解 Skills | v1.0 | 8/8 | Complete | 2026-05-26 |
| 4. 找同类题 + 组卷 + 异常处理 | v1.0 | 6/6 | Complete | 2026-05-26 |
| 5. 用户手册 + 开源准备 | v1.0 | 4/4 | Complete | 2026-05-26 |
| 6–10. v1.1 phases | v1.1 | 0/TBD | Not started | - |
