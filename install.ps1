# Install the research-to-paper skills into Claude Code and/or Codex (Windows PowerShell).
# Usage:  .\install.ps1 -Target all|claude|codex
#   claude -> %USERPROFILE%\.claude\skills\    codex -> %USERPROFILE%\.codex\skills\
param([ValidateSet("all", "claude", "codex")][string]$Target = "all")

$Root   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Skills = Join-Path $Root "skills"
if (-not (Test-Path $Skills)) { Write-Error "skills/ not found at $Skills"; exit 1 }

function Copy-Skills($dst) {
  New-Item -ItemType Directory -Force -Path $dst | Out-Null
  Get-ChildItem -Directory $Skills | ForEach-Object {
    $target = Join-Path $dst $_.Name
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Copy-Item -Recurse $_.FullName $target
  }
}
function Install-Claude { $d = Join-Path $HOME ".claude\skills"; Copy-Skills $d; Write-Host "OK Claude Code skills -> $d" }
function Install-Codex  { $d = Join-Path $HOME ".codex\skills";  Copy-Skills $d; Write-Host "OK Codex skills -> $d" }

switch ($Target) {
  "all"    { Install-Claude; Install-Codex }
  "claude" { Install-Claude }
  "codex"  { Install-Codex }
}
Write-Host "Done. Restart Claude Code / Codex, then ask it to use research-to-paper."
