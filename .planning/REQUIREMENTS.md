# Requirements: CPHO CLI

**Defined:** 2026-05-20
**Core Value:** 生成质量——真正找到题目的难点、启发点，讲清楚每一步推导的"为什么"，关联到相关题目形成知识网络。

## v1 Requirements

### 核心管线 (Core)

- [x] **CORE-01**: 用户可通过默认 `config.local.yml`、显式 `--config` 或环境变量设置 LLM API key；同一配置文件可保存多个 provider/key profile，并通过 `--provider` 选择，密钥不硬编码不提交 git
- [x] **CORE-02**: 用户可指定本地文件夹作为工作空间，工具自动发现其中所有 PDF 和图片文件作为待分析试卷，通过 Phase 02.1 切分器将多题试卷拆分为独立题目条目
- [x] **CORE-03**: 用户可通过抽象 OCR 接口提取 PDF/图片中的文本（含中文+LaTeX 混合内容），默认使用 RapidOCR，接口支持切换其他 OCR 引擎
- [x] **CORE-04**: 用户可运行 `cpho solve <题目>` 命令，通过 DAG 管线引擎分步执行 LLM 调用，每步裁剪上下文聚焦单任务，步骤间通过 blackboard 传递中间结果
- [ ] **CORE-05**: 项目包含 20-30 道精选物理竞赛题的黄金测试集，用于每次 prompt 或模型变更后的回归验证，确保解析质量不退化

### 索引层 (Index)

- [x] **IDX-01**: 用户运行 `cpho index` 对工作空间中所有题目（经 Phase 02.1 从试卷拆分）自动生成标签（物理模型、启发点、难点、数学技巧），标签存入 JSONL 索引文件
- [x] **IDX-02**: 索引系统使用内容哈希检测试卷文件变更（新增/修改），仅对变更文件重新索引
- [x] **IDX-03**: 后续 skill 执行时通过标签索引检索题目，而非重复读取原始文件全文，标签使用受控词汇表保证一致性

### 内置核心讲解 Skills (Phase 3)

- [ ] **SKILL-SOLVE-REPOSITION**: 用户运行 `cpho solve <题目>`，工具不返回新解法，而是对工作空间内匹配到的标准答案做逐步审查；发现的错误以受控 tag 形式写入 index 的 skill-tag 层（与 LLM 机打 tag 分离，含 skill 来源 / 时间 / 推理出处的 provenance），`cpho index --force` 重建只覆盖机打 tag、保留 skill 写入的 tag
- [ ] **SKILL-EXPLAIN-NEW**: 用户运行 Explain 可选择一个或多个 Tone（老师型 / 知识点密集型 / 简短型）同时生成多版输出；每版首段先用几句话陈述整道题物理图像与解题思路再开始推导；输出分栏目（原答案逐步讲解 / 超越原答案的更清晰推导 / 句子级 explain），物理为主数学为辅；讲解结束后用户可选择把新发现的 tag 回写 Index skill-tag 层（用户可手工增删）
- [ ] **SKILL-PROBE**: 用户运行"主动提问 Skill"，工具就同一道题展开连续对话寻找关键点 / 关键步骤 / 深挖处理；结束生成一份 markdown 文件（路径用户输入、有默认值、文件名含题目名），前半为所有问题、后半为对应解答

### Skill 通用跨切面能力 (Phase 3)

- [ ] **CROSS-EXPORT**: 所有 skill 运行结束都可一键导出为 markdown；路径由用户输入、每类文件有默认值、文件名必须含题目名，规则统一
- [ ] **CROSS-FOLLOWUP**: 所有 skill 运行结束后用户进入 Follow-up 对话模式，可基于本次 skill 上下文像 ChatGPT 网页版那样继续追问，直至显式退出
- [ ] **CROSS-PROGRESS**: 所有 skill 运行过程中都有类似 Claude Code 的进度显示（当前到第几步 / 正在做什么 / 已耗时）
- [ ] **CROSS-ORDER**: Solve 优先于其他 skill 运行——其他 skill (Explain/主动提问/找同类题/组卷) 默认在 Solve 校正过的标答基础上工作

### 知识网络应用 Skills (Phase 4)

- [ ] **SKILL-RELATED**: 用户对任意已索引题目运行"找同类题 skill"，工具基于 index 标签层返回按相似度排序的同类题列表，结果可作为下一个 skill（组卷 / Explain 对比等）的输入
- [ ] **SKILL-COMPOSE**: 用户准备的编排文件（题号 → 题目 ID / pass / 分类与要求）可被组卷 skill 消费，工具从原始 PDF 裁剪页面拼接生成两份 PDF（题目卷一页一题、答案卷分开），不做 LaTeX 重渲染；用户也可让 skill 完全自动选题，无需手写编排文件即可产出 PDF

### 异常边界处理 (Phase 4)

- [ ] **ROBUST-BOUNDARY**: 工作空间挂在外接硬盘且中途拔出 / 用户中途 Ctrl+C / 用户选择的文件不在当前 workspace / OCR / LLM 调用失败：工具都有明确失败提示而非卡死；任意 skill 中间产物（blackboard、partial markdown、explain 中间版本）落盘到可恢复位置，下次运行同一 skill 可选择继续或丢弃

### 用户手册 + 开源准备 (Phase 5)

- [ ] **DOCS-README**: 仓库根 README.md 遵循著名开源项目版面（简介 / 截图或 asciinema / 安装 / Quick Start / REPL 用法 / 所有内置 skill 列表与示例 / 配置 / 扩展指南 / License）；新用户从 clone 到运行第一个 skill 在 10 分钟内可完成；至少含一张运行截图或 asciinema
- [ ] **DOCS-USER**: `docs/user/` 目录存在，按 skill / 模块分章提供 README 延伸文档；至少覆盖 solve / explain（含 Tone 与回写 Index）/ 主动提问 / 找同类题 / 组卷 / index / REPL 每个 skill 的运行参数、典型用法、导出文件说明
- [ ] **PLUGIN-PY-SIMPLE**: 简化 Python 扩展机制有专门文档：明确要写哪个 Python 类 / 函数、如何复用 `core/llm.py` 与 index 读写 API、如何在 REPL 注册新 slash command；用户改代码加 skill，复杂度低于 v1 设想的 YAML loader

### TUI REPL 界面 (TUI)

- [x] **TUI-01**: 用户运行 `cpho repl` 进入 REPL 交互界面，可用 `/` 斜杠命令执行操作，命令支持 Tab 自动补全
- [x] **TUI-02**: REPL 会话内搜索结果、当前题目等上下文跨命令共享（有状态会话）
- [x] **TUI-03**: Skill 注册为 Command 对象 + 补全规则，新增 skill 不需要修改 REPL 主循环或 TUI 布局
- [x] **TUI-04**: 首批实现 `/search`（按标签/关键词查题）和 `/show`（显示题目详情）两个斜杠命令

## v2 Requirements

(暂无——v1 范围已覆盖所有当前规划能力)

## Out of Scope

| Feature | Reason |
|---------|--------|
| GUI / Web 界面 | v1 纯命令行 + TUI REPL，不做图形界面 |
| 数据库存储（PostgreSQL/Supabase） | 文件系统 + JSONL 足够 v1 使用 |
| 多用户 / 权限 / 登录系统 | 本地单用户工具 |
| LaTeX 渲染引擎 | PDF 输出采用图片拼接方案，不重渲染公式 |
| 自主 ReAct-style Agent | 使用确定性 DAG 管线，确保每一步可控可审计 |
| 和线上 CPHO Platform 的数据同步 | v2+ 联动功能 |
| 向量检索 / RAG | v1 使用结构化标签索引，更可控 |
| 手机端 / 平板端 | 仅桌面 CLI |
| YAML skill loader（旧 PLUGIN-01） | 2026-05-26 — 用户决定走简化 Python 扩展（PLUGIN-PY-SIMPLE），不再要求 YAML 这种灵活度 |
| Skill Creator 自然语言生成 skill（旧 PLUGIN-02） | 2026-05-26 — 暂时不做，之后再说 |
| `pip install` 第三方 skill 包（旧 PLUGIN-04） | 2026-05-26 — 用户改代码扩展即可，不引入 entry points 机制 |
| 知识图谱可视化 / 显式题目关联图（旧 KNOW-01） | 2026-05-26 — 同类题以"找同类题 skill"（SKILL-RELATED）按需查询替代，不维护独立图谱构件 |
| 跨 skill 自动注入相关题目上下文（旧 KNOW-02） | 2026-05-26 — 由用户在"找同类题 skill"→ 下一 skill 显式串联，不做自动注入 |
| Quiz 模式 REPL 苏格拉底对话（旧 SKILL-02） | 2026-05-26 — 用户主动提问（SKILL-PROBE）+ Follow-up（CROSS-FOLLOWUP）替代 |
| 跨题目对比分析模式（旧 SKILL-03） | 2026-05-26 — 由"找同类题 skill"输出 + Explain Follow-up 显式组合实现，不再单独立 skill |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CORE-01 | Phase 1 | Complete |
| CORE-02 | Phase 1 | Complete |
| CORE-03 | Phase 1 | Complete |
| CORE-04 | Phase 1 | Complete |
| CORE-05 | Phase 1 | Needs Review |
| IDX-01 | Phase 2 | Complete |
| IDX-02 | Phase 2 | Complete |
| IDX-03 | Phase 2 | Complete |
| TUI-01 | Phase 02.2 | Complete |
| TUI-02 | Phase 02.2 | Complete |
| TUI-03 | Phase 02.2 | Complete |
| TUI-04 | Phase 02.2 | Complete |
| SKILL-SOLVE-REPOSITION | Phase 3 | Pending |
| SKILL-EXPLAIN-NEW | Phase 3 | Pending |
| SKILL-PROBE | Phase 3 | Pending |
| CROSS-EXPORT | Phase 3 | Pending |
| CROSS-FOLLOWUP | Phase 3 | Pending |
| CROSS-PROGRESS | Phase 3 | Pending |
| CROSS-ORDER | Phase 3 | Pending |
| SKILL-RELATED | Phase 4 | Pending |
| SKILL-COMPOSE | Phase 4 | Pending |
| ROBUST-BOUNDARY | Phase 4 | Pending |
| DOCS-README | Phase 5 | Pending |
| DOCS-USER | Phase 5 | Pending |
| PLUGIN-PY-SIMPLE | Phase 5 | Pending |

**Superseded / Moved to Out of Scope (2026-05-26 重写):**
- SKILL-01（旧"逐步讲解模式"）→ 被 SKILL-EXPLAIN-NEW 取代并大幅增强
- SKILL-02（旧"主动提问/Quiz 模式"）→ 拆分为 SKILL-PROBE + CROSS-FOLLOWUP
- SKILL-03（旧"对比分析模式"）→ 移入 Out of Scope，由 SKILL-RELATED + CROSS-FOLLOWUP 显式组合替代
- SKILL-04（旧"组卷输出模式"）→ 被更具体的 SKILL-COMPOSE 取代（编排文件 + 自动选题）
- PLUGIN-01（旧 YAML skill loader）→ Out of Scope，由 PLUGIN-PY-SIMPLE 替代
- PLUGIN-02（旧 NL Skill Creator）→ Out of Scope（"之后再说"）
- PLUGIN-03（旧 Python SkillBase）→ 收敛为 PLUGIN-PY-SIMPLE（更窄、更明确）
- PLUGIN-04（旧 pip 第三方 skill）→ Out of Scope
- KNOW-01（旧知识图谱构建）→ Out of Scope，由 SKILL-RELATED 按需查询替代
- KNOW-02（旧自动相关题目注入）→ Out of Scope，由用户显式串联替代

**Coverage (重写后):**
- v1 requirements: 26 total（12 已完成 + 14 待做）
- Mapped to phases: 26 (100%)
- Unmapped: 0
- Superseded/Out of Scope: 10（旧 SKILL-01~04 / PLUGIN-01/02/03/04 / KNOW-01/02）

---
*Requirements defined: 2026-05-20*
*Last updated: 2026-05-26 — Phase 3/4 重写 + Phase 5 新增，依据 docs/new-understanding-2026-05-26.md；旧 SKILL/PLUGIN/KNOW 系列收敛或移入 Out of Scope*
