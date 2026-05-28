# Coding Conventions

**Analysis Date:** 2026-05-28

## Naming Patterns

**Files:**
- Use snake_case Python modules under `src/cpho_cli/`: examples include `src/cpho_cli/core/json_utils.py`, `src/cpho_cli/core/input_routing.py`, and `src/cpho_cli/cli/repl/model_panel.py`.
- Group domain subpackages by feature boundary: `src/cpho_cli/core/index/`, `src/cpho_cli/core/splitting/`, `src/cpho_cli/core/knowledge/`, `src/cpho_cli/cli/repl/commands/`, and `src/cpho_cli/models/`.
- Use template filenames that match skill step IDs or prompt purpose: `src/cpho_cli/builtin_skills/solve/prompts/derive.md.j2`, `src/cpho_cli/core/splitting/prompts/split_paper.md.j2`, and `src/cpho_cli/core/index/prompts/tag_refinement.md.j2`.
- Use YAML data files for packaged vocabularies and manifests: `src/cpho_cli/vocabulary/builtin.yml`, `src/cpho_cli/vocabulary/builtin/01_optics_geometric.yml`, and `src/cpho_cli/core/index/prompts/MANIFEST.yml`.

**Functions:**
- Use snake_case for public functions and helpers: `load_config()`, `resolve_provider_config()`, and `resolve_model_params()` in `src/cpho_cli/core/config.py`.
- Use leading underscore for module-private helpers: `_merge_params()` in `src/cpho_cli/core/config.py`, `_schema_name()` in `src/cpho_cli/core/llm.py`, and `_resolve_target_path()` in `src/cpho_cli/cli/repl/commands/workspace.py`.
- Use `do_<command>()` for async REPL command handlers: `do_workspace()`, `do_status()`, `do_config()`, and `do_index()` in `src/cpho_cli/cli/repl/commands/workspace.py`.
- Use factory names with `make_` or `create_` when constructing collaborators: `create_llm_provider()` in `src/cpho_cli/core/llm.py` and `make_llm_handler()` in `src/cpho_cli/core/skill_handlers.py`.

**Variables:**
- Prefer explicit domain names over abbreviations: `provider_config`, `active_llm_provider`, `workspace_root`, `target_subpath`, and `vision_capabilities` in `src/cpho_cli/core/index/builder.py`.
- Use `*_path` for `Path` values and `*_dir` for directories: `config_path`, `index_path`, `trace_path`, `checkpoint_dir`, and `output_dir` across `src/cpho_cli/core/config.py`, `src/cpho_cli/core/runtime.py`, and `src/cpho_cli/cli/app.py`.
- Use `*_count`, `*_tokens`, and `*_version` for scalar counters and versions: `candidate_tags_proposed` in `src/cpho_cli/models/index.py`, `total_tokens` in `src/cpho_cli/models/llm.py`, and `tag_schema_version` in `src/cpho_cli/models/index.py`.

**Types:**
- Use PascalCase for classes, Pydantic models, dataclasses, Protocols, and exceptions: `StrictModel` in `src/cpho_cli/models/config.py`, `SessionState` in `src/cpho_cli/cli/repl/session.py`, `LLMProvider` in `src/cpho_cli/core/llm.py`, and `SkillRuntimeError` in `src/cpho_cli/core/runtime.py`.
- Use enum classes for closed string sets: `TagCategory`, `TagVisibility`, `TagStatus`, `TagLayer`, and `TagSource` in `src/cpho_cli/models/index.py`.
- Use `TypedDict` for callback event payloads that stay dict-shaped: `IndexProgress` in `src/cpho_cli/core/index/builder.py`.
- Use `TypeVar` bounded to `BaseModel` when structured LLM responses are generic: `ResponseModel` in `src/cpho_cli/core/llm.py`.

## Code Style

**Formatting:**
- Ruff is the formatter/linter authority. Configuration lives in `pyproject.toml`.
- Use 100-character line length from `[tool.ruff] line-length = 100` in `pyproject.toml`.
- Target Python 3.11 from `[tool.ruff] target-version = "py311"` and `[tool.mypy] python_version = "3.11"` in `pyproject.toml`.
- Prefer modern type syntax such as `Path | None`, `list[str]`, and `dict[str, Any]`; examples appear in `src/cpho_cli/core/config.py`, `src/cpho_cli/core/runtime.py`, and `src/cpho_cli/models/index.py`.
- Most modules start with `from __future__ import annotations`; keep adding it in new modules under `src/cpho_cli/` and `tests/` unless matching a nearby file that omits it, such as `src/cpho_cli/cli/app.py`.

**Linting:**
- Use `uv run ruff check .` for whole-repo linting. This command is prescribed in `CONTRIBUTING.md`.
- Use `uv run mypy src/cpho_cli/` for static typing; strict mypy is enabled in `pyproject.toml`.
- Mypy is strict and `ignore_missing_imports = true`; keep public functions, tests, and callbacks typed rather than relying on implicit `Any`.
- When test doubles intentionally use dynamic signatures, local `# type: ignore[no-untyped-def]` comments are used narrowly, as in `tests/test_llm.py`, `tests/test_repl_workspace_commands.py`, and `tests/test_phase023_acceptance.py`.

## Import Organization

**Order:**
1. `from __future__ import annotations` when present.
2. Standard library imports, alphabetized by module family where practical: `datetime`, `pathlib`, `typing`, `collections.abc`, `json`, `os`, and similar.
3. Third-party imports: `httpx`, `pytest`, `yaml`, `pydantic`, `typer`, `click`, `fitz`, `jinja2`, and `prompt_toolkit`.
4. First-party imports from `cpho_cli.*`.
5. Test-only local imports from `conftest` after first-party imports, as in `tests/test_phase023_acceptance.py` and `tests/test_index_builder.py`.

**Path Aliases:**
- Package imports use the installed `src/` package name: `from cpho_cli.core.config import load_config` and `from cpho_cli.models.index import IndexEntry`.
- Tests import shared test helpers from root-level `tests/conftest.py` as `from conftest import FakeLLMProvider, FakeOCRProvider, setup_workspace`.
- Do not use relative imports between production modules; current production code imports through `cpho_cli.*`.

## Error Handling

**Patterns:**
- Define domain-specific exceptions near the domain boundary: `ConfigError` in `src/cpho_cli/core/config.py`, `LLMProviderError` in `src/cpho_cli/core/llm.py`, and `SkillRuntimeError` in `src/cpho_cli/core/runtime.py`.
- Raise typed domain exceptions from core code and translate them at the CLI boundary to `typer.BadParameter`; examples are `solve()` and `index_command()` in `src/cpho_cli/cli/app.py`.
- Chain exceptions with `from exc` when wrapping external errors: `load_config()` wraps `OSError`, `ValidationError`, and `yaml.YAMLError` in `src/cpho_cli/core/config.py`.
- Keep secret-bearing values out of errors. Use `redact_secrets()` from `src/cpho_cli/core/runtime.py` in provider paths, and assert redaction in `tests/test_llm.py` and `tests/test_config.py`.
- Use explicit validation errors for unsafe paths and invalid user input: `_resolve_target_path()` in `src/cpho_cli/cli/repl/commands/workspace.py` checks that absolute or relative paths remain under the workspace.
- Use Pydantic validation for input schemas and domain invariants. `StrictModel` forbids unknown fields in `src/cpho_cli/models/config.py`; `IndexEntry.validate_problem_page_range()` checks 1-indexed page ranges in `src/cpho_cli/models/index.py`.

## Logging

**Framework:** Standard `logging`

**Patterns:**
- Use `logging.getLogger(__name__)` at the call site for warnings, as in `src/cpho_cli/core/index/builder.py`.
- Logging is sparse and reserved for recoverable degraded behavior, such as capability detection failure and topic taxonomy load failure in `src/cpho_cli/core/index/builder.py`.
- User-facing CLI progress uses `typer.echo()` in `src/cpho_cli/cli/app.py` and `print()`/display helpers in `src/cpho_cli/cli/repl/commands/workspace.py`, not logging.

## Comments

**When to Comment:**
- Prefer short comments before non-obvious orchestration blocks. `build_index()` in `src/cpho_cli/core/index/builder.py` uses comments like "Build paper inputs" and "Load topic taxonomy" to divide the pipeline.
- Use docstrings on reusable helpers and classes when behavior matters: `FakeOCRProvider` in `tests/conftest.py`, `IndexProgress` in `src/cpho_cli/core/index/builder.py`, and `SessionState` module docstring in `src/cpho_cli/cli/repl/session.py`.
- Avoid comments that restate one-line code. Existing comments mostly explain policy, flow, or fallback decisions.

**JSDoc/TSDoc:**
- Not applicable; this is a Python codebase.
- Use Python docstrings for public classes/functions where they clarify behavior, especially command handlers, providers, and orchestration functions.

## Function Design

**Size:** Keep pure helpers short and explicit. `extract_json_text()` and `loads_json_object()` in `src/cpho_cli/core/json_utils.py` are small single-purpose helpers. Larger orchestration functions are accepted at workflow boundaries, especially `build_index()` in `src/cpho_cli/core/index/builder.py` and CLI command functions in `src/cpho_cli/cli/app.py`.

**Parameters:** Use keyword-only flags for workflow toggles after required positional inputs. `build_index()` in `src/cpho_cli/core/index/builder.py` takes `workspace_root`, optional config/provider values, then keyword-only flags such as `force`, `dry_run`, `ocr_strategy`, `target_subpath`, and `vision`.

**Return Values:** Return typed domain models instead of loose dicts for stable boundaries. Examples include `AppConfig` from `load_config()` in `src/cpho_cli/core/config.py`, `ResolvedProviderConfig` from `resolve_provider_config()`, `LLMResponse` from provider `complete()` methods in `src/cpho_cli/core/llm.py`, and `IndexRunStats` from `build_index()`.

## Module Design

**Exports:** Keep modules focused around a feature boundary:
- `src/cpho_cli/models/` defines data contracts and validation.
- `src/cpho_cli/core/` owns business logic, IO orchestration, providers, runtime, workspace discovery, and domain APIs.
- `src/cpho_cli/cli/` owns Typer commands and REPL adapters.
- `src/cpho_cli/builtin_skills/` owns packaged skill specs and prompt templates.
- `src/cpho_cli/vocabulary/` owns packaged taxonomy data.

**Barrel Files:** Use `__init__.py` selectively to expose domain APIs. `src/cpho_cli/core/index/__init__.py` is the import surface used by `src/cpho_cli/cli/app.py` for index commands. Avoid adding broad package-level re-exports unless callers already import from that package boundary.

---

*Convention analysis: 2026-05-28*
