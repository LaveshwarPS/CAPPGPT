# STEP File Analyzer

A Python script for analyzing STEP files and counting cylindrical faces in 3D CAD models.

## Features

- ✅ Reads STEP (.step/.stp) files using OpenCASCADE
- 🔍 Analyzes 3D geometry and identifies cylindrical faces
- 📊 Provides detailed analysis results
- 🔧 Cross-platform compatibility (Windows, macOS, Linux)
- 📁 Automatic STEP file detection in current directory

## Installation

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run as a Web App (Streamlit)
```bash
pip install -r requirements.txt
streamlit run app.py
```

Upload a `.step`/`.stp` file in the sidebar. Toggle "Force demo mode" if you don't have `cadquery-ocp` installed (uses mock data).

### Method 1: Auto-detect STEP file
Place a STEP file in the same directory and run:
```bash
python step_analyzer.py
```

### Method 2: Specify file path
```bash
python step_analyzer.py "path/to/your/file.step"
```

### Example Output
```
🔧 STEP File Analyzer - Cylindrical Face Counter
==================================================
✅ Successfully imported OCP libraries
🔗 Using OpenCASCADE binding: OCP
📁 Found STEP file: smol gear v1.step
📖 Reading STEP file: smol gear v1.step
🔍 Analyzing geometry...

==================================================
📊 ANALYSIS RESULTS
==================================================
📄 STEP File: smol gear v1.step
🔵 Cylindrical Faces: 178
✅ Analysis completed successfully!
```

## Supported File Formats

- `.step` files
- `.stp` files

## Requirements

- Python 3.8+
- cadquery-ocp (OpenCASCADE binding)
- numpy, matplotlib, vtk (auto-installed with cadquery-ocp)

## Troubleshooting

**Import Error**: If you get import errors, make sure cadquery-ocp is installed:
```bash
pip install cadquery-ocp
```

**File Not Found**: Ensure your STEP file is in the current directory or provide the full path.

**Permission Error**: Make sure you have read permissions for the STEP file.

## Packaging (Windows EXE)

Build a single-file executable that launches the Streamlit app:

```bat
build_windows.bat
```

The built file will be at `dist\\StepMachinabilityAnalyzer.exe`. Double-click it to run; it will open the Streamlit app in your default browser. If you see firewall prompts, allow local network access.

### Custom App Icon

Place an `app.ico` in the project root before running the build script. The icon will be embedded into the EXE automatically. If the file is missing, the default PyInstaller icon is used.

## Technical Details

This script uses the OpenCASCADE Technology (OCCT) library through the OCP Python binding to:

1. Load STEP files using `STEPControl_Reader`
2. Traverse the geometric topology using `TopExp_Explorer`
3. Identify faces and extract their underlying surfaces
4. Classify surfaces as cylindrical using `GeomAdaptor_Surface`

## License

This project is part of a Final Year Project (September 2025).