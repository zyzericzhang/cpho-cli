# Phase 03: Skill Cross-Cutting Core Skills - Research

**Researched:** 2026-05-26
**Domain:** Python CLI/REPL skill orchestration, markdown export, OpenRouter LLM streaming, index tag writes
**Confidence:** HIGH for codebase integration; MEDIUM for OpenRouter model guidance because model pricing changes frequently

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Source: `.planning/phases/03-skill-cross-cutting-core-skills/03-CONTEXT.md` [CITED: local CONTEXT.md]

#### A. 跨切面三件套

- **D-01 Markdown 导出默认路径**：XDG `~/.local/share/cpho/outputs/<workspace_hash>/<skill>/<problem_name>.md`；用户可通过 `/set out.dir <path>` 覆盖为任意目录（包括 workspace 内或 CWD）。每类 skill 有各自默认子目录名。文件名必须含题目名（problem_id / 题目标题）。
- **D-02 Follow-up 模式实现**：REPL inline 子模式。Skill 结束后提示符变为 `cpho:followup>`；输入 `/exit` 或连续两次空行退出，返回主 REPL。Follow-up 历史可选 append 到当次 skill 的 markdown 导出文件末尾。不引入 LangChain / litellm——follow-up 本质是"在 skill 输出上下文上多轮 `provider.complete` 调用"，用现有 `core/llm.py` 自建即可。
- **D-03 进度显示**：引入 `rich` 库（仅用于 `Spinner` + `Live`）。非 TTY 环境 rich 自动降级为纯文本。显示内容：当前 step 名 / 正在做什么 / 已耗时。风格类似 Claude Code。

#### B. Solve 重定位

- **D-04 错误记录方式**：不进受控词表，用自由文本 `discrepancies` 列表记录每处发现的问题（数值错误/符号错误/物理图像错误/单位错误等 LLM 自由描述）。与 B1 决定一致：不强制受控 tag，保持灵活。
- **D-05 写入时机**：Solve 跑完后展示候选 discrepancies 列表，用户 `[y]/[n]/[edit]` 逐项 confirm 后才写入 SessionState（热路径）；支持 `--auto-confirm` flag 供批量场景跳过确认。
- **D-06 执行入口与 DAG**：保留 `cpho solve` 命令名 + REPL `/solve`，但 DAG steps 全面重写为"挑错向"。新 DAG 参考结构：`extract_official_steps → check_each_step → classify_error_types → propose_discrepancies → assemble_solve_report`。旧 prompt 文件（`normalize.md.j2` 等）可参考但需按新语义重写。

#### C. Explain 增强

- **D-07 多 Tone 并发 + 流式输出**：调用层用 `asyncio.gather` 对每个选中的 Tone 各跑一次完整 `SkillRuntime.run()`（不改 runtime 核心）。每个 Tone 独立流式输出（`provider.stream()`）；rich Live 面板同时渲染 N 个 Tone 的打字机效果（并排或顺序渲染）。所有 Tone 完成后合并进单一 `.explain.md` 文件（每 Tone 一个 `## Tone: 老师型` section）。
- **D-08 分栏目执行模型（两阶段）**：
  - 阶段一（每 Tone 1 次 LLM 调用）：同时输出"原答案逐步讲解" + "超越原答案的更清晰推导（若有）"
  - 阶段二（每 Tone 1 次 LLM 调用，依赖阶段一输出）：专门做句子级 explain（输入：阶段一全文 + 原题）
  - 每 Tone 共 2 次调用；多 Tone 并行时总调用数 = 2 × N
- **D-09 Explain prompt 原则（来自 new-understanding 锁定）**：
  - 首段固定：整道题物理图像 + 解题思路描述
  - 总是先物理图像/架构描述 → 再推导逻辑 → 再完整推导
  - 物理为主，数学为辅
  - 三种 Tone 的 prompt 各写一版：老师型（引导性/"我们看"/设问自答）、知识点密集型（完整物理思维+详细数学推导）、简短型（最短最重要的物理过程和推导逻辑）
- **D-10 回写 Index 交互**：Explain 完成后展示候选 tag（LLM 从讲解中提取），用户逐项 `[y]/[n]` confirm；支持用户在 confirm 时输入 `+<tag_name>` 追加自写 tag。最终调用 `add_problem_tags(source="explain", provenance=…)`，走现有 Phase 02.3 `skill_tags` 路径。

#### D. 主动提问 Skill (Probe)

- **D-11 对话深度控制**：用户显式退出（`/exit` 或连续两次空行）；软上限默认 10 轮，到上限后提示"已达最大轮次，是否继续？"而非强制截断；上限可通过 `/set probe.max_rounds N` 配置。
- **D-12 Markdown 输出时机**：每轮 Q+A 完成后立即 append 到文件（增量落盘，防崩溃丢失）。对话结束后生成最终版文件：前半部分为所有问题、后半部分为对应解答（重新排版）。
- **D-13 触发入口（双入口）**：
  - 独立 `/probe <problem_id>` 注册为正式 REPL 命令（与 `/solve` `/explain` 并列）
  - Explain 完成后提示一行："→ 进入 Probe 模式？(`/probe` 或 Enter 跳过)"

#### E. SkillRuntime 架构

- **D-14 Tone 并行不改 runtime**：`asyncio.gather` 在 Explain 调用层管理，`SkillRuntime` 不感知 Tone。每个 Tone 有独立 trace 文件（便于单 Tone 重试）。不引入 `fan_out/fan_in` 概念，Phase 3 不需要。
- **D-15 Skill 间共享 context（两层）**：
  - **热路径**（同会话）：Solve 跑完后把 `SolveReport`（含 discrepancies）存入 `SessionState`；同一 REPL 会话内 Explain/Probe 直接从 `session.current_solve_report` 读取
  - **可选持久化**：Solve confirm 结束后提示"是否把本次发现持久化到 index？"，用户选择后调 `add_problem_tags(source="solve", provenance=…)` 写入；下次跨会话 Explain 可从 index 读取历史 solve 发现
  - Solve discrepancies（自由文本）存 SessionState 字段，不强制进 tag 词表

#### 运行顺序（已锁定）

- **D-16** Solve 优先于其他 skill——其他 skill（Explain/Probe）默认在 Solve 校正过的标答基础上工作。REPL 如果检测到当前题目没有 solve 记录，在 `/explain` `/probe` 启动时给出提示（非强制阻断）。

### the agent's Discretion

No explicit `## the agent's Discretion` section was present in CONTEXT.md. [VERIFIED: local CONTEXT.md]

### Deferred Ideas (OUT OF SCOPE)

Source: `.planning/phases/03-skill-cross-cutting-core-skills/03-CONTEXT.md` [CITED: local CONTEXT.md]

- **批量 solve 跨题目模式**（连续对多道题目运行 solve）— 属于 Phase 4 工作流范畴
- **Explain 跨会话历史（Tone 缓存/增量更新）** — Phase 4 边界处理阶段考虑
- **Probe 对话导出到 Anki/Obsidian 格式** — 超出当前 Phase 范围
- **provider.stream() 的非 OpenRouter 实现** — Phase 3 仅需 OpenRouter 路径，其他 provider 流式支持留 Phase 4+
- **已废弃旧 Phase 3 思路（Quiz/YAML）** — 归档于 `.planning/notes/archive/03-CONTEXT-2026-05-24-quiz-yaml.md`
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SKILL-SOLVE-REPOSITION | `cpho solve` reviews the official answer, records confirmed discrepancies, and may persist skill/user tags. [CITED: `.planning/REQUIREMENTS.md`] | Reuse `SkillRuntime`, rewrite `solve/skill.yml`, keep `SolveReport.discrepancies`, add confirm UI, and call `add_problem_tags`. [VERIFIED: codebase grep] |
| SKILL-EXPLAIN-NEW | Explain supports one or more tones, first-paragraph physics picture, fixed sections, sentence-level explanation, and optional index tag writeback. [CITED: `.planning/REQUIREMENTS.md`] | Run one runtime per tone at the REPL/CLI layer with `asyncio.gather`; create explicit explain models/prompts; merge sections into one markdown file. [VERIFIED: codebase grep] |
| SKILL-PROBE | Probe is a continuous Q+A skill that writes markdown with all questions first and answers second. [CITED: `.planning/REQUIREMENTS.md`] | Implement as a REPL command plus shared conversation/export helper; append each turn immediately, then rewrite final layout at exit. [VERIFIED: local workspace + CONTEXT.md] |
| CROSS-EXPORT | Every skill can export markdown using a common path and filename rule. [CITED: `.planning/REQUIREMENTS.md`] | Add small export helper over XDG data dir; sanitize real Chinese filenames and preserve problem id/title. [VERIFIED: real workspace sample] |
| CROSS-FOLLOWUP | Every skill can enter follow-up conversation after the run. [CITED: `.planning/REQUIREMENTS.md`] | Add an inline REPL loop that keeps messages in memory and optionally appends to the skill markdown. [VERIFIED: codebase grep] |
| CROSS-PROGRESS | Every skill shows current step, activity, and elapsed time. [CITED: `.planning/REQUIREMENTS.md`] | Add a `rich`-backed progress adapter around runtime step execution or wrapper calls; avoid changing DAG semantics. [VERIFIED: codebase grep; CITED: Rich docs] |
| CROSS-ORDER | Explain/Probe should prefer a prior solve report. [CITED: `.planning/REQUIREMENTS.md`] | Add `SessionState.current_solve_report` and warn, not block, when absent. [VERIFIED: codebase grep] |
</phase_requirements>

## Summary

Phase 3 should be implemented as thin adapters around the existing code instead of a runtime rewrite. `SkillRuntime` already performs topological ordering, trace writes, checkpoint writes, and blackboard passing; `03-CONTEXT.md` explicitly locks "do not modify runtime core" for tone fan-out. [VERIFIED: `src/cpho_cli/core/runtime.py`; CITED: local CONTEXT.md] The cheapest safe plan is to add shared helpers for export/progress/follow-up, then wire Solve/Explain/Probe through REPL and CLI entry points. [VERIFIED: codebase grep]

The real workspace is large and filename-heavy: sampled `/Users/ericzhang/Desktop/物理竞赛资料` is 6.7G, has 1,019 PDFs, nested Chinese directories, answer/solution names such as `解析`, `答案`, `参考解答与评分标准`, and paths with repeated spaces. [VERIFIED: `find`, `du`, `file` against real workspace] Phase 3 export code must therefore treat paths as `Path` objects end-to-end, avoid shell splitting assumptions, and sanitize only filenames, not directory names. [VERIFIED: real workspace sample]

**Primary recommendation:** implement `src/cpho_cli/core/skill_outputs.py`, `src/cpho_cli/core/skill_progress.py`, `src/cpho_cli/core/followup.py`, and narrow skill-specific modules; keep `SkillRuntime.run()` synchronous, and place `asyncio.gather` plus OpenRouter streaming in the Explain command/service layer. [VERIFIED: codebase grep]

## Project Constraints (from AGENTS.md)

- State assumptions before implementation and ask when ambiguous. [CITED: `AGENTS.md`]
- Prefer minimal code; do not create abstractions for one-off behavior. [CITED: `AGENTS.md`]
- Make precise edits only; do not refactor adjacent working code. [CITED: `AGENTS.md`]
- Define success criteria and verify with tests. [CITED: `AGENTS.md`]
- During design, research, planning, and testing, sample `/Users/ericzhang/Desktop/物理竞赛资料` and prefer real files as test data. [CITED: `AGENTS.md`]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Markdown export | CLI/REPL application layer | Filesystem/XDG storage | The user selects paths in CLI/REPL; storage is local markdown under XDG data or override path. [VERIFIED: `persistence.py`; CITED: CONTEXT.md] |
| Follow-up conversation | REPL command layer | LLM provider | Prompt loop and exit semantics belong to the REPL; each turn calls the existing provider abstraction. [VERIFIED: `builtin_skills.py`, `llm.py`] |
| Progress display | CLI/REPL display layer | Runtime wrapper | Rendering is terminal-specific; runtime can emit/accept step events without knowing Rich panels. [VERIFIED: `display.py`, `runtime.py`] |
| Solve answer review | Skill service layer | Index write API | The skill produces discrepancies; confirmed persistence goes through existing `add_problem_tags`. [VERIFIED: `models/solve.py`, `core/index/api.py`] |
| Explain tone fan-out | Skill service/REPL layer | LLM provider | `asyncio.gather` is locked outside `SkillRuntime`; streaming chunks come from OpenRouter provider support. [CITED: CONTEXT.md; VERIFIED: `runtime.py`] |
| Probe | REPL command layer | Export helper + LLM provider | Probe is interactive and incremental; output is markdown. [CITED: CONTEXT.md] |
| Index tag writeback | Index API layer | Skill confirm UI | Existing API classifies canonical vs unverified tags and records provenance. [VERIFIED: `core/index/api.py`, `models/index.py`] |

## Standard Stack

### Core

| Library/Module | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Python | `>=3.11`; local `python3` is 3.13.12 | Runtime language | Project declares `requires-python = ">=3.11"`. [VERIFIED: `pyproject.toml`; VERIFIED: local `python3 --version`] |
| `prompt_toolkit` | local 3.0.52 | Existing REPL shell | Already used by REPL and installed in the uv environment. [VERIFIED: `pyproject.toml`; VERIFIED: local importlib metadata] |
| `pydantic` | local 2.13.4 | Strict response/data models | Existing models inherit strict Pydantic models. [VERIFIED: `models/config.py`; VERIFIED: local importlib metadata] |
| `httpx` | local 0.28.1 | OpenRouter HTTP client | Existing provider uses `httpx.Client` for chat completions. [VERIFIED: `core/llm.py`; VERIFIED: local importlib metadata] |
| `jinja2` | local 3.1.6 | Prompt templates | Existing skill handler renders prompt templates with `StrictUndefined`. [VERIFIED: `core/skill_handlers.py`; VERIFIED: local importlib metadata] |
| `rich` | latest PyPI 15.0.0; not locally installed | Spinner/Live progress only | Phase context locks Rich for `Spinner` and `Live`; Rich docs define `Live` for auto-updating displays and `Status` for spinner indicators. [ASSUMED due slopcheck unavailable; CITED: Rich docs; VERIFIED: PyPI JSON] |

### Supporting

| Library/Module | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| `asyncio` | Python stdlib | Explain tone fan-out | Use only at the command/service layer for multiple `SkillRuntime.run()` calls. [CITED: CONTEXT.md] |
| OpenRouter Chat Completions | current docs checked 2026-05-26 | `complete` and `stream` provider path | OpenRouter's chat completion endpoint supports streaming and non-streaming modes via a `stream` boolean. [CITED: https://openrouter.ai/docs/api-reference/chat-completion] |
| OpenRouter Models API | current API checked 2026-05-26 | Model metadata/pricing/capability checks | Models API returns metadata including pricing and supported parameters. [CITED: https://openrouter.ai/docs/overview/models; VERIFIED: OpenRouter API] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `rich` | Existing ANSI cursor printer | Existing code is enough for simple index progress but not N-tone live panels; Rich is locked by D-03. [VERIFIED: `display.py`; CITED: CONTEXT.md] |
| Direct `provider.complete` follow-up | LangChain/litellm | Explicitly out of scope; would add dependency and hidden control flow. [CITED: CONTEXT.md] |
| Runtime fan-out/fan-in | Modify `SkillRuntime` DAG semantics | Explicitly rejected by D-14; would increase blast radius. [CITED: CONTEXT.md] |

**Installation:**

```bash
uv add 'rich>=15.0.0'
```

`rich>=13.0` is the locked minimum in CONTEXT.md; PyPI currently reports 15.0.0 as latest. [CITED: CONTEXT.md; VERIFIED: PyPI JSON]

## Package Legitimacy Audit

`slopcheck` could not be installed/run in this environment, so all new package recommendations are tagged `[ASSUMED]` and the planner should add a human verification checkpoint before install. [VERIFIED: local command]

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| `rich` | PyPI | Latest upload 2026-04-12 | pypistats endpoint returned 429 during research | `https://github.com/Textualize/rich` | unavailable | Flagged - planner must add checkpoint before install. [ASSUMED] |

**Packages removed due to slopcheck [SLOP] verdict:** none. [VERIFIED: local command]
**Packages flagged as suspicious [SUS]:** none from slopcheck because slopcheck was unavailable. [VERIFIED: local command]

## Existing Code Findings

| Area | Finding | Planning Impact |
|------|---------|-----------------|
| Runtime | `SkillRuntime.run()` is synchronous, does topological order, traces each step, and writes checkpoints only on failure. [VERIFIED: `src/cpho_cli/core/runtime.py`] | Do not make it async in Phase 3; use wrappers/services outside it. |
| LLM provider | `LLMProvider` currently has only `complete`; `_OpenAICompatibleProvider.complete()` posts to `/chat/completions`. [VERIFIED: `src/cpho_cli/core/llm.py`] | Add `stream()` to the protocol and OpenRouter provider; keep DeepSeek non-streaming or raise a clear unsupported error because non-OpenRouter streaming is deferred. |
| Multimodal | Existing handler already passes `problem_file` and `answer_file` through `build_multimodal_content` when model capabilities support file/image. [VERIFIED: `src/cpho_cli/core/skill_handlers.py`] | New Solve/Explain prompts should keep `problem_file`/`answer_file` keys available. |
| Index write API | `add_problem_tags` appends `UserTagEntry`; canonical/unverified classification is already implemented. [VERIFIED: `src/cpho_cli/core/index/api.py`] | Use existing API for Solve/Explain persistence; do not add another tag store. |
| Session state | `SessionState` has current problem/search state but no `current_solve_report`, `out_dir`, or `probe_max_rounds`. [VERIFIED: `src/cpho_cli/cli/repl/session.py`] | Add only the three Phase 3 fields required by D-01/D-11/D-15. |
| REPL settings | `/set` currently accepts only `workspace`, `max_results`, `output_format`, and `provider`. [VERIFIED: `src/cpho_cli/cli/repl/commands/set_cmd.py`] | Extend allowlist for `out.dir` and `probe.max_rounds`; preserve existing validation style. |
| REPL skills | `/explain` and `/quiz` are stubs; `/probe` and `/solve` are not registered here. [VERIFIED: `src/cpho_cli/cli/repl/commands/builtin_skills.py`] | Replace `/quiz` with `/probe`, add `/solve`, keep `Command(...)` registration pattern. |
| CLI solve | `cpho solve` currently runs old solve semantics and writes JSON/markdown under `output_dir`. [VERIFIED: `src/cpho_cli/core/solve.py`] | Reuse CLI command name, but change skill DAG and report writer semantics. |

## Real Workspace Observations

| Observation | Evidence | Impact |
|-------------|----------|--------|
| Workspace is large and mostly PDFs | Sample found 6.7G total and 1,019 `.pdf` files. [VERIFIED: `du`, `find`] | Tests should copy tiny samples to temp dirs, not run destructive or full-workspace operations. |
| Filenames are Chinese and varied | Examples include `力学2试题.pdf`, `电磁学2解析.pdf`, `理论3-答案.pdf`, `参考解答与评分标准.pdf`. [VERIFIED: `find`] | Export filenames should preserve readable Chinese where possible and only strip path separators/reserved characters. |
| Paths can contain repeated spaces | Directory `2023暑期猿辅导物理刷题  电子版` exists; a naive `xargs file` run broke paths by collapsing whitespace. [VERIFIED: `find`; VERIFIED: failed `xargs` sample] | Implementation and tests must avoid shell-splitting strings; use `Path` and Python APIs. |
| Some PDFs are very large multi-problem books | Sample includes `2023博知汇刷题班12套题.pdf` with 322 pages. [VERIFIED: `file`] | Phase 3 should consume existing index/splitting results instead of rescanning large source files during interactive skills. |
| `.cpho` exists but no `index.jsonl` was found at the sampled root | Found OCR cache file under `.cpho/cache/ocr`, no root `.cpho/index.jsonl`. [VERIFIED: `find`] | Tests should seed temp indexes; do not assume the real workspace is currently indexed. |

## Architecture Patterns

### System Architecture Diagram

```text
User command: CLI `cpho solve` or REPL `/solve` `/explain` `/probe`
  |
  v
Command parser + SessionState
  |-- resolve current problem/index entry --> Index API / JSONL storage
  |-- resolve output path -------------> skill_outputs markdown helper
  |-- progress events -----------------> skill_progress Rich/plain renderer
  v
Skill service layer
  |-- Solve: new review DAG via SkillRuntime
  |-- Explain: asyncio.gather(one SkillRuntime run per tone)
  |-- Probe: interactive turn loop + incremental markdown append
  v
LLM provider
  |-- complete(): structured JSON and follow-up turns
  |-- stream(): OpenRouter streaming chunks for Explain text panels
  v
Confirm UI
  |-- accepted discrepancies/tags -----> SessionState.current_solve_report
  |-- optional persistence ------------> add_problem_tags(... skill_name, reasoning)
  v
Final markdown export + optional follow-up append
```

### Recommended Project Structure

```text
src/cpho_cli/
├── core/
│   ├── skill_outputs.py       # XDG output path, filename sanitization, atomic/final markdown writes
│   ├── skill_progress.py      # Rich Live/Spinner wrapper with plain text fallback
│   ├── followup.py            # provider.complete loop helpers shared by REPL skills
│   └── llm.py                 # add OpenRouterProvider.stream()
├── builtin_skills/
│   ├── solve/                 # rewrite DAG and prompts for answer review
│   ├── explain/               # new skill.yml + tone prompts
│   └── probe/                 # optional prompt assets if Probe calls use templates
├── cli/repl/commands/
│   └── builtin_skills.py      # register /solve, /explain, /probe
└── models/
    ├── solve.py               # add review-oriented fields only if current model is insufficient
    └── explain.py             # small Pydantic models for tone output and tag candidates
```

This structure is intentionally small and matches the existing `skill.yml` + `prompts/*.md.j2` + `make_llm_handler` pattern. [VERIFIED: `core/skills.py`; VERIFIED: `builtin_skills/solve/skill.yml`]

### Pattern 1: Step Progress Without Runtime Rewrite

**What:** add an optional `on_step` callback to `SkillRuntime.run()` or wrap step calls in a subclass-like helper only if the callback is the smallest change. [VERIFIED: `runtime.py`]

**When to use:** use this for `CROSS-PROGRESS` so Solve and Explain both render the same step state. [CITED: CONTEXT.md]

**Example:**

```python
# Source: existing runtime loop in src/cpho_cli/core/runtime.py [VERIFIED: codebase]
runtime = SkillRuntime(handlers=handlers, trace_path=trace_path, secrets=[api_key])
with skill_progress("solve") as progress:
    result = runtime.run(spec, blackboard, on_step=progress.update)
```

If adding `on_step` changes too many tests, implement `run_skill_with_progress(runtime, spec, blackboard, progress)` by copying only the loop control needed and defer the runtime callback. [ASSUMED]

### Pattern 2: Export Path Helper

**What:** compute default output directory from XDG data home, workspace hash, skill name, and problem title/id. [CITED: CONTEXT.md]

**When to use:** every skill result, Probe incremental output, and follow-up append. [CITED: CONTEXT.md]

**Example:**

```python
# Source: XDG style from src/cpho_cli/cli/repl/persistence.py [VERIFIED: codebase]
def data_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    path = Path(base) / "cpho"
    path.mkdir(parents=True, exist_ok=True)
    return path
```

Use `hashlib.sha256(str(workspace.resolve()).encode()).hexdigest()[:12]` for `workspace_hash`; this avoids leaking the whole path into default output folders while staying deterministic. [ASSUMED]

### Pattern 3: Confirm-Then-Persist

**What:** display candidate discrepancies/tags, allow accept/reject/edit, update `SessionState`, then optionally call `add_problem_tags`. [CITED: CONTEXT.md]

**When to use:** Solve discrepancy review and Explain tag writeback. [CITED: CONTEXT.md]

**Example:**

```python
# Source: src/cpho_cli/core/index/api.py [VERIFIED: codebase]
entry = add_problem_tags(
    session.workspace_path,
    problem_id,
    accepted_tags,
    skill_name="explain",
    reasoning="Tags accepted from Phase 3 explain output.",
)
```

Current API uses `skill_name` and `reasoning`, not the `source`/`provenance` parameter names in CONTEXT.md. [VERIFIED: `core/index/api.py`] Planner should use the existing signature unless it intentionally renames the API. [VERIFIED: codebase grep]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Terminal live progress | ANSI cursor panel system | `rich` `Live`/`Status`/`Spinner` | Rich officially supports auto-updating live displays and spinner status indicators. [CITED: Rich docs] |
| Follow-up orchestration | LangChain/litellm agent chain | Existing `LLMProvider.complete` and local message history | Context explicitly forbids LangChain/litellm for follow-up. [CITED: CONTEXT.md] |
| Tag storage | New JSON file for skill tags | `add_problem_tags` / `UserTagEntry` | Existing API records canonical/unverified tags and provenance fields. [VERIFIED: `core/index/api.py`, `models/index.py`] |
| Tone fan-out runtime | DAG-level fan_out/fan_in | `asyncio.gather` in Explain command/service | Context locks runtime as tone-unaware. [CITED: CONTEXT.md] |
| Path parsing | Shell commands or string splitting | `pathlib.Path`, Python `find` equivalents in tests | Real workspace has Chinese paths and repeated spaces. [VERIFIED: real workspace sample] |

**Key insight:** Phase 3 complexity is interaction orchestration, not core DAG execution. The failure mode to avoid is turning shared UX concerns into a second runtime. [VERIFIED: codebase grep]

## OpenRouter-Capable Verification Model Guidance

Use two model tiers in tests/manual verification. [VERIFIED: OpenRouter API 2026-05-26]

| Purpose | Model | Price Snapshot | Why |
|---------|-------|----------------|-----|
| Cheapest smoke verification for text JSON/stream plumbing | `inclusionai/ling-2.6-flash` | `$0.01/M` input, `$0.03/M` output; supports `structured_outputs`, `response_format`, `tools`, `temperature` | It was the cheapest non-free text model returned by OpenRouter Models API with structured output support in this research run. [VERIFIED: OpenRouter API 2026-05-26] |
| Cheapest-ish multimodal/file smoke path among sampled current models | `google/gemini-3.1-flash-lite` | `$0.25/M` input, `$1.50/M` output; supports text/image/file inputs and structured outputs | Use only when testing PDF/image path because the cheapest text-only model cannot verify file handling. [VERIFIED: OpenRouter API 2026-05-26] |
| Existing project default | `openai/gpt-4o-mini` | default configured in `AppConfig` | Keep as backward-compatible default unless user changes config. [VERIFIED: `models/config.py`] |

Guidance: do not use the cheapest model as a physics-quality gate. Use it for "provider request works", "streaming parser works", and "structured output shape works". [ASSUMED] Physics-quality prompt checks should remain fake-provider tests plus small manual OpenRouter runs on copied real workspace samples. [VERIFIED: existing fake-provider test style; ASSUMED for manual gate]

## Common Pitfalls

### Pitfall 1: Controlled Tag Language Drift

**What goes wrong:** Solve discrepancies are free text by D-04, but Phase 3 roadmap still says "受控 tag" in one success criterion. [CITED: ROADMAP.md; CITED: CONTEXT.md]

**Why it happens:** Requirements text predates the final CONTEXT decision that discrepancies stay free text. [CITED: CONTEXT.md]

**How to avoid:** Treat discrepancies as free text in `SolveReport`/`SessionState`; only optional persistence to index uses `add_problem_tags`, where unknown strings become `unverified_tags`. [VERIFIED: `models/solve.py`; VERIFIED: `core/index/api.py`]

**Warning signs:** implementation tries to add discrepancy categories to the canonical vocabulary. [ASSUMED]

### Pitfall 2: Streaming Conflicts With Structured JSON

**What goes wrong:** Explain wants streaming text output, while existing `make_llm_handler` expects complete JSON and Pydantic validation. [VERIFIED: `core/skill_handlers.py`; CITED: CONTEXT.md]

**Why it happens:** OpenRouter streaming yields incremental chunks, but Pydantic validation requires the final content. [CITED: OpenRouter chat completion docs; VERIFIED: codebase]

**How to avoid:** For Explain visible prose, stream plain markdown sections and validate only a lightweight final object/tag extraction call if needed. [ASSUMED] Keep Solve JSON non-streaming. [ASSUMED]

**Warning signs:** `make_llm_handler` starts parsing partial stream chunks as JSON. [ASSUMED]

### Pitfall 3: Path Bugs From Real Workspace Names

**What goes wrong:** paths with repeated spaces or Chinese characters break if implementation splits command strings or shell output. [VERIFIED: real workspace sample]

**Why it happens:** a sampled `xargs file` command failed on `2023暑期猿辅导物理刷题  电子版` because whitespace was not preserved. [VERIFIED: local command]

**How to avoid:** use `Path`, Python file APIs, and prompt_toolkit args already parsed by REPL command handlers. [VERIFIED: codebase pattern]

**Warning signs:** code calls `.split()` on a path-like string. [ASSUMED]

### Pitfall 4: Mutating Index Machine Tags

**What goes wrong:** Explain/Solve persistence overwrites LLM-generated tag buckets instead of appending user/skill tags. [VERIFIED: `models/index.py`]

**Why it happens:** `IndexEntry` has both machine buckets and `user_tags`. [VERIFIED: `models/index.py`]

**How to avoid:** only call `add_problem_tags`/`update_problem_tags`/`remove_problem_tags`; never mutate `physics_model_tags`, `math_technique_tags`, or `heuristic_tags` in Phase 3. [VERIFIED: `core/index/api.py`]

**Warning signs:** Phase 3 code imports `TaggedReference` to persist Explain output. [ASSUMED]

### Pitfall 5: Overbuilding Probe

**What goes wrong:** Probe becomes the old Quiz mode or a new Socratic engine. [CITED: REQUIREMENTS.md]

**Why it happens:** old `/quiz` placeholder exists, but new requirement is a user-driven probing conversation. [VERIFIED: `builtin_skills.py`; CITED: REQUIREMENTS.md]

**How to avoid:** replace `/quiz` with `/probe`, keep the loop simple, and write markdown incrementally. [CITED: CONTEXT.md]

**Warning signs:** implementation adds scoring, Anki export, or quiz YAML. [CITED: CONTEXT.md]

## Code Examples

### Add OpenRouter Streaming Without Breaking `complete`

```python
# Source: OpenRouter chat completion docs + current provider style [CITED: OpenRouter docs; VERIFIED: core/llm.py]
def stream(self, messages: list[ChatMessage], params: ModelParams) -> Iterator[str]:
    payload = {"model": params.name, "messages": messages, "stream": True}
    with self.client.stream(
        "POST",
        f"{self.base_url}/chat/completions",
        headers={"Authorization": f"Bearer {self.api_key}"},
        json=payload,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line.startswith("data: "):
                continue
            data = line.removeprefix("data: ").strip()
            if data == "[DONE]":
                break
            yield parse_openrouter_delta(data)
```

Planner should specify tests for chunk parsing with fake SSE lines instead of live network calls. [ASSUMED]

### Confirm List Shape

```python
# Source: existing display helpers are plain functions in display.py [VERIFIED: codebase]
accepted = await confirm_list(
    candidates,
    allow_edit=True,
    allow_append=False,
    prompt="[y]/[n]/[edit]",
)
session.current_solve_report = report.model_copy(update={"discrepancies": accepted})
```

### Probe Incremental Markdown

```python
# Source: D-12 locked design [CITED: CONTEXT.md]
append_probe_turn(path, turn_no, question, answer)
if done:
    write_probe_final(path, turns)
```

The append step should use direct Python file writes and a final atomic replace for the reformatted document. [ASSUMED]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Solve generates a new solution | Solve reviews official answer for discrepancies | Phase 3 context gathered 2026-05-26 | Rewrite DAG/prompts; do not preserve old answer-generation behavior. [CITED: CONTEXT.md] |
| `/quiz` placeholder | `/probe` active questioning skill | Phase 3 requirements updated 2026-05-26 | Remove/replace quiz stub. [CITED: REQUIREMENTS.md; VERIFIED: `builtin_skills.py`] |
| Index coupling to SolveReport | Skill/user tags stored separately in `user_tags` | Phase 02.3 complete 2026-05-25 | Phase 3 persistence must use index API. [CITED: ROADMAP.md; VERIFIED: `models/index.py`] |
| ANSI-only progress | Rich Live/Spinner for skill progress | Phase 3 locked decision | Add `rich`, keep fallback simple. [CITED: CONTEXT.md; CITED: Rich docs] |

**Deprecated/outdated:**
- Old solve prompts `normalize.md.j2`, `derive.md.j2`, `cross_check.md.j2` are reference only; semantics must be rewritten to answer review. [CITED: CONTEXT.md; VERIFIED: `builtin_skills/solve/prompts/`]
- Old `/quiz` skill direction is out of scope. [CITED: REQUIREMENTS.md]

## Test Strategy

Nyquist validation architecture is omitted because `.planning/config.json` sets `workflow.nyquist_validation` to `false`. [VERIFIED: `.planning/config.json`]

Recommended focused tests:

| Behavior | Test File | Command |
|----------|-----------|---------|
| Export default path uses XDG, workspace hash, skill subdir, and Chinese-safe filename | `tests/test_skill_outputs.py` | `uv run pytest tests/test_skill_outputs.py -q` |
| `rich` progress falls back in non-TTY and renders step/elapsed text | `tests/test_skill_progress.py` | `uv run pytest tests/test_skill_progress.py -q` |
| `SessionState` stores `current_solve_report`, `out_dir`, `probe_max_rounds` | `tests/test_repl_session.py` | `uv run pytest tests/test_repl_session.py -q` |
| `/set out.dir` and `/set probe.max_rounds` validation | `tests/test_repl_builtin_commands.py` or `tests/test_repl_commands.py` | `uv run pytest tests/test_repl_builtin_commands.py tests/test_repl_commands.py -q` |
| Solve confirm updates session and optional `add_problem_tags` only touches `user_tags` | `tests/test_solve.py` + `tests/test_index_api.py` | `uv run pytest tests/test_solve.py tests/test_index_api.py -q` |
| Explain multi-tone launches N runs and writes one `.explain.md` with Tone sections | `tests/test_explain.py` | `uv run pytest tests/test_explain.py -q` |
| OpenRouter stream parser handles fake SSE chunks and `[DONE]` | `tests/test_llm.py` | `uv run pytest tests/test_llm.py -q` |
| Probe appends each turn and rewrites final markdown into questions/answers sections | `tests/test_probe.py` | `uv run pytest tests/test_probe.py -q` |
| Real workspace-shaped path sample with copied files and repeated spaces | `tests/test_phase03_acceptance.py` | `uv run pytest tests/test_phase03_acceptance.py -q` |

Baseline command already passed during research: `uv run pytest tests/test_runtime.py tests/test_repl_builtin_commands.py tests/test_index_api.py -q` returned `32 passed in 0.74s`. [VERIFIED: local test run]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | Project runtime | yes | 3.13.12 local; project requires >=3.11 | Use uv-managed Python if needed. [VERIFIED: local command; VERIFIED: `pyproject.toml`] |
| uv | Test/install workflow | yes | 0.11.6 | `python -m pip` for read-only checks, but project uses uv. [VERIFIED: local command] |
| pytest | Test strategy | yes | 9.0.3 in uv env | none needed. [VERIFIED: local importlib metadata] |
| OpenRouter network API | model metadata/pricing research | yes via `curl`; Python urllib failed cert verification | API queried successfully with `curl`; provider uses `httpx`, so implementation should keep tests fake-provider based. [VERIFIED: local commands] |
| ctx7 CLI | docs lookup fallback | no | — | Used official docs/web instead. [VERIFIED: local command] |
| slopcheck | package legitimacy | no | — | Human verification checkpoint before installing `rich`. [VERIFIED: local command] |
| `rich` | progress rendering | no | PyPI latest 15.0.0 | Install in Phase 3; non-TTY tests can fake/fallback. [VERIFIED: local `pip show`; VERIFIED: PyPI JSON] |

**Missing dependencies with no fallback:**
- `rich` is missing locally and must be installed for the locked progress UI. [VERIFIED: local `pip show`; CITED: CONTEXT.md]

**Missing dependencies with fallback:**
- `ctx7` missing; official docs were available by web/curl. [VERIFIED: local command]
- `slopcheck` missing; planner should gate `rich` install with human verification. [VERIFIED: local command]

## Security Domain

Security enforcement is enabled by default because `.planning/config.json` does not explicitly set `security_enforcement: false`. [VERIFIED: `.planning/config.json`]

### Applicable ASVS Categories

OWASP ASVS is an application security verification standard for web applications and services; this CLI maps only the locally relevant categories. [CITED: https://owasp.org/www-project-application-security-verification-standard/]

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | No app login or user auth in Phase 3. [VERIFIED: REQUIREMENTS.md] |
| V3 Session Management | partial | REPL session state is local; do not persist API keys or full LLM conversations unless user opts into markdown append. [VERIFIED: `persistence.py`; CITED: CONTEXT.md] |
| V4 Access Control | partial | Validate selected problem ids through existing index APIs and reject path traversal. [VERIFIED: `core/index/notebook.py`; VERIFIED: `tests/test_index_api.py`] |
| V5 Input Validation | yes | Use Pydantic models for LLM outputs and explicit path validation for export overrides. [VERIFIED: `models/config.py`; VERIFIED: `skill_handlers.py`] |
| V6 Cryptography | yes, narrow | Use SHA-256 for deterministic workspace hash only; do not treat it as a secret or access-control boundary. [ASSUMED] |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal in export filename or problem id | Tampering | Sanitize filenames; keep output directory as a resolved `Path`; reuse `_validate_problem_id` for indexed ids. [VERIFIED: `core/index/notebook.py`] |
| API key leakage in traces or errors | Information disclosure | Continue using `redact_secrets` in runtime traces and provider errors. [VERIFIED: `core/runtime.py`; VERIFIED: `core/llm.py`] |
| Prompt/markdown injection from official answers | Spoofing/Tampering | Treat LLM output as markdown text, not executable instructions; never shell out with generated content. [ASSUMED] |
| Overwriting user files via export path | Tampering | If target exists, prompt before overwrite or add a suffix; write via temp file then atomic replace only after confirm. [ASSUMED] |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Workspace hash should be first 12 hex chars of SHA-256 of resolved workspace path. | Architecture Patterns | Output paths could differ from user expectation; low functional risk. |
| A2 | `rich` is safe to install after human verification despite slopcheck being unavailable. | Standard Stack / Package Audit | Supply-chain risk if package legitimacy is not manually checked. |
| A3 | Cheapest text model is acceptable only for plumbing verification, not physics quality. | OpenRouter Guidance | If used as quality gate, false positives may approve bad explanations. |
| A4 | Streaming Explain should stream markdown prose and validate tags in a separate final step. | Pitfalls / Code Examples | If planner requires fully structured streaming, implementation complexity rises. |
| A5 | Export overwrite behavior should prompt or suffix. | Security Domain | User may prefer deterministic overwrite; planner should decide UX. |

## Open Questions

1. **Should `add_problem_tags` be renamed to match CONTEXT wording?**
   - What we know: CONTEXT says `source`/`provenance`, current API accepts `skill_name`/`reasoning`. [CITED: CONTEXT.md; VERIFIED: `core/index/api.py`]
   - What's unclear: whether naming consistency is worth a Phase 3 API rename.
   - Recommendation: do not rename unless planner includes a small compatibility wrapper; use existing API directly.

2. **Should CLI `cpho solve` include interactive confirm by default?**
   - What we know: D-05 requires confirm before SessionState write and `--auto-confirm` for batch. [CITED: CONTEXT.md]
   - What's unclear: CLI has no `SessionState`; confirm can only affect markdown/index persistence.
   - Recommendation: implement CLI confirm for persistence/export, and REPL confirm for `SessionState.current_solve_report`.

3. **How much real OpenRouter verification is acceptable in automated tests?**
   - What we know: existing tests use fake providers heavily and avoid network. [VERIFIED: tests]
   - What's unclear: whether CI has OpenRouter credentials.
   - Recommendation: keep automated tests fake-provider only; add one manual command using the cheapest model when credentials exist.

## Sources

### Primary (HIGH confidence)

- `.planning/phases/03-skill-cross-cutting-core-skills/03-CONTEXT.md` - locked decisions and out-of-scope items.
- `.planning/ROADMAP.md` - Phase 3 goal and success criteria.
- `.planning/REQUIREMENTS.md` - Phase 3 requirement IDs.
- `docs/new-understanding-2026-05-26.md` - user design intent.
- `src/cpho_cli/core/runtime.py` - runtime behavior.
- `src/cpho_cli/core/llm.py` - provider abstraction.
- `src/cpho_cli/core/skill_handlers.py` - prompt/LLM handler pattern.
- `src/cpho_cli/core/index/api.py` and `src/cpho_cli/models/index.py` - tag write API and data model.
- `src/cpho_cli/cli/repl/session.py`, `display.py`, `persistence.py`, `commands/builtin_skills.py`, `commands/set_cmd.py` - REPL integration points.
- Real workspace sample: `/Users/ericzhang/Desktop/物理竞赛资料` checked with `find`, `du`, and `file`.
- OpenRouter official docs: https://openrouter.ai/docs/api-reference/chat-completion and https://openrouter.ai/docs/overview/models.
- OpenRouter Models API: `https://openrouter.ai/api/v1/models`, queried 2026-05-26.
- Rich official docs: https://rich.readthedocs.io/en/stable/live.html and https://rich.readthedocs.io/en/latest/reference/status.html.
- OWASP ASVS project: https://owasp.org/www-project-application-security-verification-standard/.

### Secondary (MEDIUM confidence)

- PyPI JSON for `rich`: `https://pypi.org/pypi/rich/json`, queried 2026-05-26.
- Local PyPI index output for `rich`, queried 2026-05-26.

### Tertiary (LOW confidence)

- None used for recommendations.

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - codebase dependencies verified; `rich` package legitimacy needs human checkpoint because slopcheck was unavailable.
- Architecture: HIGH - based on current code and locked CONTEXT decisions.
- Pitfalls: HIGH for codebase/path risks; MEDIUM for OpenRouter streaming/model behavior because provider capabilities and pricing are fast-moving.

**Research date:** 2026-05-26
**Valid until:** 2026-06-02 for OpenRouter pricing/model guidance; 2026-06-25 for codebase architecture if Phase 3 implementation has not started.

## RESEARCH COMPLETE

Files changed:
- `.planning/phases/03-skill-cross-cutting-core-skills/03-RESEARCH.md`
