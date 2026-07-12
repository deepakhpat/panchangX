$ErrorActionPreference = 'Stop'

$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectPath

Write-Host "Starting PanchangX local server..." -ForegroundColor Green

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Error "Python was not found. Install Python and try again."
    exit 1
}

$serverCommand = "$($python.Source) -m http.server 3000"
Write-Host "Serving files from $projectPath on http://localhost:3000" -ForegroundColor Cyan

Invoke-Expression $serverCommand
