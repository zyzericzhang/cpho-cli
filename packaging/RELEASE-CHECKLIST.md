# Phase 9 Release Checklist

Spike decision:

- Recommendation: build-installer
- User approval recorded: 2026-05-29, user agreed to choose PyInstaller.
- CI evidence: GitHub Actions run `26590319698` on `windows-2022` produced the PyInstaller bundle, passed packaged smoke, and uploaded artifacts.
- Nuitka status: paused for v1.1 because it exceeded the spike timeout without producing an executable.

Required release artifacts:

- [ ] PyInstaller onedir build passes through `packaging/build_windows.ps1`.
- [ ] Packaged smoke passes through `packaging/smoke_packaged_windows.ps1`.
- [ ] Inno Setup installer compiles from `packaging/installer.iss`.
- [ ] GitHub Release upload completes from `.github/workflows/release.yml`.
- [ ] SmartScreen documentation is present and does not tell users to disable Defender globally.
- [ ] Mac documentation is present and uses Homebrew plus `uv tool install`, not a `.dmg`.

Windows installer compile command:

```powershell
$env:CPHO_APP_VERSION = uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"
$env:CPHO_DIST_DIR = (Resolve-Path "dist/cpho").Path
$env:CPHO_INSTALLER_OUTPUT_DIR = (Resolve-Path "dist/installer").Path
& "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" packaging/installer.iss
```

Expected output:

```text
dist/installer/cpho-cli-<version>-windows-x64-setup.exe
```
