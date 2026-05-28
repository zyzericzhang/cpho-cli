param(
  [Parameter(Mandatory = $true)]
  [string]$ExecutablePath,

  [string]$Label = "Clean-VM smoke"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Report = Join-Path $PSScriptRoot "SPIKE-REPORT.md"
$TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("cpho-packaged-smoke-" + [System.Guid]::NewGuid().ToString("N"))
$Workspace = Join-Path $TempRoot "真实题库\2026芝麻物理\复赛试题"
New-Item -ItemType Directory -Path $Workspace -Force | Out-Null

function Invoke-SmokeStep {
  param(
    [string]$Name,
    [scriptblock]$Command
  )
  try {
    & $Command
    Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- PASS $Name"
  }
  catch {
    Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- FAIL $Name`: $($_.Exception.Message)"
    throw
  }
}

Push-Location $Root
try {
  uv run python -c "from pathlib import Path; import fitz; p = Path(r'$Workspace') / '第四届芝麻物理联考 理论试题.pdf'; doc = fitz.open(); page = doc.new_page(); page.insert_text((72, 72), 'packaged CPHO smoke'); doc.save(p)"

  Add-Content -LiteralPath $Report -Encoding UTF8 -Value ""
  Add-Content -LiteralPath $Report -Encoding UTF8 -Value "## $Label"
  Invoke-SmokeStep "help" { & $ExecutablePath --help | Out-Null }
  Invoke-SmokeStep "diagnostics" { & $ExecutablePath diagnostics --packaging-smoke | Out-Null }
  try {
    $VersionOutput = & $ExecutablePath version 2>$null
    if ($LASTEXITCODE -ne 0 -or -not ($VersionOutput -match "cpho-cli")) {
      Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- PENDING update command"
    }
    else {
      Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- PASS version"
    }
  }
  catch {
    Add-Content -LiteralPath $Report -Encoding UTF8 -Value "- PENDING update command"
  }
  Invoke-SmokeStep "Chinese workspace dry-run" { & $ExecutablePath index $Workspace --dry-run | Out-Null }
}
finally {
  Pop-Location
  Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue
}
