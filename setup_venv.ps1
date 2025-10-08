#requires -Version 5.1
<#
.SYNOPSIS
Sets up the Python virtual environment for the mediateca-to-omeka project.

.DESCRIPTION
Ensures Python 3.8+, creates or reuses the project virtual environment, upgrades pip, and installs
the project in editable mode. All actions are logged to the logs directory via Start-Transcript.

.EXAMPLE
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup_venv.ps1
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
if (-not $projectRoot) {
    $projectRoot = (Get-Location).ProviderPath
}

Push-Location -LiteralPath $projectRoot
$transcriptStarted = $false
$venvActivated = $false
$exitCode = 0

try {
    $logDir = Join-Path -Path $projectRoot -ChildPath 'logs'
    if (-not (Test-Path -LiteralPath $logDir)) {
        Write-Host "Creating log directory at $logDir" -ForegroundColor Cyan
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $logFile = Join-Path -Path $logDir -ChildPath ("setup_{0}.log" -f $timestamp)

    Start-Transcript -Path $logFile -Append | Out-Null
    $transcriptStarted = $true

    Write-Host "Starting virtual environment setup for mediateca-to-omeka." -ForegroundColor Cyan

    try {
        $pythonCommand = Get-Command -Name python -ErrorAction Stop
    }
    catch {
        Write-Host "Python executable not found. Install Python 3.8 or newer and rerun the script." -ForegroundColor Red
        throw "Python executable not found."
    }

    $versionOutput = & $pythonCommand.Source --version 2>&1
    if (-not ($versionOutput -match 'Python\s+([0-9]+(?:\.[0-9]+)*)')) {
        throw "Unable to determine Python version from output: $versionOutput"
    }

    $pythonVersion = [Version]$matches[1]
    if ($pythonVersion -lt [Version]'3.8') {
        Write-Host "Detected Python version $($pythonVersion.ToString()). Python 3.8 or newer is required." -ForegroundColor Red
        throw "Python version must be 3.8 or newer."
    }

    Write-Host "Python $($pythonVersion.ToString()) detected at $($pythonCommand.Source)." -ForegroundColor Green

    $venvPath = Join-Path -Path $projectRoot -ChildPath 'venv'
    if (-not (Test-Path -LiteralPath $venvPath)) {
        Write-Host "Creating virtual environment at $venvPath" -ForegroundColor Cyan
        & $pythonCommand.Source -m venv $venvPath
    }
    else {
        Write-Host "Virtual environment already present at $venvPath" -ForegroundColor Yellow
    }

    $activateScript = Join-Path -Path $venvPath -ChildPath 'Scripts\Activate.ps1'
    if (-not (Test-Path -LiteralPath $activateScript)) {
        throw "Activation script not found at $activateScript. The virtual environment may be incomplete."
    }

    Write-Host "Activating virtual environment." -ForegroundColor Cyan
    . $activateScript
    $venvActivated = $true

    try {
        Write-Host "Upgrading pip in the virtual environment." -ForegroundColor Cyan
        python -m pip install --upgrade pip

        Write-Host "Installing project in editable mode (pip install -e .)." -ForegroundColor Cyan
        pip install -e .
    }
    finally {
        if ($venvActivated -and (Get-Command -Name deactivate -ErrorAction SilentlyContinue)) {
            Write-Host "Deactivating virtual environment." -ForegroundColor Cyan
            deactivate
        }
        $venvActivated = $false
    }

    Write-Host "Virtual environment setup completed successfully." -ForegroundColor Green
    Write-Host "Activate it manually when needed with:" -ForegroundColor Green
    Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor Green
}
catch {
    $exitCode = 1
    Write-Host "Environment setup failed: $_" -ForegroundColor Red
}
finally {
    if ($transcriptStarted) {
        try {
            Stop-Transcript | Out-Null
        }
        catch {
            Write-Host "Warning: Unable to stop transcript cleanly: $_" -ForegroundColor Yellow
        }
    }

    Pop-Location | Out-Null
}

exit $exitCode
