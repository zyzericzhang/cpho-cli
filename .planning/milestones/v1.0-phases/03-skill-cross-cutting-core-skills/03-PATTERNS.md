# Phase 3: Skill Cross-Cutting Core Skills - Pattern Map

**Mapped:** 2026-05-26
**Files analyzed:** 25 planned new/modified file groups
**Analogs found:** 24 / 25

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `pyproject.toml` | config | dependency config | `pyproject.toml` | exact |
| `src/cpho_cli/core/llm.py` | service | request-response + streaming | `src/cpho_cli/core/llm.py` | partial |
| `src/cpho_cli/core/skill_handlers.py` | service | transform + request-response | `src/cpho_cli/core/skill_handlers.py` | exact |
| `src/cpho_cli/core/solve.py` | service | file-I/O + request-response | `src/cpho_cli/core/solve.py` | exact |
| `src/cpho_cli/models/solve.py` | model | transform | `src/cpho_cli/models/solve.py` | exact |
| `src/cpho_cli/models/explain.py` | model | transform | `src/cpho_cli/models/solve.py` | role-match |
| `src/cpho_cli/models/probe.py` | model | event-driven conversation | `src/cpho_cli/models/solve.py` | role-match |
| `src/cpho_cli/cli/repl/session.py` | store | event-driven session state | `src/cpho_cli/cli/repl/session.py` | exact |
| `src/cpho_cli/cli/repl/persistence.py` | utility | file-I/O | `src/cpho_cli/cli/repl/persistence.py` | exact |
| `src/cpho_cli/cli/repl/display.py` | utility | request-response + progress events | `src/cpho_cli/cli/repl/display.py` | exact |
| `src/cpho_cli/cli/repl/commands/builtin_skills.py` | controller/route | request-response + event-driven | `src/cpho_cli/cli/repl/commands/search.py` | role-match |
| `src/cpho_cli/builtin_skills/solve/skill.yml` | config | DAG transform | `src/cpho_cli/builtin_skills/solve/skill.yml` | exact |
| `src/cpho_cli/builtin_skills/solve/prompts/*.md.j2` | config | prompt transform | `src/cpho_cli/builtin_skills/solve/prompts/*.md.j2` | exact |
| `src/cpho_cli/builtin_skills/solve/SKILL.md` | docs/config | skill metadata | `src/cpho_cli/builtin_skills/solve/SKILL.md` | exact |
| `src/cpho_cli/builtin_skills/explain/skill.yml` | config | DAG transform | `src/cpho_cli/builtin_skills/solve/skill.yml` | role-match |
| `src/cpho_cli/builtin_skills/explain/prompts/*.md.j2` | config | prompt transform | `src/cpho_cli/builtin_skills/solve/prompts/*.md.j2` | role-match |
| `src/cpho_cli/builtin_skills/explain/SKILL.md` | docs/config | skill metadata | `src/cpho_cli/builtin_skills/solve/SKILL.md` | role-match |
| `src/cpho_cli/builtin_skills/probe/skill.yml` | config | conversation transform | `src/cpho_cli/builtin_skills/solve/skill.yml` | role-match |
| `src/cpho_cli/builtin_skills/probe/prompts/*.md.j2` | config | prompt transform | `src/cpho_cli/builtin_skills/solve/prompts/*.md.j2` | role-match |
| `src/cpho_cli/builtin_skills/probe/SKILL.md` | docs/config | skill metadata | `src/cpho_cli/builtin_skills/solve/SKILL.md` | role-match |
| `tests/test_solve.py` | test | file-I/O + request-response | `tests/test_solve.py` | exact |
| `tests/test_llm.py` | test | request-response + streaming | `tests/test_llm.py` | role-match |
| `tests/test_repl_builtin_commands.py` | test | request-response | `tests/test_repl_builtin_commands.py` | exact |
| `tests/test_repl_display.py` | test | display transform | `tests/test_repl_display.py` | exact |
| `tests/test_phase03_acceptance.py` | test | acceptance | `tests/test_phase023_acceptance.py` | role-match |

## Pattern Assignments

### `src/cpho_cli/core/llm.py` (service, request-response + streaming)

**Analog:** `src/cpho_cli/core/llm.py`

**Imports pattern** (lines 1-12):
```python
from __future__ import annotations

import time
import re
from typing import Any, Protocol, TypeVar

import httpx
from pydantic import BaseModel
```

**Provider interface pattern** (lines 22-29):
```python
class LLMProvider(Protocol):
    def complete(
        self,
        messages: list[ChatMessage],
        params: ModelParams,
        response_model: type[ResponseModel] | None = None,
    ) -> LLMResponse:
        """Complete a chat request."""
```

**HTTP payload/retry/error pattern** (lines 56-112):
```python
payload: dict[str, Any] = {
    "model": params.name,
    "messages": messages,
}
headers = {"Authorization": f"Bearer {self.api_key}"}
last_error: Exception | None = None
for attempt in range(self.max_retries + 1):
    try:
        response = self.client.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
        )
        if response.status_code in {429, 500, 502, 503, 504}:
            raise httpx.HTTPStatusError("transient provider error", request=response.request, response=response)
        if response.status_code >= 400:
            raise LLMProviderError(
                redact_secrets(
                    f"{self.label} request failed: {response.status_code} {response.text}",
                    [self.api_key],
                )
            )
```

**Implementation guidance:** add `stream(...)` to the protocol and `_OpenAICompatibleProvider` using the same payload construction, header construction, retry policy, and `redact_secrets` error formatting. Keep Phase 3 stream support on the OpenRouter-compatible path. Do not change `SkillRuntime`; callers such as Explain/Follow-up can call `provider.stream()` directly.

**Test analog:** `tests/test_llm.py` lines 13-47 capture request JSON via `httpx.MockTransport`; add stream tests in the same style, asserting `stream: true` and yielded content chunks.

---

### `src/cpho_cli/core/skill_handlers.py` (service, transform + request-response)

**Analog:** `src/cpho_cli/core/skill_handlers.py`

**Imports pattern** (lines 3-17):
```python
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import jinja2
from pydantic import BaseModel, ValidationError
```

**Prompt + multimodal + structured response pattern** (lines 51-82):
```python
def handler(step: SkillStep, values: Mapping[str, Any]) -> Mapping[str, Any]:
    if step.prompt_template is None:
        raise SkillRuntimeError(f"Step {step.id} is missing prompt_template")
    try:
        prompt = env.get_template(step.prompt_template).render(**values)
    except jinja2.TemplateError as exc:
        raise SkillRuntimeError(f"Step {step.id} prompt render failed: {exc}") from exc

    output_model = (
        models_by_output.get(step.output_keys[0])
        if len(step.output_keys) == 1
        else None
    )
    content: str | list[dict[str, Any]] = prompt
    file_paths = [
        Path(value)
        for key in ("problem_file", "answer_file")
        if (value := values.get(key)) is not None
    ]
    if file_paths:
        content = build_multimodal_content(prompt, file_paths, active_capabilities) or prompt
```

**Validation/error pattern** (lines 84-101):
```python
if output_model is not None:
    try:
        return {step.output_keys[0]: output_model.model_validate_json(response.content)}
    except ValidationError as exc:
        raise SkillRuntimeError(
            f"Step {step.id} output failed {output_model.__name__} validation: {exc}"
        ) from exc

try:
    parsed = json.loads(response.content)
except json.JSONDecodeError as exc:
    raise SkillRuntimeError(f"Step {step.id} returned invalid JSON: {exc}") from exc
```

**Implementation guidance:** register new response models by output key with `response_models={...}` rather than adding skill-specific branches. Prompt files should use `StrictUndefined`; missing context should fail fast.

**Test analog:** `tests/test_runtime.py` lines 81-111 for prompt rendering/provider call; lines 114-144 for missing output failure.

---

### `src/cpho_cli/core/solve.py` (service, file-I/O + request-response)

**Analog:** `src/cpho_cli/core/solve.py`

**Imports pattern** (lines 3-16):
```python
import json
import os
from pathlib import Path

from pydantic import ValidationError

from cpho_cli.core.config import load_config, resolve_model_params, resolve_provider_config
from cpho_cli.core.documents import load_document
from cpho_cli.core.llm import LLMProvider, create_llm_provider
from cpho_cli.core.ocr import OCRProvider, RapidOCRProvider
```

**Runtime orchestration pattern** (lines 87-120):
```python
params = resolve_model_params(config, "solve", provider_name=provider_name)
skill = load_skill(_builtin_solve_skill_dir())
runtime = SkillRuntime(
    handlers={
        "python_tool": python_tool_handler,
        "llm": make_llm_handler(provider, params, skill.root),
    },
    secrets=[provider_config.api_key],
)
try:
    result = runtime.run(
        skill.spec,
        {
            "problem_text": problem_ocr.text,
            "answer_text": answer_ocr.text,
            "ocr_warnings": warnings,
            "problem_path": str(problem_path),
            "answer_path": str(answer_path),
            "problem_file": problem_path,
            "answer_file": answer_path,
        },
    )
```

**Report file pattern** (lines 27-46):
```python
output_dir.mkdir(parents=True, exist_ok=True)
json_path = output_dir / f"{report.problem_id}-report.json"
md_path = output_dir / f"{report.problem_id}-report.md"
json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
md_path.write_text(
    "\n".join(
        [
            f"# Solve Report: {report.problem_id}",
            "",
            "## OCR Warnings",
            *(f"- {warning}" for warning in report.ocr_warnings),
        ]
    ),
    encoding="utf-8",
)
```

**Implementation guidance:** keep `solve_problem(...)` as the CLI-facing service, but change the DAG/report semantics from "new solution" to "official-answer discrepancy review". Keep dry-run as a skill-load-only validation path. Add `auto_confirm` and optional index persistence at the REPL/CLI layer only if the service is kept deterministic; confirmation should not be buried inside `SkillRuntime`.

**Test analog:** `tests/test_solve.py` lines 138-220 for fake OCR/fake provider and exact prompt count; update expected step IDs and prompt markers for the new five-step DAG.

---

### `src/cpho_cli/models/solve.py`, `src/cpho_cli/models/explain.py`, `src/cpho_cli/models/probe.py` (models, transform)

**Analog:** `src/cpho_cli/models/solve.py`

**Pydantic model pattern** (lines 19-51):
```python
class DerivationStep(BaseModel):
    reasoning: str
    expression: str
    official_answer_refs: list[str]

    @field_validator("official_answer_refs")
    @classmethod
    def refs_required(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("DerivationStep requires at least one official answer reference.")
        return value

class SolveReport(BaseModel):
    problem_id: str
    derivation_steps: list[DerivationStep]
    discrepancies: list[Discrepancy] = Field(default_factory=list)
```

**Implementation guidance:** use small `BaseModel` classes with `Field(default_factory=list)` for mutable defaults. For Phase 3 Solve, keep `discrepancies` as free text or a simple item model with text fields; do not introduce a controlled enum. For Explain, model tone outputs and candidate tags separately. For Probe, model turns as ordered user/question/answer records so incremental markdown append is simple.

**Test analog:** `tests/test_solve.py` lines 91-94 validates model invariants; add equivalent tests for any required Explain/Probe fields.

---

### `src/cpho_cli/cli/repl/session.py` (store, event-driven session state)

**Analog:** `src/cpho_cli/cli/repl/session.py`

**Session dataclass pattern** (lines 24-39):
```python
@dataclass
class SessionState:
    workspace_path: Path
    config: AppConfig
    config_path: Path | None = None
    provider_name: str | None = None
    index_path: Path | None = None
    index_meta: IndexMeta | None = None
    last_search_query: str | None = None
    last_search_result_ids: list[str] = field(default_factory=list)
    current_problem_id: str | None = None
```

**Implementation guidance:** add `current_solve_report: SolveReport | None = None` to the dataclass for the hot-path Solve -> Explain/Probe handoff. If adding output config, prefer a small optional field such as `out_dir: Path | None = None`; do not persist full report objects in `session.json`.

**Test analog:** `tests/test_repl_session.py` lines 15-27 checks defaults and mutability; extend it for `current_solve_report is None`.

---

### `src/cpho_cli/cli/repl/persistence.py` (utility, file-I/O)

**Analog:** `src/cpho_cli/cli/repl/persistence.py`

**XDG directory pattern** (lines 13-23):
```python
def config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    path = Path(base) / "cpho"
    path.mkdir(parents=True, exist_ok=True)
    return path

def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    path = Path(base) / "cpho"
    path.mkdir(parents=True, exist_ok=True)
    return path
```

**Atomic JSON pattern** (lines 39-53):
```python
path = session_path()
tmp = path.with_suffix(".json.tmp")
payload = {
    "workspace_path": str(session.workspace_path),
    "last_search_query": session.last_search_query,
    "last_search_result_ids": list(session.last_search_result_ids),
}
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
tmp.replace(path)
```

**Implementation guidance:** add a `data_dir()` helper using `XDG_DATA_HOME` or `~/.local/share`, then build default markdown export roots as `data_dir() / "outputs" / workspace_hash / skill / filename`. Reuse `mkdir(parents=True, exist_ok=True)` and atomic write for finalized files; use append mode only for Probe's per-turn crash-resilient log.

**Test analog:** `tests/test_repl_persistence.py` lines 11-18 for XDG isolation and lines 26-45 for JSON allowlist/no temp file.

---

### `src/cpho_cli/cli/repl/display.py` (utility, request-response + progress)

**Analog:** `src/cpho_cli/cli/repl/display.py`

**Width-aware table pattern** (lines 37-54):
```python
def render_table(
    headers: list[str],
    rows: list[list[str]],
    max_widths: list[int] | None = None,
) -> str:
    all_rows = [headers, *rows]
    widths = [
        max(_width(str(row[i])) for row in all_rows)
        for i in range(len(headers))
    ]
```

**TTY progress fallback pattern** (lines 101-166):
```python
def make_index_progress_printer():
    """Return a callable for build_index on_progress.

    Maintains a multi-line status panel using ANSI cursor movement.
    Falls back to sequential output when stdout is not a TTY.
    """
    tty = sys.stdout.isatty()
    seq = tty

    def printer(event: dict) -> None:
        nonlocal seq
        phase = event.get("phase", "")
        ...
        if tty:
            if seq:
                sys.stdout.write("\033[F\033[K" * 3)
            sys.stdout.write("\n".join(lines) + "\033[K\n")
            sys.stdout.flush()
        else:
            for line in lines:
                print(line)
```

**Implementation guidance:** replace or complement ANSI progress with rich `Live`/`Spinner` helpers while preserving non-TTY sequential output. Put `confirm_list(items, allow_edit=True, allow_append=True)` here so Solve discrepancy confirmation and Explain tag confirmation share one implementation. Keep display helpers pure and easy to capsys-test.

**Test analog:** `tests/test_repl_display.py` lines 10-23 for display string behavior; add non-TTY progress and confirm-list tests using monkeypatched input/prompt session.

---

### `src/cpho_cli/cli/repl/commands/builtin_skills.py` (controller, request-response + event-driven)

**Analogs:** `src/cpho_cli/cli/repl/commands/search.py`, `workspace.py`, existing `builtin_skills.py`

**Command registration pattern** (existing `builtin_skills.py` lines 14-25):
```python
def register(registry: dict[str, Command]) -> None:
    for name, help_text in {
        "/explain": "讲解当前题目（Phase 3）",
        "/quiz": "基于当前题目生成追问（Phase 3）",
    }.items():
        registry[name] = Command(
            name=name,
            help=help_text,
            usage=name,
            handler=do_phase3_stub,
            category="技能",
        )
```

**Parser + session mutation pattern** (`search.py` lines 186-218):
```python
async def do_show(session: SessionState, args: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="/show", add_help=False)
    parser.add_argument("ref", nargs="?")
    parser.add_argument("--full", action="store_true")
    ...
    session.current_problem_id = entry.problem_id
    detail = _render_detail(session, entry, full=ns.full)
```

**Interactive prompt pattern** (`workspace.py` lines 35-40):
```python
async def _confirm_index_run(session: SessionState, prompt_text: str) -> bool:
    ps = session.prompt_session
    if ps is None:
        return input(prompt_text).strip().lower() in {"y", "yes"}
    result = await ps.prompt_async(prompt_text)  # type: ignore[union-attr]
    return result.strip().lower() in {"y", "yes"}
```

**Implementation guidance:** implement `/solve`, `/explain`, and `/probe` as async handlers in this file or split into small helper functions if it grows. Use `argparse.ArgumentParser(..., add_help=False)` and `display.error(...)` on `SystemExit`, matching `search.py`. Use `session.current_problem_id` by default and require explicit problem id only when no current problem exists. For Explain multi-tone, use `asyncio.gather` in the command handler, one independent `SkillRuntime.run()` per tone. For Follow-up, loop on `session.prompt_session.prompt_async("cpho:followup> ")`, exiting on `/exit` or two empty lines.

**Test analog:** `tests/test_repl_builtin_commands.py` lines 28-36 for command registration/output; replace placeholder expectations with `/solve`, `/explain`, `/probe` behavior tests. Use `tests/test_repl_runtime.py` lines 14-24 `FakePromptSession` for follow-up and confirm flows.

---

### `src/cpho_cli/builtin_skills/solve/*` (skill config/docs/prompts, DAG transform)

**Analog:** `src/cpho_cli/builtin_skills/solve/skill.yml`

**Current DAG pattern** (lines 1-44):
```yaml
name: solve
inputs:
  - problem_text
  - answer_text
  - ocr_warnings
  - problem_file
  - answer_file
outputs:
  - solve_report
steps:
  - id: extract_problem_answer
    kind: python_tool
    input_keys: [problem_text, answer_text]
    output_keys: [raw_problem, raw_answer]
  - id: normalize_problem
    kind: llm
    input_keys: [raw_problem, problem_file, answer_file]
    output_keys: [normalized_problem]
    prompt_template: normalize.md.j2
```

**Prompt style pattern** (`prompts/final_report.md.j2` lines 1-16):
```jinja
Normalized problem:
{{ normalized_problem }}

Derivations:
{{ subproblem_derivations }}

Assemble final SolveReport JSON. Every derivation step must cite official_answer_refs.
```

**Implementation guidance:** rewrite Solve DAG to the locked five-step review shape: `extract_official_steps -> check_each_step -> classify_error_types -> propose_discrepancies -> assemble_solve_report`. Keep `problem_file` and `answer_file` in LLM input keys so multimodal content still flows through `make_llm_handler`. Prompts must ask for strict JSON with exactly the configured output key.

**Test analog:** `tests/test_solve.py` lines 76-88 asserts exact built-in step IDs; update it to the new five IDs. `tests/test_skills.py` lines 64-80 renders every built-in prompt with strict undefined variables.

---

### `src/cpho_cli/builtin_skills/explain/*` (new skill config/docs/prompts, DAG transform)

**Analog:** `src/cpho_cli/builtin_skills/solve/*`

**Skill folder loader contract** (`src/cpho_cli/core/skills.py` lines 32-61):
```python
def load_skill(skill_dir: Path) -> LoadedSkill:
    readme_path = skill_dir / "SKILL.md"
    spec_path = skill_dir / "skill.yml"
    if not readme_path.exists() or not spec_path.exists():
        raise SkillDefinitionError("Skill folder must contain SKILL.md and skill.yml.")
    ...
    for step in spec.steps:
        if step.prompt_template:
            prompt_path = skill_dir / "prompts" / step.prompt_template
            if not _inside(prompt_path, skill_dir / "prompts"):
                raise SkillDefinitionError("Prompt template path escapes skill prompts directory.")
```

**Implementation guidance:** create a normal skill folder: `SKILL.md`, `skill.yml`, and `prompts/*.md.j2`. Do not encode tone fan-out in `skill.yml`; the REPL Explain handler runs the same skill per tone with different initial blackboard values. Keep the two-stage model as two LLM steps: stage one main explanation/clearer derivation, stage two sentence-level explanation dependent on stage one. Add a tag extraction output if it is part of the same skill, then confirm before `add_problem_tags(skill_name="explain", ...)`.

**Test analog:** `tests/test_skills.py` lines 31-44 for load contract and path traversal; add `test_builtin_explain_skill_prompt_templates_exist_and_render`.

---

### `src/cpho_cli/builtin_skills/probe/*` (new skill config/docs/prompts, event-driven conversation)

**Analog:** `src/cpho_cli/builtin_skills/solve/*` plus REPL prompt loop

**Implementation guidance:** use a skill folder for the per-turn LLM prompt, but keep the loop, max-round check, `/exit`, two-empty-lines exit, and incremental markdown append in the REPL command layer. The skill should accept current problem context, optional `current_solve_report`, previous turns, and the latest user answer, then output the next question/answer payload.

**Test analog:** use `tests/test_repl_runtime.py` lines 14-24 `FakePromptSession` to simulate multiple prompt inputs and EOF/exit.

---

### `pyproject.toml` (config, dependency config)

**Analog:** `pyproject.toml`

**Dependency list pattern** (lines 7-18):
```toml
dependencies = [
  "httpx>=0.27",
  "jinja2>=3.1",
  "onnxruntime>=1.18",
  "pydantic>=2.7",
  "pymupdf>=1.24",
  "prompt_toolkit>=3.0.50",
  "pyyaml>=6.0",
  "rapidocr>=3.0",
  "typer>=0.12",
  "wcwidth>=0.2.13",
]
```

**Implementation guidance:** add `rich>=13.0` in alphabetical-ish dependency style near `rapidocr`/`typer`. No new dependency is needed for `asyncio`.

---

## Shared Patterns

### Skill Runtime Boundaries

**Source:** `src/cpho_cli/core/runtime.py` lines 75-127

**Apply to:** Solve, Explain, Probe skill execution

```python
def run(self, spec: SkillSpec, initial_blackboard: Mapping[str, Any]) -> SkillRunResult:
    blackboard: dict[str, Any] = dict(initial_blackboard)
    statuses: dict[str, str] = {}
    for step in self._order(spec):
        missing = [key for key in step.input_keys if key not in blackboard]
        if missing:
            raise SkillRuntimeError(f"Step {step.id} missing input keys: {missing}")
        handler = self.handlers.get(step.kind)
        if handler is None:
            raise SkillRuntimeError(f"No handler registered for step kind: {step.kind}")
        ...
        blackboard.update(outputs)
```

Phase 3 must not add fan-out/fan-in to `SkillRuntime`; Explain tone concurrency belongs in the command/service caller via `asyncio.gather`.

### Index Skill-Tag Writes

**Source:** `src/cpho_cli/core/index/api.py` lines 128-162

**Apply to:** Solve optional persistence, Explain confirmed tag writeback

```python
def _make_user_tag_entry(
    workspace_root: Path,
    tags: list[str],
    *,
    skill_name: str,
    reasoning: str,
) -> UserTagEntry:
    canonical, unverified = _classify_user_tags(workspace_root, tags)
    return UserTagEntry(
        tags=tags,
        canonical_tags=canonical,
        unverified_tags=unverified,
        skill_name=skill_name,
        timestamp=datetime.now(timezone.utc),
        reasoning_snippet=reasoning,
    )
```

Use `add_problem_tags(...)`, not direct index mutation. `skill_name` should be `"solve"` or `"explain"` and `reasoning` should be a short provenance snippet from the confirmed output.

### REPL Error Handling

**Source:** `src/cpho_cli/cli/repl/app.py` lines 85-103

**Apply to:** All new REPL skill handlers

```python
async def dispatch(self, line: str) -> None:
    try:
        parts = shlex.split(line)
    except ValueError as exc:
        display.error(f"输入解析失败: {exc}")
        return
    ...
    try:
        await command.handler(self.session, parts[1:])
    except KeyboardInterrupt:
        display.warn("中断")
    except Exception as exc:
        _logger().error("handler failed\n%s", traceback.format_exc())
        display.error(str(exc))
```

Handlers should catch expected user/config/index errors and print `display.error(...)`; unexpected errors can bubble to the dispatcher.

### Current Problem Context

**Source:** `src/cpho_cli/cli/repl/commands/search.py` lines 209-218

**Apply to:** `/solve`, `/explain`, `/probe`

```python
entry = get_problem_entry(session.workspace_path, problem_id)
if entry is None:
    display.error(f"未找到题目: {problem_id}")
    return
session.current_problem_id = entry.problem_id
```

Use indexed problem metadata and OCR cache where possible. If Explain/Probe sees no `session.current_solve_report`, warn but do not block, matching Phase 3 D-16.

### Real Workspace Shape

**Source:** `AGENTS.md` lines 67-82 and `tests/test_phase023_acceptance.py` lines 162-210

**Apply to:** acceptance tests and output naming

```python
pdf = _first_existing(sorted(REAL_WORKSPACE.rglob("*.pdf")))
image = _first_existing(
    sorted(
        chain(
            REAL_WORKSPACE.rglob("*.jpg"),
            REAL_WORKSPACE.rglob("*.jpeg"),
            REAL_WORKSPACE.rglob("*.png"),
        )
    )
)
...
assert any("物理竞赛资料" not in str(path) for path in copied), "real samples copied; originals untouched"
```

I sampled `/Users/ericzhang/Desktop/物理竞赛资料`; it contains nested Chinese-named folders and PDF-heavy answer/problem files such as `芝麻物理第四届联考/第四届芝麻物理联考试卷参考答案.pdf`. Tests should copy samples into temp dirs and never mutate originals.

## Test Analogs

| Planned Test File | Copy Pattern From | Concrete Guidance |
|---|---|---|
| `tests/test_solve.py` | lines 14-47, 138-220 | Fake provider returns one JSON object per DAG step; assert prompt count, prompt markers, final `SolveReport` validation, and markdown/json output. |
| `tests/test_runtime.py` | lines 81-144 | Use temp skill prompt dirs and fake providers to test handler JSON parsing and missing output errors. |
| `tests/test_llm.py` | lines 13-47, 110-123 | Use `httpx.MockTransport` to assert provider payloads and secret redaction; add streaming payload/chunk tests. |
| `tests/test_repl_builtin_commands.py` | lines 15-36 | Register commands into an empty registry and call async handlers with fake sessions. Replace placeholder assertions. |
| `tests/test_repl_runtime.py` | lines 14-24, 58-65 | Reuse `FakePromptSession` for follow-up/probe prompt flows and session persistence checks. |
| `tests/test_repl_display.py` | lines 10-23 | Assert rendered text behavior, not terminal control sequences. Add rich/non-TTY fallback tests. |
| `tests/test_repl_persistence.py` | lines 11-18, 26-45 | Monkeypatch XDG env vars and assert generated paths/atomic writes. |
| `tests/test_index_api.py` | lines 272-356 | Seed index with `_make_entry`, call tag APIs, assert provenance/classification/path traversal behavior. |
| `tests/test_skills.py` | lines 64-80 | Load each built-in skill and render every prompt with all declared input keys. |
| `tests/test_phase03_acceptance.py` | `tests/test_phase023_acceptance.py` lines 82-210 | Add source-shape assertions plus copied-real-workspace smoke tests. |

## No Analog Found

| File/Feature | Role | Data Flow | Reason |
|---|---|---|---|
| `LLMProvider.stream()` exact behavior | service | streaming | No existing streaming provider method exists; copy `complete()` payload/retry/error conventions and add new stream-specific tests. |

## Metadata

**Project instructions read:** `AGENTS.md`
**Local project skills:** none found under `.codex/skills/` or `.agents/skills/`
**Phase context read:** `.planning/phases/03-skill-cross-cutting-core-skills/03-CONTEXT.md`
**Research file:** no `03-RESEARCH.md` found in the phase directory
**Analog search scope:** `src/cpho_cli`, `tests`, `src/cpho_cli/builtin_skills/solve`, `pyproject.toml`, real workspace sample listing
**Files scanned:** 138 files under `src/cpho_cli` and `tests`
**Pattern extraction date:** 2026-05-26
