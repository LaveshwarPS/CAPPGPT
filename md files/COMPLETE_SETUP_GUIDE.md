# 🔧 CAPP Application Suite - Complete Setup & Usage Guide

## Overview

You now have a complete **Computer-Aided Process Planning (CAPP) System** for turning operations with multiple interfaces:

1. **capp_app.py** - Professional GUI with table display (RECOMMENDED)
2. **browser.py** - Terminal-based file browser
3. **batch_optimizer.py** - Batch processing multiple files
4. **step_analyzer.py** - Command-line analysis

---

## 🚀 Quick Start

### Easiest: Double-Click Launcher
1. Open File Explorer
2. Navigate to `C:\Users\Adm\Desktop\CAPP-AI project`
3. Double-click **`launch_capp.bat`**
4. GUI application opens automatically ✨

### Alternative: PowerShell
```powershell
cd "C:\Users\Adm\Desktop\CAPP-AI project"
.\venv312\Scripts\Activate.ps1
python capp_app.py
```

---

## 📋 Application Comparison

| Feature | GUI App | Terminal Browser | Batch | CLI |
|---------|---------|------------------|-------|-----|
| File Upload | ✅ Easy | ✅ Menu | ✅ Auto | ✅ Manual |
| Process Plan | ✅ Table View | ✅ Text | ✅ JSON | ✅ Text |
| AI Recommendations | ✅ Tab | ✅ Yes | ✅ JSON | ✅ Text |
| Single File | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Multiple Files | ❌ One at a time | ❌ One at a time | ✅ Batch | ❌ One at a time |
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

---

## 📖 User Guides

### For GUI Application
See: **`CAPP_APP_GUIDE.md`** (in project folder)

### For Terminal Browser
```powershell
python browser.py
```

### For Batch Processing
```powershell
python batch_optimizer.py --help
```

### For Command-Line
```powershell
python step_analyzer.py --help
```

---

## 🎯 GUI Application (capp_app.py)

### Main Features

**Upload Section:**
- Browse and select STEP files
- Clear selection
- Status display

**Options:**
- AI Recommendations toggle
- JSON export toggle
- AI Model selection (phi, llama2, neural-chat)

**Results Display (4 Tabs):**
1. **Operations** - Turning operations with parameters
2. **Tools** - Required tool specifications
3. **Summary** - Analysis overview
4. **AI Recommendations** - Optimization suggestions

### Workflow
```
Upload STEP File
    ↓
Configure Options
    ↓
Click "Analyze"
    ↓
View Results in Tables
    ↓
(Optional) Export Results
```

---

## 🎨 What the GUI Shows

### Operations Table Example
```
Op | Name              | Type      | Tool           | Speed | Feed  | DOC  | Time
───┼──────────────────┼───────────┼────────────────┼───────┼───────┼──────┼──────
1  | Face & Center    | facing    | Facing Insert  | 1,212 | 0.15  | 1.0  | 2.0
3  | Finish Turning   | turning   | Finishing ins. | 1,455 | 0.1   | 0.5  | 10.0
5  | Threading        | threading | Threading ins. | 242   | 0.5   | 0.5  | 2.5
```

### Tools Table Example
```
# | Name          | Type         | Material | Coating | Purpose
──┼───────────────┼──────────────┼──────────┼─────────┼──────────────────────
1 | Facing Insert | CNMG 432 M08 | Carbide  | TiAlN   | For facing operations
2 | Turning Insert| VNMG 431     | Carbide  | TiAlN   | For rough/finish turning
3 | Threading Ins.| TT09T304     | Carbide  | TiN     | For external threading
```

---

## ⚡ Quick Commands

### Launch GUI
```powershell
.\venv312\Scripts\Activate.ps1; python capp_app.py
```

### Launch Terminal Browser
```powershell
.\venv312\Scripts\Activate.ps1; python browser.py
```

### Batch Process All Files
```powershell
.\venv312\Scripts\Activate.ps1; python batch_optimizer.py
```

### Batch Process with AI
```powershell
.\venv312\Scripts\Activate.ps1; python batch_optimizer.py --output results_with_ai.json
```

### Analyze Single File (CLI)
```powershell
.\venv312\Scripts\Activate.ps1; python step_analyzer.py "path\to\file.step" --capp-turning --ai
```

---

## 📊 Results You'll Get

### From GUI Application
- ✅ Formatted tables (Operations, Tools)
- ✅ Summary statistics
- ✅ AI recommendations (if enabled)
- ✅ Export to TXT or JSON

### From Terminal Browser
- ✅ Full analysis report
- ✅ Process plan text
- ✅ AI recommendations (if enabled)
- ✅ JSON export (if enabled)

### From Batch Optimizer
- ✅ Summary JSON with all files
- ✅ Individual JSON for each file
- ✅ Statistics across all parts

---

## 🔧 System Information

- **Python**: 3.13.1
- **Virtual Environment**: `venv312` (Python 3.12, required for OCP)
- **OCP Library**: cadquery-ocp 7.8.1.1
- **Ollama Model**: phi (for AI)
- **GUI Framework**: tkinter (built-in)

---

## 📁 Project Files

### Core Modules
- `step_analyzer.py` - STEP file analysis engine
- `capp_turning_planner.py` - Process planning logic
- `cad_ai_analyzer.py` - AI analysis
- `chat_ollama.py` - Ollama integration

### Applications
- `capp_app.py` ⭐ **GUI Application (RECOMMENDED)**
- `browser.py` - Terminal file browser
- `batch_optimizer.py` - Batch processing
- `launch_capp.py` - Python launcher
- `launch_capp.bat` - Windows batch launcher

### Documentation
- `CAPP_APP_GUIDE.md` - GUI guide
- `CAPP_TURNING_GUIDE.md` - CAPP reference
- `AI_OPTIMIZATION_GUIDE.md` - AI tuning guide
- `README.md` - Project overview

---

## 🎓 Learning Path

### For Beginners
1. Double-click `launch_capp.bat`
2. Click "📂 Browse & Select STEP File"
3. Select a sample STEP file
4. Click "🚀 Analyze & Generate Plan"
5. Review results in tabs

### For Advanced Users
1. Use `batch_optimizer.py` for multiple files
2. Customize AI prompts in `capp_turning_planner.py`
3. Export JSON for data processing
4. Integrate into CAM software

### For Developers
1. Review `step_analyzer.py` for geometry analysis
2. Study `capp_turning_planner.py` for process planning
3. Check `cad_ai_analyzer.py` for AI integration
4. Modify as needed for custom features

---

## 🆘 Troubleshooting

### GUI Won't Open
```powershell
# Check Python installation
python --version

# Activate environment manually
.\venv312\Scripts\Activate.ps1

# Run directly
python capp_app.py
```

### File Upload Fails
- Make sure file is `.step` or `.stp` format
- Check file is not corrupted
- Ensure file path has no special characters

### Analysis Hangs
- Check if Ollama is running (if using AI)
- Try disabling AI recommendations
- Check system memory

### No Tables Display
- Verify part has turning score ≥ 40
- Try different STEP file
- Check terminal for error messages

---

## 🎯 Common Use Cases

### Case 1: Single Part Analysis
```
1. Launch capp_app.py
2. Upload STEP file
3. Enable AI recommendations
4. Click "Analyze"
5. Review operations and tools
6. Export results for documentation
```

### Case 2: Batch Production Planning
```
1. Use batch_optimizer.py
2. Processes all STEP files in folder
3. Generates JSON for each
4. Creates summary report
5. Identifies suitable vs unsuitable parts
```

### Case 3: Design Optimization
```
1. Upload design STEP file
2. Review process plan
3. Note complex operations
4. Modify design in CAD
5. Re-analyze to verify improvements
```

---

## 📈 Performance Tips

### For Faster Analysis
- Use `phi` model instead of `llama2`
- Disable AI recommendations
- Close other applications
- Use smaller STEP files

### For Better Recommendations
- Use `llama2` or `neural-chat` model
- Enable AI recommendations
- Provide detailed STEP files
- Include material information in filename

---

## 🚀 Next Steps

1. ✅ **Immediate**: Try the GUI with a sample file
2. 📊 **Short Term**: Analyze multiple parts for comparison
3. 🤖 **Medium Term**: Experiment with AI models
4. 🔗 **Long Term**: Integrate with CAM software

---

## 📞 Quick Reference

| Need | Command | File |
|------|---------|------|
| Launch GUI | Double-click `launch_capp.bat` | `capp_app.py` |
| Terminal Browser | `python browser.py` | `browser.py` |
| Batch Processing | `python batch_optimizer.py` | `batch_optimizer.py` |
| Help | Read `CAPP_APP_GUIDE.md` | Documentation |
| Custom Analysis | `python step_analyzer.py --help` | `step_analyzer.py` |

---

## 🎉 You're All Set!

Everything is configured and ready to use:
- ✅ Python environment
- ✅ OCP libraries
- ✅ Ollama integration
- ✅ Multiple applications
- ✅ Complete documentation

**Start with:** `launch_capp.bat` (easiest!)

**Enjoy your CAPP system!** 🚀

