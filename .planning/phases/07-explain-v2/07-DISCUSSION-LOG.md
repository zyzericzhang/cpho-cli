# Phase 7: Explain v2 + 模型面板 + 输入路由 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-27
**Phase:** 07-explain-v2
**Areas discussed:** Explain 板块输出结构, 模型面板交互方式, 输入路由决策点, 模型列表缓存与更新, Explain v2 与 SkillPipeline 集成, 降级提示 UX

---

## Area 1: Explain 板块输出结构

| Option | Description | Selected |
|--------|-------------|----------|
| 单文件 + 目录 | 一个 markdown 文件，顶部目录，板块一级标题 | ✓ |
| 每板块独立文件 | 思路描述.md / 标答替换.md / 其他方法.md | |
| 单文件无目录 | 一个文件内板块按顺序排列 | |

**Q1: 输出文件结构** → 单文件 + 顶部目录 (1c)

| Option | Description | Selected |
|--------|-------------|----------|
| 完全不出现在输出 | 未选板块不留痕迹 | ✓ |
| 留空占位标题 | 注明"未选择" | |

**Q2: 未选板块处理** → 完全不出现在输出中 (2a)

| Option | Description | Selected |
|--------|-------------|----------|
| 文中内联 + 末尾汇总 | 两处都有标注 | ✓ |
| 仅文中内联 | 引用出现在对应句子处 | |
| 仅末尾汇总 | 板块末尾单独一节 | |

**Q3: 来源标注格式** → 文中内联 + 每板块末尾汇总 (3c)

**Notes:** 引用粒度：文件名 + canonical_tag_id + 段落/小节标题。与 Phase 6 Specific Ideas 中的"文中内联 + 板块末尾汇总"一致。

---

## Area 2: 模型面板交互方式

| Option | Description | Selected |
|--------|-------------|----------|
| `/skill panel` 命令 | 独立 slash 命令，可复用 | |
| 执行前自动弹出 | 每次运行前弹出配置 | |
| 执行后摘要 + 引导 | 不打断执行，摘要引导用户 | ✓ |

**Q4: 打开方式** → skill 执行后展示摘要 + `/skill panel` 命令引导 (4c)

**Q5: 修改后行为** → 下次运行生效，不自动重跑 (5a)

**Q6: 展示内容** → 步骤名 + 模型 + prompt 路径 + 依赖关系图 (6b)

**Notes:** 数据来源为 Phase 6 `SkillSpec.describe()` (D-10)。Phase 6 D-09 已锁定 per-step 选模型。

---

## Area 3: 输入路由决策点

| Option | Description | Selected |
|--------|-------------|----------|
| Skill 级别 | 运行前检查一次，全程一致 | |
| Step 级别 | 每步独立判断 | |
| 混合 | input step 多模态，推理 step 文本 | ✓ |

**Q7: 决策粒度** → 混合，与 Phase 6 `requires_multimodal` 对齐 (7c)

**Q8: 降级行为** → 自动降级 + 实时提示哪个步骤为什么降级 (8c)

**Q9: PDF 回退链** → PDF→图片→OCR 两层回退 (9c)

**Notes:** Q7/Q8 与 Phase 6 D-08 一致。Q9 是新增细节。用户纠正：一道题不会同时有 PDF 和图片源，回退是"模型能力不支持时的降级路径"而非"文件类型选择"。

---

## Area 4: 模型列表缓存与更新

| Option | Description | Selected |
|--------|-------------|----------|
| JSON + mtime | 零依赖，自写 TTL | |
| diskcache 库 | 成熟、自动过期、SQLite 底层 | ✓ |
| 内存 + JSON | 重启后首次需拉取 | |

**Q10: 缓存方案** → python-diskcache (10b)

**Q11: Bundled fallback** → 上次成功拉取的 snapshot 随仓库更新 (11c)

**Q12: Force-refresh** → `/model refresh` + 面板刷新按钮 (12c)

**Notes:** diskcache 是纯 Python 库，不违反 Python-only 约束。

---

## Area 5: Explain v2 与 SkillPipeline 集成

| Option | Description | Selected |
|--------|-------------|----------|
| 每板块独立 pipeline | 完全解耦 | |
| 单 pipeline 分支 | 内部串行 | |
| 共享 preamble + 并行 | 知识查询共享，板块并行 | ✓ |

**Q13: 板块编排** → 共享 preamble + 三板块并行 (13c)

**Q14: 旧代码** → 完全删除 v1.0 Tone 代码 (14a)

**Q15: 来源引用粒度** → 文件名 + tag + 具体小节 (15c)

**Notes:** Q14 与 Phase 6 D-11（v1.0 skills 不迁移）一致。Q13 与当前 `asyncio.gather` per-tone 并行模式对应。此轮用户要求用大白话解释 SkillPipeline 关联，确认理解后再做选择。

---

## Area 6: 降级提示 UX

| Option | Description | Selected |
|--------|-------------|----------|
| REPL warning | 流式前/后打印 | |
| 仅文件顶部 | 事后查看 | |
| REPL 预警 + provenance | 实时 + 可追溯 | ✓ |

**Q16: 提示位置** → REPL 简短预警（流式开始前一行）+ provenance 字段 (16c)

**Q17: 多 step 降级** → 每 step 单独一行 (17a)

**Notes:** Phase 6 D-08 已锁定"降级时实时提示哪个步骤为什么降级"。Q16-17 确定具体展示形式。

---

## Prior Context Referenced

讨论过程中确认 Phase 6 CONTEXT.md 已锁定以下决策，无需重复讨论：
- D-08: `requires_multimodal` + 降级实时提示
- D-09: `default_model` step 级模型
- D-10: `SkillSpec.describe()` 返回完整 DAG
- D-11: v1.0 skills 不迁移
- Specific Ideas: 文中内联 + 板块末尾汇总

Phase 8 CONTEXT.md 已锁定社区知识注入格式：
- D-07: `<knowledge_reference source="community" repo="...">` 标签
- D-08: 系统前导双保险防 prompt injection

## Claude's Discretion

None — 所有领域均由用户决策。

## Deferred Ideas

None.
