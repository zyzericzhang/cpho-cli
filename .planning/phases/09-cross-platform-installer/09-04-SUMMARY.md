# Plan 09-04 Summary

## Completed

- Recorded the approved PyInstaller spike decision in `packaging/RELEASE-CHECKLIST.md`.
- Added `packaging/installer.iss` for wrapping `dist/cpho/**` into a Windows setup executable.
- Added `.github/workflows/release.yml`, triggered only by `v*` tags, to build PyInstaller on `windows-2022`, run packaged smoke, compile the Inno Setup installer, upload workflow artifacts, and upload the installer to GitHub Releases.
- Added `docs/user/install.md` and linked it from README and the user-doc index.
- Updated README scope so Phase 9 install work is no longer described as future work.

## Development/Release Split

- Development remains macOS local work plus ordinary tests.
- Windows PyInstaller and installer construction happen in GitHub Actions release jobs only.
- Ordinary pull-request and push validation are not burdened with installer construction.

## Verification

- `uv run pytest tests/test_docs_user.py -q`
  - Result: 2 passed.
- Release artifact structure check:
  - Result: `packaging/installer.iss` and `.github/workflows/release.yml` contain the required Windows runner, smoke, Inno Setup, artifact, and GitHub Release upload references.
