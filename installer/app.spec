# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for CAPP Turning Planner application.

Build with:
  pyinstaller installer/app.spec

This creates a standalone Windows executable with all dependencies bundled.
Python runtime is NOT bundled to reduce installer size; user must have Python 3.12 installed.
"""

import sys
import os
from pathlib import Path

# Ensure we're using the right Python
assert sys.version_info >= (3, 12), "Python 3.12+ required"

# Project root directory
ROOT_DIR = Path(__file__).parent.parent

a = Analysis(
    [str(ROOT_DIR / "capp_app.py")],
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=[
        (str(ROOT_DIR / "requirements.txt"), "."),
    ],
    hiddenimports=[
        "step_analyzer",
        "capp_turning_planner",
        "chat_ollama",
        "tkinter",
        "numpy",
        "OCP",
        "cadquery",
        "OCP.Standard",
        "OCP.BRepBuilderAPI",
        "OCP.TopoDS",
        "OCP.BRepGProp",
        "OCP.GProp",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[
        "pytest",
        "notebook",
        "jupyter",
        "streamlit",  # Not used in GUI mode
        "matplotlib.backends.backend_qt5agg",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="CAPP_Turning_Planner",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Set to path of .ico file if available
)

# Optional: Create a directory distribution instead of one-file EXE
# Uncomment to use directory mode (faster startup, slightly larger install)
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name="CAPP_Turning_Planner",
# )
