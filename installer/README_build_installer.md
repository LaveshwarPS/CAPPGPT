# Building the CAPP Turning Planner Installer

This directory contains all the scripts and configuration needed to build a professional Windows installer for the CAPP Turning Planner application.

## Quick Start

### Option 1: Build Just the EXE (Recommended First Step)

```powershell
# From the project root directory
.\installer\build.ps1 -SkipInnoSetup
```

This creates a standalone `CAPP_Turning_Planner.exe` in `dist/CAPP_Turning_Planner/`.

### Option 2: Build Everything (EXE + Installer Setup)

```powershell
.\installer\build.ps1
```

This creates both the EXE and a Windows installer setup `.exe`.

## Prerequisites

### 1. Python 3.12+

The application requires **Python 3.12 or later**. Install from: https://www.python.org/downloads/

**Important**: During installation, check "Add Python to PATH"

Verify installation:
```powershell
python --version  # Should show 3.12+
```

### 2. Virtual Environment

The project uses `venv312` (Python 3.12 virtual environment). The build script creates it automatically if it doesn't exist.

Manual setup:
```powershell
python -m venv venv312
venv312\Scripts\Activate.ps1
```

### 3. Dependencies

All dependencies are listed in `requirements.txt` and installed automatically during build.

Key packages:
- `pyinstaller`: Builds standalone EXE
- `cadquery-ocp`: 3D CAD analysis
- `requests`: HTTP client for Ollama API
- `numpy`, `vtk`, `matplotlib`: Scientific computing
- `streamlit`: Optional web interface

### 4. Inno Setup (Optional, for installer .exe)

Download from: https://jrsoftware.org/isdl.php

Default install path: `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`

If Inno Setup is not found, the build script skips the installer creation but still builds the standalone EXE.

### 5. Ollama (Runtime Dependency)

Users will need **Ollama** installed to use AI features.

Download: https://ollama.com/download

The application will detect if Ollama is running and show appropriate status messages.

## Build Process

### What the `build.ps1` Script Does

1. **Validates environment** - Checks for Python, venv, and optional Inno Setup
2. **Cleans previous builds** - Removes `dist/` and `build/` directories
3. **Sets up venv** - Creates virtual environment if needed
4. **Installs dependencies** - Runs `pip install -r requirements.txt`
5. **Builds EXE** - Uses PyInstaller with `app.spec` configuration
6. **Builds Installer** - Uses Inno Setup to create Windows installer setup

### Build Output

The script creates:

```
dist/
├── CAPP_Turning_Planner/
│   ├── CAPP_Turning_Planner.exe  ← Standalone executable
│   ├── requirements.txt
│   ├── README.md
│   └── ... (all dependencies)
└── CAPP_Turning_Planner_Setup_1.0.0.exe  ← Installer (if Inno Setup available)
```

## Configuration Files

### `app.spec` (PyInstaller Configuration)

This file tells PyInstaller how to build the EXE:

- **Entry point**: `capp_app.py`
- **Hidden imports**: Modules that PyInstaller might miss (OCP, numpy, etc.)
- **Data files**: Resources to bundle
- **Icon**: Application icon (set to `None` by default)

Customize:
```python
# To add an icon:
icon=r"path\to\your\icon.ico",

# To change console/windowed mode:
console=False,  # No console window (True = show console)
```

### `installer.iss` (Inno Setup Configuration)

This file defines the Windows installer:

- **App metadata**: Name, version, publisher
- **Installation directory**: Default install location
- **Icons and shortcuts**: Desktop, Start Menu, etc.
- **Files**: What to include in the installer
- **Pre-installation checks**: Python 3.12 requirement

Customize:
```ini
#define MyAppVersion "1.0.0"          ; Change version here
#define MyAppPublisherURL "..."       ; Your project URL
```

## Version Management

### Updating Version Numbers

Update version in both files:

1. **`installer.iss`**:
   ```ini
   #define MyAppVersion "1.0.1"
   OutputBaseFilename=CAPP_Turning_Planner_Setup_{#MyAppVersion}
   ```

2. **`build.ps1`** (optional, for reference):
   ```powershell
   $Version = "1.0.1"
   ```

3. Or pass as parameter:
   ```powershell
   .\installer\build.ps1 -Version "1.0.1"
   ```

## Troubleshooting

### "Python 3.12 not found"

Install Python 3.12 from https://www.python.org/downloads/ and ensure it's added to PATH.

Verify:
```powershell
python --version
```

### "PyInstaller build failed"

Check for circular imports or missing hidden imports:

1. Add missing modules to `app.spec` in the `hiddenimports` list
2. Try a manual test: `pyinstaller --help`

### "Cannot find Inno Setup"

Install from https://jrsoftware.org/isdl.php or skip with:
```powershell
.\installer\build.ps1 -SkipInnoSetup
```

### EXE crashes on startup

The EXE might be missing dependencies. Check:

1. `requirements.txt` includes all imports
2. `hiddenimports` in `app.spec` includes all OCP/cadquery modules
3. Python version compatibility (3.12+ required for cadquery-ocp)

## Distribution

### For Users

1. **Simple**: Share the standalone EXE
   - No installation needed
   - Slower startup (first run loads all libraries)
   - Larger file size (~200-300 MB)

2. **Professional**: Use the Inno Setup installer
   - Easy installation to `C:\Program Files\...`
   - Fast startup (no re-extraction)
   - Creates Start Menu shortcuts
   - Uninstall support

### System Requirements

Users need:

- **Windows 10 or 11**
- **Python 3.12+** (for standalone EXE; bundled in full installer if we add it)
- **Ollama** (for AI features, must be installed separately)
- **~500 MB disk space** (EXE + dependencies)

### Installation Instructions

Provide users with:

```
1. Install Python 3.12 from https://www.python.org/downloads/
   (check "Add Python to PATH")

2. Install Ollama from https://ollama.com/download

3. Run: CAPP_Turning_Planner.exe
   OR
   Run: CAPP_Turning_Planner_Setup_1.0.0.exe (if using installer)

4. Start Ollama:
   - Run "ollama serve" in a terminal
   - OR start the Ollama app

5. Pull a model:
   ollama pull phi

6. Use the CAPP application!
```

## Advanced: Bundling Python Runtime

To bundle Python 3.12 in the installer (larger file, no Python dependency):

1. Download Python 3.12 embeddable archive from python.org
2. Extract to `installer/python312/`
3. Modify `installer.iss` to include Python files
4. Update installer to set `PYTHONHOME`

Note: This significantly increases installer size (~100+ MB).

## Support

For issues:

1. Check build output for specific errors
2. Verify all prerequisites are installed
3. Ensure Python 3.12+ is on PATH
4. Check `requirements.txt` for missing packages

## Next Steps

After building:

1. **Test locally**: Run the EXE directly
2. **Test fresh install**: Run the installer on a clean system
3. **Update version** in files before each release
4. **Sign the EXE** (optional, for production releases)
   - Code signing requires a certificate
   - Improves user trust and UAC prompts

## References

- PyInstaller: https://pyinstaller.org/
- Inno Setup: https://jrsoftware.org/isinfo.php
- Python: https://python.org/
- Ollama: https://ollama.com/
