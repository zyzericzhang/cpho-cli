Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("cpho-phase09-" + [System.Guid]::NewGuid().ToString("N"))
$Workspace = Join-Path $TempRoot "真实题库\2026芝麻物理\复赛试题"
New-Item -ItemType Directory -Path $Workspace -Force | Out-Null

$PdfPath = Join-Path $Workspace "第四届芝麻物理联考 理论试题.pdf"
Push-Location $Root
try {
  uv run python -c "from pathlib import Path; import fitz; p = Path(r'$PdfPath'); doc = fitz.open(); page = doc.new_page(); page.insert_text((72, 72), '中文路径 smoke: CPHO Phase 9'); doc.save(p)"
  uv run cpho diagnostics --packaging-smoke
  uv run cpho index $Workspace --dry-run

  if ($env:CPHO_REAL_WORKSPACE) {
    uv run cpho index $env:CPHO_REAL_WORKSPACE --dry-run
  }
}
finally {
  Pop-Location
  Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue
}
