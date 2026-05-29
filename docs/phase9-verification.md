# Phase 9 Verification

Date: 2026-05-29
Branch: `main`

## Scope

Phase 9 delivered:

- Windows compatibility smoke and `cpho diagnostics --packaging-smoke`.
- A Windows packaging spike executed by GitHub Actions on `windows-2022`.
- PyInstaller as the approved Windows packaging path.
- `cpho version` and a short-timeout GitHub Release update check.
- A tag-triggered Windows release workflow that builds the PyInstaller onedir bundle, runs packaged smoke, compiles an Inno Setup installer, uploads an artifact, and uploads the installer to GitHub Releases.
- User install docs for Windows installer download and Mac command-line installation.

Development and release are intentionally separate:

- Development path: macOS local development plus ordinary tests.
- Release path: GitHub Actions `windows-2022` builds PyInstaller and the Windows installer only for `v*` tags.

## Commands Run

- `uv run pytest tests/test_update_check.py tests/test_repl_runtime.py -q`
  - Result: 11 passed, 5 PyMuPDF/SWIG deprecation warnings.
- `uv run cpho version`
  - Result: printed `cpho-cli 0.1.0` and `https://github.com/zyzericzhang/cpho-cli`.
- `uv run pytest tests/test_docs_user.py -q`
  - Result: 2 passed.
- Release artifact structure check:
  - Result: `packaging/installer.iss` and `.github/workflows/release.yml` contain the required Windows runner, smoke, Inno Setup, artifact, and GitHub Release upload references.
- `uv run pytest tests/test_phase09_windows_acceptance.py tests/test_update_check.py tests/test_phase09_acceptance.py -q`
  - Result: 13 passed.
- `uv run ruff check .`
  - Result: all checks passed.
- `uv run pytest -q`
  - Result: 471 passed, 5 PyMuPDF/SWIG deprecation warnings.

## GitHub Actions Evidence

- Packaging spike run: `26590319698`
  - Runner: `windows-2022`
  - Result: PyInstaller bundle produced, packaged smoke passed, artifact uploaded.
  - Nuitka result: timed out without producing an executable, so it is not the v1.1 main path.
- Windows compatibility run: `26590319699`
  - Runner: `windows-2022`
  - Result: tests, CLI help, packaging diagnostics, and Windows smoke passed.

## Release Smoke Status

The final Windows installer build is tag-triggered through `.github/workflows/release.yml`.

This local macOS verification did not compile the Inno Setup installer because installer construction belongs to the release workflow on a Windows runner. The workflow is guarded by acceptance tests so it remains tag-only and does not enter ordinary push/pull-request development validation.

## Notes

- No secrets were printed or written.
- SmartScreen docs describe the per-app warning path and do not tell users to disable Defender globally.
- Mac v1.1 distribution is documentation-only through Homebrew plus `uv tool install`; no `.dmg` is shipped.
