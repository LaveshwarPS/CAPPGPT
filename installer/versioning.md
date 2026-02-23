# Version Management Guide

This document explains how to manage version numbers for the CAPP Turning Planner project.

## Version Scheme

We use **Semantic Versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR** (1.0.0): Breaking changes, major features
- **MINOR** (1.1.0): New features, backwards compatible
- **PATCH** (1.0.1): Bug fixes

Example: `1.2.3` = Major version 1, Minor version 2, Patch 3

## Files to Update

When releasing a new version, update these files:

### 1. `installer/installer.iss`

```ini
#define MyAppVersion "1.0.0"
```

This version appears in:
- Windows installer file name: `CAPP_Turning_Planner_Setup_1.0.0.exe`
- Control Panel "Add/Remove Programs"
- Registry entries

### 2. `installer/app.spec` (Optional)

No version string in spec file, but update comments if needed.

### 3. Project README (Recommended)

Add to `README.md`:
```markdown
## Latest Version: 1.0.0

See [Changelog](CHANGELOG.md) for release notes.
```

### 4. `CHANGELOG.md` (Recommended)

Create a `CHANGELOG.md` in project root:

```markdown
# Changelog

## [1.0.0] - 2025-01-15

### Added
- Initial release
- Ollama integration with streaming support
- Tkinter GUI for STEP file analysis
- AI-powered process recommendations
- Health check for Ollama availability

### Fixed
- Thread safety issues in chat interface
- Configurable timeout for long-running AI queries
- Improved error messages

### Known Issues
- Ollama must be manually installed and started

## [0.9.0] - 2024-12-01

### Added
- Beta release
```

## Release Process

### Step 1: Update Version Number

Edit `installer/installer.iss`:

```ini
#define MyAppVersion "1.1.0"  ; Updated version
```

### Step 2: Update Changelog

Add entry to `CHANGELOG.md` with:
- Date
- Version number
- What changed (Added, Fixed, Removed, etc.)

### Step 3: Build the Release

```powershell
# Clean previous build
Remove-Item -Recurse dist, build -Force -ErrorAction SilentlyContinue

# Build with new version
.\installer\build.ps1

# Or manually:
pyinstaller installer/app.spec
# Then run Inno Setup
```

### Step 4: Test the Release

On a clean system:

```powershell
# Run the EXE directly
dist\CAPP_Turning_Planner\CAPP_Turning_Planner.exe

# Or run the installer
dist\CAPP_Turning_Planner_Setup_1.1.0.exe
```

Test:
- Application starts
- Chat with AI (Ollama) works
- File analysis completes
- UI is responsive

### Step 5: Tag in Git (Recommended)

```bash
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

## Version History Reference

Document your releases:

| Version | Date | Notes |
|---------|------|-------|
| 1.0.0 | 2025-01-15 | Initial stable release |
| 0.9.0 | 2024-12-01 | Beta release |

## Automatic Version Updates

To automate version updates across files, create a script:

```powershell
param([string]$NewVersion)

# Update installer.iss
(Get-Content installer/installer.iss) `
    -replace '#define MyAppVersion ".*"', "#define MyAppVersion `"$NewVersion`"" `
    | Set-Content installer/installer.iss

# Update README.md
(Get-Content README.md) `
    -replace 'Latest Version: [\d.]+', "Latest Version: $NewVersion" `
    | Set-Content README.md

Write-Host "✅ Updated version to $NewVersion"
```

Save as `update-version.ps1` and run:
```powershell
.\update-version.ps1 -NewVersion "1.1.0"
```

## Python Version Compatibility

Current configuration targets:

- **Python**: 3.12+ (required)
- **cadquery-ocp**: >=7.7.0 (requires Python 3.12+)
- **vtk**: ==9.3.1
- **numpy**: >=1.23.0

If you need to support older Python:

1. Test with target Python version
2. Update `requirements.txt` version constraints
3. Update this documentation
4. Update installer Python version check in `installer.iss`

## Distribution Version Tracking

When distributing:

1. **Version in filename**: `CAPP_Turning_Planner_Setup_1.0.0.exe`
2. **Version in installer**: Control Panel shows version
3. **Version in EXE**: Right-click EXE → Properties → Details → File version

All should match for consistency.

## Release Notes Template

When releasing, provide users with:

```
CAPP Turning Planner v1.0.0

What's New:
- Feature 1
- Feature 2
- Bug fix 1

System Requirements:
- Windows 10/11
- Python 3.12+
- Ollama (for AI features)
- 500 MB disk space

Installation:
1. Download CAPP_Turning_Planner_Setup_1.0.0.exe
2. Run installer
3. Install Ollama from https://ollama.com
4. Run CAPP application

Troubleshooting:
- See installer/README_build_installer.md
- Check that Ollama is running
```

## References

- Semantic Versioning: https://semver.org/
- Git Tagging: https://git-scm.com/book/en/v2/Git-Basics-Tagging
- Python Versioning: https://peps.python.org/pep-0440/
