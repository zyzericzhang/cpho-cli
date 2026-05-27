# CPHO CLI

## What This Is

CPHO CLI 是一个本地命令行工具，帮助物理竞赛教练和深度学习者对试卷文件夹进行 AI 驱动的结构化分析。用户在自己本地的试卷文件夹（PDF/图片 + 答案）中工作，工具自动将多题试卷拆分为独立题目条目，通过可扩展的 skill 系统运行多种分析模式——包括逐步讲解、主动提问、挑错审查、找同类题、组卷输出。它是物理竞赛领域的 Obsidian + AI agent：文件夹即知识库，标签索引驱动高效检索，解析质量优先于一切。

**v1.0 shipped.** v1.1 将引入知识记录系统（Knowledge Base）、Explain 板块重设计、模型选择面板、跨平台安装包等。

## Core Value

**生成质量**——真正找到题目的难点、启发点，讲清楚每一步推导的"为什么"，关联到相关题目形成知识网络。这是系统内置 skill 需要反复打磨的核心。

## Requirements

### Validated (v1.0)

- ✓ 本地 LLM API key 支持：默认读取 gitignored `config.local.yml`，支持多 provider/key profile — v1.0
- ✓ 题目文件夹即工作空间：PDF/图片直接可被索引和分析 — v1.0
- ✓ 题目标签索引系统：对每道题自动生成标签（物理模型、启发点、难点、数学技巧），受控词汇表保证一致性 — v1.0
- ✓ 多题试卷切分：PaperFile/ProblemEntry 模型，规则优先 + LLM 兜底 — v1.0
- ✓ TUI REPL：prompt_toolkit REPL，slash command 注册机制，/search /show — v1.0
- ✓ Index 读写 API：标签层读写分离，skill-tag provenance 与 LLM-tag 分开存储 — v1.0
- ✓ Solve skill：对标准答案做逐步审查，错误以受控 tag 写入 index（含 provenance） — v1.0
- ✓ Explain skill（v1.0 Tone 设计）：多 Tone × 分栏目 × 句子级 × 回写 Index — v1.0 (**将被 v1.1 板块设计取代**)
- ✓ Probe skill：主动提问对话，输出问答 markdown 文件 — v1.0
- ✓ 跨切面能力：Markdown 导出 / Follow-up 对话 / 进度显示 / Solve 优先执行序 — v1.0
- ✓ 找同类题 skill：基于 index 标签层返回相似度排序同类题 — v1.0
- ✓ PDF 组卷 skill：编排文件驱动 + 自动选题，图片拼接不做 LaTeX 重渲染 — v1.0
- ✓ 异常边界：外接硬盘/Ctrl+C/文件越界/API 失败有明确提示，中间产物可恢复 — v1.0
- ✓ README + docs/user/ + Python 扩展机制文档 — v1.0

### Active (v1.1 目标)

- [ ] **知识记录系统**：维护"知识本"（物理模型总结/方法描述），支持用户本地私有 + 社区 GitHub 开源库；与 Explain 联动（tag 对应知识文件为第一优先级）；多模态导入（图片/Word 直接处理，不 OCR）；两步标准化 skill（草稿审核 → 知识区）
- [ ] **Explain v2 重设计**：去掉 Tone，改为板块选择（思路描述 / 标答替换 / 其他方法）；知识文件第一优先级；skill 架构重构（不在现有架构下妥协）；输出标注知识来源
- [ ] **模型选择与 Skill 配置面板**：每个 skill 展示后台步骤、提示词位置、每步调用模型；用户可调整每步模型；模型列表从官网实时抓取（OpenRouter / Google AI Studio 等），不写死
- [ ] **输入策略强化**：其他 skill 运行时优先用原始图片/PDF（多模态）；模型不支持时自动降级 OCR；Index 仍用 OCR
- [ ] **错误处理文档化**：所有报错 + 对应解决方案写入 README 和 docs/user；各功能失败提示一目了然（"改哪里"）
- [ ] **黄金测试集**（CORE-05 延续）：20-30 道精选物理竞赛题 + 答案，供回归验证
- [ ] **跨平台安装包**：Windows 兼容 + Mac/Windows 一键安装包（免 uv 依赖）

### Out of Scope

- GUI / Web 界面 — v1 纯命令行 + TUI REPL，不做图形界面
- 数据库存储（PostgreSQL/Supabase） — 文件系统 + JSONL 足够
- 多用户 / 权限 / 登录系统 — 本地单用户工具
- LaTeX 渲染引擎 — PDF 输出采用图片拼接方案，不重渲染公式
- 自主 ReAct-style Agent — 使用确定性 DAG 管线，确保每一步可控可审计
- 和线上 CPHO Platform 的数据同步 — v2+ 联动功能
- 向量检索 / RAG — v1 使用结构化标签索引，更可控
- 手机端 / 平板端 — 仅桌面 CLI
- YAML skill loader — 用 PLUGIN-PY-SIMPLE 替代
- Skill Creator 自然语言生成 skill — 暂时不做，之后再说
- pip 第三方 skill 包 — 用户改代码扩展即可
- 知识图谱可视化 — 由 SKILL-RELATED 按需查询替代

## Context

**v1.0 shipped 2026-05-27.**  
~17,458 Python LOC | 51 plans | 190 git commits | 8 days  
`uv run pytest -q` — 415 passed  
Tech stack: Python 3.12, uv, RapidOCR, prompt_toolkit, PyMuPDF, Jinja2, Pydantic, Typer, OpenRouter API

**v1.1 focus:** Knowledge Base system + Explain v2 (板块) + Model panel + error docs + cross-platform packaging. Reference: `docs/new-understanding-2026-05-27.md`.

## Constraints

- **技术栈**: Python only，不引入 Node.js/TypeScript 依赖
- **本地优先**: 除 LLM API 调用外，所有处理在本地完成，不上传题目文件到任何远程服务
- **安全**: API Key 只能从环境变量或 gitignored 本地配置文件读取，严禁硬编码或提交到 git
- **开源协议**: MIT License，面向物理竞赛社区
- **解析质量**: 严谨防幻觉，解析结果必须基于题目原文和标准答案

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| DAG pipeline over autonomous agent | 物理竞赛解析步骤已知，每步聚焦单任务确保质量；自主 Agent 在长题解析中会跳过中间细节 | ✓ Good — 所有 skills 结构清晰，无"跳步"幻觉 |
| PaperFile/ProblemEntry split model | 真实工作空间是试卷文件（含多道题），索引消费单位是题目；形状错配需在 Phase 02.1 修复 | ✓ Good — 正确解耦文件层与题目层 |
| Tag provenance (LLM tag vs skill tag) | force-rebuild 只覆盖 LLM 机打 tag，保留 skill 写入的 tag（含 provenance） | ✓ Good — skills 的标注不被 reindex 覆盖 |
| PDF composition via image stitching | 物理题含大量公式，重渲染成本高；从原始 PDF 裁剪拼接更务实 | ✓ Good — PyMuPDF 方案稳健 |
| Simplified Python extension over YAML loader | 教练/学者用户门槛低，直接改代码即可扩展，无需 YAML DSL | ✓ Good — 与 GitHub 开源受众对齐 |
| prompt_toolkit REPL over Click-style CLI | 有状态 REPL 会话保存搜索结果/当前题目，slash command 注册机制零摩擦扩展 | ✓ Good — Phase 3-5 skills 通过注册无缝接入 |
| Explain Tone design (v1.0) | 多 Tone 满足原始需求 | ⚠ Revisit — 2026-05-27 新理解用"板块选择"取代，v1.1 重构 |
| Remove golden_tests eval (Phase 02.3) | 框架未验证；tests 覆盖结构不覆盖质量 | ⚠ Revisit — CORE-05 质量回归测试仍是开放 gap |

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
*Last updated: 2026-05-27 after v1.0 milestone close*
