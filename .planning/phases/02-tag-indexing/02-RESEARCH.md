# Research: Phase 2 — Tag Indexing

**Researched:** 2026-05-23
**Domain:** Local JSONL knowledge index over Phase 1 SolveReports + OCR cache, with LLM tagging refinement, three-tier controlled vocabulary, three-tier incremental hashing, and Python query API
**Confidence:** HIGH for code reuse / data-shape decisions (verified from Phase 1 source); MEDIUM for starter vocabulary content (curatorial choice) and determinism strategy (depends on OpenRouter behavior).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**索引架构**
- **D-01:** 混合架构 — 核心模块 `cpho_cli/core/index.py` 拥有 schema、JSONL 存储、哈希/指纹、stale 检测、词表归一化、查询函数。LLM 打标签步骤复用既有 DAG/skill-runtime 约定（prompt 版本化、结构化输出校验、模型参数、traceability），但 index 不作为普通 built-in skill 注册。
- **D-02:** LLM 打标签必须使用既有 `cpho_cli/core/llm.py` provider 抽象，不走独立 LLM 路径。
- **D-03:** 索引模块必须导出 Python API：`query_index`、`get_problem_entry`、`find_related_problems`。下游 skill 通过这些 API 直接调用，不通过 CLI subprocess。

**标签来源策略**
- **D-04:** 索引定位为学习记忆/错题本层，不是纯自动标注管线。
- **D-05:** 来源优先级：用户笔记/确认难点 → SolveReport → Q&A → OCR fallback。
- **D-06:** 索引器运行专用归一化/精炼 pass — 不盲抄 SolveReport 标签。
- **D-07:** 索引字段：canonical knowledge/model tags、canonical math technique tags、heuristic/insight tags、user-confirmed key points、user-confirmed 卡点、source provenance（user_note / solve_report / qa_history / ocr_fallback）。
- **D-08:** 不使用 easy/medium/hard 难度。改为记录"难在哪里"。

**受控词表体系**
- **D-09:** 三层词表 — built-in / workspace / 用户私有错题本。
- **D-10:** 半开放词表 — LLM 提议新 tag 进入 candidate/pending 状态。
- **D-11:** 每 canonical tag 含中文展示名 + 英文 snake_case 内部 ID + aliases。
- **D-12:** Review skill 可建议 user-note → canonical 映射，但映射必须进入 pending review（Phase 3 工作）。
- **D-13:** Git/export 工作流让用户选择哪些词汇层公开（Phase 4 工作）。

**增量更新与哈希**
- **D-14:** 三层哈希 — 文件层 / 语义层 / 用户学习层。
- **D-15:** 分层存储 — 主索引 / fingerprint 状态 / vocabulary / 用户错题本 / OCR cache 各独立。
- **D-16:** OCR engine name+version+config 进入 fingerprint，变更后让用户选择 (a) 全部重建 / (b) 受影响重建 / (c) 跳过 / (d) 只索引新增。
- **D-17:** `cpho index` 输出分层统计 — 文件 / OCR / 系统标签 / 用户笔记 / refinement / pending review。

### Claude's Discretion

所有关键实现决策均由用户明确指定。具体实现细节（文件格式、API 签名、错误处理）由 planner 和 researcher 根据代码库既有模式决定。

### Deferred Ideas (OUT OF SCOPE)

**Phase 3:**
- 用户错题本编辑交互（CLI/TUI/编辑器）
- Review/refinement skill：user-note → canonical-tag mapping + pending review 完整流程
- Pending review CLI/UI
- 用户笔记变化触发 refinement 的完整链路
- Q&A 历史作为标签来源接入

**Phase 4:**
- commit/export 可见性选择 workflow
- 知识图谱关联（KNOW-01）
- 相关题目上下文自动注入分析管线（KNOW-02）

**后续：** 布尔表达式查询（AND/OR/NOT）、完整物理学 taxonomy。

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| IDX-01 | 用户运行 `cpho index` 对工作空间所有题目自动生成标签（物理模型、启发点、难点、数学技巧），标签存入 JSONL 索引文件 | §1 Data Model, §2 Storage Layout, §4 LLM Tagging Pipeline, §6 Starter Vocabulary, §8 CLI Design |
| IDX-02 | 索引系统使用内容哈希检测题目文件变更（新增/修改），仅对变更文件重新索引 | §3 Three-Tier Hashing, §10 OCR Cache + Engine Fingerprint |
| IDX-03 | 后续 skill 通过标签索引检索题目，而非重复读取原始文件全文；标签使用受控词汇表保证一致性 | §5 Controlled Vocabulary Mechanics, §7 Python API Surface, §11 Determinism Strategy |

</phase_requirements>

## Project Constraints (from CLAUDE.md / AGENTS.md)

- **简单优先：** 用最少代码解决问题。不为单一用途代码做抽象。不做未被要求的"灵活性"。
- **精准修改：** 只动必须动的。不"改进"相邻代码。匹配现有风格。
- **目标驱动：** 每个任务必须有可验证的成功标准。
- **测试同时落地：** 每个实现任务必须创建或更新聚焦测试（来自 Phase 1 PATTERNS.md）。
- **芯-壳分离：** `core/` 纯库不依赖 CLI 框架，不直接 print/input。CLI 是薄适配层。
- **YAML 配置驱动：** 所有可调参数通过 YAML 控制，密钥不入 git。
- **Pydantic 严格模式：** 全部 schema 使用 `StrictModel`（`extra="forbid"`）。
- **JSON mode + schema：** LLM 结构化输出走 `response_format=json_schema`，不走正则兜底。
- **中文 UX：** CLI 文案、错误信息、帮助文本默认中文。
- **不提交私有数据：** `.cpho/` 已在 `.gitignore`。用户笔记和私人词表层默认不污染 git。

---

## Summary

Phase 2 在 Phase 1 已交付的「workspace 发现 → OCR → LLM → SolveReport」管线之上加一层**持久化、可查询的知识索引**。索引核心是 `.cpho/index.jsonl`（每行一个 `IndexEntry`），由 LLM "tag refinement pass" 把 SolveReport 的自由格式标签和 OCR 文本归一化成受控词表（中文显示名 + 英文 snake_case 内部 ID）。Phase 1 已有所有需要的基础设施（`LLMProvider`、`SkillRuntime`、`SolveReport`、`discover_workspace`），Phase 2 只需新增 `core/index.py` 一个芯模块 + `vocabulary/` 资源 + `cli/app.py` 的一个新命令。

关键架构判断 — Phase 2 不是「自动标注管线」而是「学习记忆基础设施」（D-04）。索引必须支持下游 skill 通过 Python API 直接读取（D-03），不通过 CLI subprocess。**三层结构反复出现：** 三层词表（内置/workspace/私有）、三层哈希（文件/语义/用户）、三层 source provenance（user_note → solve_report → qa_history → ocr_fallback）。这是 Phase 2 -> 3 -> 4 演化的脊柱：Phase 2 把数据边界画清楚（包括预留字段），Phase 3 把用户编辑 UX 填进去，Phase 4 把图谱和共享 workflow 接上。

最大的实现挑战是**确定性**（成功标准 4 — 同题重新索引产生相同标签）。LLM 本身随机，所以确定性必须从架构而非模型保证：(1) fingerprint-cached 结果跳过 LLM 重跑，(2) 严格 prompt 限定到现有 canonical tag 列表，(3) 后 LLM 的 deterministic canonical-mapping pass 把自由文本归一到内部 ID。

最大的未知是 **Phase 1 SolveReport 在真实题目上的标签产出质量**。Phase 1 状态是「Needs Review」(V-01)，golden 数据集尚未充实；Phase 2 plan 必须假设 `physics_model_tags / heuristic_insight_tags / math_technique_tags` 可能为空或质量低，所以 OCR fallback 与 tag-from-statement 路径必须可用。

**Primary recommendation:** 建 4-6 个 plan：(P1) data model + JSONL storage + vocabulary loader、(P2) hash/fingerprint 三层 + 增量 detector、(P3) LLM tagging step + canonical-mapping pass、(P4) Python query API + `cpho index` CLI、(P5) starter vocabulary content (30-50 entry) + golden index 测试。Plan 1-3 可大并行，Plan 4 依赖 1+2+3，Plan 5 与 1 并行（纯内容）。

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| JSONL index read/write | `core/index.py` (storage layer) | — | 纯文件 IO + Pydantic 序列化，没有 LLM 决策；芯层独立可单测 |
| Three-tier hashing / fingerprint | `core/index.py` (hash layer) | — | sha256 + 排序拼接，纯 deterministic；不调 LLM |
| Controlled vocabulary loading | `core/index.py` (vocab layer) | `vocabulary/builtin.yml` (packaged data) | YAML 解析 + 别名归一化 + 三层合并，纯库逻辑 |
| LLM tagging refinement | `core/index.py` (tagging step) | `core/llm.py` (provider) + `core/runtime.py` (trace) | 复用 D-02 的 provider 抽象 + D-01 的 trace 约定，但不注册为 SkillSpec |
| OCR cache shared with solve | `core/index.py` (cache layer) | `core/ocr.py` + `core/solve.py` (consumer) | Phase 1 solve 当前没有 cache — 必须在 Phase 2 抽出共享层（见 §10） |
| Python query API | `core/index.py` exports | — | `query_index / get_problem_entry / find_related_problems` 是芯层导出 |
| `cpho index` CLI 命令 | `cli/app.py` (Typer shell) | `core/index.py` (logic) | 薄适配 — 解析参数，render 输出，不放业务逻辑 |
| User-note storage stub | `core/index.py` (notebook layer, stub) | — | Phase 2 只做数据模型 + API stub；编辑 UX → Phase 3 |
| Candidate-tag pending storage | `core/index.py` (vocab pending layer) | — | LLM 提议新 tag 写入 `.cpho/vocabulary/pending.yml`；审批 UI → Phase 3 |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | >=2.7 (already pinned) | Schema 验证、JSON mode 输出 | [VERIFIED: pyproject.toml] Phase 1 全栈使用，D-12 (Phase 1) 已锁 |
| pyyaml | >=6.0 (already pinned) | vocabulary YAML 加载、config 加载 | [VERIFIED: pyproject.toml] Phase 1 config / skill spec 已用 |
| hashlib (stdlib) | — | sha256 fingerprint | [VERIFIED: stdlib] Python 标准库，无依赖 |
| pathlib (stdlib) | — | 文件路径 | [VERIFIED: stdlib] Phase 1 全栈使用 |
| typer | >=0.12 (already pinned) | CLI 命令 | [VERIFIED: pyproject.toml] Phase 1 `cpho solve` / `cpho eval` 已用 |
| httpx | >=0.27 (already pinned) | LLM HTTP（间接，通过 `core/llm.py`） | [VERIFIED: pyproject.toml] 已在 `core/llm.py` 中使用 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `json` (stdlib) | — | JSONL 序列化 + 读取 | 所有 `.jsonl` IO |
| `unicodedata` (stdlib) | — | 别名归一化（NFKC + casefold + 中文标点折叠） | alias matching for canonical tag lookup |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| 自实现 JSONL append | `jsonlines` 第三方库 | 不必要：JSONL 是 `open(path, "a"); f.write(json.dumps(obj) + "\n")` 三行代码，引入额外依赖违反 AGENTS.md §2 "简单优先" |
| sha256 文件哈希 | blake2b | sha256 是项目其它地方（如未来 git-style content addressing）默认；性能差异在 PDF 题目尺寸下不重要 |
| SQLite 索引 | JSONL | 违反 PROJECT.md "数据库存储 — Out of Scope"。JSONL 可 grep、可 append、可版本控制 |
| 向量检索 / embeddings | tag-match 启发式 | 违反 REQUIREMENTS.md Out of Scope ("向量检索 / RAG — v1 使用结构化标签索引，更可控") |

**Installation:** Phase 2 无新依赖。Phase 1 现有依赖（pydantic / pyyaml / typer / httpx / pymupdf / rapidocr）已覆盖。

**Version verification:** `pyproject.toml` 已 pin。Phase 2 不修改 `[project]` / `[dependency-groups]`。

## Package Legitimacy Audit

Phase 2 不引入任何新外部包。复用 Phase 1 已经审计过的依赖集（pydantic / pyyaml / typer / httpx / pymupdf / rapidocr / onnxruntime / jinja2）。

| Package | Registry | Disposition |
|---------|----------|-------------|
| (none new) | — | — |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## 1. Data Model Design

新增文件：`src/cpho_cli/models/index.py`。所有模型继承 `StrictModel`（`ConfigDict(extra="forbid")`）以匹配 Phase 1 风格（见 `models/config.py:6`）。

```python
# src/cpho_cli/models/index.py
from __future__ import annotations
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal
from pydantic import Field
from cpho_cli.models.config import StrictModel  # reuse 现有 StrictModel


# ============ Vocabulary ============

class TagCategory(str, Enum):
    PHYSICS_MODEL = "physics_model"     # 物理模型
    MATH_TECHNIQUE = "math_technique"   # 数学技巧
    HEURISTIC = "heuristic"             # 启发点/推理过程
    SYSTEM_SELECTION = "system_selection"  # 研究对象选择
    APPROXIMATION = "approximation"     # 近似/简化策略


class TagVisibility(str, Enum):  # D-13 预留枚举
    PRIVATE = "private"
    TEAM = "team"
    PUBLIC = "public"


class TagStatus(str, Enum):  # D-10 半开放
    CANONICAL = "canonical"          # 已确认正式 tag
    CANDIDATE = "candidate"          # LLM 提议未审批
    DEPRECATED = "deprecated"        # 历史 tag, 不再使用


class TagLayer(str, Enum):  # D-09 三层词表
    BUILTIN = "builtin"
    WORKSPACE = "workspace"
    USER_PRIVATE = "user_private"


class CanonicalTag(StrictModel):
    """A controlled-vocabulary tag entry."""
    internal_id: str                     # e.g. "newton_second_law"; stable snake_case
    display_zh: str                      # e.g. "牛顿第二定律"
    category: TagCategory
    aliases: list[str] = Field(default_factory=list)  # 中文别名 + 英文同义词
    description: str | None = None       # 一行说明
    status: TagStatus = TagStatus.CANONICAL
    visibility: TagVisibility = TagVisibility.PUBLIC  # 预留, Phase 2 不强制
    layer: TagLayer = TagLayer.BUILTIN   # 来自哪一层


class Vocabulary(StrictModel):
    """Merged vocabulary loaded from three layers."""
    version: str                         # e.g. "v0.1"
    tags: dict[str, CanonicalTag]        # keyed by internal_id
    alias_index: dict[str, str]          # normalized_alias -> internal_id (derived)


class CandidateTag(StrictModel):
    """LLM-proposed tag awaiting human confirmation. D-10."""
    internal_id_suggestion: str          # LLM 提议的 snake_case id
    display_zh_suggestion: str
    category: TagCategory
    proposed_aliases: list[str] = Field(default_factory=list)
    rationale: str                       # LLM 为什么提议这个新 tag
    first_seen_problem_id: str
    first_seen_at: datetime
    occurrences: int = 1                 # 这个候选被几个题目触发


# ============ Hash / Fingerprint ============

class FileFingerprint(StrictModel):
    """Layer 1 (D-14): 文件层指纹."""
    problem_sha256: str                  # sha256 of problem file bytes
    answer_sha256: str | None            # nullable: 题目可能没配答案
    problem_size_bytes: int
    answer_size_bytes: int | None
    problem_mtime_ns: int                # 仅用于诊断, 不参与 hash 决策


class SemanticFingerprint(StrictModel):
    """Layer 2 (D-14): 语义层指纹 — 决定是否重生成 canonical tags."""
    file_fp_hash: str                    # 嵌入 file fingerprint 短哈希做依赖
    ocr_engine: str                      # 'rapidocr'
    ocr_engine_version: str              # 'v3.x'
    ocr_config_hash: str                 # sha256(json.dumps(ocr_config, sort_keys=True))
    tag_prompt_version: str              # 例 'v1' — 跟 prompt 模板 manifest 走
    tag_schema_version: str              # 例 'v1' — 跟 IndexEntry schema 走
    model_name: str                      # 'openai/gpt-4o-mini'
    model_temperature: float             # 0.0
    vocabulary_version: str              # 来自 Vocabulary.version


class UserLearningFingerprint(StrictModel):
    """Layer 3 (D-14): 用户学习层指纹 — Phase 2 预留, 触发 refinement-only pass."""
    notes_sha256: str | None = None      # sha256 of UserNotebookEntry serialized
    user_tags_sha256: str | None = None
    qa_history_sha256: str | None = None  # Phase 3 才会真正填


class IndexFingerprint(StrictModel):
    """Composed fingerprint stored per IndexEntry."""
    file: FileFingerprint
    semantic: SemanticFingerprint
    user_learning: UserLearningFingerprint = Field(default_factory=UserLearningFingerprint)


# ============ Source provenance (D-07) ============

class TagSource(str, Enum):
    USER_NOTE = "user_note"              # priority 1
    SOLVE_REPORT = "solve_report"        # priority 2
    QA_HISTORY = "qa_history"            # priority 3 (Phase 3)
    OCR_FALLBACK = "ocr_fallback"        # priority 4


class TaggedReference(StrictModel):
    """A single tag attached to a problem, with provenance."""
    internal_id: str                     # references CanonicalTag.internal_id
    source: TagSource
    confidence: float | None = None      # LLM 自报置信度, 可空


# ============ User notebook (data model only — Phase 2) ============

class UserNotebookEntry(StrictModel):
    """Per-problem user notes. Phase 2: data model + get/set API stubs only."""
    problem_id: str
    key_points: list[str] = Field(default_factory=list)  # 用户确认的关键步骤
    stuck_points: list[str] = Field(default_factory=list)  # 用户确认的卡点
    free_text_notes: str = ""            # Phase 3 编辑 UX 写入此字段
    user_tags: list[str] = Field(default_factory=list)   # 用户私人 tag 文本
    updated_at: datetime | None = None


# ============ Main index entry ============

class IndexEntry(StrictModel):
    """One problem's full index row in .cpho/index.jsonl."""
    # Identity
    problem_id: str                      # stable id (file path hash or user-named)
    problem_path: Path                   # relative to workspace root
    answer_path: Path | None
    indexed_at: datetime

    # Canonical tags (D-07)
    physics_model_tags: list[TaggedReference] = Field(default_factory=list)
    math_technique_tags: list[TaggedReference] = Field(default_factory=list)
    heuristic_tags: list[TaggedReference] = Field(default_factory=list)

    # Difficulty: 不是 easy/medium/hard, 而是"难在哪里" (D-08)
    difficulty_aspects: list[str] = Field(default_factory=list)
    # 例: ["选系统时容易忽略约束", "近似展开到二阶非显然"]
    # Phase 2 这是自由文本; Phase 3 review skill 可建议映射到 canonical heuristic

    # User layer (Phase 2 reserved — D-07 user_confirmed_*)
    user_confirmed_key_points: list[str] = Field(default_factory=list)  # 从 UserNotebookEntry 投影
    user_confirmed_stuck_points: list[str] = Field(default_factory=list)

    # Fingerprint (D-14) — 用于增量检测
    fingerprint: IndexFingerprint

    # Pointers (不内嵌大对象, 索引保持轻)
    solve_report_path: Path | None       # 指向 output/{problem_id}-report.json
    ocr_cache_path: Path | None          # 指向 .cpho/cache/ocr/{...}.json

    # Statistics
    ocr_text_length: int                 # OCR 字符数, 诊断用
    tag_prompt_version: str              # 与 semantic fingerprint 一致, 冗余存便于查询


# ============ Run statistics (D-17) ============

class IndexRunStats(StrictModel):
    total_problems: int
    file_changed: int                    # 文件 hash 变了
    file_unchanged: int
    ocr_reused: int                      # 命中 OCR cache
    ocr_regenerated: int
    ocr_engine_upgrade_detected: bool
    tags_regenerated: int                # 语义层变了, 重跑 LLM
    tags_skipped: int                    # 跳过, fingerprint 命中
    refinement_only: int                 # 仅用户笔记层变化 (Phase 2 占位, 通常 0)
    candidate_tags_proposed: int
    pending_review_items: int            # 累计待审 (来自 pending.yml)
```

**Phase 2 IN-scope fields:** 全部上述字段。
**Phase 2 reserved-but-empty:** `UserNotebookEntry.free_text_notes / user_tags`、`UserLearningFingerprint.qa_history_sha256`、`IndexEntry.user_confirmed_*` 在 Phase 2 不写入（Phase 3 编辑 UX 才会填）。`IndexRunStats.refinement_only` Phase 2 一般为 0。

## 2. Storage Layout

```
workspace_root/
├── problem.pdf
├── problem-answer.pdf
├── .cpho/                              # gitignored (已在 .gitignore)
│   ├── index.jsonl                     # 主索引: one IndexEntry per line
│   ├── fingerprints.jsonl              # 上次运行的 fingerprint 状态 (用于 diff)
│   │                                   # 实际上 fingerprint 已在 IndexEntry 里, 这个文件
│   │                                   # 仅在 dry-run / 强制重建场景做对比快照
│   ├── cache/
│   │   └── ocr/
│   │       └── {file_sha256[:16]}__{ocr_engine}_{ocr_version}.json
│   │                                   # 例: a3f2b1c8d9e0__rapidocr_3.0.json
│   │                                   # 内容: OCRResult.model_dump_json()
│   ├── vocabulary/
│   │   ├── workspace.yml               # workspace 词表 (D-09 第二层)
│   │   │                               # 可 commit, 项目/团队共享
│   │   ├── private.yml                 # 用户私有词表 (D-09 第三层) — gitignored
│   │   └── pending.yml                 # 候选 tag (D-10)
│   ├── notebook/
│   │   └── {problem_id}.json           # UserNotebookEntry per file
│   │                                   # Phase 2 只有 get/set stub; 实际写由 Phase 3
│   └── run-trace.jsonl                 # TraceRecord 累加 (复用 SkillRuntime 写法)
│
└── (packaged data, 不在 workspace)
src/cpho_cli/vocabulary/
└── builtin.yml                         # 内置基础词表 (D-09 第一层)
                                        # 30-50 starter tags, 随项目发布
```

**JSONL schema (`.cpho/index.jsonl`):**
- 每行：`IndexEntry.model_dump_json()` 单行
- 追加写：增量索引时, 旧条目通过 problem_id 在内存里 dedupe, 整文件重写（题目数量 100-1000 级别, 不需要 streaming append-only）
- 编码：UTF-8, `ensure_ascii=False`（中文展示名直接存中文）

**Vocabulary YAML 格式 (builtin.yml / workspace.yml / private.yml / pending.yml):**

```yaml
version: "v0.1"
tags:
  - internal_id: newton_second_law
    display_zh: 牛顿第二定律
    category: physics_model
    aliases: ["F=ma", "Newton 第二", "动力学基本方程"]
    description: 力等于质量乘加速度
    status: canonical
    visibility: public
    layer: builtin
  - internal_id: ...
```

**pending.yml schema** — `list[CandidateTag]`，结构同上但 `status: candidate` 且含 `rationale / first_seen_problem_id / occurrences`。

**.gitignore 提示** — Phase 2 任务必须更新 `.gitignore` 增加 `.cpho/vocabulary/private.yml` 显式排除（虽然整个 `.cpho/` 已忽略，再加一行保证用户在自己 workspace 下不会误删整个 `.cpho/` 后 private.yml 跑出去）。事实上 `.cpho/` 整体已 gitignored — 只在文档里说明。

**OCR cache key 形式:** `{file_sha256[:16]}__{ocr_engine}_{ocr_version}.json`。短哈希前缀保持文件名可读，后缀 engine+version 让 D-16 OCR 升级时旧 cache 自然失效但不删除（用户选 (a)/(b)/(c)/(d) 决定怎么处理旧 cache）。

## 3. Three-Tier Hashing Strategy

### Layer 1: File Fingerprint
- **Inputs:** 题目文件字节、答案文件字节（若有）
- **Algorithm:** `hashlib.sha256(path.read_bytes()).hexdigest()`
- **Triggers (when changed):**
  - 重新 OCR（除非 OCR cache 已经针对新 hash 存在 — 一般不会, 因为 hash 是 cache key）
  - 重新跑 LLM tagging
  - 全部下游层都失效

### Layer 2: Semantic Fingerprint
- **Inputs (concatenated sorted JSON):**
  - `file_fp_hash` (short prefix of layer-1, 让 layer-2 隐式依赖 layer-1)
  - `ocr_engine + ocr_engine_version + ocr_config_hash`
  - `tag_prompt_version` (例 "v1" — 来自 `cpho_cli/index/prompts/MANIFEST.yml` 里的版本号)
  - `tag_schema_version` (例 "v1" — 来自 `IndexEntry` 类常量)
  - `model_name + model_temperature` (来自 resolved ModelParams)
  - `vocabulary_version` (来自合并后的 Vocabulary.version)
- **Algorithm:** `sha256(json.dumps({...}, sort_keys=True, ensure_ascii=False))`
- **Triggers:**
  - OCR 不变 (layer-1 不变) 时, layer-2 变化 → 仅重新跑 LLM tagging, 复用 OCR cache
  - 若 OCR 引擎升级 → layer-2 变, layer-1 也"看起来变"（cache key 含 ocr 版本）→ 进入 D-16 用户确认流程

### Layer 3: User Learning Fingerprint
- **Inputs:**
  - `sha256(UserNotebookEntry.model_dump_json(sort_keys=True))` — 即 key_points / stuck_points / free_text / user_tags 任何变化都会触发
  - `qa_history_sha256` — Phase 2 始终为 None (Phase 3 接入)
- **Triggers (D-14 第三层):**
  - 仅触发 refinement pass（非 OCR、非完整 LLM tagging）
  - Phase 2 的 refinement pass = "把 UserNotebookEntry 的 key_points/stuck_points 投影到 IndexEntry.user_confirmed_* 字段", 无 LLM
  - 真正的 user-note → canonical-tag 建议是 Phase 3 review skill 的工作

### Composition decision algorithm

```python
def decide_action(old: IndexEntry | None, new_fp: IndexFingerprint) -> str:
    if old is None:
        return "full_index"  # 新题
    if old.fingerprint.file != new_fp.file:
        return "re_ocr_and_re_tag"  # 文件变, 完整重跑
    if old.fingerprint.semantic != new_fp.semantic:
        return "re_tag_only"  # 复用 OCR, 重跑 LLM
    if old.fingerprint.user_learning != new_fp.user_learning:
        return "refinement_only"  # 仅投影用户笔记
    return "skip"  # 三层都不变
```

四种 action 对应 §1 `IndexRunStats` 的统计字段。`--force` flag 强制走 `re_ocr_and_re_tag`，`--only-new` 跳过任何 `old is not None` 的题。

## 4. LLM Tagging Pipeline

按 D-01：tagging step **复用 DAG/skill-runtime 约定**（prompt 版本化、trace 写入、JSON schema 校验），但**不**作为 built-in skill 注册（不进 `cpho_cli/builtin_skills/`，也不通过 `cpho_cli/core/skills.py:load_skill` 加载）。原因：索引器是芯模块独立编排，不是用户可发现/调用的 skill。

### Pipeline (per problem with action ∈ {full_index, re_tag_only})

```
[1] Gather inputs
    ├── OCR text (cached or fresh from RapidOCR via core/ocr.py)
    ├── SolveReport (if output/{problem_id}-report.json exists from `cpho solve`)
    │   - 读 physics_model_tags / heuristic_insight_tags / math_technique_tags
    │   - 注意: 这些是自由文本, Phase 2 必须归一化 (D-06 — 不盲抄)
    └── Current Vocabulary (merged builtin + workspace + private)

[2] LLM tagging call (走 core/llm.py:LLMProvider.complete)
    System prompt:
      "你是物理竞赛题目标签归一化助手。给定题目 OCR 文本和 SolveReport 的
       自由格式标签, 从受控词表中选出最匹配的 canonical tags。
       严格仅从提供的 canonical_tags 列表中选择。
       如果发现需要的概念不在列表里, 仅在 candidates 数组里提议新 tag。"
    User prompt (Jinja2 template):
      problem_text (truncated, first ~3000 chars)
      solve_report_tags (raw lists from SolveReport)
      controlled_vocabulary (list of {internal_id, display_zh, category, aliases})
    response_format: json_schema strict (TagRefinementOutput Pydantic model)

[3] Validate output (Pydantic strict)
    class TagRefinementOutput(StrictModel):
        selected_physics_models: list[str]    # list of internal_id
        selected_math_techniques: list[str]
        selected_heuristics: list[str]
        difficulty_aspects: list[str]         # 自由文本 — D-08 "难在哪里"
        candidates: list[CandidateTag]        # 提议的新 tag

[4] Canonical-mapping pass (deterministic, no LLM)
    - 把 LLM 输出的 internal_id 列表对照 Vocabulary 验证
    - 若 LLM 返回了不在 vocab 的 id, 移到 candidates
    - 别名归一化: 调用 vocab.alias_index 把可能的别名映射到 canonical id

[5] Write trace
    - TraceRecord (复用 models/runtime.py:TraceRecord)
      step_id = f"tag_{problem_id}"
      input_keys = ["ocr_text", "solve_report", "vocabulary_v{X}"]
      output_keys = ["tag_refinement"]
    - 追加到 .cpho/run-trace.jsonl
    - 调用 redact_secrets (core/runtime.py:20) 不必要 — 这一步没碰 API key, key 已在 provider 内层处理

[6] Update IndexEntry + pending.yml
    - 已确认 internal_ids → IndexEntry.{physics_model,math_technique,heuristic}_tags
    - candidates → 合并进 .cpho/vocabulary/pending.yml (occurrences ++ if 已存在)
```

### Where the prompt lives

不放 `cpho_cli/builtin_skills/`（不是注册 skill）。建议放：

```
src/cpho_cli/core/index/
├── __init__.py            # re-exports
├── prompts/
│   ├── MANIFEST.yml       # 版本号 — 进入 SemanticFingerprint.tag_prompt_version
│   └── tag_refinement.md.j2
```

可选简化：如果 prompt 只有一个模板，可以直接 inline 在 `core/index.py` 里的多行字符串（AGENTS.md §2 简单优先）。但版本控制需求（D-14 把 tag_prompt_version 纳入 fingerprint）天然倾向独立文件 + MANIFEST。

### Concrete trace record example

```json
{
  "step_id": "tag_p001",
  "status": "passed",
  "input_keys": ["ocr_text", "solve_report", "vocabulary_v0.1"],
  "output_keys": ["tag_refinement"],
  "retry_count": 0,
  "started_at": "2026-05-23T10:00:00Z",
  "finished_at": "2026-05-23T10:00:08Z",
  "error": null
}
```

## 5. Controlled Vocabulary Mechanics

### Three-layer merge (D-09)

```python
def load_merged_vocabulary(workspace_root: Path) -> Vocabulary:
    builtin = load_yaml_vocab(_builtin_vocab_path())                   # packaged
    workspace = load_yaml_vocab(workspace_root / ".cpho/vocabulary/workspace.yml", optional=True)
    private = load_yaml_vocab(workspace_root / ".cpho/vocabulary/private.yml", optional=True)

    merged: dict[str, CanonicalTag] = {}
    for layer in [builtin, workspace, private]:  # 后者覆盖前者
        for tag in layer.tags.values():
            merged[tag.internal_id] = tag
    return Vocabulary(
        version=_compose_version(builtin, workspace, private),
        tags=merged,
        alias_index=_build_alias_index(merged),
    )
```

**Conflict resolution:** 同 `internal_id` 时后层（private > workspace > builtin）胜出。这允许用户在私有词表里改 builtin tag 的 display_zh 但不能改 internal_id（id 是身份）。

### Alias matching normalization

```python
def normalize_alias(text: str) -> str:
    # 1. NFKC 统一全角半角
    text = unicodedata.normalize("NFKC", text)
    # 2. casefold 大小写折叠（英文）
    text = text.casefold()
    # 3. 移除空白和常见标点
    text = re.sub(r"[\s\-_.,;:'\"()（）「」]+", "", text)
    return text


def _build_alias_index(tags: dict[str, CanonicalTag]) -> dict[str, str]:
    index: dict[str, str] = {}
    for tag in tags.values():
        for label in [tag.internal_id, tag.display_zh, *tag.aliases]:
            index[normalize_alias(label)] = tag.internal_id
    return index
```

### Candidate-tag lifecycle (D-10 half-open)

- LLM 提议新 tag → 写入 `.cpho/vocabulary/pending.yml`，`status=candidate`
- 同一 candidate 多次出现 → `occurrences` 累加（去重 key = `normalize_alias(display_zh_suggestion)`）
- Phase 2 只暴露**只读列表**：CLI `cpho index --list-candidates` 打印待审 candidates；无确认/拒绝交互
- Phase 3 review skill 才负责 candidate → canonical 升级流程（D-12）

### Visibility (D-11/D-13) Phase 2 处理

- `TagVisibility.PRIVATE / TEAM / PUBLIC` 三值枚举存进 CanonicalTag
- builtin.yml 默认 `public`，workspace.yml 默认 `team`，private.yml 默认 `private`
- Phase 2 **不做** 任何基于 visibility 的过滤、export、git workflow — 只是记录
- Phase 4 commit/export 功能读这个字段决定哪些层公开

## 6. Starter Vocabulary (30-50 entries)

下表是 builtin.yml 起步内容。物理竞赛常见主题覆盖力学/电磁/热力/光学/数学/启发。**这些是 [ASSUMED] —— 基于通用物理竞赛知识，需要用户在实际题目上跑过 Phase 2 后调整。**

### Physics models (15) — `category: physics_model`

| internal_id | display_zh | aliases (sample) |
|-------------|-----------|------------------|
| newton_second_law | 牛顿第二定律 | F=ma, 动力学基本方程 |
| momentum_conservation | 动量守恒 | conservation of momentum, p 守恒 |
| energy_conservation | 能量守恒 | 机械能守恒, conservation of energy |
| angular_momentum_conservation | 角动量守恒 | L 守恒 |
| circular_motion | 圆周运动 | uniform circular motion, 向心力 |
| simple_harmonic_motion | 简谐振动 | SHM, 谐振子 |
| rigid_body_rotation | 刚体定轴转动 | rotational dynamics |
| ideal_gas_law | 理想气体状态方程 | PV=nRT |
| first_law_thermo | 热力学第一定律 | Q=ΔU+W |
| second_law_thermo | 热力学第二定律 | 熵增, entropy |
| electrostatics_gauss | 高斯定律 | Gauss's law, 通量定理 |
| circuit_kirchhoff | 基尔霍夫定律 | KVL, KCL, 节点电压 |
| electromagnetic_induction | 电磁感应 | 法拉第定律, EMF |
| geometric_optics | 几何光学 | 折射, 反射, 透镜公式 |
| wave_interference | 波动干涉 | 相位差, 路径差 |

### Math techniques (12) — `category: math_technique`

| internal_id | display_zh | aliases (sample) |
|-------------|-----------|------------------|
| dimensional_analysis | 量纲分析 | 量纲法 |
| small_angle_approximation | 小角近似 | sinθ≈θ, 一阶展开 |
| taylor_expansion | 泰勒展开 | 级数展开 |
| separation_of_variables | 分离变量 | ODE 分离变量法 |
| ode_first_order | 一阶常微分方程 | first-order ODE |
| ode_second_order | 二阶常微分方程 | second-order ODE |
| vector_decomposition | 矢量分解 | 正交分解 |
| coordinate_transform | 坐标变换 | polar/cartesian 切换 |
| calculus_integral | 积分计算 | 定积分, 不定积分 |
| binomial_approximation | 二项式近似 | (1+x)^n≈1+nx |
| symmetry_argument | 对称性论证 | symmetry analysis |
| limit_analysis | 极限分析 | 取极限验证, 极限情况 |

### Heuristics / insights (15) — `category: heuristic` and `system_selection` / `approximation`

| internal_id | display_zh | category | aliases (sample) |
|-------------|-----------|----------|------------------|
| system_selection | 研究对象选择 | system_selection | "选什么系统", 整体法/隔离法 |
| reference_frame_choice | 参考系选择 | heuristic | 惯性系/非惯性系切换 |
| conservation_law_selection | 守恒律选择 | heuristic | 选用能量/动量/角动量 |
| coordinate_system_choice | 坐标系选择 | heuristic | 极坐标/直角坐标 |
| free_body_diagram | 受力分析 | heuristic | FBD, 力图 |
| approximation_to_first_order | 一阶近似 | approximation | 线性近似 |
| approximation_to_second_order | 二阶近似 | approximation | 保留二阶项 |
| identify_constraint | 识别约束 | heuristic | 约束方程 |
| symmetry_recognition | 对称性识别 | heuristic | 利用对称简化 |
| limiting_case_check | 极限情形校验 | heuristic | sanity check, 极限验证 |
| boundary_condition_setup | 边界条件设置 | heuristic | BC, 初始条件 |
| variable_substitution | 变量替换 | heuristic | u 代换 |
| equivalent_circuit | 等效电路 | heuristic | 戴维南/诺顿 |
| superposition_principle | 叠加原理 | heuristic | superposition |
| analogy_mapping | 类比映射 | heuristic | 力学-电学类比 |

**总计：42 starter tags**（落在 30-50 区间内）。每个 entry 在 YAML 里需补 `description` 一行简介（可由 plan 5 任务负责生成）。

## 7. Python API Surface

```python
# src/cpho_cli/core/index/__init__.py — exported surface

from pathlib import Path
from cpho_cli.models.index import IndexEntry, Vocabulary, IndexRunStats, CandidateTag


def build_index(
    workspace_root: Path,
    config_path: Path | None = None,
    provider_name: str | None = None,
    *,
    force: bool = False,
    only_new: bool = False,
    dry_run: bool = False,
    ocr_strategy: str = "prompt",  # one of: prompt | reuse | rebuild | new-only
) -> IndexRunStats:
    """主入口: 扫 workspace, 计算 fingerprint, 增量决定 action, 调 LLM, 写 jsonl.
    Errors: IndexError (custom) on missing files, ConfigError on bad config."""


def query_index(
    workspace_root: Path,
    *,
    physics_model_ids: list[str] | None = None,
    math_technique_ids: list[str] | None = None,
    heuristic_ids: list[str] | None = None,
    match_mode: str = "any",  # "any" or "all"
) -> list[IndexEntry]:
    """按标签匹配返回索引条目. Phase 2: 简单匹配, 无布尔表达式.
    Errors: IndexNotFoundError if .cpho/index.jsonl missing.
    """


def get_problem_entry(
    workspace_root: Path,
    problem_id: str,
) -> IndexEntry | None:
    """精确 ID 查询. 返回 None 表示未索引."""


def find_related_problems(
    workspace_root: Path,
    problem_id: str,
    *,
    min_shared_tags: int = 1,
    max_results: int = 10,
    same_category_weight: bool = True,  # Phase 2 实现: 相同 category 内重叠 +1, 跨 category +0.5
) -> list[tuple[IndexEntry, float]]:
    """基于标签重叠的相关题目搜索. Phase 2 实现 = 共享 canonical tag 计数 + 简单加权.
    无 embedding, 无图谱算法 (Phase 4 KNOW-01 才上).
    Errors: IndexNotFoundError, ProblemNotIndexedError."""


# User notebook stubs (Phase 2: data model only, no editor UX)

def get_problem_notes(
    workspace_root: Path,
    problem_id: str,
) -> UserNotebookEntry | None:
    """读取 .cpho/notebook/{problem_id}.json. 返回 None 表示无笔记."""


def set_problem_notes(
    workspace_root: Path,
    notes: UserNotebookEntry,
) -> None:
    """写入笔记文件. Phase 2 没有 UI 调用, 但 API 必须存在以满足 contract."""


# Vocabulary read

def load_vocabulary(workspace_root: Path) -> Vocabulary:
    """合并加载三层词表."""


def list_pending_candidates(workspace_root: Path) -> list[CandidateTag]:
    """读取 .cpho/vocabulary/pending.yml. Phase 2 只读."""
```

**Error hierarchy:**

```python
class IndexError(RuntimeError): pass
class IndexNotFoundError(IndexError): pass   # .cpho/index.jsonl 不存在
class ProblemNotIndexedError(IndexError): pass  # problem_id 不在索引里
class VocabularyError(IndexError): pass      # 词表 YAML 损坏
```

匹配 Phase 1 风格 (`SolveError`, `ConfigError`, `EvalConfigError` 都是 `RuntimeError` / `ValueError` 子类)。

## 8. CLI Design (`cpho index`)

```python
@app.command(name="index")
def index_command(
    workspace: Path = typer.Argument(Path.cwd(), help="Workspace directory to index."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Local YAML config path."),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Provider profile."),
    force: bool = typer.Option(False, "--force", help="重建全部索引, 忽略 fingerprint."),
    only_new: bool = typer.Option(False, "--only-new", help="仅索引新增题目, 跳过已存在条目."),
    dry_run: bool = typer.Option(False, "--dry-run", help="仅验证, 不调 LLM 不写文件."),
    ocr_strategy: str = typer.Option(
        "prompt", "--ocr-strategy",
        help="OCR 升级处理: prompt|reuse|rebuild|new-only (D-16)",
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="只输出错误."),
    list_candidates: bool = typer.Option(
        False, "--list-candidates", help="只列出 pending candidates 不重建索引."
    ),
) -> None:
    """对工作空间题目生成结构化索引."""
    ...
```

**Output format (D-17 分层统计, 中文 UX):**

```
索引统计 (workspace: ./problems/)
─────────────────────────
扫描题目数:        45
  新增:            3
  文件变化:        2
  无变化:          40

OCR 复用:          42 / 45
OCR 重生成:        3
OCR 引擎升级:      未检测到

标签层:
  重新生成:        5
  跳过 (fingerprint 命中): 40
  精炼层 (用户笔记):  0  (Phase 2 预留)

候选词表:
  本次新提议:      2
  累计待审:        7  (运行 `cpho index --list-candidates` 查看)

完成. 索引: .cpho/index.jsonl
```

**OCR 升级交互（仅 `--ocr-strategy prompt` 时）:**

```
检测到 OCR 引擎升级: rapidocr 3.0 → rapidocr 4.1
受影响条目: 42

请选择:
  [a] 重建全部 42 条
  [b] 仅重建受影响条目 (同上, 但跳过手动 force 的)
  [c] 暂时跳过, 保持现有 OCR
  [d] 仅索引新增题目, 不动旧条目

选择 [a/b/c/d]: _
```

CLI 层是薄壳，所有决策由 `core/index.py:build_index` 通过参数对象传回。芯-壳分离禁止 core 直接 `input()` — 解决方法：core 返回 `OcrUpgradeDecisionRequired` 异常，CLI 捕获后 prompt 用户，重新调用 core 时传 `ocr_strategy="rebuild"|"new-only"|...`。

## 9. Reuse Map (Phase 1 → Phase 2)

| Phase 2 需要 | Phase 1 已有 | 怎么用 |
|--------------|--------------|--------|
| 发现 workspace 中的题目 | `core/workspace.py:discover_workspace` | 直接调用，得到 `pairs / unmatched / ambiguous`。Phase 2 索引仅处理 `pairs`（带配对答案）+ `unmatched`（只有题目，无答案）。`ambiguous` 警告但跳过 |
| LLM 调用 + JSON schema | `core/llm.py:LLMProvider.complete` + `OpenRouterProvider` | 完全复用。Tagging 调用走 `provider.complete(messages, params, response_model=TagRefinementOutput)` |
| Model params resolution | `core/config.py:resolve_model_params(config, "index")` | 直接调用，传 skill_name="index"。允许 config.local.yml 的 `skills.index.model` 覆盖（如指定低 temperature） |
| Provider config resolution | `core/config.py:resolve_provider_config` | 同 solve 流程 |
| Trace 写入 | `core/runtime.py:SkillRuntime._write_trace` 的模式 | **不实例化** SkillRuntime（D-01 不注册 skill）。Phase 2 抽出小函数 `_append_trace(trace_path, record)` 或直接复制 9 行（AGENTS.md §2 简单优先）。`TraceRecord` 模型直接复用 (`models/runtime.py:TraceRecord`) |
| OCR | `core/ocr.py:RapidOCRProvider.extract` + `OCRProvider` Protocol | 复用 Protocol；index 层在 OCRProvider 外加一层 cache wrapper（见 §10） |
| Document 加载 | `core/documents.py:load_document` | 直接调用，得到 `DocumentInput` 喂给 OCR |
| SolveReport 读取 | `models/solve.py:SolveReport` + `output/{problem_id}-report.json` | Pydantic 反序列化 `SolveReport.model_validate_json(path.read_text())`。注意：Phase 1 report 文件命名是 `{problem_id}-report.json`（见 `solve.py:_write_report`） |
| CLI 注册 | `cli/app.py:app` | 直接加 `@app.command(name="index")` 装饰器 |
| Secrets redaction | `core/runtime.py:redact_secrets` | trace 写入前过滤 API key |
| StrictModel 基类 | `models/config.py:StrictModel` | 全部新模型继承 |

**复用边界澄清：** Phase 2 **不**注册新 `SkillSpec` / **不**调用 `load_skill` / **不**走 `SkillRuntime.run`。索引器是自己写的小编排循环，但**约定**对齐（trace schema、prompt 版本化、JSON schema 严格）。

## 10. OCR Cache + Engine Fingerprint

### 现状（重要 — Phase 1 没有 cache）

`core/solve.py:71-78` 每次都 `ocr.extract(problem_doc)` 跑全量 OCR。没有任何缓存。Phase 1 SUMMARY 也没记录 OCR cache 工作。

**Implication:** Phase 2 是**第一个**引入 OCR cache 的 phase。这意味着：
1. Phase 2 必须新建 `.cpho/cache/ocr/` 目录约定
2. solve.py 当前不会因为 Phase 2 而自动复用 cache — 如果未来希望 solve 也复用，是后续 phase 工作（可记入 STATE.md 的 deferred）
3. Phase 2 给 index 使用的 OCR cache 抽象建议放 `core/index.py`，不污染 `core/ocr.py`

### Cache layout

```
.cpho/cache/ocr/{file_sha256[:16]}__{ocr_engine}_{ocr_version}.json
```

文件内容: `OCRResult.model_dump_json(indent=2)`。

### Cache wrapper

```python
# src/cpho_cli/core/index/ocr_cache.py
class CachedOCRProvider:
    """Wraps an OCRProvider with file-content-addressed disk cache."""

    def __init__(self, inner: OCRProvider, cache_dir: Path, engine_name: str, engine_version: str):
        self.inner = inner
        self.cache_dir = cache_dir
        self.engine_name = engine_name
        self.engine_version = engine_version

    def extract(self, document: DocumentInput) -> tuple[OCRResult, bool]:
        # 返回 (result, was_cached) — bool 用于统计
        file_hash = sha256_file(document.path)
        key = f"{file_hash[:16]}__{self.engine_name}_{self.engine_version}.json"
        path = self.cache_dir / key
        if path.exists():
            return OCRResult.model_validate_json(path.read_text(encoding="utf-8")), True
        result = self.inner.extract(document)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        return result, False
```

### Engine fingerprint detection (D-16)

```python
def detect_ocr_engine_upgrade(workspace_root: Path) -> OcrEngineDelta | None:
    """检查 .cpho/index.jsonl 中现有条目 fingerprint 与当前 OCR 引擎是否一致."""
    if not (workspace_root / ".cpho/index.jsonl").exists():
        return None
    entries = load_index(workspace_root)
    current = (RAPIDOCR_NAME, RAPIDOCR_VERSION, ocr_config_hash())  # config_hash 涵盖 low_confidence_threshold 等
    affected = [
        e.problem_id for e in entries
        if (e.fingerprint.semantic.ocr_engine,
            e.fingerprint.semantic.ocr_engine_version,
            e.fingerprint.semantic.ocr_config_hash) != current
    ]
    if not affected:
        return None
    return OcrEngineDelta(old_engine=..., new_engine=..., affected_count=len(affected))
```

### Resolving `rapidocr` version

```python
def _rapidocr_version() -> str:
    try:
        import rapidocr  # type: ignore
        return getattr(rapidocr, "__version__", "unknown")
    except ImportError:
        return "unknown"
```

### User-confirmation strategies

`--ocr-strategy` flag 四值（对应 D-16 a/b/c/d）：

| Flag | 含义 |
|------|------|
| `prompt` (default) | 检测到升级时交互询问 |
| `rebuild` | 直接重建受影响条目（= D-16 选项 b）|
| `reuse` | 跳过升级检测，保留现有 cache（= D-16 选项 c）|
| `new-only` | 仅新增题目走新 OCR（= D-16 选项 d）|

无 `force-rebuild-all` 子值，因为整体重建已由顶层 `--force` 覆盖（= D-16 选项 a）。

## 11. Determinism Strategy

成功标准 4：同题重新索引 → 相同 canonical tags。LLM 本质随机，所以**确定性必须来自架构层**。

### 四个机制叠加

| 机制 | 强度 | 实现 |
|------|------|------|
| **(M1) Fingerprint-cached skip** | 决定性 | 三层 fingerprint 全部命中 → 完全跳过 LLM。**这是首要确定性来源** — 同一文件 + 同一 vocab + 同一 prompt 版本 → action=skip → 上次的 tag 原封返回 |
| **(M2) Strict prompt vocabulary** | 强 | Prompt 把整个 Vocabulary 列表作为 enum 注入：「仅从以下 internal_id 中选择」。配合 JSON schema strict mode 减少漂移 |
| **(M3) Deterministic canonical-mapping pass** | 决定性 | LLM 输出后跑纯函数 alias 归一化 + vocab 过滤。即使 LLM 输出 "Newton 第二" 也会被归一到 `newton_second_law`。不在 vocab 的 → candidates 桶（不进 IndexEntry） |
| **(M4) Low temperature + fixed model params** | 弱 | config 默认 `model.temperature=0.0` for skill `index`。OpenRouter 不一定支持 seed — 不依赖 seed |

### Plan 必须实现的检查

- **Unit test:** 用 fake LLMProvider 返回相同 content 两次 → 两次索引产出**bytewise** 相同 JSONL（除了 `indexed_at`）。
- **Integration test:** 真 provider（如果 CI 有 OPENROUTER_API_KEY）跑两次，断言 canonical tag 列表完全相同（M1 命中 fingerprint）。

### 已知风险

- **M1 弱点：** 如果用户改 `config.local.yml` 中 `model.temperature` 从 0.0 → 0.1，semantic fingerprint 会变 → 重新跑 LLM → 可能拿到不同 canonical tag。**这是设计意图**（用户改了模型行为，应当重跑）。
- **M3 边界：** 如果 LLM 同时给同一个概念输出两个 vocab id（如 "newton_second_law" 和 "momentum_conservation" 都被选了），dedupe 后保留两个。Phase 2 不试图判断哪个更对。

## 12. Validation Architecture

> Phase 1 PATTERNS.md 要求："Every implementation task must create or update focused tests alongside production changes."

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >=8.2 [VERIFIED: pyproject.toml] |
| Config file | `pyproject.toml` `[tool.pytest.ini_options] testpaths = ["tests"]` |
| Quick run command | `uv run pytest tests/test_index*.py -x` |
| Full suite command | `uv run pytest -q && uv run ruff check . && uv run mypy .` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| IDX-01 | `cpho index` 产出 JSONL with canonical tags | integration (fake LLM) | `pytest tests/test_index_cli.py::test_index_produces_canonical_jsonl -x` | ❌ Wave 0 |
| IDX-01 | LLM tagging 用 `core/llm.py` provider | unit | `pytest tests/test_index_tagging.py::test_tagging_uses_llm_provider -x` | ❌ Wave 0 |
| IDX-01 | 内置词表 30-50 条加载 | unit | `pytest tests/test_index_vocabulary.py::test_builtin_vocabulary_loads -x` | ❌ Wave 0 |
| IDX-02 | 文件未变 → skip | unit | `pytest tests/test_index_hashing.py::test_unchanged_file_skipped -x` | ❌ Wave 0 |
| IDX-02 | 文件变 → re-OCR + re-tag | integration (fake) | `pytest tests/test_index_hashing.py::test_changed_file_rebuilds -x` | ❌ Wave 0 |
| IDX-02 | OCR 引擎升级触发提示 | unit | `pytest tests/test_index_ocr_upgrade.py::test_engine_change_detected -x` | ❌ Wave 0 |
| IDX-02 | 分层统计正确 | unit | `pytest tests/test_index_stats.py::test_layered_stats -x` | ❌ Wave 0 |
| IDX-03 | `query_index` 按标签返回 | unit | `pytest tests/test_index_api.py::test_query_by_tag -x` | ❌ Wave 0 |
| IDX-03 | `get_problem_entry` 精确查询 | unit | `pytest tests/test_index_api.py::test_get_problem_entry -x` | ❌ Wave 0 |
| IDX-03 | `find_related_problems` 标签重叠 | unit | `pytest tests/test_index_api.py::test_find_related_by_overlap -x` | ❌ Wave 0 |
| IDX-03 | 受控词表一致性 — 同输入两次 → 同 internal_id | integration | `pytest tests/test_index_determinism.py::test_same_input_same_tags -x` | ❌ Wave 0 |
| Success criterion 4 | Determinism end-to-end | integration | `pytest tests/test_index_determinism.py::test_reindex_identical_output -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_index_<focus>.py -x`
- **Per wave merge:** `uv run pytest -q && uv run ruff check . && uv run mypy .`
- **Phase gate:** Full suite green + `uv run cpho index --dry-run` 在 starter workspace 上跑通 + `cpho index` 真跑（如果有 API key）确认 JSONL 产出。

### Wave 0 Gaps

- [ ] `tests/test_index_vocabulary.py` — 三层词表加载、别名归一化、冲突解决
- [ ] `tests/test_index_hashing.py` — file/semantic/user 三层 fingerprint 计算与差分
- [ ] `tests/test_index_tagging.py` — LLM tagging step with fake provider, 验证 prompt 包含 vocabulary
- [ ] `tests/test_index_api.py` — `query_index / get_problem_entry / find_related_problems`
- [ ] `tests/test_index_determinism.py` — 同输入两次产出对比
- [ ] `tests/test_index_ocr_upgrade.py` — engine version 变化检测
- [ ] `tests/test_index_cli.py` — `cpho index` 命令端到端（fake LLM + tmp workspace）
- [ ] `tests/test_index_stats.py` — 分层统计计数正确
- [ ] `tests/fixtures/builtin_vocab_test.yml` — 小型测试词表
- [ ] `tests/fixtures/sample_solve_report.json` — 模拟 Phase 1 输出

### Golden index fixture（额外）

- 一个 tiny workspace（1-2 个 fake PDF + 配对 answer）+ 期望 IndexEntry JSON 快照
- 通过 fake LLMProvider 返回预设 TagRefinementOutput 来稳定测试
- 路径：`tests/fixtures/golden_index_workspace/`

## 13. Risks and Unknowns

### R1 — Phase 1 SolveReport 标签质量未知 (HIGH)

Phase 1 状态是 "Needs Review" (V-01)。`tests/test_solve.py::test_solve_non_dry_run_uses_llm_provider` 只用 fake LLM 跑，没有真实 LLM + 真题验证。`SolveReport.physics_model_tags / heuristic_insight_tags / math_technique_tags` 在生产中可能：

- 完全为空（LLM 没填）
- 自由文本与受控词表完全不对齐
- 不同 prompt 版本下质量飘忽

**Mitigation in Phase 2:** Tagging pipeline 必须能在 SolveReport 缺失或标签为空时**只**从 OCR text 走（D-05 的 priority 4 OCR_FALLBACK）。Plan 必须包含 test: `test_tagging_works_without_solve_report`。

### R2 — Cold-start vocabulary (MEDIUM)

42 starter tags 不可能覆盖物理竞赛全部场景。真实题目跑下来，candidates 数量可能爆炸。

**Mitigation:** Phase 2 接受 candidates 累积 — 不阻塞索引产出。`--list-candidates` 让用户看到累积情况。Phase 3 的 review skill 是消化点。**Plan 必须设 `IndexRunStats.candidate_tags_proposed` 字段**，让用户在每次跑完知道有多少待审。

### R3 — LLM 输出 internal_id 不在 vocabulary (HIGH-likelihood)

即使 prompt strict，LLM 可能编出新的 snake_case id。

**Mitigation:** §11 (M3) canonical-mapping pass — 任何不在 vocab 的 id 一律降级到 candidates，不进 IndexEntry 主标签。这是 deterministic post-processing，必须测试覆盖。

### R4 — OCR cache + Phase 1 solve 共享 (LOW, deferred)

Phase 2 引入 cache 路径，但 solve.py 不知道。如果用户先跑 `cpho solve`，再跑 `cpho index`，OCR 会跑两次。这违反 D-15 "OCR cache 共享" 的精神但 Phase 2 不在 scope 改 solve。

**Recommendation:** 记入 STATE.md "Phase 3 deferred" — "把 solve.py 接入 OCR cache"。Phase 2 不做（精准修改原则）。

### R5 — JSONL 文件锁定/并发 (LOW)

如果用户在 `cpho index` 运行中查询 `query_index`，可能读到半写状态。

**Mitigation:** 写入采用 `tmp + atomic rename` 模式（`pathlib.Path.replace`）。Plan 任务必须用这个模式。

### R6 — Phase 1 V-01 未关闭（real golden problems 缺失）

如果 Phase 1 始终没有真实物理题目可测，Phase 2 也无法在真实场景验证。

**Mitigation:** Phase 2 测试用 fake LLM + fake OCR + minimal fake PDF 完成所有 contract 验证。真实物理题目验证是 Phase 2 完成后的 manual review 环节（与 Phase 1 V-01 共用 problem set）。

### R7 — UserNotebookEntry 数据模型预留但完整链路不通 (KNOWN)

D-07 要求 IndexEntry 含 `user_confirmed_key_points / user_confirmed_stuck_points`。Phase 2 实现这些字段，但 Phase 2 没有写入路径（编辑 UX 是 Phase 3）。

**Mitigation:** `get_problem_notes / set_problem_notes` API 在 Phase 2 实现并测试。`build_index` 在每次跑时读取 `.cpho/notebook/{problem_id}.json` 投影到 IndexEntry。如果用户手动写 JSON 文件，Phase 2 已经能消费。Phase 3 加 CLI 编辑器。

### R8 — 未验证的 [ASSUMED] starter vocabulary 内容

§6 列出的 42 个 tag 是基于通用物理竞赛知识的提议，未与真实教练用户校验。可能命名/分类不符合中国物理竞赛圈习惯。

**Mitigation:** Plan 5 应包含一个 "vocab review checkpoint" — 由用户在 plan 完成后人工 review 一次 builtin.yml，调整 display_zh / aliases。

## 14. Out-of-Scope Reminders

**Phase 2 NOT doing (deferred to Phase 3):**
- 用户错题本编辑 CLI/TUI/外部编辑器
- Review/refinement skill (user-note → canonical-tag mapping)
- Pending review 的确认/拒绝交互
- 用户笔记变化触发完整 refinement 链路（Phase 2 只做"投影到 user_confirmed_* 字段"，无 LLM）
- Q&A 历史作为标签来源（Quiz skill 在 Phase 3 才存在）
- 把 `cpho solve` 接入 OCR cache（Phase 2 cache 独立）

**Phase 2 NOT doing (deferred to Phase 4):**
- commit/export visibility workflow（D-13 字段预留但 workflow 无）
- 知识图谱关联（KNOW-01 — `find_related_problems` 只做标签重叠，无图算法）
- 相关题目上下文自动注入分析管线（KNOW-02）

**Phase 2 NOT doing (out of v1):**
- 布尔表达式查询（AND/OR/NOT）
- Embedding / vector retrieval
- 数据库存储
- 完整物理学 taxonomy（42 tag 起步）

**关键提醒给 planner:** §1 中标 "reserved-but-empty" 的字段必须**在数据模型中存在**，否则 Phase 3 升级要改 schema、要重跑全部历史索引（违反 D-14 schema 稳定性）。Plan 任务的"完成"判据必须包括"字段存在 + 默认值正确 + JSON 序列化测试通过"，**即使 Phase 2 不写非默认值**。

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Starter vocabulary 42 个 tag 的命名 / display_zh / aliases 覆盖物理竞赛主流场景 | §6 | candidates 数量爆炸；用户体验差但不阻塞架构 |
| A2 | OpenRouter `temperature=0.0` 加 strict JSON schema 配合 prompt vocab enum 能让 canonical tag 输出在多次运行间稳定 | §11 | 决定性测试可能 flaky；M1 fingerprint-cached skip 兜底 |
| A3 | RapidOCR 暴露 `__version__` 属性 | §10 | `_rapidocr_version` fallback "unknown" — 但同 workspace 内不会触发误检测，因为统一返回 "unknown" |
| A4 | Phase 1 `output/{problem_id}-report.json` 文件命名稳定不变 | §9 reuse map | 如果命名变, IndexEntry.solve_report_path 失效；可加 fallback 扫描 |
| A5 | LLM 在被 prompt 严格限制后会输出 vocab 之外的 internal_id（"prompt 不可信"假设） | §11 R3 | 即使错也只是 mitigation 多余, 不会破坏功能 |
| A6 | `.cpho/` 整体已在 .gitignore（确认: 是, line 8 of .gitignore） | §2 | [VERIFIED: .gitignore] 无风险 |
| A7 | `SkillRuntime._write_trace` 模式可以小范围复制而不实例化 SkillRuntime | §9 reuse map | AGENTS.md §2 简单优先支持复制；如果未来抽 helper 也只是 9 行重构 |
| A8 | Phase 1 SolveReport 在真实题目上至少能产出**非空**自由文本 tag（即使质量低） | §13 R1 | Mitigation 已包含 OCR fallback 路径，所以即使 SolveReport tags 全空也工作 |
| A9 | 100-1000 题量级下整文件重写 `.cpho/index.jsonl` 性能可接受 | §2 | 1000 IndexEntry 单条约 2-5KB → 全文件 2-5MB，整写 < 100ms；如未来到 10000+ 需要 streaming append 重构 |

## Open Questions (RESOLVED)

1. **Vocabulary version 命名规则**
   - What we know: §3 把 vocabulary_version 嵌入 SemanticFingerprint
   - What's unclear: 三层独立版本号合并成什么字符串？例 `builtin-v0.1+workspace-sha8+private-sha8`
   - **RESOLVED:** Recommendation: Plan 1 决定具体格式；推荐 `f"{builtin.version}+ws-{workspace_sha8 if exists else 'none'}+pv-{private_sha8 if exists else 'none'}"`

2. **Problem ID 生成策略**
   - What we know: D 提到"用户可能命名 (2019-IPhO-P1) 或自动生成 (路径 hash)"
   - What's unclear: Phase 2 自动 fallback 怎么算？
   - **RESOLVED:** Recommendation: `problem_id = path.stem` 优先（人类可读），重复时附加 `_{path_sha[:8]}`。Plan 1 决定。

3. **`cpho index` 是否应触发 `cpho solve`？**
   - What we know: D-05 把 SolveReport 列为 priority 2 source
   - What's unclear: 如果 SolveReport 不存在, Phase 2 是否 auto-run solve?
   - **RESOLVED:** Recommendation: **不**。Phase 2 只**消费**现有 SolveReport，缺失时降级到 OCR-only path（R1 R8 mitigation 已覆盖）。理由：solve 调用昂贵、解耦更清晰。CLI 可建议 "提示：3 个题目没有 SolveReport, 运行 `cpho solve` 提升标签质量"。

4. **Trace 文件位置**
   - What we know: §4 写 `.cpho/run-trace.jsonl`
   - What's unclear: Phase 1 solve 用 `traces/` (gitignored)
   - **RESOLVED:** Recommendation: Phase 2 走 `.cpho/run-trace.jsonl` 保持索引相关产物统一在 `.cpho/`。

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All | ✓ | >=3.11 (pyproject) | — |
| pydantic | Models | ✓ | >=2.7 | — |
| pyyaml | Vocab YAML | ✓ | >=6.0 | — |
| typer | CLI | ✓ | >=0.12 | — |
| httpx | LLM (via core/llm.py) | ✓ | >=0.27 | — |
| pymupdf (fitz) | PDF 加载 | ✓ | >=1.24 | — |
| rapidocr | OCR | ✓ | >=3.0 | — |
| onnxruntime | rapidocr 依赖 | ✓ | >=1.18 | — |
| OpenRouter API key | LLM tagging | ⚠️ | — | dry-run / fake provider for tests |
| Real physics problem set | E2E validation | ✗ | — | Phase 1 V-01 共享缺口；Phase 2 用 fake PDF + fake LLM 完成单元/集成测试 |

**Missing dependencies with no fallback:** OpenRouter API key 在 CI 缺失 → 所有 LLM 调用走 fake provider（与 Phase 1 测试一致）。
**Missing dependencies with fallback:** 真实题目缺失 → fake PDF + 预设 OCR text。

## Sources

### Primary (HIGH confidence) — verified by reading source code
- `src/cpho_cli/core/llm.py` — LLMProvider Protocol + OpenRouterProvider implementation
- `src/cpho_cli/core/workspace.py` — discover_workspace logic
- `src/cpho_cli/core/runtime.py` — SkillRuntime, TraceRecord, redact_secrets
- `src/cpho_cli/core/solve.py` — Phase 1 solve pipeline, report file naming
- `src/cpho_cli/core/config.py` — resolve_provider_config, resolve_model_params, merge logic
- `src/cpho_cli/core/ocr.py` — OCRProvider, RapidOCRProvider
- `src/cpho_cli/core/skills.py` — load_skill (used for understanding but Phase 2 doesn't call)
- `src/cpho_cli/models/solve.py` — SolveReport fields (physics_model_tags etc.)
- `src/cpho_cli/models/documents.py` — ProblemFile, AnswerKeyFile, ProblemAnswerPair
- `src/cpho_cli/models/config.py` — StrictModel base, ModelParams, AppConfig.skills dict
- `src/cpho_cli/models/runtime.py` — TraceRecord, CheckpointRecord, ResumeState
- `src/cpho_cli/models/ocr.py` — OCRBlock, OCRPageResult, OCRResult
- `src/cpho_cli/cli/app.py` — Typer command shape
- `tests/test_solve.py` — fake LLM provider pattern for tests
- `pyproject.toml` — pinned dependencies
- `.gitignore` — `.cpho/` already ignored
- `.planning/REQUIREMENTS.md` — IDX-01/02/03 wording, Out of Scope items
- `.planning/ROADMAP.md` — Phase 2 success criteria (4)
- `.planning/phases/02-tag-indexing/02-CONTEXT.md` — D-01 to D-17 + scope boundary
- `.planning/phases/01-core-foundation/01-VERIFICATION.md` — Phase 1 gaps (V-01, V-02)
- `.planning/phases/01-core-foundation/01-PATTERNS.md` — test-with-implementation requirement
- `docs/architecture-decisions.md` — 6 architecture decisions
- `docs/product-spec.md` — v1 scope
- `CLAUDE.md` / `AGENTS.md` — coding conventions

### Secondary (MEDIUM confidence)
- §6 starter vocabulary content — physics olympiad common knowledge (not yet user-verified)

### Tertiary (LOW confidence)
- §11 (M2) determinism claim about strict prompt + JSON schema — depends on OpenRouter / underlying model behavior, validated via Phase 2 determinism tests

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries already in pyproject.toml, no new deps
- Architecture (芯-壳, hashing, three-tier vocab, JSONL): HIGH — derived from locked decisions + verified Phase 1 patterns
- Data model: HIGH — sourced from D-07/D-09/D-10/D-11/D-14 directly, cross-checked against SolveReport fields
- LLM pipeline: HIGH — reuses Phase 1 LLMProvider with new prompt; no new infrastructure
- Starter vocabulary content: MEDIUM — categories and structure HIGH; specific tag names/aliases are ASSUMED, need user review
- Determinism strategy: MEDIUM-HIGH — fingerprint-cached skip mechanism is deterministic; LLM-output stability depends on model behavior (mitigated by post-processing pass)
- Phase 1 readiness: MEDIUM — Phase 1 code is solid, but "Needs Review" status + V-01 mean SolveReport quality in real use unknown

**Research date:** 2026-05-23
**Valid until:** 2026-06-23 (30 days for stable infrastructure work; Phase 1 status change or external dep upgrade would shorten this)

---

## RESEARCH COMPLETE

**Phase:** 02 - Tag Indexing
**Confidence:** HIGH (architecture & code reuse), MEDIUM (vocabulary content), MEDIUM (LLM determinism)

### Key Findings
1. **Zero new dependencies** — Phase 2 builds entirely on Phase 1's pyproject.toml stack.
2. **Single new core module:** `src/cpho_cli/core/index/` (split into `__init__.py`, `ocr_cache.py`, `prompts/`) + `src/cpho_cli/models/index.py` + `src/cpho_cli/vocabulary/builtin.yml`. CLI adds one `index` command.
3. **OCR cache is brand new** — Phase 1 solve does not cache OCR at all. Phase 2 introduces `.cpho/cache/ocr/` as a content-addressed cache and wraps OCRProvider; solve.py integration is deferred.
4. **Determinism comes from architecture, not the model** — fingerprint-cached skip (M1) is the primary guarantee; LLM strict prompt (M2) + deterministic canonical-mapping pass (M3) handle the cases where fingerprint misses.
5. **Phase 2 OUT-of-scope discipline is critical** — reserve schema fields (`user_confirmed_*`, `visibility`, `user_learning fingerprint`) but do not implement Phase 3 UX. The data model is the load-bearing artifact; Phase 3 fills it in.

### File Created
`/Users/ericzhang/Desktop/cpho-cli/.planning/phases/02-tag-indexing/02-RESEARCH.md`

### Confidence Assessment
| Area | Level | Reason |
|------|-------|--------|
| Standard Stack | HIGH | All deps already pinned & verified in Phase 1 |
| Architecture | HIGH | Locked by D-01..D-17 + verified Phase 1 patterns |
| Data Model | HIGH | Direct projection of D-07/D-09/D-10/D-11/D-14 |
| LLM Pipeline | HIGH | Reuses Phase 1 provider abstraction unchanged |
| Vocabulary Content | MEDIUM | 42 tags proposed; needs user review (R8) |
| Determinism | MEDIUM | Fingerprint skip deterministic; LLM call relies on post-processing |
| Pitfalls | HIGH | Phase 1 V-01 + OCR cache novelty + cold-start vocab identified |

### Open Questions (handed to planner)
1. Vocabulary version composition string format (Q1)
2. Problem ID generation rules (Q2)
3. Whether `cpho index` should auto-run solve (Q3 — recommend NO)
4. Trace file location consolidation (Q4 — recommend `.cpho/run-trace.jsonl`)

### Recommended Plan Breakdown (4-6 plans)
- **Plan 02-01 (Wave 1):** Data models (`models/index.py`) + JSONL read/write + atomic file ops + vocabulary YAML loader + three-tier merge + alias index — pure芯 layer, no LLM. Tests: `test_index_vocabulary.py`, model schema tests.
- **Plan 02-02 (Wave 1):** Three-tier hashing + fingerprint composition + action decision algorithm. Tests: `test_index_hashing.py`. Parallel with 02-01.
- **Plan 02-03 (Wave 2, depends 02-01+02-02):** OCR cache wrapper + engine upgrade detection + `--ocr-strategy` resolution. Tests: `test_index_ocr_upgrade.py`.
- **Plan 02-04 (Wave 2, depends 02-01):** LLM tagging pipeline (prompt template + TagRefinementOutput schema + canonical-mapping pass + trace writing). Tests: `test_index_tagging.py`, `test_index_determinism.py`. Parallel with 02-03.
- **Plan 02-05 (Wave 3, depends 02-01..02-04):** `build_index` orchestration + `cpho index` CLI command + statistics rendering + Python API exports. Tests: `test_index_cli.py`, `test_index_api.py`, `test_index_stats.py`.
- **Plan 02-06 (Wave 1, parallel with all):** Starter vocabulary content `builtin.yml` (42 entries) + tests verifying it loads + checkpoint for user review (R8).

### Ready for Planning
Research complete. Planner can now create 4-6 PLAN.md files using the breakdown above.
