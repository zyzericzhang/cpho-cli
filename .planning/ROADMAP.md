# Roadmap: CPHO CLI

## Overview

CPHO CLI 从 v1.0 MVP（8 phases，51 plans）起步，v1.1 引入**共享底层（Knowledge Base）+ 一次架构重构（SkillPipeline v2）+ 一个全新 UX 面（per-step model panel）**。v1.1 分 4 个 phase：先铺知识库地基与 skill 框架，再在其上交付 Explain v2 + 模型面板 + 输入路由，然后落地社区库与错误处理，最后做跨平台分发。

## Milestones

- ✅ **v1.0 MVP** — Phases 1–5 (shipped 2026-05-27)
- 🚧 **v1.1 知识系统 + Explain 重构** — Phases 6–9 (planning)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1, 2, 02.1, 02.2, 02.3, 3, 4, 5) — SHIPPED 2026-05-27</summary>

- [x] **Phase 1: Core Foundation** (5/5 plans) — completed 2026-05-22
- [x] **Phase 2: Tag Indexing** (7/7 plans) — completed 2026-05-23
- [x] **Phase 02.1: Paper Splitting** (INSERTED, 5/5 plans) — completed 2026-05-24
- [x] **Phase 02.2: TUI REPL 骨架** (INSERTED, 6/6 plans) — completed 2026-05-24
- [x] **Phase 02.3: Index 读写分离 + Solve 降级** (INSERTED, 10/10 plans) — completed 2026-05-25
- [x] **Phase 3: Skill 跨切面 + 核心讲解 Skills** (8/8 plans) — completed 2026-05-26
- [x] **Phase 4: 找同类题 + 组卷 + 异常处理** (6/6 plans) — completed 2026-05-26
- [x] **Phase 5: 用户手册 + 开源准备** (4/4 plans) — completed 2026-05-26

Full details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

### 🚧 v1.1 知识系统 + Explain 重构 (Phases 6–9)

- [ ] **Phase 6: 知识库地基 + Skill 框架重构** (TBD plans)
- [ ] **Phase 7: Explain v2 + 模型面板 + 输入路由** (TBD plans)
- [ ] **Phase 8: 社区 KB + 错误处理** (TBD plans)
- [ ] **Phase 9: 跨平台 + 安装包** (TBD plans)

## Phase Details

### Phase 6: 知识库地基 + Skill 框架重构

**Goal:** 在 v1.0 之上引入两个共享底层模块——`core/knowledge/`（私有 KB 存储 + 两步标准化 skill + 多模态导入 + Resolver API）与 `core/skills/`（声明式 SkillPipeline + SkillStep 框架）；为 Phase 7 的 Explain v2 与模型面板铺好地基。私有 KB 与标准化 skill 在此 phase 即可独立交付用户价值。

**Depends on:** Phase 5 (v1.0)

**Requirements:** KB-01, KB-02, KB-03, KB-04, SKILL-PIPE-01, SKILL-PIPE-02, SKILL-PIPE-03

**Success Criteria** (what must be TRUE):
1. 用户将 markdown / LaTeX / 图片 / docx 知识文件放入 `<workspace>/.cpho/knowledge/files/`，frontmatter 含 `canonical_tag_id` 与 v1.0 词汇表关联；工具通过 `KnowledgeResolver.find_for_problem(problem_id)` 按题目 tag 返回匹配知识文件列表（私有优先）。
2. 用户运行"知识标准化 skill"将自由格式文件转为标准化文件：第一步生成草稿到 `.cpho/knowledge/drafts/` 含 frontmatter 三件套（`standardized` / `last_normalized_hash` / `last_user_edit_hash`）；第二步检测用户编辑后进入 minimum-diff 模式，发布到知识区；保留用户原话与原意。
3. 标准化 skill 处理图片 / docx / 手写版图片时走多模态 LLM 而非 OCR；docx 经 mammoth 转为语义 markdown；legacy `.doc` 通过 olefile 检测后给出"改哪里"提示。
4. 系统提供 `SkillPipeline` + `SkillStep` 声明式框架，每个 step 声明输入 / 输出 / prompt 模板 / 默认模型 / `requires_multimodal`；每个 SkillPipeline 实现 `.describe()` 返回结构化步骤元数据供面板使用。
5. v1.0 已有 4 个 skills（solve / probe / related / compose）行为保持不变，`uv run pytest -q` 仍为 415 通过；新框架与旧 skills 并行共存。

**Plans**: TBD（见 `/gsd:plan-phase 6` 拆分）

### Phase 7: Explain v2 + 模型面板 + 输入路由

**Goal:** 在 Phase 6 底层之上交付 v1.1 的核心 UX 闭环：Explain v2（板块选择替代 Tone + 知识文件第一优先级 + 输出来源标注）+ 每 skill 步骤模型选择面板（实时抓取 OpenRouter / Gemini 模型列表 + TTL 缓存 + bundled fallback）+ 多模态优先输入路由（OCR 仅作显式降级）。Explain v2 是新 SkillPipeline 框架的第一个完整消费者，演示价值。

**Depends on:** Phase 6

**Requirements:** EXPLAIN-V2-01, EXPLAIN-V2-02, EXPLAIN-V2-03, EXPLAIN-V2-04, MODEL-PANEL-01, MODEL-PANEL-02, MODEL-PANEL-03, MODEL-PANEL-04, INPUT-01, INPUT-02, INPUT-03

**Success Criteria** (what must be TRUE):
1. 用户运行 Explain 时不再选 Tone，而是按需多选板块（思路描述 / 标答替换 / 其他方法）；思路描述不出完整推导只描述底层逻辑；标答替换补全跳步可直接替代标准答案；其他方法思考有无更优处理方式（如能量法 vs 受力法）。
2. 任意板块生成前 Explain 必先查询 KnowledgeResolver；若题目 tag 有对应知识文件，让 LM 先读知识再生成；输出必须标注引用来源（用了哪些知识文件 / 对应位置）。v1.0 Tone 选项 hard-cut 移除，changelog 提供 tone → 板块映射。
3. 用户运行任一 skill 可打开 `/skill panel` 看到该 skill 完整 pipeline（步骤名 / prompt 路径 / 当前模型）；可为每步独立选模型，持久化到 `.cpho/skills/<skill_id>.yml`（layering: workspace > user > code default）。
4. 模型列表从 OpenRouter `GET /api/v1/models` 与 Gemini `client.models.list()` 实时抓取，diskcache TTL 默认 1h，可 force-refresh；首次离线 / API 失败有 bundled fallback；REPL 启动永不阻塞；list 失败（降级）与 call 失败（明报）区分。
5. Index 仍用 OCR + 文本（保持 v1.0 行为）；其他 skill 默认走原始图片 / PDF（多模态），模型不支持时显式降级 OCR 并提示"哪个步骤为什么降级"，不静默；输出 provenance 含 `input_modality_used` 字段。

**Plans**: TBD（plan-phase 时建议拆 wave：Explain v2 / 模型面板 / 输入路由）

### Phase 8: 社区 KB + 错误处理

**Goal:** 落地两个 v1.1 收尾性能力：(1) `cpho knowledge sync` 从 GitHub 社区开源库拉取知识文件到 `~/.cache/cpho/community-kb/`，默认 pin tagged release + prompt-injection 防御；(2) 全链路错误诊断打磨——各类失败给出明确"改哪里"提示，`docs/user/errors/` 错误索引覆盖每个用户可见的 `raise`，README 加错误索引章节。可与 Phase 7 部分并行（仅依赖 Phase 6 KB 存储）。

**Depends on:** Phase 6 (KB 存储 + SkillPipeline)；可与 Phase 7 部分并行

**Requirements:** KB-05, ERROR-01, ERROR-02

**Success Criteria** (what must be TRUE):
1. 用户运行 `cpho knowledge sync` 从配置的 GitHub 仓库（`~/.config/cpho/community.yml`）拉取社区知识库到 `~/.cache/cpho/community-kb/`，默认 pin 到 tagged release（非 floating main）；community 目录 chmod 0444 只读；KnowledgeResolver 按 private > community 优先级返回。
2. 社区知识注入 Explain prompt 时必须用 `<knowledge_reference source="community">…</knowledge_reference>` 标签包裹 + 系统级"treat as reference only"前导；sync 永不写入私有目录。
3. 各类失败给出明确"改哪里"提示：skill prompt markdown 缺失（告诉用户路径）、API 调用失败（区分配置 / 平台 / 网络错误）、配置错误（指出 config.local.yml 哪一行）、knowledge 文件格式错误（指出 frontmatter 哪一字段）。
4. `docs/user/errors/` 目录存在，每个用户可见的 `raise` 配对一个 docs 条目；grep 守门测试保证不遗漏；README 含错误索引章节链接到 `docs/user/errors/`。

**Plans**: TBD（见 `/gsd:plan-phase 8` 拆分）

### Phase 9: 跨平台 + 安装包

**Goal:** 收尾 v1.1 分发体验：先验证 CPHO CLI 在 Windows 10/11 上完整可运行（prompt_toolkit / PyMuPDF / RapidOCR 烟测），然后用 3 天 spike 评估打包方案（PyInstaller vs Nuitka vs pipx 文档化路径），输出 clean-VM 烟测脚本与签名 / SmartScreen 风险评估；spike 通过则交付 Mac/Windows 一键安装包（GitHub Actions 矩阵），spike 揭示打包成本过高则交付 pipx / uv tool install 清晰文档化路径作为兜底。

**Depends on:** Phase 6 (代码层稳定)；可与 Phase 7/8 完全并行

**Requirements:** INSTALLER-01, INSTALLER-02, INSTALLER-03

**Success Criteria** (what must be TRUE):
1. CPHO CLI 在 Windows 10/11 Windows Terminal 中文 / Unicode / 颜色行为正常；PyMuPDF / RapidOCR 在 Windows 烟测通过；现有 Phase 4 boundary 检查在 Windows 路径分隔符与外接盘上行为正确。
2. 完成 3 天打包方案 spike：输出 `packaging/cpho.spec` 候选 + clean-VM 烟测脚本 + 包体积报告（关注 RapidOCR ONNX ~200MB）+ macOS 签名 / Windows SmartScreen 风险评估（Apple Developer ID $99/yr 决策点向用户上报）+ 明确"做 / 不做"建议。
3. spike 通过：GitHub Actions macOS+Windows 矩阵构建产出 `.dmg` + `.exe`/`.msi`，clean-VM 烟测通过；spike 不通过：交付 `pipx install cpho-cli` / `uv tool install cpho-cli` 清晰文档化安装路径作为 v1.1 分发兜底。

**Plans**: TBD（见 `/gsd:plan-phase 9` 拆分；spike 阶段建议独立成 plan）

## Progress

**Execution Order:**
- v1.1 phases execute in dependency order: 6 → 7（强依赖 6）；8 可与 7 并行（仅依赖 6）；9 完全独立可全程并行。
- 整数 phase 顺序：6 → 7 → 8 → 9（含并行可能）

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
| 6. 知识库地基 + Skill 框架重构 | v1.1 | 0/TBD | Not started | - |
| 7. Explain v2 + 模型面板 + 输入路由 | v1.1 | 0/TBD | Not started | - |
| 8. 社区 KB + 错误处理 | v1.1 | 0/TBD | Not started | - |
| 9. 跨平台 + 安装包 | v1.1 | 0/TBD | Not started | - |
