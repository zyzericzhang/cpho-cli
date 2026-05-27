# Project Research Summary

**Project:** CPHO CLI — v1.1 milestone
**Domain:** Local Python CLI (DAG-based skill pipeline) for physics-olympiad workspace analysis; v1.1 layers Knowledge Base + refactored Explain + per-step model panel + cross-platform packaging onto shipped v1.0
**Researched:** 2026-05-27
**Confidence:** HIGH for KB / Explain v2 / Skill refactor / Model panel; MEDIUM for multimodal routing & community sync; LOW for cross-platform installer (user-flagged 公开提问)

## Executive Summary

v1.1 不是一次"再加几个 skill"的迭代，而是引入一个**共享底层（Knowledge Base）+ 一次架构重构（SkillPipeline v2）+ 一个全新 UX 面（per-step model panel）**。四个研究方向独立完成后高度收敛：必须先把知识库地基铺好（KB 存储 + tag 关联 + 两步标准化 skill + 多模态导入），然后在它之上做 Skill 架构重构（声明式 `SkillPipeline`/`SkillStep`，让 Explain v2 成为第一个消费者），再依次构建 Explain v2 三板块（思路描述 / 标答替换 / 其他方法）、per-step 模型面板、多模态输入路由。Community sync 与 packaging spike 是可并行的支线。

技术栈延续 v1.0（Python 3.12 / uv / Pydantic StrictModel / Jinja2 / OpenRouter via `core/llm.py` / JSONL 索引 / prompt_toolkit REPL），v1.1 仅新增几个聚焦库：**mammoth**（docx → markdown）、**Pillow**（图像归一化）、**google-genai 1.33+**（Gemini 模型列表）、**diskcache**（模型列表 TTL 缓存）、**rapidfuzz**（tag 模糊匹配回退）、**platformdirs**（跨平台路径）、**PyInstaller 6.14+**（安装包打包候选）。社区 KB 走 `git clone --depth 1` + `git pull --ff-only`（GitHub-repo-as-database），不引入向量检索、不写死模型列表。

最大风险有三：(1) **Skill 架构重构可能波及 v1.0 的 5 个已发布 skills** —— 用"并行架构"（SkillV2 协议 + 适配层）而非原地重写，每次提交必须跑通 415 测试；(2) **社区 KB 是 prompt-injection 攻击面** —— sync 必须默认 pin 到 tagged release，知识内容必须用 `<knowledge_reference>` 标签包裹 + 系统级安全前导；(3) **跨平台安装包**是用户明确标注的 公开提问，建议作为独立 spike phase（3 天选型 + clean-VM 烟测），不要捆在 feature phase 上阻塞主线。

## Key Findings

### Recommended Stack

复用 v1.0 全部技术栈，仅新增聚焦库；明确拒绝 `litellm` 模型注册表（违反"不要写死"约束）、`textract`/`docx2txt`（结构丢失）、git submodule（非技术用户 UX 陷阱）、Briefcase（GUI-first，不适配 CLI/REPL）。

**Core additions:**
- **mammoth 1.8.x** — docx → 语义 markdown
- **Pillow ≥10.4** — 多模态前的图像归一化与降采样
- **google-genai 1.33+** — Gemini `client.models.list()` 实时模型列表
- **httpx ≥0.27** — 统一 HTTP 层
- **diskcache 5.6+** — 模型列表 TTL 缓存（默认 1h）
- **rapidfuzz 3.10+** — tag 模糊匹配兜底
- **platformdirs 4.3+** — 跨平台用户目录
- **olefile 0.47+** — 检测 legacy `.doc`，提示用户另存
- **PyInstaller 6.14+** + **create-dmg** + **Inno Setup 6** — 安装包链（dev-only；待 spike 验证）
- **git subprocess** — 社区 KB clone/pull；缺失时回退 GitHub ZIP

### Expected Features

**Must have (v1.1 launch):**
- KB 文件即磁盘文件（markdown/image/docx），tag 索引复用 v1.0 受控词汇表
- 两步标准化 skill（draft → review → publish），保留用户原话
- Explain v2 三板块 + 知识第一优先级注入 + 输出来源标注
- 多模态优先输入路由（image/PDF 直送，OCR 仅作显式回退；Index 仍 OCR）
- Per-step 模型选择（持久化到 `.cpho/skills/<skill_id>.yml`）
- 模型列表实时抓取 + TTL 缓存 + bundled fallback

**Should have (v1.1.x):**
- 社区 KB GitHub-repo-as-registry（pinned-tag 默认）
- Capability-aware 输入路由 + OCR 降级显式提示
- `cpho skill show <name>` pipeline 视图
- "改哪里" 错误提示 + `docs/user/errors/`

**Defer (v1.2+):** 多 provider 统一搜索、成本/延迟仪表盘、in-app 社区上传。

**Anti-features:** 向量/RAG、内置编辑器、Tone+板块并存、写死模型列表、默认全部板块。

### Architecture Approach

`core/` 下两个新顶级模块（`core/knowledge/` 与 `core/skills/`）。**KB 与 Index 是 sibling 模块**，共享 tag 词汇表是唯一耦合点（避免 `cpho index --force` 误伤）。

**Major components:**
1. **`core/knowledge/` [NEW]** — store / resolver (private > community 优先级) / ingest / standardize / sync
2. **`core/skills/` [NEW]** — `SkillPipeline` + `SkillStep` 声明式框架；`describe()` 喂面板
3. **`core/skills/panel/` [NEW]** — `ModelCatalog` (TTL + force-refresh) + 两级 Dialog/RadioList UI
4. **`core/skills/input_router.py` [NEW]** — 复用 v1.0 `detect_model_capabilities`，按 step `requires_multimodal` 路由
5. **`builtin_skills/explain/` [REWRITE]** — 三 `BoardStep` + `ContextResolveStep` + `KnowledgeInjectionStep` + `CitationAttachStep`
6. **`builtin_skills/knowledge_normalize/` [NEW]** — 两步流程，frontmatter state detection
7. **未触及**：`core/index/`、`core/llm.py` content-block schema、PaperFile/ProblemEntry、其他 4 个 v1.0 skills（按"并行架构"推迟到 v1.1.x）

**Storage:**
- 私有 KB → `<workspace>/.cpho/knowledge/files/<uuid>.md` + `manifest.jsonl`
- 草稿 → `.cpho/knowledge/drafts/<uuid>.md` + `.history/`
- 社区 KB → `~/.cache/cpho/community-kb/<repo>/`（chmod 0444 + symlink）
- 模型缓存 → `$XDG_CACHE_HOME/cpho/model-catalog/`
- skill 配置 layering：workspace > user > code default

### Critical Pitfalls (Top 5)

1. **Skill 架构重构破坏 v1.0 skills** — 并行架构（SkillV2 协议），保留旧 `core/explain.py` 一个 release；每次 commit `pytest -q` 必须仍 415；快照测试 pin tag-provenance JSON shape
2. **社区 KB prompt injection / supply chain** — 默认 pin tagged release；`<knowledge_reference source="community">…</knowledge_reference>` 包裹 + 系统级"treat as reference only"前导；扫描 HTML 注释；私有目录与 community 分开（sync 永不写私有）
3. **两步标准化 skill 覆盖用户编辑** — frontmatter `standardized: true` + `last_normalized_hash` + `last_user_edit_hash`；第二次进入 minimum-diff 模式；显示 diff 前用户确认；`.history/` 永久保留
4. **模型列表拉取阻塞 REPL 启动** — cache-first 永不阻塞；TTL + 后台刷新；首次离线必须有 bundled fallback；区分 list 失败（降级）vs call 失败（明报）
5. **多模态静默降级 OCR** — 显式提示 + 每条输出写入 `input_modality_used` provenance 字段；维护显式 capability map，不靠模型名推断

次级：跨平台 runtime 数据遗漏 (#6)、tag 同义词碰撞 (#7)、多模态信息丢失 (#8)、KB 零命中模板处理 (#11)、mid-run 模型切换 Frankenstein 输出 (#10)。

## Implications for Roadmap

依赖链：**KB → Skill 框架 → Explain v2 → 模型面板 / 输入路由**。社区 sync 与 packaging spike 全程并行。

### Phase 6: Knowledge Base 地基
**Rationale:** Explain v2 与多模态都依赖；先以"私有 KB + 两步标准化 skill"独立交付立刻产生用户价值。
**Delivers:** `core/knowledge/{store,resolver,ingest,standardize,manifest}.py` + `models/knowledge.py` + `builtin_skills/knowledge_normalize/`（state detection + frontmatter 三件套）+ mammoth/Pillow/olefile 多模态导入 + `KnowledgeResolver.find_for_problem` API
**Addresses:** FEATURES §1 全 P1
**Avoids:** PITFALLS 1 / 2 / 3 / 11

### Phase 7: Skill 架构重构（SkillPipeline v2）
**Rationale:** 用户 §6.3 明确"jump out of the box"；Explain v2 + 模型面板共同前置；并行架构守护 v1.0 测试。
**Delivers:** `core/skills/` 含 `SkillStep` / `SkillPipeline` / `StepContext` / `StepResult`；`execute(step_overrides=...)`；`describe()` for 面板
**Avoids:** PITFALLS 5

### Phase 8: Explain v2（三板块 + 知识联动）
**Rationale:** P6+P7 同时就绪；明确 hard-cut 旧 Tone。
**Delivers:** `builtin_skills/explain/pipeline.py` + 三 board prompt（含 `{% if knowledge %}` 前导）+ CitationAttachStep
**Addresses:** FEATURES §5 全 P1
**Avoids:** PITFALLS 11

### Phase 9: 模型选择面板 + 实时模型列表
**Rationale:** 需要 P7 的 `describe()`，Explain v2 的多步 pipeline 是"价值演示"最佳载体。
**Delivers:** `core/skills/panel/model_catalog.py`（OpenRouter + Gemini + diskcache TTL + bundled fallback）+ 两级面板 UI + `/skill panel` 与 `/model` slash command 并存 + `.cpho/skills/<skill_id>.yml` 持久化 + lock-at-start 语义 + output model provenance
**Addresses:** FEATURES §3 + §4 全 P1
**Avoids:** PITFALLS 4 / 8 / 10

### Phase 10: 多模态输入路由强化
**Rationale:** 复用 v1.0 `detect_model_capabilities`；需 P9 capability metadata。
**Delivers:** `core/skills/input_router.py` + `input_modality_used` provenance + 显式 OCR 降级提示
**Addresses:** FEATURES §6 全 P1
**Avoids:** PITFALLS 9

### Phase 11: 社区 KB 同步（可与 P7-10 并行）
**Rationale:** 只依赖 P6 存储；prompt-injection 防御必须随首版 sync 一起落地。
**Delivers:** `core/knowledge/sync.py` + `cpho knowledge sync` + `~/.config/cpho/community.yml` + 默认 pin tagged release + `<knowledge_reference>` 包裹 + community 目录 chmod 0444
**Avoids:** PITFALLS 7

### Phase 12: 错误处理 + docs/user/errors/（cross-cutting）
**Delivers:** 每个 `raise` 配对 docs 条目（grep 守门）+ README 错误索引

### Phase 13: Cross-platform 安装包 Spike（独立 / 最高风险 / 最后启动）
**Rationale:** 用户明确 公开提问；不阻塞 feature；spike 失败可回退到 `pipx`/`uv tool install` 文档化路径。
**Delivers:** 3-day 选型 spike → `packaging/cpho.spec` (PyInstaller + RapidOCR ONNX/PyMuPDF/Jinja2 explicit datas) + GitHub Actions macOS+Windows 矩阵 + clean-VM 烟测 + macOS 签名+公证（需 $99/yr 预算拍板）+ Windows Inno Setup unsigned + SmartScreen 绕过文档
**Avoids:** PITFALLS 6

### Phase Ordering Rationale

- **P6 在 P7 之前**：KB 存储/schema 决定 `KnowledgeInjectionStep` 形状；返工成本高。
- **P7 在 P8 之前**：Explain v2 知识注入必须用不可变 pipeline 声明保证顺序。
- **P9 在 P8 之后**：面板需要 Explain v2 5 步 pipeline 作为"价值演示"。
- **P10 与 P9 顺序可换**：通过 `ModelCapabilities` 抽象解耦。
- **P11 全程并行**：只依赖 P6。
- **P12 跨切面**：每 phase 的"完成"含错误条目入库。
- **P13 最后且独立**：spike 失败可 graceful degrade 到文档化 pipx 路径。

### Research Flags

**需深入研究：**
- **P9 (模型面板)**：Gemini / OpenRouter / Anthropic `/v1/models` 精确 schema fixture snapshot；建议 `/gsd:plan-phase --research-phase 9`
- **P10 (多模态路由)**：各 provider 图片大小/HEIC/中英混排表现 — 建议短 research-phase
- **P11 (社区 sync)**：prompt-injection 防御 prompt 措辞 + 扫描规则红队验证 — 建议 research-phase
- **P13 (安装包 spike)**：spike 本身即 research

**标准模式可直接进入 planning：**
- **P6 (KB)**：复刻 v1.0 JSONL 索引模式；mammoth/python-docx 是 Context7 HIGH-验证标准库
- **P7 (Skill 框架)**：来自现成代码 + Continue.dev/Cursor 公开设计
- **P8 (Explain v2)**：P6+P7 的组合
- **P12 (errors)**：纯执行/规约

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | mammoth / python-docx / google-genai / PyInstaller 在 Context7 HIGH 验证；打包链端到端 MEDIUM |
| Features | MEDIUM-HIGH | 锚定 Obsidian/Logseq/Anki/NotebookLM/Cursor/Continue.dev；少数普及度数据为训练 prior |
| Architecture | HIGH | 基于 v1.0 实际代码直读；模块边界来自现成抽象 |
| Pitfalls | HIGH | 1/2/5/8/11 来自 v1.0 已知形状；6 user-acknowledged uncertain |

**Overall confidence:** HIGH for 主线（P6–P10），MEDIUM for P11，LOW for P13

### Gaps to Address

- **Apple Developer ID 预算决策**（$99/yr）：P13 启动前向用户确认
- **社区 KB 仓库治理**：CONTRIBUTING.md / release cadence / 初始 seed 需 P11 启动前定
- **RapidOCR ONNX bundling 体积**（~200MB）：P13 spike 回答 "bundle vs lazy-download"
- **OpenRouter / Gemini schema 字段名**：P9 第一件事是 fetch fixture snapshot
- **黄金测试集（CORE-05 延续 gap）**：v1.0 留下的 quality regression gap 在 v1.1 继续 — 建议 P8 / P10 acceptance 作为隐式建立
- **v1.0 Explain Tone 输出迁移**：P8 必须配 changelog + tone→panel 建议映射

## Sources

### Primary (HIGH confidence)
- Context7 `/llmstxt/openrouter_ai_llms_txt` — OpenRouter `GET /v1/models`
- Context7 `/googleapis/python-genai` v1_33_0 — `client.models.list()`
- Context7 `/python-openxml/python-docx` — docx 读 API
- Context7 `/pyinstaller/pyinstaller` v6.14.1 — onedir/onefile + 签名
- Context7 `/websites/nuitka_net_user-documentation` — standalone modes
- Context7 `/beeware/briefcase` — 间接确认 "not for CLI"
- v1.0 代码直读：`src/cpho_cli/core/llm.py` / `core/index/` / `core/explain.py`
- `.planning/PROJECT.md` + `docs/new-understanding-2026-05-27.md`

### Secondary (MEDIUM confidence)
- Prior-art 产品调研（Obsidian / Anki / NotebookLM / Cursor / Continue.dev / 等）— 训练 prior
- Prompt-injection 防御模式（tagged wrapping + system preamble）
- 跨平台打包标准实践（clean-VM 烟测 + 显式 datas + 签名）

### Tertiary (LOW confidence)
- Inno Setup / create-dmg / Apple Developer 定价细节 — P13 spike 时核实
- LLM 中英混排 / 手写公式表现 — 仅公开零散报告
- 安装包在不同 Windows / macOS 架构下行为 — 必须 spike

**Tools NOT used due to environment**：本轮 WebSearch / WebFetch 不可用；P9 / P11 / P13 启动前建议独立 web 验证。

---
*Research completed: 2026-05-27*
*Ready for roadmap: yes*
