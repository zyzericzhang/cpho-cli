# Phase 4: 找同类题 + 组卷 + 异常处理 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-26
**Phase:** 04-related-problems-compose-exceptions
**Areas discussed:** 找同类题 skill 行为与下游链路、组卷编排文件格式与位置、PDF 拼接与布局、自动选题策略、异常边界

---

## 找同类题 Skill 行为与下游链路

| 选项 | 描述 | 选定 |
|------|------|------|
| 只 CLI 表格 | 打印表格，不存 session | |
| 只 REPL session | 存 last_related，不打印 | |
| 两者都支持 | CLI 表格 + REPL last_related | ✓ |

**A2 – 链路衔接:**

| 选项 | 描述 | 选定 |
|------|------|------|
| 显式 `--from last-related` | 组卷时显式读取 last_related | ✓ |
| 隐式注入 | 组卷 skill 自动读 last_related | |
| 两者都要 | | |

**A3 – 打分调整:**

| 选项 | 描述 | 选定 |
|------|------|------|
| 沿用 + 物理模型优先权重 | physics_model > math_technique > heuristic | ✓ |
| 完全不动现有 | | |
| `--mode strict/loose` | | |

**A4 – 默认参数:**

| 选项 | 描述 | 选定 |
|------|------|------|
| max=10, min_shared=1 | 推荐默认值 | ✓ |
| max=5, min_shared=2 | | |
| 用户自定 | | |

**Notes:** 使用 `--all --batch --analyze` 批量处理，用户直接确认推荐选项。

---

## 组卷编排文件格式与位置

**B1 – 格式:**

| 选项 | 描述 | 选定 |
|------|------|------|
| YAML | 与 skill.yml 同一 loader | ✓ |
| TOML | | |
| Markdown 表格 | | |

**B2 – 存放位置:**

| 选项 | 描述 | 选定 |
|------|------|------|
| `.cpho/compositions/<name>.yml` | 隐藏目录，工具内部 | ✓ |
| workspace 根 | 显眼但污染用户文件夹 | |
| 用户每次指定 | | |

**B3 – 题位 schema:**

| 选项 | 描述 | 选定 |
|------|------|------|
| `slot + (problem_id | pass | spec)` | 三选一 Pydantic 强校验 | ✓ |
| 只支持 `problem_id | pass` | | |
| 用户自描述 | | |

---

## PDF 拼接与布局

**C1 – 拼接库:**

| 选项 | 描述 | 选定 |
|------|------|------|
| pymupdf (fitz) | 已在依赖，直接做页裁剪 | ✓ |
| pypdf | 纯 Python，功能较弱 | |
| 研究后再说 | | |

**C2 – 一页一题:**

| 选项 | 描述 | 选定 |
|------|------|------|
| 跨页就多页，不缩放 | 忠实原版式 | ✓ |
| 强制缩放到一页 | 失真 | |
| 跨页时报错 | | |

**C3 – 题号呈现:**

| 选项 | 描述 | 选定 |
|------|------|------|
| PDF outline/书签"第 N 题" | 不破坏版式 | ✓ |
| 页眉水印 | 破坏原版式 | |
| 插题号封面页 | 污染文件 | |

**C4 – 输出位置:**

| 选项 | 描述 | 选定 |
|------|------|------|
| `<workspace>/exports/compose/...` | workspace 根下可见目录 | |
| `.cpho/exports/compose/...` | 与 traces 同层隐藏目录 | ✓ |
| 当前工作目录 | | |

**User's choice:** C4 选 b（`.cpho/exports/compose/`），其余推荐。

---

## 自动选题策略

**D1 – 触发方式:**

| 选项 | 描述 | 选定 |
|------|------|------|
| spec-per-slot + `compose auto` 两者 | 灵活 | ✓ |
| 只 spec-per-slot | | |
| 只 compose auto | | |

**D2 – 多样性:**

| 选项 | 描述 | 选定 |
|------|------|------|
| 去重 + physics_model 上限 | | |
| 只去重 problem_id | 简单，v1 够用 | ✓ |
| 不做多样性 | | |

**User's choice:** D2 选 b（只去重 problem_id），physics_model_tag 上限推到 v2。

**D3 – 选不到题:**

| 选项 | 描述 | 选定 |
|------|------|------|
| 报错列出实际可选数 | 可控，不自动放宽 | ✓ |
| 自动放宽到 topic 父节点 | 可能选到不相关题 | |
| 静默 pass | 用户察觉不到 | |

---

## 异常边界

**E1 – Checkpoint 粒度:**

| 选项 | 描述 | 选定 |
|------|------|------|
| step 级（每个 DAG step 后落盘） | 与 SkillRuntime 自然对齐 | ✓ |
| 整个 skill 结束后 | 无法恢复中途中断 | |
| 每个 LLM call 后 | 最细，IO 开销大 | |

**E2 – Checkpoint 位置:**

| 选项 | 描述 | 选定 |
|------|------|------|
| `.cpho/runs/<skill>/<problem_id>/<run_id>.json` | 与 traces 同层 | ✓ |
| 与 trace 合并写 | 耦合高 | |
| `.cpho-resume/` | 另一套命名体系 | |

**E3 – LLM/OCR 失败:**

| 选项 | 描述 | 选定 |
|------|------|------|
| 自动 3 次指数退避后透传 | 覆盖间歇性 5xx | ✓ |
| 不重试直接失败 | | |
| 交互式 retry/skip/abort | 实现复杂 | |

**E4 – 文件越界/挂载丢失:**

| 选项 | 描述 | 选定 |
|------|------|------|
| `_ensure_in_workspace` + `path.exists()` + 中文报错 | 统一入口 | ✓ |
| OS 原生错误裸冒泡 | 无中文提示 | |
| 用户自描述 | | |

---

## Claude's Discretion

- `run_id` 生成策略（UUID / 时间戳 / 哈希）
- 软链接在 `_ensure_in_workspace` 中的处理方式
- REPL `/search-related` 参数设计（是否支持 `--top N`）
- `cpho compose new` stub 模板的具体 YAML 内容

## Deferred Ideas

- 难度控制（difficulty 字段）— v2
- physics_model_tag 数量上限（多样性 v2）— v2
- 软链接 workspace 完整支持 — 专项设计
- `--mode strict/loose` preset — v2
- `unverified` 标签提升为 canonical 的 UI — 遗留自 Phase 02.3
