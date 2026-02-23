#!/usr/bin/env pwsh
<#
.SYNOPSIS
Build script for CAPP Turning Planner Windows installer and executable.

.DESCRIPTION
This PowerShell script automates the complete build process:
1. Clean previous builds
2. Install/upgrade PyInstaller
3. Build the standalone EXE with PyInstaller
4. Build the Windows installer with Inno Setup (optional)

.PARAMETER SkipInnoSetup
Skip the Inno Setup installer build (just build the EXE).

.PARAMETER Version
Version number for the build (default: read from VERSION file or 1.0.0).

.EXAMPLE
# Build everything
.\installer\build.ps1

# Build just the EXE
.\installer\build.ps1 -SkipInnoSetup

# Build with custom version
.\installer\build.ps1 -Version "1.0.1"

#>

param(
    [switch]$SkipInnoSetup = $false,
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Header($message) {
    Write-Host "`n════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host $message -ForegroundColor Cyan
    Write-Host "════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "⚠️  $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
}

# Get script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$distDir = Join-Path $projectRoot "dist"
$buildDir = Join-Path $projectRoot "build"

Write-Header "CAPP Turning Planner Build System"
Write-Host "Project Root: $projectRoot"
Write-Host "Version: $Version"
Write-Host "SkipInnoSetup: $SkipInnoSetup`n"

# Check prerequisites
Write-Header "Checking Prerequisites"

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found on PATH"
    Write-Host "Install from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Success "Python found: $pythonVersion"

# Check for venv
if (-not (Test-Path (Join-Path $projectRoot "venv312"))) {
    Write-Warning "Virtual environment not found. Creating venv312..."
    python -m venv (Join-Path $projectRoot "venv312")
}

# Activate venv
$activateScript = Join-Path $projectRoot "venv312\Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Error "Cannot find venv activation script"
    exit 1
}

Write-Success "Virtual environment found"

# Check Inno Setup (if not skipping)
if (-not $SkipInnoSetup) {
    $innoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if (-not (Test-Path $innoSetupPath)) {
        Write-Warning "Inno Setup not found at: $innoSetupPath"
        Write-Host "Install from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
        $SkipInnoSetup = $true
    } else {
        Write-Success "Inno Setup found"
    }
}

# Clean previous builds
Write-Header "Cleaning Previous Builds"
if (Test-Path $distDir) {
    Remove-Item -Recurse -Force $distDir
    Write-Success "Cleaned $distDir"
}

if (Test-Path $buildDir) {
    Remove-Item -Recurse -Force $buildDir
    Write-Success "Cleaned $buildDir"
}

# Activate virtual environment and install dependencies
Write-Header "Setting Up Environment"

& $activateScript
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to activate virtual environment"
    exit 1
}

Write-Success "Virtual environment activated"

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip -q
if ($LASTEXITCODE -ne 0) {
    Write-Warning "pip upgrade had issues, continuing anyway..."
}

# Install requirements
Write-Host "Installing dependencies from requirements.txt..."
pip install -r (Join-Path $projectRoot "requirements.txt") -q
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install requirements"
    exit 1
}

Write-Success "Dependencies installed"

# Install PyInstaller
Write-Host "Installing PyInstaller..."
pip install pyinstaller -q
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install PyInstaller"
    exit 1
}

Write-Success "PyInstaller installed"

# Build EXE with PyInstaller
Write-Header "Building Standalone EXE with PyInstaller"

$specFile = Join-Path $scriptDir "app.spec"
if (-not (Test-Path $specFile)) {
    Write-Error "Spec file not found: $specFile"
    exit 1
}

Write-Host "Building from spec: $specFile"
Write-Host "This may take several minutes..."

pyinstaller $specFile --distpath $distDir --buildpath $buildDir --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller build failed"
    exit 1
}

Write-Success "EXE built successfully: $distDir\CAPP_Turning_Planner\CAPP_Turning_Planner.exe"

# Test the built EXE
Write-Header "Verifying Built EXE"
$exePath = Join-Path $distDir "CAPP_Turning_Planner\CAPP_Turning_Planner.exe"
if (Test-Path $exePath) {
    Write-Success "EXE exists and is ready: $exePath"
    $exeSize = (Get-Item $exePath).Length / 1MB
    Write-Host "EXE size: {0:F1} MB`n" -f $exeSize
} else {
    Write-Error "EXE not found after build"
    exit 1
}

# Build Inno Setup installer
if (-not $SkipInnoSetup) {
    Write-Header "Building Windows Installer with Inno Setup"
    
    $issFile = Join-Path $scriptDir "installer.iss"
    $innoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    
    Write-Host "Building installer from: $issFile"
    & $innoSetupPath $issFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Installer built successfully"
        Get-ChildItem (Join-Path $projectRoot "dist") -Filter "CAPP_Turning_Planner_Setup_*.exe" | ForEach-Object {
            $size = $_.Length / 1MB
            Write-Success "Installer: $($_.Name) ({0:F1} MB)" -f $size
        }
    } else {
        Write-Error "Inno Setup build failed"
        exit 1
    }
} else {
    Write-Host "⏭️  Skipping Inno Setup installer build" -ForegroundColor Yellow
    Write-Host "To build the installer later, run: .\installer\build.ps1 -SkipInnoSetup:\$false`n"
}

# Summary
Write-Header "Build Complete!"
Write-Host "Build Outputs:"
Write-Host "  • EXE: $distDir\CAPP_Turning_Planner\CAPP_Turning_Planner.exe"
Write-Host "  • Installer: $distDir\CAPP_Turning_Planner_Setup_*.exe (if built)"
Write-Host ""
Write-Host "Next Steps:"
Write-Host "  1. Test the EXE: Run the .exe file directly"
Write-Host "  2. Distribute: Copy the installer .exe to users"
Write-Host "  3. Users should have Python 3.12+ installed"
Write-Host ""
