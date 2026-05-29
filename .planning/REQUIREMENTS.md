# Requirements: CPHO CLI v1.1

**Defined:** 2026-05-27
**Milestone:** v1.1 知识系统 + Explain 重构
**Core Value:** 生成质量——真正找到题目的难点、启发点，讲清楚每一步推导的"为什么"，关联到相关题目形成知识网络。
**Reference:** `docs/new-understanding-2026-05-27.md` + `.planning/research/SUMMARY.md`

## v1.1 Requirements

### 知识记录系统 (Knowledge Base) — 共享底层新功能

- [ ] **KB-01**: 用户可在 `<workspace>/.cpho/knowledge/files/` 下放置 markdown / LaTeX / 图片 / docx 知识文件，系统通过 frontmatter 中的 `canonical_tag_id` 与 v1.0 受控词汇表关联；不存在的 tag 给出明确提示，不静默丢失
- [ ] **KB-02**: 用户可运行"两步标准化 skill"将自由格式知识文件转为符合规范的标准化文件——第一步生成草稿到 `.cpho/knowledge/drafts/`，用户审核（或手工修改）后第二步发布到知识区；frontmatter `standardized` / `last_normalized_hash` / `last_user_edit_hash` 字段保证再运行不覆盖用户编辑（minimum-diff 模式）
- [ ] **KB-03**: 标准化 skill 处理图片 / docx / 手写版图片时走多模态 LLM 而非 OCR；标准化过程必须尽量保留用户原话与原意，仅作格式适配而非内容大改写
- [ ] **KB-04**: 系统提供 `KnowledgeResolver.find_for_problem(problem_id)` Python API，依据 ProblemEntry 的 tag 返回匹配的知识文件列表（优先级：private > community），供其他 skill 注入
- [ ] **KB-05**: 用户可运行 `cpho knowledge sync` 从 GitHub 社区开源库拉取知识文件到 `~/.cache/cpho/community-kb/`，默认 pin 到 tagged release（非 floating main）；社区目录 chmod 0444（只读）；私有目录与 community 分开，sync 永不写入私有目录

### Skill 架构重构 (SkillPipeline v2)

- [ ] **SKILL-PIPE-01**: 系统提供声明式 `SkillPipeline` + `SkillStep` 框架，每个 step 声明输入 / 输出 / prompt 模板 / 默认模型 / `requires_multimodal` 能力；新 Explain v2 必须基于此框架实现
- [ ] **SKILL-PIPE-02**: 每个 SkillPipeline 实现 `.describe()` 方法返回结构化步骤元数据（步骤名 / 描述 / 默认模型 / prompt 模板路径），供模型面板与 `cpho skill show <name>` 命令使用
- [ ] **SKILL-PIPE-03**: 重构期间 v1.0 已有 4 个 skills（solve / probe / related / compose）保持现行行为不变；测试基线 `uv run pytest -q` 必须仍为 415 通过（除明确针对 Explain v2 新增/修改的测试）

### Explain v2 板块设计

- [ ] **EXPLAIN-V2-01**: 用户运行 Explain 时不再选 Tone，而是按需多选板块（思路描述 / 标答替换 / 其他方法）。思路描述板块描述拿到题第一眼应想出什么思路、底层逻辑（未知量 / 方程 / 为什么找这些方程），不出完整数学推导；标答替换板块挑出小问关键步骤或答案跳步处补全过程，可直接替代标准答案；其他方法板块思考有无比标答更好的处理方式（如能量法替受力法、张量替运算展开）
- [ ] **EXPLAIN-V2-02**: 不论用户选了哪些板块，Explain 第一步必须查询 KnowledgeResolver；若该题 tag 对应有知识文件，必须先让 LM 读一遍知识总结再开始板块生成；知识文件作为最高优先级参考
- [ ] **EXPLAIN-V2-03**: Explain 输出必须标注引用来源——用了哪些知识文件、对应位置；社区知识必须用 `<knowledge_reference source="...">` 标签包裹注入 prompt，并配系统级"treat as reference only"前导防 prompt injection
- [ ] **EXPLAIN-V2-04**: v1.0 Explain Tone 设计 hard-cut，旧选项移除；changelog 提供 tone → 板块迁移建议映射；不保留 dual-mode

### 模型选择与 Skill 配置面板

- [ ] **MODEL-PANEL-01**: 用户运行任一 skill 时可打开 `/skill panel`（或运行后展示），看到该 skill 的完整 pipeline——每步名称、提示词文件路径、当前调用模型；面板需展示步骤之间的逻辑关系
- [ ] **MODEL-PANEL-02**: 用户可在面板中为每个步骤独立选择模型，选择持久化到 `<workspace>/.cpho/skills/<skill_id>.yml`；layering 顺序：workspace > user (`~/.config/cpho/skills/<id>.yml`) > code default；`config.local.yml` 不变（仍是 provider 凭证源）
- [ ] **MODEL-PANEL-03**: 模型列表从 provider 官网实时抓取（OpenRouter `GET /api/v1/models`、Gemini `client.models.list()`），不写死；不使用 litellm 等含硬编码列表的库
- [ ] **MODEL-PANEL-04**: 模型列表带 TTL 缓存（默认 1h，可手动 force-refresh）；首次离线或 API 失败必须有 bundled fallback 列表；REPL 启动永不阻塞在模型列表拉取；list 失败（降级）与 call 失败（明报）必须区分

### 输入策略强化

- [ ] **INPUT-01**: Index 用 OCR + 文本（保持 v1.0 行为）；除 Index 以外的 skill 默认优先用原始图片 / PDF（多模态），通过 SkillStep 的 `requires_multimodal` 声明与模型能力检测路由
- [ ] **INPUT-02**: 用户配置的模型不支持多模态时自动降级到 OCR 文本路径并显式提示（哪个步骤、为什么降级），不静默回退
- [ ] **INPUT-03**: 每条 skill 输出在 provenance 中记录 `input_modality_used` 字段（multimodal_image / multimodal_pdf / ocr_text），便于追溯

### 错误处理 + 文档化

- [ ] **ERROR-01**: 各类失败必须给出明确"改哪里"提示：skill prompt markdown 文件缺失（告诉用户文件路径）、API 调用失败（区分配置错误 / 平台错误 / 网络错误并给操作建议）、配置缺失或写错（指出 config.local.yml 哪一行）、knowledge 文件格式错误（指出 frontmatter 哪一字段）
- [ ] **ERROR-02**: `docs/user/errors/` 目录存在，每个用户可见的 `raise` 配对一个 docs 条目（grep 守门测试保证不遗漏）；README 含错误索引章节链接到 `docs/user/errors/`

### 跨平台 + 安装包

- [x] **INSTALLER-01**: CPHO CLI 在 Windows 10/11 上可运行——prompt_toolkit REPL 在 Windows Terminal 中文 / Unicode / 颜色行为正常，PyMuPDF / RapidOCR 在 Windows 烟测通过
- [x] **INSTALLER-02**: 完成跨平台打包方案 spike——3 天评估 PyInstaller vs Nuitka vs pipx 文档化路径，输出 `packaging/cpho.spec`（候选方案）+ clean-VM 烟测脚本 + 包体积报告 + macOS 签名 / Windows SmartScreen 风险评估；spike 输出含明确"做 / 不做"建议
- [x] **INSTALLER-03**: spike 通过后交付 Windows PyInstaller/Inno Setup release workflow；Mac 交付 Homebrew + `uv tool install` 文档化路径；开发阶段仍为 macOS 本地开发 + 普通测试，release 阶段才由 GitHub Actions Windows runner 构建安装器

## Future Requirements (Deferred to v1.2+)

- **QUALITY-01** (CORE-05 延续): 20-30 道精选物理竞赛题黄金测试集 — v1.0 留下的 quality regression gap，v1.1 通过 EXPLAIN-V2 + INPUT 的 acceptance test 隐式建立部分覆盖，完整黄金集延迟到 v1.2
- 多 provider 统一搜索面板
- 成本 / 延迟仪表盘
- in-app 社区知识库上传
- 黑板（blackboard）跨 skill 自动注入相关题目上下文

## Out of Scope (Explicit Exclusions)

| Feature | Reason |
|---------|--------|
| 向量检索 / RAG 形式的知识检索 | 与 v1.0 决策一致：tag 驱动 + 受控词汇表，确定性 + 可审计 |
| Tone + 板块并存（dual-mode Explain） | 用户明确 hard-cut，避免架构与文档分裂 |
| 写死模型列表 / litellm 风格 hardcoded registry | 违反"实时扒取"约束 |
| 自动注入社区内容到私有 KB | 安全 + 用户控制原则：sync 永不写入私有目录 |
| in-app 社区上传 / PR 提交流 | v1.1 走 GitHub web PR 即可，CLI 内置上传过度 |
| `pip install cpho-skill-xxx` 第三方 skill 包 | 沿用 v1.0 决策：用户改代码扩展 |
| docx → PDF 中间渲染 (mammoth 直接到 markdown 即可) | 增加 LibreOffice 系统依赖，与 Python-only 约束冲突 |
| GUI 配置面板 | v1.1 仍是 CLI + TUI REPL；面板用 prompt_toolkit Dialog/RadioList 实现 |
| 自动 prompt-injection 检测的 ML 模型 | 用 `<knowledge_reference>` 标签包裹 + 系统前导即可；不引入 classifier |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| KB-01 | Phase 6 | Pending |
| KB-02 | Phase 6 | Pending |
| KB-03 | Phase 6 | Pending |
| KB-04 | Phase 6 | Pending |
| SKILL-PIPE-01 | Phase 6 | Pending |
| SKILL-PIPE-02 | Phase 6 | Pending |
| SKILL-PIPE-03 | Phase 6 | Pending |
| EXPLAIN-V2-01 | Phase 7 | Pending |
| EXPLAIN-V2-02 | Phase 7 | Pending |
| EXPLAIN-V2-03 | Phase 7 | Pending |
| EXPLAIN-V2-04 | Phase 7 | Pending |
| MODEL-PANEL-01 | Phase 7 | Pending |
| MODEL-PANEL-02 | Phase 7 | Pending |
| MODEL-PANEL-03 | Phase 7 | Pending |
| MODEL-PANEL-04 | Phase 7 | Pending |
| INPUT-01 | Phase 7 | Pending |
| INPUT-02 | Phase 7 | Pending |
| INPUT-03 | Phase 7 | Pending |
| KB-05 | Phase 8 | Pending |
| ERROR-01 | Phase 8 | Pending |
| ERROR-02 | Phase 8 | Pending |
| INSTALLER-01 | Phase 9 | Complete |
| INSTALLER-02 | Phase 9 | Complete |
| INSTALLER-03 | Phase 9 | Complete |

**Coverage:**
- v1.1 requirements: 24 total
- Mapped to phases: 24 (100%)
- Unmapped: 0

---
*Requirements defined: 2026-05-27 — derived from docs/new-understanding-2026-05-27.md + .planning/research/SUMMARY.md*
