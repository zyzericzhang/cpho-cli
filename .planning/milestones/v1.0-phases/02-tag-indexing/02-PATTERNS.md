# Phase 2: Tag Indexing — Pattern Map

**Mapped:** 2026-05-23
**Files analyzed:** 14 new + 4 modified (per RESEARCH.md §1, §2, §7, §8)
**Analogs found:** 18 / 18 — every Phase 2 file has at least one strong Phase-1 analog
**Confidence:** HIGH — Phase 1 establishes uniform conventions (StrictModel,芯-壳, Provider Protocol, JSONL append-with-redaction, Typer command shell) that Phase 2 must mirror exactly.

---

## File Classification

Grouped by RESEARCH.md plan waves. Match Quality codes:
- **exact** — same role, same data flow as analog
- **role-match** — same role, different data flow (still copy structure)
- **partial** — analog gives orientation; novel territory

### Wave 1 (parallel, no LLM)

| New / Modified File | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|
| `src/cpho_cli/models/index.py` (NEW) | model | Pydantic schema (JSON-mode + storage) | `src/cpho_cli/models/solve.py`, `src/cpho_cli/models/config.py` (StrictModel) | exact |
| `src/cpho_cli/core/index/__init__.py` (NEW) | core public API | re-export surface | `src/cpho_cli/models/__init__.py` (empty), `src/cpho_cli/core/__init__.py` (empty); no current re-export pattern | partial — Phase 2 introduces convention |
| `src/cpho_cli/core/index/storage.py` (NEW) | service | file I/O (JSONL read/write, atomic rename) | `src/cpho_cli/core/runtime.py:59-66` (`_write_trace` JSONL append); `src/cpho_cli/core/solve.py:25-44` (`_write_report` atomic-ish write) | role-match |
| `src/cpho_cli/core/index/vocabulary.py` (NEW) | service | YAML load + merge + normalization | `src/cpho_cli/core/config.py:30-47` (`load_config` YAML + `model_validate`); `src/cpho_cli/core/skills.py:32-61` (`load_skill` YAML + `SkillSpec.model_validate`) | exact |
| `src/cpho_cli/core/index/hashing.py` (NEW) | utility | pure deterministic transforms (sha256) | None — new territory. Mirror `core/config.py`'s small-pure-function layout. | partial |
| `src/cpho_cli/vocabulary/builtin.yml` (NEW) | config / data | static YAML data | `src/cpho_cli/builtin_skills/solve/skill.yml` (packaged YAML inside the wheel) | role-match |
| `tests/test_index_models.py` (NEW) | test | unit (schema) | `tests/test_solve.py:28-62`, `tests/test_config.py:137-142` (StrictModel `extra="forbid"` test) | exact |
| `tests/test_index_vocabulary.py` (NEW) | test | unit (file IO) | `tests/test_config.py` (entire file — tmp_path + YAML strings) | exact |
| `tests/test_index_hashing.py` (NEW) | test | unit (pure) | `tests/test_runtime.py:60-62` (1-liner deterministic-pure-fn pattern) | role-match |

### Wave 2 (depends on Wave 1)

| New / Modified File | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|
| `src/cpho_cli/core/index/ocr_cache.py` (NEW) | service | wraps OCRProvider with disk cache | `src/cpho_cli/core/ocr.py:35-65` (`RapidOCRProvider` — class wraps engine) | role-match |
| `src/cpho_cli/core/index/tagging.py` (NEW) | service | LLM call + trace write | `src/cpho_cli/core/solve.py:79-111` (LLM provider call + response_model + ValidationError); `src/cpho_cli/core/runtime.py:59-66, 96-105` (TraceRecord append) | exact |
| `src/cpho_cli/core/index/prompts/MANIFEST.yml` (NEW) | config | static YAML version pin | `src/cpho_cli/builtin_skills/solve/skill.yml` | role-match |
| `src/cpho_cli/core/index/prompts/tag_refinement.md.j2` (NEW) | template | Jinja2 prompt | `src/cpho_cli/builtin_skills/solve/prompts/*.md.j2` | exact |
| `tests/test_index_ocr_upgrade.py` (NEW) | test | unit (fingerprint diff) | `tests/test_runtime.py:21-34` (fake handler + assert trace) | role-match |
| `tests/test_index_tagging.py` (NEW) | test | unit (fake LLM) | `tests/test_solve.py:65-127` (`FakeProvider` + `FakeOCR` pattern) | exact |
| `tests/test_index_determinism.py` (NEW) | test | integration (re-run same input) | `tests/test_solve.py:65-127` | role-match |

### Wave 3 (depends on Wave 1 + 2)

| New / Modified File | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|
| `src/cpho_cli/core/index/builder.py` (NEW) | core orchestrator | pipeline (discover → hash → OCR → LLM → write) | `src/cpho_cli/core/solve.py:47-111` (`solve_problem`); `src/cpho_cli/core/eval.py:33-81` (`run_eval` — multi-case loop + stats counters) | exact |
| `src/cpho_cli/cli/app.py` (MODIFY — add `index` command) | CLI | Typer subcommand | `src/cpho_cli/cli/app.py:13-42` (`solve` command), `:45-72` (`eval_command`) | exact |
| `src/cpho_cli/models/config.py` (MODIFY — extend) | model | add `IndexConfig`-style nested field on `AppConfig` | `src/cpho_cli/models/config.py:35-46` (existing `SkillConfig` + `AppConfig.skills` dict) | exact |
| `src/cpho_cli/core/config.py` (MODIFY — IF needed) | service | (likely no change — `resolve_model_params(config, "index")` already works generically) | `src/cpho_cli/core/config.py:115-124` | exact |
| `tests/test_index_cli.py` (NEW) | test | CLI smoke via CliRunner | `tests/test_cli.py` (entire file) | exact |
| `tests/test_index_api.py` (NEW) | test | unit (query/get/related) | `tests/test_workspace.py` (entire file — tmp_path workspace fixtures) | role-match |
| `tests/test_index_stats.py` (NEW) | test | unit (counter aggregation) | `tests/test_eval.py` (stat counts assertion) | exact |
| `tests/fixtures/golden_index_workspace/...` (NEW) | fixture | static test fixture | `golden_tests/` (Phase 1 directory layout) | role-match |

---

## Pattern Assignments

### Wave 1

---

#### `src/cpho_cli/models/index.py` (model, Pydantic schema)

**Analog A:** `src/cpho_cli/models/solve.py` (data-shape, Field defaults, no extra config)
**Analog B:** `src/cpho_cli/models/config.py` (`StrictModel` base + `ConfigDict(extra="forbid")`)

**Imports + base-class pattern** (must mirror `models/config.py:1-7`):

```python
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
```

**Decision:** Do **not** redefine `StrictModel` in `models/index.py`. Import the existing one: `from cpho_cli.models.config import StrictModel`. RESEARCH.md §1 already specifies this.

**Field-default pattern** (mirror `models/solve.py:38-46`):

```python
class SolveReport(BaseModel):
    problem_id: str
    derivation_steps: list[DerivationStep]
    discrepancies: list[Discrepancy] = Field(default_factory=list)
    ocr_warnings: list[str] = Field(default_factory=list)
    physics_model_tags: list[str] = Field(default_factory=list)
```

→ Apply to every list field on `IndexEntry`, `UserNotebookEntry`, `CandidateTag`. Use `Field(default_factory=list)` not `= []` (mutable default).

**Enum pattern** (no precedent in Phase 1 — Phase 2 introduces). Use stdlib `str, Enum` so Pydantic serializes string value:

```python
from enum import Enum
class TagCategory(str, Enum):
    PHYSICS_MODEL = "physics_model"
    ...
```

**Validator pattern** (mirror `models/solve.py:24-28` — only add when a non-default constraint is real):

```python
@field_validator("official_answer_refs")
@classmethod
def refs_required(cls, value: list[str]) -> list[str]:
    if not value:
        raise ValueError("...")
    return value
```

→ Apply sparingly. Per AGENTS.md §2 do not add validators for theoretical constraints. Likely only needed on `CanonicalTag.internal_id` (snake_case regex check) if Plan 02-01 decides to enforce.

**Divergence notes:**
- RESEARCH.md §1 calls every new model `StrictModel`. `models/solve.py` uses plain `BaseModel` (Phase 1 quirk — should not be replicated). **Phase 2 must use `StrictModel` for all new models** per AGENTS.md "Pydantic 严格模式" and RESEARCH.md user_constraints line 78.
- `IndexEntry.fingerprint` is a nested model, not a primitive. Pydantic 2 handles nested validation automatically; no additional config needed.

---

#### `src/cpho_cli/core/index/storage.py` (service, JSONL I/O)

**Analog A:** `src/cpho_cli/core/runtime.py:59-66` — JSONL append with parent-mkdir and secret redaction.
**Analog B:** `src/cpho_cli/core/solve.py:25-44` — JSON write with `model_dump_json(indent=2)`.

**JSONL append pattern** (`runtime.py:59-66`):

```python
def _write_trace(self, record: TraceRecord) -> None:
    if self.trace_path is None:
        return
    self.trace_path.parent.mkdir(parents=True, exist_ok=True)
    text = record.model_dump_json()
    text = redact_secrets(text, self.secrets)
    with self.trace_path.open("a", encoding="utf-8") as handle:
        handle.write(text + "\n")
```

→ Reuse exactly for `append_index_entry`. Note: `model_dump_json()` (no indent) for JSONL, `encoding="utf-8"` mandatory, parent-mkdir before write.

**Full-rewrite pattern** (RESEARCH.md §2 says re-write the whole file each run because <1000 entries):

```python
# storage.py
def write_index(path: Path, entries: list[IndexEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(entry.model_dump_json() + "\n")
    tmp.replace(path)  # atomic on POSIX; required by RESEARCH.md §13 R5
```

The atomic `.tmp + replace` is **new in Phase 2** (no Phase 1 analog — solve.py writes report non-atomically). Per RESEARCH.md §13 R5 this is mandatory.

**Read pattern** (mirror `core/solve.py:114-116`):

```python
def load_index(workspace_root: Path) -> list[IndexEntry]:
    path = workspace_root / ".cpho" / "index.jsonl"
    if not path.exists():
        raise IndexNotFoundError(...)
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(IndexEntry.model_validate_json(line))
    return entries
```

Use `model_validate_json` on a per-line basis (Phase 1 uses this on solve.py:106).

**Divergence:** Phase 1 has **no JSONL reader** (only writer). Phase 2 must add one. Pattern is straightforward stdlib; no analog needed.

---

#### `src/cpho_cli/core/index/vocabulary.py` (service, YAML loader + merge)

**Analog A:** `src/cpho_cli/core/config.py:30-47` (`load_config`) — YAML safe_load + Pydantic validate + ConfigError-style exception.
**Analog B:** `src/cpho_cli/core/skills.py:32-61` (`load_skill`) — multi-file YAML load + validation.
**Analog C:** `src/cpho_cli/core/config.py:106-124` (`_merge_params` + `resolve_model_params`) — three-tier merge pattern.

**YAML load + validate** (must mirror `config.py:35-47` exactly):

```python
def load_yaml_vocab(path: Path, optional: bool = False) -> Vocabulary | None:
    if not path.exists():
        if optional:
            return None
        raise VocabularyError(f"Vocabulary file not found: {path}")
    try:
        raw_text = path.read_text(encoding="utf-8")
        raw = yaml.safe_load(raw_text) or {}
        if not isinstance(raw, dict):
            raise VocabularyError("Vocabulary file must contain a YAML mapping.")
        return Vocabulary.model_validate(raw)
    except ValidationError as exc:
        raise VocabularyError(f"Invalid vocabulary: {exc}") from exc
    except yaml.YAMLError as exc:
        raise VocabularyError(f"Invalid YAML: {exc}") from exc
```

This is literally `config.py:35-47` with `AppConfig` → `Vocabulary` and `ConfigError` → `VocabularyError`. **Copy the structure verbatim.**

**Three-tier merge** (mirror `config.py:106-124` `_merge_params` + `resolve_model_params`):

```python
# config.py pattern:
def _merge_params(base: ModelParams, override: ModelParams | None) -> ModelParams:
    if override is None: return base
    data = base.model_dump()
    for key, value in override.model_dump(exclude_none=True).items():
        data[key] = value
    return ModelParams.model_validate(data)

def resolve_model_params(config, skill_name, cli_overrides=None) -> ModelParams:
    params = config.model
    skill = config.skills.get(skill_name)
    if skill is not None:
        params = _merge_params(params, skill.model)
    return _merge_params(params, cli_overrides)
```

→ Apply the same chain to `load_merged_vocabulary(workspace_root)`: load builtin → merge workspace → merge private (per RESEARCH.md §5). Last layer wins on `internal_id` collision.

**Exception pattern** (mirror `config.py:16-17`):

```python
class VocabularyError(ValueError):
    """Raised when vocabulary cannot be loaded or resolved."""
```

Phase 1 uses `ValueError` subclass for config errors and `RuntimeError` for solve errors. RESEARCH.md §7 specifies `VocabularyError(IndexError)` where `IndexError(RuntimeError)`. **Use RESEARCH.md's hierarchy** — `IndexError(RuntimeError)` matches `SolveError(RuntimeError)` shape.

**Alias normalization** — no Phase 1 analog. Pure stdlib (`unicodedata.normalize("NFKC", ...)` + `casefold()` + regex). RESEARCH.md §5 has the implementation.

**Divergence notes:**
- Phase 1's `ConfigError` extends `ValueError`. Phase 2's `IndexError` extends `RuntimeError`. This is intentional per RESEARCH.md §7 — config errors are user-input errors (ValueError), runtime errors are operational (RuntimeError, like `SolveError`).
- `_legacy_*` paths in `config.py:54-60` are NOT a pattern to copy. They are tech debt for backwards-compat; Phase 2 vocabulary has no legacy.

---

#### `src/cpho_cli/core/index/hashing.py` (utility, pure deterministic)

**No close analog.** Phase 1 has no hashing module. Mirror the small-pure-function layout of `core/config.py` (top-level functions, no class).

**Pattern shape**:

```python
from __future__ import annotations
import hashlib
import json
from pathlib import Path

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def sha256_json(obj: object) -> str:
    text = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
```

**`ensure_ascii=False`** — match RESEARCH.md §2 (vocab YAML stores Chinese inline); also matches `core/solve.py:116` (`json.dumps(data, ensure_ascii=False)`).

**Determinism check pattern**: tests should assert byte-identical output across two calls. Mirror `tests/test_runtime.py:60-62`:

```python
def test_trace_redacts_secret() -> None:
    assert "sk-secret" not in redact_secrets("token sk-secret", ["sk-secret"])
```

→ One-line pure-function assertions are the project style for hashing/normalization tests.

---

#### `src/cpho_cli/vocabulary/builtin.yml` (config / data)

**Analog:** `src/cpho_cli/builtin_skills/solve/skill.yml` — packaged YAML data shipped in the wheel.

Key implication: `builtin.yml` lives **under `src/cpho_cli/`** so it is included in the wheel. Located via:

```python
def _builtin_vocab_path() -> Path:
    return Path(__file__).resolve().parents[1] / "vocabulary" / "builtin.yml"
```

This mirrors `core/solve.py:21-22`:

```python
def _builtin_solve_skill_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "builtin_skills" / "solve"
```

**Verify wheel inclusion**: `pyproject.toml` must include `vocabulary/*.yml` in package-data. Plan should check current pyproject configuration for `[tool.hatch.build.targets.wheel]` or equivalent. If `builtin_skills/` is currently bundled, the same mechanism extends to `vocabulary/`.

**Content** — RESEARCH.md §6 lists all 42 entries with `internal_id`, `display_zh`, `category`, sample `aliases`. Plan 02-06 owns content authorship + an R8 review checkpoint.

---

### Wave 2

---

#### `src/cpho_cli/core/index/ocr_cache.py` (service, OCR cache wrapper)

**Analog:** `src/cpho_cli/core/ocr.py:35-65` (`RapidOCRProvider` — class that wraps an engine and implements the `OCRProvider` Protocol).

**Wrapper class shape** (mirror `ocr.py:35-65`):

```python
class CachedOCRProvider:
    """Wraps an OCRProvider with file-content-addressed disk cache."""

    def __init__(
        self,
        inner: OCRProvider,
        cache_dir: Path,
        engine_name: str,
        engine_version: str,
    ) -> None:
        self.inner = inner
        self.cache_dir = cache_dir
        self.engine_name = engine_name
        self.engine_version = engine_version

    def extract(self, document: DocumentInput) -> OCRResult:
        # implementation per RESEARCH.md §10
```

**Critical contract match**: `CachedOCRProvider.extract` must return `OCRResult` (same return type as `OCRProvider` Protocol on `core/ocr.py:10-12`). RESEARCH.md §10 sketches `tuple[OCRResult, bool]` for cache-hit reporting; **prefer adding the hit count to a separate side channel** (counter passed via constructor, or a `last_was_cached` attribute) rather than changing the Protocol return type. This keeps `solve.py`-style `ocr_provider` injection compatible.

**OCRResult round-trip** — `OCRResult` is a Pydantic `BaseModel` (`models/ocr.py:19`). Write with `model_dump_json(indent=2)`, read with `OCRResult.model_validate_json(...)`. Same round-trip Phase 1 uses for `SolveReport` (`solve.py:29` and `solve.py:106`).

**Divergence note (anti-pattern):** Phase 1 `solve.py:70-72` instantiates `RapidOCRProvider()` directly with no cache. **Phase 2 must not "fix" solve.py to use the cache** — RESEARCH.md §13 R4 explicitly defers solve cache integration to a later phase. Phase 2 index uses `CachedOCRProvider(RapidOCRProvider(), ...)` only inside `core/index/builder.py`.

---

#### `src/cpho_cli/core/index/tagging.py` (service, LLM call + trace)

**Analog A:** `src/cpho_cli/core/solve.py:79-111` — LLMProvider invocation with `response_model` + ValidationError handling.
**Analog B:** `src/cpho_cli/core/runtime.py:59-66, 96-118` — TraceRecord write with secret redaction.

**LLM call shape** (must mirror `solve.py:79-111`):

```python
provider = llm_provider or OpenRouterProvider(
    api_key=provider_config.api_key,
    base_url=provider_config.base_url,
)
params = resolve_model_params(config, "index")  # NB: skill_name="index"
response = provider.complete(
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": rendered_user_prompt},
    ],
    params=params,
    response_model=TagRefinementOutput,
)
try:
    output = TagRefinementOutput.model_validate_json(response.content)
except ValidationError as exc:
    raise IndexError(f"LLM response failed TagRefinementOutput validation: {exc}") from exc
```

**Critical reuse:** `LLMProvider.complete` with `response_model=` triggers OpenRouter strict JSON schema mode (`llm.py:58-67`). This is the **only** structured-output path; never parse free-text. Aligns with AGENTS.md "JSON mode + schema：LLM 结构化输出走 `response_format=json_schema`，不走正则兜底".

**Provider injection** — accept `llm_provider: LLMProvider | None = None` like `solve.py:55-56`. This is the testing seam for fake providers (see `tests/test_solve.py:65-127`).

**Trace write pattern** (mirror `runtime.py:59-66`):

Per RESEARCH.md §4 and §9 — **do NOT instantiate `SkillRuntime`**. Phase 2 is not a registered skill (D-01). Copy the 6-line append helper:

```python
def _append_trace(trace_path: Path, record: TraceRecord, secrets: list[str]) -> None:
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    text = record.model_dump_json()
    text = redact_secrets(text, secrets)
    with trace_path.open("a", encoding="utf-8") as handle:
        handle.write(text + "\n")
```

`TraceRecord` is reused as-is from `models/runtime.py:9-17`. `redact_secrets` is imported from `core/runtime.py:20-25` (`from cpho_cli.core.runtime import redact_secrets`).

**TraceRecord field shape** (must match `models/runtime.py:9-17`):

```python
TraceRecord(
    step_id=f"tag_{problem_id}",
    status="passed",  # or "failed"
    input_keys=["ocr_text", "solve_report", f"vocabulary_{vocab.version}"],
    output_keys=["tag_refinement"],
    retry_count=0,
    started_at=started,
    finished_at=datetime.now(timezone.utc),
    error=None,
)
```

**Datetime pattern** (mirror `runtime.py:85, 103`): always `datetime.now(timezone.utc)`. Never naive datetimes.

**Jinja2 template loading** — Phase 1 has Jinja2 templates under `builtin_skills/solve/prompts/*.md.j2` but does not actually render them in code (Phase 1 inlines the prompt at `solve.py:88-100`). Phase 2 will be **the first** to load and render Jinja2:

```python
from jinja2 import Environment, FileSystemLoader, StrictUndefined

env = Environment(
    loader=FileSystemLoader(str(Path(__file__).parent / "prompts")),
    undefined=StrictUndefined,  # fail loudly on undefined vars
    autoescape=False,
)
template = env.get_template("tag_refinement.md.j2")
rendered = template.render(problem_text=..., solve_report_tags=..., vocabulary=...)
```

Use `StrictUndefined` to fail fast on missing context (AGENTS.md §2 + D-08 "fail fast").

**Anti-pattern from Phase 1:** `solve.py` builds the prompt by f-string at lines 88-100 (`f"Problem OCR text:\n{problem_ocr.text}\n\n..."`). This is a regression vs. D-11 "模板引擎 **Jinja2**". **Phase 2 must not follow this f-string pattern.** Use Jinja2 templates per D-11 and RESEARCH.md §4.

---

#### `src/cpho_cli/core/index/prompts/tag_refinement.md.j2` (Jinja2 template)

**Analog:** `src/cpho_cli/builtin_skills/solve/prompts/derive.md.j2` (filename, extension, location convention).

The directory layout under `core/index/prompts/` matches the `builtin_skills/solve/prompts/` convention. RESEARCH.md §4 explicitly recommends this. Content per RESEARCH.md §4 — vocabulary list injected as enum, ask LLM to choose from internal_ids only.

---

#### `src/cpho_cli/core/index/prompts/MANIFEST.yml`

**Analog:** `src/cpho_cli/builtin_skills/solve/skill.yml` (top-level YAML metadata bundled with the package).

Minimal shape:

```yaml
version: "v1"
templates:
  tag_refinement: tag_refinement.md.j2
```

The `version` field flows into `SemanticFingerprint.tag_prompt_version` (RESEARCH.md §3 layer 2). Plan 02-04 must wire the read.

---

### Wave 3

---

#### `src/cpho_cli/core/index/builder.py` (orchestrator)

**Analog A:** `src/cpho_cli/core/solve.py:47-111` — single-problem pipeline orchestration.
**Analog B:** `src/cpho_cli/core/eval.py:33-81` — multi-case loop with stats counters.

**Top-level orchestration** (combines `solve_problem` shape with `run_eval`'s loop + counter pattern):

From `eval.py:40-63`:

```python
def run_eval(...) -> EvalRunResult:
    cases = load_eval_cases(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    passed = failed = skipped = 0
    for case in cases:
        if dry_run or ...:
            skipped += 1
            rows.append({"id": case.id, "status": "SKIPPED", ...})
            continue
        result = solve_problem(...)
        ...
        passed += 1
    total = len(cases)
    failed = total - passed - skipped
    return EvalRunResult(total=total, passed=passed, failed=failed, ...)
```

→ `build_index` mirrors this: discover via `workspace.discover_workspace`, loop pairs, increment per-action counters (`file_changed / ocr_reused / ocr_regenerated / tags_regenerated / tags_skipped / refinement_only` — all defined on `IndexRunStats` in RESEARCH.md §1 last block). Return `IndexRunStats`.

**Config + provider resolution at top** (must mirror `solve.py:66-67`):

```python
config = load_config(config_path)
provider_config = resolve_provider_config(config, os.environ, provider_name)
```

**Dry-run pattern** (`solve.py:62-64`):

```python
if dry_run:
    # validate skill / vocabulary loads, but no LLM, no writes
    load_vocabulary(workspace_root)  # validates YAML files
    return IndexRunStats(...)  # all zeros
```

**Discovery reuse:**

```python
from cpho_cli.core.workspace import discover_workspace
result = discover_workspace(workspace_root)
# Process result.pairs AND result.unmatched_problems (problems without answer key still indexable)
# Log warning on result.ambiguous, do not process
```

RESEARCH.md §9 line 821 explicitly says: index processes `pairs + unmatched_problems`; `ambiguous` is warned and skipped. This **diverges** from `solve.py:59-60` which requires `answer_path` to exist (`SolveError` on missing). Indexing must tolerate missing answer keys.

**Exception hierarchy** (mirror `solve.py:17-18`):

```python
class IndexError(RuntimeError):
    """Raised when index operations cannot proceed."""

class IndexNotFoundError(IndexError): pass
class ProblemNotIndexedError(IndexError): pass
class VocabularyError(IndexError): pass
```

Per RESEARCH.md §7. Note the **rename collision**: Python builtin `IndexError` exists. Plan 02-05 must either (a) accept the shadow (caller's `from cpho_cli.core.index import IndexError` always wins inside that module) or (b) name it `IndexBuildError`. **Recommendation: rename to `IndexBuildError`** to avoid the shadow — RESEARCH.md §7 listing is descriptive not prescriptive on naming.

**Decision algorithm placement** — RESEARCH.md §3's `decide_action(old, new_fp)` function belongs in `core/index/hashing.py` (pure) and is called from `builder.py`. Keep the pure decision separate from the I/O orchestration.

**Action dispatch** (Phase 2 introduces; no Phase 1 analog for action-typed dispatch):

```python
action = decide_action(old_entry, new_fingerprint)
if action == "skip":
    stats.tags_skipped += 1
    continue
if action == "refinement_only":
    # Phase 2: project UserNotebookEntry → IndexEntry.user_confirmed_*, no LLM
    ...
if action == "re_tag_only":
    # reuse OCR cache, re-run LLM
    ...
if action == "re_ocr_and_re_tag" or action == "full_index":
    # complete pipeline
    ...
```

**OCR upgrade prompt handoff** — RESEARCH.md §8 specifies芯-壳分离: core raises `OcrUpgradeDecisionRequired`, CLI catches and prompts. Pattern is analogous to `solve.py:57-60` raising `SolveError("Missing answer key. Provide --answer ...")` — core raises typed exception, CLI translates to user-facing message. Add a new exception type:

```python
class OcrUpgradeDecisionRequired(IndexBuildError):
    def __init__(self, delta: OcrEngineDelta) -> None:
        self.delta = delta
        super().__init__(f"OCR engine upgrade detected: {delta.summary()}")
```

CLI catches and re-prompts. No `input()` in core.

---

#### `src/cpho_cli/cli/app.py` (CLI — add `index` command)

**Analog:** Existing `solve` (`cli/app.py:13-42`) and `eval_command` (`:45-72`).

**Decorator + signature pattern** (must mirror `:13-23`):

```python
@app.command(name="index")
def index_command(
    workspace: Path = typer.Argument(Path.cwd(), help="Workspace 目录."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Local YAML config path."),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Provider profile."),
    force: bool = typer.Option(False, "--force", help="重建全部索引."),
    only_new: bool = typer.Option(False, "--only-new", help="仅索引新增题目."),
    dry_run: bool = typer.Option(False, "--dry-run", help="仅验证, 不调 LLM."),
    ocr_strategy: str = typer.Option("prompt", "--ocr-strategy", help="OCR 升级: prompt|reuse|rebuild|new-only"),
    quiet: bool = typer.Option(False, "--quiet", "-q"),
    list_candidates: bool = typer.Option(False, "--list-candidates"),
) -> None:
    """对工作空间题目生成结构化索引."""
```

**Error → BadParameter translation** (must mirror `:34-35` and `:66-67`):

```python
try:
    stats = build_index(workspace, config_path=config, provider_name=provider, ...)
except (ConfigError, IndexBuildError) as exc:
    raise typer.BadParameter(str(exc)) from exc
except OcrUpgradeDecisionRequired as exc:
    # interactive prompt here; core never prompts directly
    choice = typer.prompt("选择 [a/b/c/d]")
    stats = build_index(workspace, ..., ocr_strategy=_map_choice(choice))
```

**Output rendering** (mirror `:69-72`):

```python
typer.echo(f"扫描题目数: {stats.total_problems}")
typer.echo(f"  新增: {stats.file_changed - stats.file_unchanged}")  # etc.
```

Chinese UX per `cli/app.py` already-Chinese help text (line 10 `"CPHO local physics analysis CLI."` is English — Phase 2 should use Chinese for new help strings per AGENTS.md "中文 UX").

**Imports header** (mirror `:1-8`):

```python
from cpho_cli.core.index import build_index, IndexBuildError, OcrUpgradeDecisionRequired
```

The public surface comes from `core/index/__init__.py` re-exports.

---

#### `src/cpho_cli/models/config.py` (MODIFY — extend with index settings)

**Analog:** Existing `SkillConfig` + `AppConfig.skills` dict (`models/config.py:35-46`).

**Per-skill config dict already exists.** `AppConfig.skills: dict[str, SkillConfig]` already supports `config.skills["index"].model.temperature = 0.0`. Plan 02-04 / 02-05 likely needs **no new fields on AppConfig** — `resolve_model_params(config, "index")` already works via the dict.

**If Phase 2 needs additional index-specific config** (e.g., `vocabulary_paths`, `cache_dir_override`), add a parallel nested model:

```python
class IndexConfig(StrictModel):
    cache_dir: Path | None = None            # default `.cpho/cache/`
    workspace_vocab_path: Path | None = None
    private_vocab_path: Path | None = None
    # ... only fields the user might actually override

class AppConfig(StrictModel):
    ...
    index: IndexConfig = Field(default_factory=IndexConfig)
```

**Divergence note:** Per AGENTS.md §2 "不做未被要求的灵活性". Start with **zero new AppConfig fields**. Only add `IndexConfig` if a Plan demonstrates an actual configurability need. RESEARCH.md does not mandate any new config fields — all paths can be derived from `workspace_root`.

---

### Test File Patterns

---

#### `tests/test_index_models.py` (schema unit tests)

**Analog:** `tests/test_solve.py:28-62`.

**Pattern (mirror `:28-30` for field-level validation, `:45-62` for round-trip):**

```python
def test_canonical_tag_requires_internal_id() -> None:
    with pytest.raises(Exception):
        CanonicalTag(internal_id="", display_zh="x", category=TagCategory.PHYSICS_MODEL)

def test_index_entry_round_trip() -> None:
    entry = IndexEntry(problem_id="p1", ...)
    serialized = entry.model_dump_json()
    restored = IndexEntry.model_validate_json(serialized)
    assert restored == entry
```

**Extra-field rejection test** (mirror `tests/test_config.py:137-142`):

```python
def test_index_entry_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        IndexEntry.model_validate({"problem_id": "p1", "unknown_field": 1, ...})
```

Required to verify `StrictModel(extra="forbid")` is wired correctly on all new types.

---

#### `tests/test_index_vocabulary.py`

**Analog:** `tests/test_config.py` (entire file).

**Tmp-path + YAML-string pattern** (`test_config.py:33-56`):

```python
def test_workspace_layer_overrides_builtin(tmp_path: Path) -> None:
    workspace_vocab = tmp_path / ".cpho" / "vocabulary" / "workspace.yml"
    workspace_vocab.parent.mkdir(parents=True)
    workspace_vocab.write_text(
        """
version: "v0.1"
tags:
  - internal_id: newton_second_law
    display_zh: 牛顿第二（自定义）
    category: physics_model
""",
        encoding="utf-8",
    )
    vocab = load_merged_vocabulary(tmp_path)
    assert vocab.tags["newton_second_law"].display_zh == "牛顿第二（自定义）"
```

---

#### `tests/test_index_tagging.py` (fake LLM provider)

**Analog:** `tests/test_solve.py:65-127` — `FakeProvider` + `FakeOCR` classes.

**FakeProvider pattern (must mirror `:83-104`):**

```python
class FakeLLMProvider:
    called = False
    def complete(self, messages, params, response_model=None):
        self.called = True
        return LLMResponse(
            content=TagRefinementOutput(
                selected_physics_models=["newton_second_law"],
                ...
            ).model_dump_json()
        )
```

**Test assertion shape (`:124-126`):**

```python
assert provider.called is True
assert "newton_second_law" in result.physics_model_tags  # or read from JSONL
```

---

#### `tests/test_index_cli.py`

**Analog:** `tests/test_cli.py` (entire file — 30 lines, CliRunner pattern).

**Pattern:**

```python
from typer.testing import CliRunner
from cpho_cli.cli.app import app

def test_index_help_lists_options() -> None:
    result = CliRunner().invoke(app, ["index", "--help"])
    assert result.exit_code == 0
    assert "--force" in result.output
    assert "--only-new" in result.output
    assert "--dry-run" in result.output
    assert "--ocr-strategy" in result.output
```

Plus a dry-run smoke test that exercises `build_index(dry_run=True)`.

---

#### `tests/test_index_api.py`

**Analog:** `tests/test_workspace.py` (uses tmp_path + small static fixtures).

**Pattern (`test_workspace.py:11-20`):**

```python
def test_query_index_returns_entries_with_tag(tmp_path: Path) -> None:
    # Seed .cpho/index.jsonl with two entries
    write_index_jsonl(tmp_path, [entry_a, entry_b])
    results = query_index(tmp_path, physics_model_ids=["newton_second_law"])
    assert {r.problem_id for r in results} == {"p1"}
```

---

## Shared Patterns

### 1. `StrictModel` base everywhere

**Source:** `src/cpho_cli/models/config.py:6-7`
**Apply to:** All new models in `models/index.py`.

```python
class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
```

**Import, don't redefine:** `from cpho_cli.models.config import StrictModel`. RESEARCH.md §1 line 165 confirms.

---

### 2. `from __future__ import annotations`

**Source:** Every Phase 1 module (e.g., `core/config.py:1`, `models/solve.py:1`, `core/solve.py:1`).
**Apply to:** All new `.py` files in Phase 2.

Required for forward references in type hints (`Path | None`, etc.) under Python 3.11.

---

### 3. Pydantic JSON round-trip

**Source:** `core/solve.py:29` (write) + `:106` (read).
**Apply to:** All persistence boundaries — `IndexEntry`, `OCRResult` cache, `UserNotebookEntry`, `Vocabulary`.

```python
# Write
path.write_text(model.model_dump_json(indent=2), encoding="utf-8")
# Read
model = ModelClass.model_validate_json(path.read_text(encoding="utf-8"))
```

For JSONL: drop `indent=2`, use `.open("a")` and `\n` between rows.

---

### 4. Provider injection for testability

**Source:** `core/solve.py:54-56` — accept `ocr_provider: OCRProvider | None = None, llm_provider: LLMProvider | None = None`.
**Apply to:** `build_index` and `tagging.refine_tags` in Phase 2.

Default to real providers; tests inject fakes. Mirror `tests/test_solve.py:65-127` for the fake-provider construction pattern.

---

### 5. Secret redaction in any trace/log path

**Source:** `core/runtime.py:20-25` (`redact_secrets`) + `core/llm.py:82-85, 105` (applied at HTTP error path).
**Apply to:** Any new TraceRecord write, any exception message that might contain `provider_config.api_key`.

```python
from cpho_cli.core.runtime import redact_secrets
text = redact_secrets(text, [provider_config.api_key])
```

Phase 2 has no new secrets, so `redact_secrets` may be called with `[]` in many paths. Still call it — explicit > silent.

---

### 6. `Path | None = None` for optional outputs

**Source:** `models/solve.py:49-50`, `core/solve.py:54-55`.
**Apply to:** Optional path parameters everywhere — `config_path`, `cache_dir_override`, etc.

---

### 7. Exception hierarchy attached to user-facing channel

**Source:** `core/solve.py:17-18` (`SolveError(RuntimeError)`), `core/config.py:16-17` (`ConfigError(ValueError)`), `core/eval.py:13-14` (`EvalConfigError(ValueError)`).
**CLI catches and translates:** `cli/app.py:34-35, 66-67`:

```python
try:
    ...
except (ConfigError, SolveError) as exc:
    raise typer.BadParameter(str(exc)) from exc
```

**Phase 2 mapping** — define `IndexBuildError(RuntimeError)` (operational), `VocabularyError(IndexBuildError)` (operational), and catch `(ConfigError, IndexBuildError)` in the CLI command. Per RESEARCH.md §7.

---

### 8. CLI is shell, core is library (芯-壳)

**Source:** AGENTS.md "芯-壳分离"; enforced in `cli/app.py` (only `typer.echo` and exception translation) vs. `core/*.py` (no `print`, no `input`).

**Mandatory:** `core/index/*` must not import `typer` or call `print()` / `input()`. The OCR-upgrade-prompt flow (RESEARCH.md §8) uses a raised exception (`OcrUpgradeDecisionRequired`) so the CLI can perform `typer.prompt`. Core has no interactive surface.

---

## Anti-Patterns (Phase 1 quirks Phase 2 must NOT replicate)

### AP-1: f-string inline prompts (regression vs. D-11)

**Where:** `core/solve.py:88-100` — system + user content built by f-string instead of Jinja2 templates.

> Phase 1's `builtin_skills/solve/prompts/*.md.j2` files exist but `solve.py` does not render them.

**Phase 2 directive:** Use Jinja2 (`jinja2.Environment` + `FileSystemLoader` + `StrictUndefined`) per D-11 and RESEARCH.md §4. Don't copy the f-string approach.

---

### AP-2: No OCR cache in `solve.py`

**Where:** `core/solve.py:70-72` re-runs `RapidOCRProvider().extract(...)` on every call. Same problem PDF → repeated OCR cost.

**Phase 2 directive:** Introduce `CachedOCRProvider` in `core/index/ocr_cache.py` for the index path. **Do not modify `solve.py` to use the cache** (RESEARCH.md §13 R4 — out of scope; risks regressions). Record in STATE.md as a "deferred to later phase" item.

---

### AP-3: Plain `BaseModel` instead of `StrictModel`

**Where:** `models/solve.py:8-46` — uses `class X(BaseModel)` directly, no `extra="forbid"`. `SolveReport` silently accepts unknown fields.

**Phase 2 directive:** All new index models use `StrictModel`. AGENTS.md "Pydantic 严格模式" is binding. `test_unknown_config_fields_fail`-style coverage required (`tests/test_config.py:137-142`).

---

### AP-4: Non-atomic file writes

**Where:** `core/solve.py:29-43` — direct `path.write_text(...)`. If interrupted mid-write, partial JSON left on disk.

**Phase 2 directive:** Use `tmp.replace(final_path)` for `.cpho/index.jsonl` writes (RESEARCH.md §13 R5). Query callers (`query_index`) may run concurrently.

---

### AP-5: Mutable default in field annotation

**Where:** Hypothetical — not observed in Phase 1, but easy to slip when adding fields. Phase 1 correctly uses `Field(default_factory=list)` (e.g., `models/solve.py:41, 42, 43, 44, 45`).

**Phase 2 directive:** Continue the `Field(default_factory=list)` and `Field(default_factory=...)` pattern. Never `field: list[str] = []`.

---

### AP-6: English help text on user-facing options

**Where:** `cli/app.py:10` — `"CPHO local physics analysis CLI."` and most option helps are English.

**Phase 2 directive:** Per AGENTS.md "中文 UX", new `index` command help text should be Chinese. Do not "fix" Phase 1 English text per AGENTS.md §3 "精准修改".

---

### AP-7: SolveReport tag fields are free-text strings, not controlled IDs

**Where:** `models/solve.py:43-45` — `physics_model_tags: list[str]`, free format.

**Phase 2 directive:** Per D-06 "不盲抄 SolveReport 标签", the tagging pipeline must run a canonical-mapping pass (RESEARCH.md §11 M3) to convert free-text Phase 1 tags into vocabulary `internal_id`s. Do not expose `SolveReport.physics_model_tags` directly in the index — always pass through normalization first.

---

### AP-8: Trace path hardcoded in Phase 1 to `traces/`; Phase 2 should use `.cpho/`

**Where:** Phase 1 uses `traces/` (gitignored).

**Phase 2 directive:** Per RESEARCH.md §Open Question 4, index trace goes to `.cpho/run-trace.jsonl` to keep all index-related artifacts under `.cpho/`. Don't reuse `traces/`.

---

## No Analog Found

| File | Reason | Mitigation |
|------|--------|------------|
| `core/index/hashing.py` | Phase 1 has zero hashing. | Pure stdlib (`hashlib` + `json.dumps(sort_keys=True)`). RESEARCH.md §3 provides the algorithm. Style-match `core/config.py`'s top-level-function layout. |
| `core/index/__init__.py` (public API re-exports) | Phase 1 `__init__.py` files are empty. | Introduce convention: explicit re-export of public symbols. RESEARCH.md §7 gives the full surface. |
| Jinja2 rendering in code | Phase 1 has `.md.j2` files but never renders them. | First-time use; RESEARCH.md §4 + Jinja2 docs. Use `StrictUndefined`. |
| Atomic file rename (`tmp + replace`) | Phase 1 writes are non-atomic. | Stdlib `pathlib.Path.replace`. RESEARCH.md §13 R5. |

---

## Metadata

**Analog search scope:**
- `src/cpho_cli/core/*.py` (9 modules)
- `src/cpho_cli/models/*.py` (8 modules)
- `src/cpho_cli/cli/app.py`
- `src/cpho_cli/builtin_skills/solve/` (directory structure)
- `tests/test_*.py` (10 test files)
- `.planning/phases/01-core-foundation/*.md` (PATTERNS, CONTEXT, VERIFICATION)

**Files scanned:** 28 source + 10 test + 5 planning docs = 43.
**Pattern extraction date:** 2026-05-23
**Phase 1 baseline:** commit `a542b0d` (feature/phase2 branch HEAD).
