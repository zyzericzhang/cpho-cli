# Phase 05: 用户手册 + 开源准备 - Context

**Gathered:** 2026-05-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 05 交付三样东西：

1. **README.md 重写** — ripgrep/fzf 风格的 hero 级开源 README（Quick Start 最前 → 简介 → 功能矩阵 → REPL → Skill 列表 → 配置 → 扩展 → License），纯中文，含 asciinema Demo，目标是新用户 10 分钟内从 clone 跑出 `/explain`。
2. **`docs/user/` 延伸文档** — 按 skill 分章，每章固定模板，覆盖 Phase 3/4 交付的全部 skill。
3. **简化 Python 扩展机制** — 以"复制 builtin_skill 目录改 Python"为入口的扩展文档，含完整最小 skill 示例。

**这不是新功能开发。** 所有能力来自 Phase 3（solve 重定位 / explain / 主动提问）和 Phase 4（找同类题 / 组卷 / 异常处理）的交付物。Phase 05 在 Phase 4 完成后执行。

**已废弃（README Out of Scope 段要明确列出）：**
- YAML skill loader（旧 PLUGIN-01）
- 自然语言生成 skill（旧 Skill Creator）
- pip 第三方包安装机制

</domain>

<decisions>
## Implementation Decisions

### D1：README 风格与版面

- **D-01:** 参考风格：**ripgrep / fzf 风**（极简 hero、密集对比表格、强说服力的"为什么用 cpho"段落）。
- **D-02:** 语言：**纯中文**，命令 / 代码块原样保留英文。
- **D-03:** 章节顺序（Quick Start 最前）：
  ```
  Quick Start（5 分钟跑起来）
  → 这是什么 / 为什么做
  → 功能矩阵（skill 对照表）
  → REPL 用法
  → 完整 Skill 列表与示例
  → 配置
  → 扩展指南
  → 依赖与鸣谢
  → License
  ```
- **D-04:** 长度上限：**300–600 行**，复杂细节全推 `docs/user/`。
- **D-05:** Badges：License + Python 版本 + uv（三个，简洁不过载）。
- **D-06:** README 末尾独立一段 **Out of Scope**，明确列出废弃功能，防止 issue 涌入。

### D2：Demo 媒介

- **D-07:** 主 Demo 格式：**asciinema SVG**，嵌入 README。
- **D-08:** Demo 内容：**完整学习流程** — `cpho index examples/` → 进 REPL → `/solve` → `/explain`（选 Tone）→ `/search`（找同类题）。Phase 4 完成后录制，一次性覆盖所有 skill。
- **D-09:** 文件放置：**`.github/assets/`**（GitHub 惯例位置）。
- **D-10:** 录制时机：Phase 5 执行阶段一次性录制，不提前分批录。

### D3：`docs/user/` 结构

- **D-11:** 组织方式：**按 skill 分章**，一 skill 一文件（`docs/user/solve.md`、`docs/user/explain.md` 等）。
- **D-12:** 顶层导航：`docs/user/README.md`（GitHub 惯例，skill 列表 + 一行简介 + 内链）。
- **D-13:** 每章固定模板段（严格按此顺序）：
  1. 用途（一句话）
  2. 前置条件
  3. 用法 / 参数
  4. 典型输出
  5. 导出文件说明
  6. 端到端完整示例（从 CLI/REPL 命令到最终输出）
- **D-14:** REPL 通用用法（slash command 补全、`/help`、`/set`、workspace 切换）**分散在各 skill 章节里**，不单独成章。
- **D-15:** 覆盖 skill：solve / explain（含 3 Tone × 分栏目 × 句子级 × 回写 Index）/ 主动提问 / 找同类题 / 组卷 / index / （REPL 通用操作穿插）。

### D4：Python 扩展机制

- **D-16:** 扩展方式：**复制 `builtin_skills/` 任意目录作模板**，修改指定 Python 函数，纯 Python，零新接口。
- **D-17:** REPL 注册：**自动扫描 `builtin_skills/` 目录**，符合命名约定的子目录自动注册为 slash command。
- **D-18:** 文档必须明确的 API 入口：
  - `core/llm.py` — `LLMProvider` 调用入口（如何发起 LLM 请求）
  - `core/index/api.py` — `add_problem_tags` / `remove_problem_tags` / `update_problem_tags` 读写接口
  - REPL slash command 命名约定（目录名 → `/命令名` 映射规则）
- **D-19:** 文档含**完整最小 skill 示例**（如"统计当前 workspace 题目总数"），从空目录到 REPL 可调用，完整代码附注释。
- **D-20:** 扩展文档开头放 **Out of Scope 框**：
  ```
  不支持：YAML 配置式 skill / 自然语言生成 skill / pip 安装第三方 skill
  ```

### D5：Quick Start 10 分钟路径

- **D-21:** **重心在 REPL 交互体验**，Quick Start 的终点是用户在 REPL 里跑出 `/explain` 的完整输出。
- **D-22:** 步骤设计：
  ```
  1. 克隆 + uv sync（含 API key 配置 config.local.yml）
  2. cpho index examples/（索引 sample 题目）
  3. cpho repl → /explain（选 Tone，看输出，Markdown 导出）
  ```
- **D-23:** Quick Start 第 1 步就引导 `config.local.yml` 配置，不等用户报错。
- **D-24:** Sample 数据：`examples/` 目录放 **1 道 IPhO 公开题**（题目 PNG + 答案 PNG），README 里注明来源（IPhO 官网，公开赛题）；正文一行注明"替换为自己的题库目录即可"。

### D6：开源准备清单

- **D-25:** Phase 5 必须新建的文件：
  - `LICENSE`（MIT，填入年份和作者名）
  - `CONTRIBUTING.md`（轻量，5–10 行，说明 issue / PR 规范）
  - `CODE_OF_CONDUCT.md`（标准 Contributor Covenant 模板）
  - `.github/ISSUE_TEMPLATE/bug_report.md`
  - `.github/ISSUE_TEMPLATE/feature_request.md`
- **D-26:** `README.md` 末尾加「依赖与鸣谢」段，列出主要依赖库（rapidocr / pymupdf / prompt_toolkit / openrouter / uv）及其 license。
- **D-27:** `.gitignore` 补充 `.claude/` 显式排除（当前未追踪但应明确）；**不做 git 历史重写**；`.planning/` 随仓库公开。

### Claude's Discretion

- asciinema 录制工具选型（`vhs` / `asciinema` 原生 / `termtosvg`）——研究 agent 调研后决定
- `docs/user/` 各章的具体示例输出内容——执行时基于 Phase 3/4 真实输出生成
- IPhO 题目选哪道——找一道力学基础题（如 IPhO 1967 P1 或类似）；版权确认后选定
- CONTRIBUTING.md 的具体贡献流程——参照 ripgrep / uv 同类项目模板

</decisions>

<canonical_refs>
## Canonical References

**下游 agent（researcher / planner）在规划前必须读这些文件。**

### 需求与范围
- `.planning/ROADMAP.md` §Phase 5 — Goal / Success Criteria / Requirements（DOCS-README, DOCS-USER, PLUGIN-PY-SIMPLE）
- `.planning/REQUIREMENTS.md` — DOCS-README / DOCS-USER / PLUGIN-PY-SIMPLE 条目；Out of Scope 列表（YAML loader / NL skill creator / pip plugin）
- `.planning/PROJECT.md` — 项目核心价值、Key Decisions（DAG 管线 / 三层 skill / 中文 UX）、Constraints（MIT 协议 / 本地优先 / Python only）

### Skill 设计决策（文档的内容基础）
- `docs/new-understanding-2026-05-26.md` — **最重要**：每个 skill 的设计决策（explain 3 Tone / 主动提问输出结构 / 组卷编排文件 / Markdown 导出约定 / 运行过程显示要求）；Phase 3/4 实现的功能集即 Phase 5 文档要覆盖的内容

### 现有代码结构（了解扩展机制的基础）
- `src/cpho_cli/builtin_skills/solve/` — 当前唯一内置 skill，是用户扩展的参照模板
- `src/cpho_cli/cli/repl/commands/` — REPL slash command 注册位置（builtin_skills.py / help_cmd.py / search.py / set_cmd.py）
- `src/cpho_cli/core/` — `llm.py`（LLMProvider）、`index/api.py`（标签读写 API）

### 产品规格
- `docs/product-spec.md` — 产品定位与用户故事（README 简介段的内容来源）

### 参考 CONTEXT（已完成阶段的决策，避免矛盾）
- `.planning/phases/02.3-index-solve-solvereport-index-golden-tests-index-api-skills/02.3-CONTEXT.md` — index 标签读写 API（D-03 ~ D-09）、solve 降级为 builtin skill、UserTagEntry 数据结构

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/cpho_cli/builtin_skills/solve/` — 扩展机制文档的模板来源；`skill.yml` + `prompts/` + Python entry 是用户复制的起点
- `src/cpho_cli/cli/repl/commands/builtin_skills.py` — 展示 skill 如何注册为 REPL slash command；自动发现逻辑将在此扩展
- `README.md`（当前 68 行）— 「这是什么 / 为什么做 / 开发命令 / 配置」已有基础段落，重写时可保留核心内容
- `pyproject.toml` — `[project]` 中的 `description`、`dependencies`、`requires-python` 可直接用于 README badge 和依赖鸣谢段

### Established Patterns
- **芯-壳分离**：`core/` 是纯库，`cli/` 是薄适配层——文档中扩展 API 应指向 `core/` 而非 `cli/`
- **中文 UX**：所有用户可见的 README / docs 内容保持中文；命令名、参数名、文件名保持英文
- **`config.local.yml` 模式**：API key 配置已有完整示例在现有 README（可直接移植到 Quick Start）

### Integration Points
- Phase 3/4 完成后，`builtin_skills/` 将新增 `explain/`、`quiz/`（主动提问）、`search_similar/`（找同类题）、`compose/`（组卷）——Phase 5 文档要覆盖这些目录
- `examples/` 目录需新建，放置 IPhO sample 题目（PNG × 2）
- `.github/assets/` 目录需新建，放置 asciinema SVG 录制文件
- `.github/ISSUE_TEMPLATE/` 目录需新建，放置两个 issue 模板

</code_context>

<specifics>
## Specific Ideas

- **Quick Start 参照感**：用户说参考 ripgrep / fzf 风，意思是 README 要有"为什么不用 [X]？"式的强对比段落（比如"为什么不直接用 ChatGPT 网页版？"），展示 cpho-cli 的核心差异点
- **asciinema SVG**：录完整 REPL 会话，要能在 GitHub README 上直接"播放"——使用 `svg-term-cli` 将 `.cast` 转换为 SVG，或直接用 `vhs` 生成
- **IPhO sample 题**：找一道 IPhO 官网公开的力学题（推荐 IPhO 1967–1980 年代的基础力学题，公开赛题），题目 PNG + 答案 PNG 放 `examples/`，README 里标注"来源：IPhO [年份] Problem [N]"
- **扩展文档最小 skill 示例**：示例 skill 建议做"统计 workspace 内题目总数"（`/count`），只需读 index、不需 LLM 调用，代码最短，展示注册机制最清晰
- **Out of Scope 框视觉**：README 里用 `> **不在计划内：**` blockquote 而非 HTML 折叠，保持 fzf 风的简洁

</specifics>

<deferred>
## Deferred Ideas

- **多语言 README**（EN/CN 切换）——用户选择纯中文，英文版可在社区需求明确后再做
- **GitBook / Docusaurus 文档站**——`docs/user/` 现在是 Markdown 文件，如果社区增长可以升级为静态文档站
- **asciinema 托管**（asciinema.org）——当前决定放 `.github/assets/`，托管方案可在仓库成熟后迁移
- **SECURITY.md**——纯本地工具暂不需要；有社区后补

</deferred>

---

*Phase: 05-user-manual-opensource*
*Context gathered: 2026-05-26*
