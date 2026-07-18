$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $root
$nodeDir = Join-Path $root "tools\node"
$env:PATH = "$nodeDir;" + $env:PATH

Set-Location (Join-Path $root "frontend")

Write-Host "Running Playwright frontend verification..."
& "$nodeDir\npx.cmd" playwright test tests/e2e/verification.spec.ts --project=chromium --reporter=line
Write-Host "Done."
