<# .SYNOPSIS
    Start the DivyaDrishti backend using a Python 3.11/3.12 virtual environment.

    pyswisseph provides prebuilt wheels for Python 3.11/3.12; using 3.14 or later
    requires a full C/C++ build toolchain and source compilation.
#>
param(
    [string]$VenvPath = ".venv311",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

# Prefer the Windows Python launcher so multiple installed versions are handled.
$py = "py"
$supportedVersions = @("3.11", "3.12")
$selectedVersion = $null
foreach ($v in $supportedVersions) {
    & $py -$v --version *>$null
    if ($LASTEXITCODE -eq 0) {
        $selectedVersion = $v
        break
    }
}

if (-not $selectedVersion) {
    Write-Error "Python 3.11 or 3.12 is required. Install it or update your PATH."
    exit 1
}

Write-Host "Using Python $selectedVersion"

if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment at $VenvPath ..."
    & $py -$selectedVersion -m venv $VenvPath
}

$pythonExe = Join-Path $VenvPath "Scripts\python.exe"
$venvVersion = & $pythonExe --version
Write-Host "Virtual-env interpreter: $venvVersion"

Write-Host "Installing/updating package dependencies ..."
& $pythonExe -m pip install -q --disable-pip-version-check -e . 2>&1 | Out-Null

Write-Host "Starting uvicorn on port $Port ..."
& $pythonExe -m uvicorn divyadrishti.main:app --reload --host 0.0.0.0 --port $Port
