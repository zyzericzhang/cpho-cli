# Testing Patterns

**Analysis Date:** 2026-05-28

## Test Framework

**Runner:**
- pytest >=8.2
- Config: `pyproject.toml` under `[tool.pytest.ini_options]`
- Test path: `tests`
- Async support: `pytest-asyncio >=0.23`, used with `@pytest.mark.asyncio` in files such as `tests/test_repl_workspace_commands.py` and `tests/test_repl_runtime.py`.

**Assertion Library:**
- Native `assert` statements.
- `pytest.raises` for exception behavior.
- Typer CLI tests use `typer.testing.CliRunner`.
- HTTP provider tests use `httpx.MockTransport`.

**Run Commands:**
```bash
uv run pytest -q              # Run all tests
uv run pytest tests/<file>.py -q              # Run one test module
uv run pytest tests/<file>.py::test_name -q   # Run one test
uv run ruff check .           # Lint check required by CONTRIBUTING.md
uv run mypy src/cpho_cli/     # Strict type check from pyproject.toml
```

Coverage tooling is not configured in `pyproject.toml`; no `pytest-cov` dependency or coverage target is enforced.

## Test File Organization

**Location:**
- Tests live in top-level `tests/`.
- Shared fakes and fixtures live in `tests/conftest.py`.
- Static fixtures live under `tests/fixtures/`, including `tests/fixtures/golden_index_workspace/` and `tests/fixtures/splitting/`.
- Tests are mostly organized by production module or feature: `tests/test_config.py`, `tests/test_llm.py`, `tests/test_index_builder.py`, `tests/test_repl_workspace_commands.py`, and `tests/test_compose_cli.py`.
- Phase acceptance tests are named `tests/test_phase*_acceptance.py` and encode milestone gates.

**Naming:**
- Test modules use `test_<feature>.py`.
- Test functions use `test_<expected_behavior>()`.
- Private test helpers use leading underscores: `_write_pdf()`, `_fingerprint()`, `_seed_workspace()`, `_ocr()`, `_paper()`, and `_client_for_tarball()`.
- Fake providers/classes use `Fake...` or private underscored classes: `FakeOCRProvider`, `FakeLLMProvider`, `FakeSplitProvider`, `_SolveOCR`, and `_SolveProvider`.

**Structure:**
```text
tests/
├── conftest.py
├── fixtures/
│   ├── golden_index_workspace/
│   ├── paper_with_5_problems.json
│   └── splitting/
├── test_<core_feature>.py
├── test_repl_<command_or_area>.py
├── test_<cli_area>_cli.py
└── test_phaseNN_acceptance.py
```

## Test Structure

**Suite Organization:**
```python
from __future__ import annotations

from pathlib import Path

import pytest

from cpho_cli.core.config import ConfigError, load_config


def test_unknown_config_fields_fail(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    config_path.write_text("unexpected: true\n", encoding="utf-8")

    with pytest.raises(ConfigError):
        load_config(config_path)
```

This pattern appears in `tests/test_config.py`: arrange temp files under `tmp_path`, act through the public function, then assert the typed result or error.

**Patterns:**
- Prefer public API tests through core functions: `build_index()` in `tests/test_index_builder.py`, `query_index()` and tag APIs in `tests/test_index_api.py`, `solve_problem()` in `tests/test_solve.py`, and `load_config()` in `tests/test_config.py`.
- Use CLI runner tests for Typer surfaces: `tests/test_compose_cli.py`, `tests/test_topic_cli.py`, `tests/test_knowledge_cli.py`, and `tests/test_cli.py`.
- Use async tests for REPL commands and app dispatch: `tests/test_repl_workspace_commands.py`, `tests/test_repl_runtime.py`, `tests/test_repl_compose_commands.py`, and `tests/test_repl_related_commands.py`.
- Use `tmp_path` for every filesystem-writing test. Tests write temporary workspaces, `.cpho` directories, YAML configs, PDFs, JSONL indexes, and markdown outputs under `tmp_path`.
- Use `monkeypatch` for environment variables and collaborator replacement. Examples include `XDG_CONFIG_HOME` in `tests/test_repl_workspace_commands.py`, `_rapidocr_version` in `tests/test_index_builder.py`, and LLM fallback replacement in `tests/test_splitting_golden.py`.
- Use `capsys` only for stdout assertions around user-facing REPL output, as in `tests/test_repl_workspace_commands.py`.

## Mocking

**Framework:** pytest monkeypatch, hand-written fakes, `httpx.MockTransport`

**Patterns:**
```python
def handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}]})

provider = OpenRouterProvider(
    api_key="<redacted-test-key>",
    client=httpx.Client(transport=httpx.MockTransport(handler)),
)
```

Provider HTTP tests in `tests/test_llm.py` and `tests/test_community_sync.py` inject `httpx.Client(transport=httpx.MockTransport(handler))` rather than calling real services.

```python
class FakeLLMProvider:
    def complete(self, messages, params, response_model=None):
        return LLMResponse(content=self.fixed_output.model_dump_json(), usage=LLMUsage())
```

Shared fake providers live in `tests/conftest.py`; feature-specific fakes live near the tests that need them, such as `FakeSplitProvider` in `tests/test_splitting_llm.py` and `_SolveProvider` in `tests/test_phase023_acceptance.py`.

**What to Mock:**
- Mock network clients and LLM providers by injecting `httpx.MockTransport`, fake provider classes, or monkeypatched module functions.
- Mock OCR with `FakeOCRProvider` or small local classes when testing index/solve orchestration.
- Mock environment with `monkeypatch.setenv()` for config, XDG paths, and cache path behavior.
- Mock expensive or nondeterministic fallback paths, such as `split_paper_with_llm` in `tests/test_splitting_golden.py`.

**What NOT to Mock:**
- Do not mock Pydantic validation for domain models; tests instantiate real `IndexEntry`, `ModelParams`, `OCRResult`, `SolveReport`, and related models.
- Do not mock filesystem writes for workspace behavior; tests assert real temp files such as `.cpho/index.jsonl`, checkpoints, trace files, composition YAML, and generated PDFs.
- Do not call live LLM APIs in normal test coverage. Real API verification is documented separately in `docs/test-001-real-api-verification.md` and `docs/test-002-real-api-verification.md`.

## Fixtures and Factories

**Test Data:**
```python
def setup_workspace(
    tmp_path: Path,
    problem_names: list[str] | None = None,
    with_answers: bool = True,
    with_config: bool = True,
) -> Path:
    ...
```

`tests/conftest.py` provides reusable builders:
- `setup_workspace()` creates a minimal problem/answer workspace with PNG-like files and optional config.
- `make_index_entry()` builds validated `IndexEntry` objects for index/REPL tests.
- `repl_workspace_with_index` creates a fixture workspace with `.cpho/ocr/` text files and `.cpho/index.jsonl`.
- `FakeOCRProvider` and `FakeLLMProvider` provide deterministic OCR/LLM behavior.

**Location:**
- Shared factories: `tests/conftest.py`
- Golden workspace fixtures: `tests/fixtures/golden_index_workspace/`
- Splitting regression fixture: `tests/fixtures/splitting/ipho_style_multi_problem.expected.json`, plus paired PDFs in the same directory.
- Generic JSON fixture: `tests/fixtures/paper_with_5_problems.json`

The real user workspace at `/Users/ericzhang/Desktop/物理竞赛资料` is relevant to smoke tests and fixture design because it contains year/provider directories, Chinese path names, PDFs, images, answer files, and a `.cpho/cache` tree. Tests that need this shape copy representative files into `tmp_path` and skip when the workspace is unavailable; they must not mutate originals or persist copied content outside temporary workspaces. The existing pattern is in `tests/test_phase023_acceptance.py`.

## Coverage

**Requirements:** None enforced by tooling.

**View Coverage:**
```bash
# Not configured. Add pytest-cov before expecting this to work consistently.
uv run pytest --cov=cpho_cli
```

Existing quality gates emphasize:
- Full suite: `uv run pytest -q`
- Lint: `uv run ruff check .`
- Type checking: `uv run mypy src/cpho_cli/`

`CONTRIBUTING.md` requires pytest and Ruff before submitting changes. Verification docs such as `docs/final-verification.md`, `docs/phase7-verification.md`, and `docs/phase8-verification.md` record phase-specific test subsets plus full-suite checks.

## Test Types

**Unit Tests:**
- Small pure-function/model tests live in files such as `tests/test_json_utils.py`, `tests/test_config.py`, `tests/test_index_hashing.py`, `tests/test_boundary.py`, and `tests/test_input_routing.py`.
- Assert exact return values, validation errors, deterministic hashes, and redaction behavior.

**Integration Tests:**
- Workspace and index orchestration tests use real temp files and injected fakes in `tests/test_index_builder.py`, `tests/test_index_api.py`, `tests/test_index_storage.py`, and `tests/test_topic_builder_integration.py`.
- CLI integration tests use `CliRunner` against `src/cpho_cli/cli/app.py` in `tests/test_compose_cli.py`, `tests/test_topic_cli.py`, and `tests/test_knowledge_cli.py`.
- REPL integration tests call async command handlers directly with `SessionState` in `tests/test_repl_workspace_commands.py`, `tests/test_repl_builtin_commands.py`, and related REPL files.
- PDF composition tests use PyMuPDF through `fitz` and real temp PDFs in `tests/test_compose_pdf.py` and `tests/test_compose_cli.py`.

**E2E Tests:**
- Phase acceptance tests in `tests/test_phase021_acceptance.py`, `tests/test_phase023_acceptance.py`, `tests/test_phase03_acceptance.py`, through `tests/test_phase08_acceptance.py` serve as repository-level end-to-end and regression gates.
- `tests/test_phase1_e2e.py` covers early full-flow behavior.
- Real-workspace-shaped smoke tests copy samples from `/Users/ericzhang/Desktop/物理竞赛资料` when present, but use fake OCR/LLM providers for deterministic execution.

## Common Patterns

**Async Testing:**
```python
@pytest.mark.asyncio
async def test_index_dry_run_cancel_and_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ...
    await do_index(session, ["--all"])
```

Use `@pytest.mark.asyncio` for async REPL command functions in `tests/test_repl_workspace_commands.py` and `tests/test_repl_runtime.py`. Construct a `SessionState` with `AppConfig()` and temp workspace paths, then call command handlers directly.

**Error Testing:**
```python
with pytest.raises(ConfigError) as exc:
    resolve_provider_config(config, {}, "missing")

assert "missing" in str(exc.value)
assert "<secret-prefix>" not in str(exc.value)
```

Use `pytest.raises(..., match=...)` when matching stable error text, as in `tests/test_index_api.py`, `tests/test_composition_models.py`, and `tests/test_runtime.py`. For secret-redaction tests, assert that configured key names may appear but secret values do not, as in `tests/test_config.py` and `tests/test_llm.py`.

**CLI Testing:**
```python
runner = CliRunner()

result = runner.invoke(
    app,
    ["compose", "new", "mock", "--count", "2", "--workspace", str(tmp_path)],
)

assert result.exit_code == 0
assert (tmp_path / ".cpho" / "compositions" / "mock.yml").exists()
```

Use one module-level `runner = CliRunner()` per CLI test module, as in `tests/test_compose_cli.py`. Assert both exit codes and filesystem/user-output side effects.

**Golden Regression Testing:**
```python
expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))
paper_ocr = OCRResult.model_validate(expected["problem_ocr_pages"])
answer_ocr = OCRResult.model_validate(expected["answer_ocr_pages"])
outcome = split_paper(paper_ocr, answer_ocr, ...)
```

Keep golden data in `tests/fixtures/` and assert deterministic behavior without live LLM fallback. `tests/test_splitting_golden.py` is the reference pattern.

---

*Testing analysis: 2026-05-28*
