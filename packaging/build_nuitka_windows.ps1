Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Report = Join-Path $PSScriptRoot "SPIKE-REPORT.md"
$OutputDir = Join-Path $Root "build\nuitka"
$EntryPoint = Join-Path $OutputDir "cpho_entry.py"

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
Set-Content -LiteralPath $EntryPoint -Encoding UTF8 -Value @"
from cpho_cli.cli.app import app

app()
"@

Push-Location $Root
try {
  $Started = Get-Date
  $Args = @(
    "run", "--with", "nuitka", "python", "-m", "nuitka",
    "--standalone",
    "--output-dir=build/nuitka",
    "--include-package-data=cpho_cli",
    "--include-package=rapidocr",
    "--include-package=onnxruntime",
    "--include-data-dir=src/cpho_cli/builtin_skills=cpho_cli/builtin_skills",
    "--include-data-dir=src/cpho_cli/core/index/prompts=cpho_cli/core/index/prompts",
    "--include-data-dir=src/cpho_cli/core/splitting/prompts=cpho_cli/core/splitting/prompts",
    "--include-data-dir=src/cpho_cli/core/knowledge/prompts=cpho_cli/core/knowledge/prompts",
    "--include-data-dir=src/cpho_cli/vocabulary=cpho_cli/vocabulary",
    "--include-data-dir=src/cpho_cli/data/model_catalog=cpho_cli/data/model_catalog",
    $EntryPoint
  )
  & uv @Args
  $ExitCode = $LASTEXITCODE
  $Elapsed = (Get-Date) - $Started
  $DistDir = Join-Path $OutputDir "cpho_entry.dist"
  if (Test-Path $DistDir) {
    $SizeBytes = (Get-ChildItem -LiteralPath $DistDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
  }
  else {
    $SizeBytes = 0
  }
  $SizeMb = [Math]::Round($SizeBytes / 1MB, 2)

  Add-Content -LiteralPath $Report -Encoding UTF8 -Value ""
  Add-Content -LiteralPath $Report -Encoding UTF8 -Value "## Nuitka result"
  Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- Command: ``uv $($Args -join ' ')``"
  Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- Exit code: $ExitCode"
  Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- Elapsed: $([Math]::Round($Elapsed.TotalSeconds, 1))s"
  Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- Output size: ${SizeMb} MB"
  if ($ExitCode -ne 0) {
    Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- Failure reason: Nuitka trial failed; inspect console output above."
  }

  exit 0
}
finally {
  Pop-Location
}
