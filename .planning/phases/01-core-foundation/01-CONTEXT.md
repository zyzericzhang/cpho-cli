# Phase 1: Core Foundation - Context

**Gathered:** 2026-05-21
**Status:** Ready for planning

## Phase Boundary

Phase 1 交付端到端的分析管线——从 API key 配置和 workspace 发现，经 OCR 提取，到结构化 LLM 物理推导 + 答案交叉验证，由 golden test suite 保障输出质量。用户可运行 `cpho solve <problem.pdf>` 获得可信的、分步的物理推导，推导与标准答案交叉对照，OCR 错误被检测并标记而非静默传播。

**这不是一次性解题脚本。** 这是 CPHO 物理竞赛知识库 + skills runtime + agent workflow 原型的核心管线。Skills 必须可复用、可追踪、可调试、可重复调用——这个架构约束从 Phase 1 第一天就要成立。

## Implementation Decisions

### 工程脚手架

- **D-01:** 包管理器使用 **uv**，负责依赖、虚拟环境、lock 文件和运行命令
- **D-02:** 项目布局采用 **src-layout**（`src/cpho_cli/`），pyproject.toml 在根目录
- **D-03:** 最低 Python 版本 **3.11+**
- **D-04:** 代码质量工具 **ruff**（lint + format）+ **mypy**（类型检查）。从第一天就要有明确命令：`uv sync`、`uv run cpho --help`、`uv run ruff check .`、`uv run mypy .`、`uv run pytest`——这些是 Agent 提交代码时必须报告的工程证据

### 管线引擎（Skill Runtime）

- **D-05:** 自定义轻量 skill runner，不做 hardcoded 求解器。引擎是通用的——执行 skill 定义，不绑定物理领域
- **D-06:** **Hybrid skill-based 架构**：每个 skill 是一个自包含文件夹 — `SKILL.md`（自然语言说明 + 触发描述）+ YAML 元数据（name、inputs、outputs、required context、DAG step 序列）+ Jinja2 prompt 模板（`prompts/*.md.j2`）+ 可选 Python tools（PDF 读取、OCR、索引、检索、标签、PDF 导出、JSON repair 等非 LLM 操作）——内置高质量物理 skills 先实现，用户无需写 Python 即可创建/修改 skill
- **D-07:** 步骤间状态流采用 **声明式 key-based blackboard**：每个 step 声明 input_keys/output_keys，引擎执行前验证 key 存在。重要内置 skill 可加 Pydantic 校验，但默认保持 key-based 以支持 YAML/Markdown skill 配置和 trace/checkpoint/resume
- **D-08:** 错误处理 = **LLM/API 瞬时故障**：指数退避重试 N 次 + **非可重试错误**：fail fast 并输出清晰诊断（缺少输入文件/标准答案、skill 定义错误、OCR 失败、schema mismatch）——每个 step 写入 trace record 和 checkpoint，用户可检查失败 step、修改 skill/prompt/config、从失败点 resume。**Fallback chain 不默认开启**——如需要必须由 skill 显式定义，避免掩盖 prompt/skill 质量问题
- **D-09:** 内置 solve skill 管线：**(1)** 提取题目+答案内容 → **(2)** normalize 题目 + 拆分子问题 → **(3)** 验证标准答案存在 + 识别答案结构 → **(4)** 按子问题逐步推导 → **(5)** 专门 cross-check 官方答案 → **(6)** 标记差异、跳步、可疑答案错误 → **(7)** 合成最终结构化报告（主线推导、物理思维重构、真正难点、heuristic insight、模型标签、数学处理标签、后续追问建议）。Step 边界为未来 derive→verify→reconcile loop 保留升级空间。每步保存中间输出

### LLM & Prompt 管理

- **D-10:** **轻量 provider 抽象**：base class + OpenRouter 实现，从第一天就抽象，后续加新 provider 只需实现同一接口。配置层支持 `providers.<name>` profile，默认读取 gitignored `config.local.yml`，CLI 通过 `--provider <name>` 选择本次运行使用哪组 provider/key
- **D-11:** 模板引擎 **Jinja2**：模板文件 `prompts/*.md.j2`，支持变量插入、条件、循环、可选上下文块。不用简单字符串替换（未来 prompt 需要条件和循环），不把长 prompt inline 到 YAML
- **D-12:** 结构化输出用 **JSON mode + Pydantic 验证**。解析失败时：原始输出 + parse error + validation error 写入 trace，必要时显式运行 JSON repair step。**不静默正则兜底**——中间结构化结果优先 JSON + schema，Markdown 仅用于最终报告
- **D-13:** 模型参数 **三层优先级**：`config.local.yml` / 显式 `--config` 全局默认 → per-skill YAML 覆盖 → CLI flag 最高。不同 skill 对模型需求不同（答案检查低 temperature、完整讲解长输出、题目比较长上下文）

### Golden Test Suite

- **D-14:** 测试策略：**manual-first evaluation loop** — 用户手动运行 skill → 检查输出 → 指出差距 → Agent 分析根因（prompt/step/schema/retrieval/model/answer key）→ 修改 → 重跑。只有重要/典型/容易回归的失败样本才沉淀为 golden regression case
- **D-15:** 测试格式：**per-problem YAML** 作为机器存储格式。用户主要输入是自然语言或 `EXPECTATION.md`，Agent 帮转 `spec.yml`。Criteria-based 设计（id、area、priority、expectation），可扩展——新增评价板块只需新 area 值，不改读取器
- **D-16:** 评判标准早期以 **人工判断** 为主，中后期 rubric + LLM judge 辅助自动筛查，human-defined expected criteria + known failure modes 驱动。LLM judge 只是筛查器，边界样本/核心 skill 发布前/模型大幅变化后需人工复核
- **D-17:** 运行方式：**pytest**（dev/CI 标准入口）+ **`cpho eval golden_tests/`**（用户友好的本地评估）。Makefile 封装可选，不做第一版主机制
- **D-18:** 初始规模：从 **3-5 道手动测试**起步，逐步把真实失败样本沉淀成 regression suite。架构支持用户自定义 golden set，项目可提供官方推荐小集合

### Claude's Discretion

无——所有关键实现决策均由用户明确指定。

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 架构与产品方向
- `docs/architecture-decisions.md` — 六项架构决策：纯本地 CLI、芯-壳分离、Python 生态、基座框架策略、配置文件驱动、用户策略
- `docs/product-spec.md` — 产品定位、典型用户场景（教练/开发者/学生）、v1 范围、核心假设

### 项目元信息
- `.planning/PROJECT.md` — 项目总览、约束条件、关键决策表（DAG 管线、三层 skill 系统、图片拼接 PDF）
- `.planning/REQUIREMENTS.md` — v1 18 项需求及 Phase 1 分配（CORE-01 到 CORE-05）
- `.planning/ROADMAP.md` — 四阶段路线图，Phase 1 成功标准

### 待调研（Phase 1 research 输入）
- `docs/research-questions.md` — 五个关键技术问题：agent 基座框架、本地 OCR、prompt 管理、DAG 调度、CLI↔线上联动接口

## Existing Code Insights

### Reusable Assets

- `src/cpho_cli/core/config.py` and `src/cpho_cli/models/config.py` are the canonical config and provider profile resolution path.
- `src/cpho_cli/core/llm.py` defines the provider protocol and current OpenRouter implementation.
- `src/cpho_cli/cli/app.py` is the thin Typer shell; provider selection belongs in CLI options and is passed into core as plain values.

### Established Patterns

以下模式由架构决策文档锁定，Phase 1 实现必须遵循：
- **芯-壳分离**：`src/cpho_cli/core/` 纯库无界面依赖，`src/cpho_cli/cli/` 薄适配层。core 不 import CLI 框架，不直接 print/input
- **YAML 配置驱动**：所有可调参数通过 YAML 文件控制，默认读取 gitignored `config.local.yml`，实验记录存 JSONL
- **确定性 DAG 管线**：不使用自主 ReAct-style agent，确保每一步可控可审计

### Integration Points

- **Phase 2 (Tag Indexing)** 需要索引系统读取 skill trace 中的标签输出来构建 JSONL 索引——Phase 1 的 trace schema 是 Phase 2 的输入接口。Phase 02.1 已在索引前插入试卷切分阶段，将多题试卷拆分为 ProblemEntry 后再进入索引管线。
- **Phase 3 (Skill System)** 扩展 skills 目录发现机制——Phase 1 的 skill loader 必须设计为可扩展的
- **Phase 4 (Knowledge Network)** 从 trace 中读取标签关联构建知识图谱——trace 中必须包含标签信息

## Specific Ideas

- Skills 参考 **Claude Code / OpenClaw 社区 skills 模式**：自包含文件夹，可复制、可分享、可版本化
- 每次运行保存完整 trace：输入文件引用、选中上下文、prompt、模型参数、输出、中间错误、生成物
- trace 和 checkpoint 机制是第一优先级的基础设施——没有它就无法调试 skill、无法 regression test、无法 resume
- 技能目录推荐结构：`skills/<name>/` → `SKILL.md` + `prompts/` + `schemas/` + `examples/` + 可选 `tools/`

## Deferred Ideas

无——讨论全程在 Phase 1 范围内。

---

*Phase: 1-Core Foundation*
*Context gathered: 2026-05-21*
