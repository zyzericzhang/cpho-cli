---
phase: 09-cross-platform-installer
plan: 09-01
subsystem: infra
tags: [windows, ci, packaging, diagnostics, unicode]
requires:
  - phase: 08-community-kb-error-handling
    provides: stable CLI surface and full pytest baseline
provides:
  - Windows compatibility GitHub Actions workflow
  - packaging diagnostics command for runtime dependency checks
  - synthetic Chinese-path Windows smoke script
  - Phase 9 Windows acceptance tests
affects: [installer, packaging, release, cli]
tech-stack:
  added: []
  patterns: [Typer diagnostics command, Windows CI smoke workflow, Chinese-path acceptance fixture]
key-files:
  created:
    - .github/workflows/windows-compat.yml
    - scripts/phase09_windows_smoke.ps1
    - docs/phase9-windows-compat.md
    - tests/test_phase09_windows_acceptance.py
  modified:
    - src/cpho_cli/cli/app.py
    - tests/test_cli.py
key-decisions:
  - "Diagnostics checks import fitz, rapidocr, and onnxruntime without calling external APIs."
  - "CI uses synthetic Chinese-path fixtures by default and only reads CPHO_REAL_WORKSPACE when explicitly configured."
patterns-established:
  - "Packaging smoke commands must prove package data lookup, binary imports, and Unicode workspace dry-runs."
requirements-completed: [INSTALLER-01]
duration: 8 min
completed: 2026-05-28
---

# Phase 09 Plan 01: Windows Compatibility Baseline Summary

**Windows CI and packaging diagnostics that prove CPHO can import binary dependencies, read bundled resources, and dry-run Chinese-path workspaces**

## Performance

- **Duration:** 8 min
- **Started:** 2026-05-28T14:49:38Z
- **Completed:** 2026-05-28T14:57:08Z
- **Tasks:** 4
- **Files modified:** 6

## Accomplishments

- Added `cpho diagnostics --packaging-smoke` with package version, package data, PyMuPDF, RapidOCR, and ONNX Runtime checks.
- Added a Windows GitHub Actions workflow on `windows-2022` running full pytest, CLI help, diagnostics, and the Phase 9 PowerShell smoke script.
- Added a synthetic nested Chinese workspace smoke script and docs, with optional `CPHO_REAL_WORKSPACE` validation for local private data.
- Added Phase 9 acceptance tests for Chinese path boundaries, Chinese table rendering, and package data coverage.

## Task Commits

Each task was committed atomically:

1. **Task 1: Runtime diagnostics command** - `a3fb6bb` (feat)
2. **Task 2: Windows CI workflow** - `bd09503` (ci)
3. **Task 3: Windows smoke script** - `26c9fcf` (test)
4. **Task 4: Phase 9 Windows acceptance tests** - `2220203` (test)

**Plan metadata:** committed separately with this summary.

## Files Created/Modified

- `.github/workflows/windows-compat.yml` - Windows runner workflow for full test and smoke coverage.
- `scripts/phase09_windows_smoke.ps1` - Synthetic Chinese workspace smoke script.
- `docs/phase9-windows-compat.md` - Smoke command documentation and `CPHO_REAL_WORKSPACE` instructions.
- `tests/test_phase09_windows_acceptance.py` - Acceptance tests for Windows-relevant assumptions.
- `src/cpho_cli/cli/app.py` - Added diagnostics command.
- `tests/test_cli.py` - Covered diagnostics in CLI tests.

## Decisions Made

- Diagnostics import heavy binary dependencies only; they do not instantiate OCR or call external APIs.
- CI never depends on the private real workspace; local users can opt in through `CPHO_REAL_WORKSPACE`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Local `pwsh` is not installed in this macOS environment, so `scripts/phase09_windows_smoke.ps1` could not be executed locally. The script is invoked by the new `windows-2022` GitHub Actions job, and local verification covered the workflow assertions plus Python acceptance tests.

## Verification

- `uv run cpho diagnostics --packaging-smoke` - passed.
- `uv run pytest tests/test_cli.py tests/test_phase09_windows_acceptance.py -q` - 7 passed.
- Workflow content assertion for `windows-2022`, `uv run pytest -q`, `uv run cpho --help`, `uv run cpho diagnostics --packaging-smoke`, and `scripts/phase09_windows_smoke.ps1` - passed.
- `pwsh -NoProfile -File scripts/phase09_windows_smoke.ps1` - not run locally because `pwsh` is unavailable; covered by Windows CI configuration.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Wave 2 can build on a diagnostics command and Windows CI baseline. The packaging spike should use `cpho diagnostics --packaging-smoke` as the first packaged-executable smoke check.

## Self-Check: PASSED

---
*Phase: 09-cross-platform-installer*
*Completed: 2026-05-28*
