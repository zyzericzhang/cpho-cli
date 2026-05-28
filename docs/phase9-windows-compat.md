# Phase 9 Windows Compatibility

Run the baseline packaging diagnostics from the repo root:

```bash
uv run cpho diagnostics --packaging-smoke
```

Expected output is one `OK` or `FAIL` line for package version, package data, `fitz`, `rapidocr`, and `onnxruntime`. With `--packaging-smoke`, any `FAIL` exits nonzero.

Run the Windows smoke script:

```powershell
pwsh -NoProfile -File scripts/phase09_windows_smoke.ps1
```

The script creates a temporary nested Chinese workspace, writes a one-page PDF with PyMuPDF, runs diagnostics, and runs `cpho index <workspace> --dry-run`. To also check a real local workspace, set `CPHO_REAL_WORKSPACE` before running:

```powershell
$env:CPHO_REAL_WORKSPACE = "C:\path\to\物理竞赛资料"
pwsh -NoProfile -File scripts/phase09_windows_smoke.ps1
```
