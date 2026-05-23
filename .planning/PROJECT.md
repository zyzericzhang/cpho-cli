# CPHO CLI

## What This Is

CPHO CLI 是一个本地命令行工具，帮助物理竞赛教练和深度学习者对题目文件夹进行 AI 驱动的结构化分析。用户在自己本地的题目文件夹（PDF/图片 + 答案）中工作，通过可扩展的 Skill 插件系统运行多种分析模式——包括主动提问、逐步讲解、多题对比分析、组卷输出。它是物理竞赛领域的 Obsidian + AI agent：文件夹即知识库，标签索引驱动高效检索，解析质量优先于一切。

## Core Value

**生成质量**——真正找到题目的难点、启发点，讲清楚每一步推导的"为什么"，关联到相关题目形成知识网络。这是系统内置 skill 需要反复打磨的核心。

## Requirements

### Validated

- [x] 题目标签索引系统：对每道题自动生成标签（物理模型、启发点、难点、数学技巧），存入本地索引，后续操作通过标签检索而非重复读取原始文件 — Validated in Phase 2
- [x] 本地 LLM API key 支持：默认读取 gitignored `config.local.yml`，支持多 provider/key profile，并可通过 `--provider` 选择本次运行的 key — Validated in Phase 1
- [x] 题目文件夹即工作空间：无需导入流程，文件夹内的 PDF/图片直接可被索引和分析 — Validated in Phase 1

### Active

- [ ] Skill 插件系统：用户可编写和安装自定义分析 skill，支持三层模式（纯 prompt / 声明式配置 YAML / Python 脚本）
- [ ] Skill Creator：用户输入自然语言描述，自动生成完整的 skill 配置文件和 prompt 管线
- [ ] 内置 skill — 主动提问模式：检查答案正确性 → 提取启发点 → 生成标签 → 向学生提问，交互支持问题列表和 REPL 对话两种方式
- [ ] 内置 skill — 逐步讲解模式：完整体现每一步推导的思维逻辑（"为什么这一步推到下一步"），不只是数学计算
- [ ] 内置 skill — 对比分析模式：用户选择两道或多道题目，找出共同模型、共同思路，或基于标签关联其他题目进行联合分析
- [ ] 内置 skill — 组卷输出：将关联题目及其答案分别拼接为两份 PDF（题目卷 + 答案卷）
- [ ] DAG 分步管线：长题按步骤/小问拆分，每步仅注入裁剪过的上下文，避免注意力稀释导致跳步

### Out of Scope

- GUI / TUI / Web 界面 — v1 是纯命令行
- 数据库存储 — 文件系统 + JSON/JSONL 足够
- 多用户 / 权限 / 登录
- LaTeX 渲染引擎 — PDF 输出使用图片拼接方案
- 自主 ReAct-style Agent — 使用确定性 DAG 管线，不依赖模型自行规划执行路径

## Context

Phase 1（Core Foundation）和 Phase 2（Tag Indexing）已完成。用户可以 `cpho solve` 解题、`cpho index` 索引工作空间（自动 OCR + LLM 标签提取 + 主题分类）、`cpho topic` 浏览主题树、`cpho compose` 组卷筛选。Python API 已导出供 Phase 3 skills 使用。216 个测试全部通过。

技术方向（不锁定）：
- Python 生态（AI/LLM 工具链最成熟）
- 芯-壳分离架构：core 纯库无界面依赖，CLI 是薄适配层
- OCR 通过抽象接口隔离
- LLM 调用先支持 OpenRouter API；配置层支持多 provider/key profile，后续 provider 复用同一选择机制
- 基于现有开源 agent 框架定制，不做 greenfield 开发

## Constraints

- **技术栈**: Python only，不引入 Node.js/TypeScript 依赖
- **本地优先**: 除 LLM API 调用外，所有处理在本地完成，不上传题目文件到任何远程服务
- **安全**: API Key 只能从环境变量或 gitignored 本地配置文件读取，严禁硬编码或提交到 git
- **开源协议**: MIT License，面向物理竞赛社区
- **解析质量**: 严谨防幻觉，解析结果必须基于题目原文和标准答案

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Agent 架构用 DAG 管线而非自主 Agent | 物理竞赛解析步骤已知，每步聚焦单任务确保质量；自主 Agent 在长题解析中会跳过中间细节 | — Pending |
| Skill 系统分三层 + Skill Creator | 覆盖不同用户门槛：教练只写 prompt、进阶用户写 YAML、开发者写 Python | — Pending |
| 内置 skill 的核心价值在 prompt 管线打磨 | 真正的质量来自经过几十道题反复测试的 prompt 分步策略，不是框架代码 | — Pending |
| PDF 输出用图片拼接而非 LaTeX 渲染 | 物理题含大量公式，重渲染成本高；从原始 PDF 裁剪拼接更务实 | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition:**
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone:**
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-23 after Phase 2 completion*
