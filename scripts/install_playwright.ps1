$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $root
$nodeDir = Join-Path $root "tools\node"
$env:PATH = "$nodeDir;" + $env:PATH

Set-Location (Join-Path $root "frontend")

Write-Host "Installing Playwright Chromium..."
& "$nodeDir\npx.cmd" playwright install chromium
Write-Host "Done."
