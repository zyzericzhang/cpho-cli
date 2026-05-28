# Phase 9 Packaging Spike Report

## PyInstaller result

Status: populated by the `Packaging spike` GitHub Actions workflow on `windows-2022`.

The candidate spec is `packaging/cpho.spec`. It builds a console `onedir` executable named `cpho`, disables UPX, collects `cpho_cli`, `rapidocr`, and `onnxruntime`, and explicitly includes bundled skills, prompts, vocabulary, and model catalog data.

The CI workflow runs:

```powershell
pwsh -NoProfile -File packaging/build_windows.ps1
```

## Nuitka result

Status: populated by the `Packaging spike` GitHub Actions workflow on `windows-2022`.

The fallback script attempts a standalone Nuitka build and records elapsed time, output size, exit code, and failure reason without treating "Nuitka unsuitable" as a malformed-script failure.

The CI workflow runs:

```powershell
pwsh -NoProfile -File packaging/build_nuitka_windows.ps1
```

## Bundle size

Status: populated by the `Packaging spike` GitHub Actions workflow on `windows-2022`.

Expected first-pass range remains 300-500 MB because the bundle includes Python, PyMuPDF, ONNX Runtime, RapidOCR, and CPHO package data. The build scripts append measured sizes here after execution.

## Clean-VM smoke

Status: populated by the `Packaging spike` GitHub Actions workflow on `windows-2022`.

The CI workflow runs this against each produced executable and uploads the filled report as an artifact:

```powershell
pwsh -NoProfile -File packaging/smoke_packaged_windows.ps1 -ExecutablePath .\dist\cpho\cpho.exe
```

The smoke covers `--help`, `diagnostics --packaging-smoke`, `version` when available, and `index --dry-run` against a generated nested Chinese workspace.

## SmartScreen/signing risk

Unsigned Windows installers and executables may show Microsoft Defender SmartScreen reputation warnings, especially for first releases. A code-signing certificate can improve publisher identity but does not guarantee first-download warning suppression. v1.1 should document this honestly and avoid advising users to disable Defender globally.

## Mac scope note

Phase 9 context chooses a documented macOS install path rather than a `.dmg`: Apple Silicon users get the primary Homebrew/command-line path, Intel Mac users get pipx/uv fallback docs, and Apple Developer ID signing is out of scope for v1.1.

## Recommendation

The authored scripts are ready for the Windows spike. The source-controlled report is intentionally a template; the authoritative filled report is the `phase9-spike-report` artifact from the `Packaging spike` GitHub Actions workflow.

Recommendation: continue-spike
