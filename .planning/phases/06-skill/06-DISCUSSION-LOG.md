# Phase 6: 知识库地基 + Skill 框架重构 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-27
**Phase:** 06-知识库地基 + Skill 框架重构
**Areas discussed:** 知识文件存储结构, KnowledgeResolver 匹配策略, SkillPipeline 框架增强, 知识标准化 Skill 流程

---

## 知识文件存储结构

| Option | Description | Selected |
|--------|-------------|----------|
| (a) 单一 files/ 目录 | 用户放原始文件到此，标准化后原地加 frontmatter 标记 | |
| (b) 分离目录 | 原始文件放 `files/inbox/`，标准化后移入 `files/published/` | ✓ |
| (c) 任意位置 | 用户任意位置放原始文件，标准化后统一输出到 files/ | |

| Option | Description | Selected |
|--------|-------------|----------|
| (a) 极简 frontmatter | 仅 4 必填字段 | |
| (b) 结构化 | 必填 + 额外结构化字段全部必填 | |
| (c) 混合 | 必填 + 可选结构化字段，Resolver 有则用 | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| (a) .txt/.rst 支持 | 支持这两种纯文本格式 | |
| (b) 仅 4 种 | 仅需求列出的 markdown/LaTeX/docx/图片 | |
| (c) 任意文本 | 接受任意文本文件，未知格式当纯文本 | ✓ |

**User's choice:** 1b, 2c, 3c
**Notes:** Q4（草稿位置）与 Q1 重复，1b 的 inbox/published 分离已覆盖。

---

## KnowledgeResolver 匹配策略

| Option | Description | Selected |
|--------|-------------|----------|
| (a) 精确匹配 | 问题的所有 tag 与知识文件精确比对 | ✓ (with b) |
| (b) 精确优先 + category 回退 | 无结果时放宽到同 category | ✓ |
| (c) 用户可选 | 精确/宽松可选 | |

| Option | Description | Selected |
|--------|-------------|----------|
| (a) 按匹配数排序 | 匹配 tag 数量越多越前 | |
| (b) 按 category 优先级 | physics_model > math_technique > ... | |
| (c) 平等排序 | 不做区分 | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| (a) 纯路径列表 | `list[Path]` | |
| (b) 结构化对象 | `KnowledgeMatch` 含 path/tag_id/source/repo | ✓ |
| (c) 双 API | 两种都提供 | |

| Option | Description | Selected |
|--------|-------------|----------|
| (a) 仅 workspace_root | 自动发现所有路径 | ✓ |
| (b) +vocabulary | 需传入词汇表 | |
| (c) +community | 需传入社区路径 | |

**User's choice:** Q1: a+b 都支持, Q2: c, Q3/Q4: 结合社区方案一步到位 — (b) 结构化 + (a) workspace_root 自动发现
**Notes:** 社区 sync 方案已在先前讨论中确认（GitHub API tarball / token 可选 / ~/.config/cpho/community.yml / 幂等+force / community-kb/<repo-name>/），Resolver 构造函数签名为 `workspace_root`，community 目录自动发现。

---

## SkillPipeline 框架增强

| Option | Description | Selected |
|--------|-------------|----------|
| (a) 仅声明意图 | step 声明需要多模态，运行时检测，不支持报错 | |
| (b) 强制路由 | 自动将输入作为图片/PDF | |
| (c) 声明 + 自动路由 + 降级提示 | SkillRuntime 自动路由 + 降级时实时提示 | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| (a) step 级 | 每个 step 独立指定 default_model | ✓ |
| (b) pipeline 级 | SkillSpec 设默认，所有 step 共享 | |
| (c) 两层 | pipeline 默认 + step 覆盖 | |

| Option | Description | Selected |
|--------|-------------|----------|
| (a) 步骤列表 | `list[StepMeta]` | |
| (b) 完整 DAG | 步骤列表 + 依赖边 + 输入输出连线 | ✓ |
| (c) 两者 | — | |

**User's choice:** 1c, 2a, 3b
**Notes:** 决策依据来自 Phase 7 讨论中用户对输入路由（7c step 级混合路由）、模型面板（每步独立选模型）、面板展示（含依赖关系图）的决策。v1.0 skills 不迁移（用户反问"为什么要迁移"），新字段为可选，旧 skill.yml 不改。

---

## 知识标准化 Skill 流程

| Option | Description | Selected |
|--------|-------------|----------|
| (a) 单文件 | `cpho knowledge normalize <file>` | |
| (b) 批量 | `cpho knowledge normalize --all` | |
| (c) 两者 | 单文件 + --all | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| (a) 多模态 LLM 一步 | 直接调多模态 LLM 生成标准化草稿 | ✓ |
| (b) 先提取再标准化 | docx→mammoth 转文字, 图片→多模态 LLM 转文字, 再做标准化 | |
| (c) 按类型分叉 | docx 走 mammoth，图片走多模态 LLM | |

| Option | Description | Selected |
|--------|-------------|----------|
| (a) 跳过 | 检测 hash 未变，提示"已是最新" | |
| (b) minimum-diff | 检测用户编辑位置，仅对增量重新标准化 | ✓ |
| (c) 全量重生成 | 不保留用户修改 | |

| Option | Description | Selected |
|--------|-------------|----------|
| (a) 手动 | 用户自己移动文件 | |
| (b) 命令 | `cpho knowledge publish <file>` | |
| (c) skill 内交互 | 标准化结束时问"是否发布？[y/N]" | ✓ |

**User's choice:** 1c, 2a, 3b, 4c
**Notes:** docx 也走多模态 LLM 而非 mammoth，因为 docx 里也可能包含图片。

---

## Claude's Discretion

无 — 所有领域均由用户决策。

## Deferred Ideas

无 — 讨论保持在 Phase 6 范围内。
