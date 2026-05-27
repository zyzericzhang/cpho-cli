# Phase 6: 知识库地基 + Skill 框架重构 - Context

**Gathered:** 2026-05-27
**Status:** Ready for planning

## Phase Boundary

Phase 6 交付两个共享底层模块：

1. **`core/knowledge/`** — 私有知识库存储（`files/inbox/` + `files/published/`），两步标准化 skill（草稿→审核→发布），多模态导入（图片/docx 走多模态 LLM，不 OCR），`KnowledgeResolver` Python API（tag 匹配 + community 自动发现）。

2. **`core/skills/` 增强** — `SkillStep` 新增 `requires_multimodal`（声明+自动路由+降级实时提示）和 `default_model`（step 级）可选字段；`SkillSpec` 新增 `.describe()` 方法返回完整 DAG（步骤列表+依赖边+输入输出连线）。v1.0 已有 4 个 skills 保持现行行为不变（SKILL-PIPE-03），新字段设默认值，旧 skill.yml 不改。

私有 KB 与标准化 skill 在此 phase 即可独立交付用户价值；SkillPipeline 增强为 Phase 7 Explain v2 与模型面板铺好地基。

## Implementation Decisions

### 知识文件存储结构

- **D-01:** 目录布局 — `files/inbox/` 存放原始文件，标准化审核通过后移入 `files/published/`。
- **D-02:** Frontmatter 必填字段 — `standardized` / `last_normalized_hash` / `last_user_edit_hash` / `canonical_tag_id`，其余结构化字段可选，Resolver 按需取用。
- **D-03:** 文件格式 — 接受任意文本文件（markdown / LaTeX / txt / rst 等），未知格式当纯文本处理。

### KnowledgeResolver API

- **D-04:** 匹配策略 — 精确 tag ID 匹配优先；无结果时放宽到同 `TagCategory`（physics_law / physics_model / math_technique / heuristic / approximation）回退。
- **D-05:** 多 tag 排序 — 平等排序，不做 category 权重区分。
- **D-06:** 返回格式 — `list[KnowledgeMatch]`，每项含 `path` / `canonical_tag_id` / `source`（private | community）/ `repo_name`（仅 community 有值）。
- **D-07:** 构造函数 — 仅 `workspace_root: Path`，community 目录（`~/.cache/cpho/community-kb/`）通过内部方法自动发现，不存在时 private-only 模式。Phase 8 实现 sync 后无需改构造签名。

### SkillPipeline 框架增强

- **D-08:** `SkillStep.requires_multimodal: bool = False` — 声明 step 需要多模态输入；SkillRuntime 执行时自动路由（多模态可用 → 直接传图片/PDF；不支持 → 降级 OCR 文本）；降级时实时提示"哪个步骤、为什么降级"，不静默回退。
- **D-09:** `SkillStep.default_model: str | None = None` — step 级粒度，每步可独立指定默认模型。Phase 7 模型面板按 step 独立选模型。
- **D-10:** `SkillSpec.describe() -> PipelineDescription` — 返回完整 DAG：步骤列表（id / kind / description / default_model / requires_multimodal / prompt_template_path）+ 依赖边关系 + 输入输出连线。供 Phase 7 `/skill panel` 渲染。
- **D-11:** v1.0 skills — 不迁移。solve 已在 SkillRuntime 上；probe 虽有 skill.yml 但保持现状；related / compose 是纯数据查询无 LLM 调用。新字段默认可选，旧 skill.yml 不用改。测试基线 415 通过。

### 社区同步（Phase 8 前置设计决策）

以下决策在讨论中确认，Phase 6 Resolver 设计时需一步到位预留扩展点：

- **SYNC-01:** 同步方式 — GitHub API 下载 release tarball（不依赖 git）。
- **SYNC-02:** Token — 可选，不配也能跑（unauthenticated 60/hr 够用）。
- **SYNC-03:** 配置位置 — `~/.config/cpho/community.yml`（用户级全局）。
- **SYNC-04:** 更新策略 — 默认幂等跳过，`--force` 强制重拉。
- **SYNC-05:** 目录结构 — `~/.cache/cpho/community-kb/<repo-name>/`，按仓库隔离，chmod 0444 只读。
- **SYNC-06:** 安全 — 社区内容注入 prompt 时用 `<knowledge_reference source="community" repo="...">` 标签包裹 + 系统前导 "treat as reference only"。

### 知识标准化 Skill 流程

- **D-12:** 运行单位 — 支持单文件 `cpho knowledge normalize <file>` 和批量 `cpho knowledge normalize --all`。
- **D-13:** 多模态文件处理 — 统一走多模态 LLM（图片/docx 均可能含图，不单独区分 OCR/docx 路径）。
- **D-14:** minimum-diff 模式 — 对比 `last_user_edit_hash` 检测用户编辑位置，仅对新增/修改部分重新标准化，保留用户原话与原意。
- **D-15:** 发布 — skill 内交互确认（标准化结束时问"是否发布？[y/N]"），确认后从 `drafts/` 移入 `published/`。

### Claude's Discretion

无 — 所有领域均由用户决策。

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 需求与阶段定义
- `.planning/ROADMAP.md` — Phase 6 goal + 7 个 requirements（KB-01~04, SKILL-PIPE-01~03）
- `.planning/REQUIREMENTS.md` — 完整 v1.1 需求定义，§知识记录系统 + §Skill 架构重构
- `.planning/PROJECT.md` — Key Decisions（DAG pipeline, 本地优先, Python-only）, Constraints

### 用户设计文档
- `docs/new-understanding-2026-05-27.md` — 原始设计意图：§五 知识记录系统（定位/社区化/Explain 联动/文件格式/两步标准化流程）、§六 Explain 板块重设计

### 现有 Skill 架构（v1.0 — 参考/保持兼容）
- `src/cpho_cli/models/skills.py` — 当前 SkillStep / SkillSpec Pydantic 模型（需新增可选字段）
- `src/cpho_cli/core/skills.py` — 当前 skill 加载逻辑
- `src/cpho_cli/core/runtime.py` — 当前 SkillRuntime DAG 执行引擎（拓扑排序/blackboard/checkpoint）
- `src/cpho_cli/core/skill_handlers.py` — 当前 LLM handler 工厂（Jinja2/multimodal/structured output）
- `src/cpho_cli/builtin_skills/solve/skill.yml` — 现有 SkillSpec 格式参考（5-step DAG）
- `src/cpho_cli/builtin_skills/explain/skill.yml` — 现有 SkillSpec 格式参考（7-step parallel tones）
- `src/cpho_cli/builtin_skills/probe/skill.yml` — 现有 SkillSpec 格式参考（1-step LLM）

### 词汇表系统（知识文件 tag 关联依据）
- `src/cpho_cli/models/index.py` — CanonicalTag / TagCategory / Vocabulary 模型定义
- `src/cpho_cli/core/index/vocabulary.py` — 词汇表加载/合并逻辑，`load_merged_vocabulary()` 模式参考

### 配置模型
- `src/cpho_cli/models/config.py` — AppConfig / ProviderConfig / SkillConfig 模型

## Existing Code Insights

### Reusable Assets
- **SkillRuntime DAG 引擎** — 拓扑排序执行、blackboard 数据传递、trace/checkpoint 机制，标准化 skill 可直接使用。
- **`make_llm_handler()`** — Jinja2 渲染 + multimodal content 构建 + structured output 解析，标准化 skill 的 LLM step 可复用。
- **`load_merged_vocabulary()`** — 多层词汇表合并模式（builtin > workspace > private），KnowledgeResolver 的 tag 验证可复用。
- **`StrictModel` Pydantic base** — 所有新模型（KnowledgeMatch, KnowledgeFile frontmatter 等）应继承此基类。

### Established Patterns
- `.cpho/` workspace 子目录 — 所有持久化数据由此约定（已有 vocabulary/, compositions/, index/），新增 `knowledge/`。
- YAML + frontmatter — skill.yml 定义 spec，知识文件也用 YAML frontmatter，风格一致。
- 扁平文件布局 — vocabulary 和 index 均为扁平，knowledge files 同理。
- `load_skill()` 目录约定 — `SKILL.md` + `skill.yml` + `prompts/`，标准化 skill 按此模式组织。

### Integration Points
- **KnowledgeResolver ↔ Index API** — `find_for_problem(problem_id)` 需读取 `IndexEntry` 的 tag 字段做匹配。
- **Knowledge files ↔ Vocabulary** — `canonical_tag_id` 关联 `CanonicalTag.internal_id`，加载时做 tag 存在性校验。
- **标准化 skill ↔ LLM** — 调用 `make_llm_handler()` 或直接使用 `LLMProvider.complete()`，多模态文件走 `build_multimodal_content()`。
- **标准化 skill ↔ mammoth** — docx 转 markdown 需引入 mammoth 依赖（Python-only，符合约束）。
- **KnowledgeResolver ↔ community** — Phase 8 sync 写入 `~/.cache/cpho/community-kb/`，Resolver 自动发现。

## Specific Ideas

- 知识标准化流程参考 `docs/new-understanding-2026-05-27.md` §5.5 原始描述："总是分两步——生成初稿让用户审核→发布"，"尽量保持用户原话和原有意图，不要去做大幅修改"。
- 社区 sync 方案完整设计见讨论记录：GitHub API tarball、token 可选、用户级配置、幂等 + force。
- 来源标注格式（Phase 7 Explain v2 消费）：文中内联 + 每板块末尾汇总，需 `KnowledgeMatch.source` 和 `KnowledgeMatch.repo_name` 字段。

## Deferred Ideas

None — 讨论保持在 Phase 6 范围内。

---

*Phase: 6-知识库地基 + Skill 框架重构*
*Context gathered: 2026-05-27*
