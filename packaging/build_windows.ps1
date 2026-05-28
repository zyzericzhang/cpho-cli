Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Report = Join-Path $PSScriptRoot "SPIKE-REPORT.md"
$DistDir = Join-Path $Root "dist\cpho"

Push-Location $Root
try {
  $Started = Get-Date
  uv run --with pyinstaller pyinstaller --clean --noconfirm packaging/cpho.spec
  $ExitCode = $LASTEXITCODE
  $Elapsed = (Get-Date) - $Started

  if (Test-Path $DistDir) {
    $SizeBytes = (Get-ChildItem -LiteralPath $DistDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
  }
  else {
    $SizeBytes = 0
  }
  $SizeMb = [Math]::Round($SizeBytes / 1MB, 2)

  Add-Content -LiteralPath $Report -Encoding UTF8 -Value ""
  Add-Content -LiteralPath $Report -Encoding UTF8 -Value "## PyInstaller result"
  Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- Command: ``uv run --with pyinstaller pyinstaller --clean --noconfirm packaging/cpho.spec``"
  Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- Exit code: $ExitCode"
  Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- Elapsed: $([Math]::Round($Elapsed.TotalSeconds, 1))s"
  Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- Bundle size: ${SizeMb} MB"

  if ($ExitCode -ne 0) {
    exit $ExitCode
  }
}
finally {
  Pop-Location
}
