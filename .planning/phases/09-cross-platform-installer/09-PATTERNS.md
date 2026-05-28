# Phase 09: cross-platform-installer - Pattern Map

**Gathered:** 2026-05-28
**Status:** Ready for planning

## Files and Closest Existing Analogs

| Planned Area | New/Modified Files | Closest Existing Pattern | Notes |
|---|---|---|---|
| Windows CI | `.github/workflows/windows-compat.yml` | No existing workflow | Repo has `.github/` only for issue templates/assets. Use standard uv setup and keep commands explicit. |
| Phase acceptance tests | `tests/test_phase09_windows_acceptance.py` | `tests/test_phase06_acceptance.py`, `tests/test_phase07_acceptance.py`, `tests/test_phase08_acceptance.py` | Prior phases use a single phase acceptance file to prove end-to-end requirements. |
| Packaging scripts/spec | `packaging/cpho.spec`, `packaging/build_windows.ps1`, `packaging/smoke_packaged_windows.ps1`, `packaging/installer.iss` | No existing packaging directory | Keep as isolated build artifacts; do not mix with runtime package modules. |
| Update check core | `src/cpho_cli/core/update_check.py`, `src/cpho_cli/models/update.py` | `src/cpho_cli/core/community_sync.py`, `src/cpho_cli/core/model_catalog.py`, `src/cpho_cli/core/llm.py` | Existing HTTP code uses `httpx`, typed models, short wrappers, and tests with `httpx.MockTransport`. |
| CLI version/update command | `src/cpho_cli/cli/app.py` | Existing Typer subcommands in same file | Add narrow command surface; avoid refactoring command registration. |
| REPL startup notice | `src/cpho_cli/cli/repl/app.py`, `src/cpho_cli/cli/repl/display.py` | Existing `display.warn/info` and `ReplApp.run()` banner flow | Check update after banner with timeout and fail closed on network errors. |
| Installer docs | `README.md`, `docs/user/install.md`, `docs/user/README.md` | Existing `docs/user/*.md` topic pages | Docs are concise command-first pages; add install page and link from README docs list. |
| Verification doc | `docs/phase9-verification.md` | `docs/phase6-verification.md`, `docs/phase7-verification.md`, `docs/phase8-verification.md` | Record targeted tests, full pytest, ruff, Windows CI evidence, and packaging smoke status. |

## Source Patterns to Preserve

### Typer CLI

`src/cpho_cli/cli/app.py` keeps all top-level Typer commands in one module and maps exceptions to `typer.BadParameter`. New commands should follow that style instead of introducing a new command framework.

### REPL Startup

`src/cpho_cli/cli/repl/app.py` currently prints `display.banner(self.session)` and then enters the prompt loop. Any update notice should be short, non-blocking in failure cases, and placed after the banner so startup still works offline.

### HTTP Testing

`tests/test_llm.py`, `tests/test_model_catalog.py`, and `tests/test_phase08_acceptance.py` use `httpx.MockTransport`. Update-check tests should follow that pattern to avoid real network calls.

### Package Data

`pyproject.toml` is the source of truth for package data. Packaging smoke must verify the bundled executable can read skill prompts, vocabulary YAML, and model catalog JSON, not just import Python modules.

### Real Workspace Shape

Tests should synthesize nested Chinese paths and filenames based on `/Users/ericzhang/Desktop/物理竞赛资料`, but not commit private data. Smoke scripts may accept `CPHO_REAL_WORKSPACE` for local validation against the actual folder.

## Pattern Gaps

- No release workflow exists; Phase 9 will establish the first CI/release workflow conventions.
- No current version command exists; version and update check need a small new runtime seam.
- No packaging directory exists; keep the spike self-contained and do not add runtime dependencies unless the spike proves they are required.

## PATTERN MAPPING COMPLETE

