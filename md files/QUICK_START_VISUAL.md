# 🚀 CAPP GUI Application - Visual Quick Start

## Launch the Application

### Option 1: Double-Click (Easiest) ⭐
```
1. Open File Explorer
2. Navigate to: C:\Users\Adm\Desktop\CAPP-AI project
3. Double-click: launch_capp.bat
4. Done! GUI opens instantly
```

### Option 2: Command Line
```powershell
cd "C:\Users\Adm\Desktop\CAPP-AI project"
.\.venv\Scripts\Activate.ps1
python capp_app.py
```

---

## Application Window Overview

```
╔════════════════════════════════════════════════════════════════════════════╗
║   🔧 CAPP Turning Process Planner - Professional Edition                  ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  LEFT PANEL                              RIGHT PANEL                      ║
║  ─────────────────────────────────────   ────────────────────────────     ║
║                                                                            ║
║  📁 FILE & OPTIONS                       📊 PROCESS PLAN RESULTS          ║
║  ────────────────────                                                     ║
║                                                                            ║
║  Selected File:                          [Operations] [Tools]            ║
║  ✓ cotter_3_v2.step                     [Summary]    [AI Recs]           ║
║                                                                            ║
║  [📂 Browse] [✕ Clear]                  ┌─────────────────────────────┐ ║
║                                         │ Op │ Name │ Tool │ Speed   │ ║
║  ─────────────────────────────           │ 1  │Face  │CNMG  │ 1,212  │ ║
║                                         │ 3  │Turn  │VNMG  │ 1,455  │ ║
║  ⚙️ ANALYSIS OPTIONS                    │ 5  │Thread│TT09  │ 242    │ ║
║  ────────────────────                   └─────────────────────────────┘ ║
║                                                                            ║
║  ☑ AI Optimization                                                         ║
║  ☑ Export to JSON                                                          ║
║  AI Model: [phi ▼]                                                         ║
║                                                                            ║
║  ─────────────────────────────                                            ║
║                                                                            ║
║  🎯 ACTIONS                                                                ║
║  ───────────                                                               ║
║                                                                            ║
║  [🚀 Analyze & Generate Plan]                                             ║
║  [📥 Export Results]                                                       ║
║                                                                            ║
║  ─────────────────────────────                                            ║
║                                                                            ║
║  Status: ✓ Complete                                                        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
```

---

## Step-by-Step Workflow

### STEP 1️⃣: Upload File
```
Click: 📂 Browse & Select STEP File
       ↓
    File Dialog Opens
       ↓
    Select your STEP file
       ↓
    File name appears in display
       ↓
    Status: "Ready - filename.step selected"
```

### STEP 2️⃣: Configure Options
```
Toggle Options as needed:
  ☑ AI Optimization (default: ON)
  ☑ Export to JSON (default: ON)
  
Select AI Model:
  φ (fast)
  λ (detailed)  
  ◇ (balanced)

Status: "Ready - waiting for analysis"
```

### STEP 3️⃣: Analyze
```
Click: 🚀 Analyze & Generate Plan
       ↓
    Status: "⏳ Analyzing..."
       ↓
    Process plan generated
       ↓
    Tables populate with data
       ↓
    Status: "✓ Complete - filename.step"
```

### STEP 4️⃣: Review Results
```
Check Tabs:

📋 Operations Tab
   ├─ Operation numbers
   ├─ Operation names
   ├─ Cutting speeds (RPM)
   ├─ Feed rates (mm/rev)
   └─ Estimated times

🔧 Tools Tab
   ├─ Tool IDs
   ├─ Tool names
   ├─ Tool types
   ├─ Materials
   ├─ Coatings
   └─ Purposes

📊 Summary Tab
   ├─ File info
   ├─ Machinability score
   ├─ Number of operations
   ├─ Total time
   └─ Export location

🤖 AI Recommendations
   ├─ Tool optimizations
   ├─ Speed/feed suggestions
   ├─ Coolant strategies
   ├─ Setup tips
   └─ Quality improvements
```

### STEP 5️⃣: Export (Optional)
```
Click: 📥 Export Results
       ↓
    Save Dialog Opens
       ↓
    Choose format:
    • .txt (formatted text)
    • .json (structured data)
       ↓
    Choose location
       ↓
    File saved successfully
```

---

## Table Display Examples

### Operations Table (Full Example)
```
╔════╦════════════════╦═══════════╦═════════════════╦═════════╦════════╦══════╦═══════╗
║ Op ║ Operation Name ║ Type      ║ Tool            ║ Speed   ║ Feed   ║ DOC  ║ Time  ║
║    ║                ║           ║                 ║ (RPM)   ║(mm/rev)║(mm)  ║(min)  ║
╠════╬════════════════╬═══════════╬═════════════════╬═════════╬════════╬══════╬═══════╣
║ 1  ║ Face & Center  ║ facing    ║ Facing Insert   ║ 1,212   ║ 0.15   ║ 1.0  ║ 2.0   ║
║    ║                ║           ║ (CNMG 432)      ║         ║        ║      ║       ║
╠════╬════════════════╬═══════════╬═════════════════╬═════════╬════════╬══════╬═══════╣
║ 3  ║ Finish Turning ║ turning   ║ Finishing Insert║ 1,455   ║ 0.1    ║ 0.5  ║ 10.0  ║
║    ║                ║           ║ (VNMG R0.4)     ║         ║        ║      ║       ║
╠════╬════════════════╬═══════════╬═════════════════╬═════════╬════════╬══════╬═══════╣
║ 5  ║ Threading      ║ threading ║ Threading Ins.  ║ 242     ║ 0.5    ║ 0.5  ║ 2.5   ║
║    ║                ║           ║ (TT09T304)      ║         ║        ║      ║       ║
╠════╬════════════════╬═══════════╬═════════════════╬═════════╬════════╬══════╬═══════╣
║ 6  ║ Grooving       ║ grooving  ║ Grooving Insert ║ 1,039   ║ 0.15   ║ 0.8  ║ 1.5   ║
║    ║                ║           ║ (MGMN 300-M)    ║         ║        ║      ║       ║
╠════╬════════════════╬═══════════╬═════════════════╬═════════╬════════╬══════╬═══════╣
║ 7  ║ Parting Off    ║ parting   ║ Parting Blade   ║ 646     ║ 0.08   ║ 10.0 ║ 1.0   ║
║    ║                ║           ║ (MGHR-3-M)      ║         ║        ║      ║       ║
╚════╩════════════════╩═══════════╩═════════════════╩═════════╩════════╩══════╩═══════╝
```

### Tools Table (Full Example)
```
╔═══╦════════════════╦══════════════════╦══════════╦═════════╦══════════════════════╗
║ # ║ Tool Name      ║ Type/Model       ║ Material ║ Coating ║ Purpose              ║
╠═══╬════════════════╬══════════════════╬══════════╬═════════╬══════════════════════╣
║ 1 ║ Facing Insert  ║ CNMG 432 M0804   ║ Carbide  ║ TiAlN   ║ For facing and end   ║
║   ║                ║                  ║          ║         ║ turning operations   ║
╠═══╬════════════════╬══════════════════╬══════════╬═════════╬══════════════════════╣
║ 2 ║ Turning Insert ║ VNMG 431         ║ Carbide  ║ TiAlN   ║ For rough and finish ║
║   ║                ║                  ║          ║         ║ turning              ║
╠═══╬════════════════╬══════════════════╬══════════╬═════════╬══════════════════════╣
║ 3 ║ Threading Ins. ║ TT09T304         ║ Carbide  ║ TiN     ║ For external         ║
║   ║                ║                  ║          ║         ║ threading            ║
╠═══╬════════════════╬══════════════════╬══════════╬═════════╬══════════════════════╣
║ 4 ║ Grooving Inser ║ MGMN 300-M       ║ Carbide  ║ TiAlN   ║ For grooving         ║
║   ║                ║                  ║          ║         ║ operations           ║
╠═══╬════════════════╬══════════════════╬══════════╬═════════╬══════════════════════╣
║ 5 ║ Parting Blade  ║ MGHR-3-M         ║ Carbide  ║ TiN     ║ For parting off      ║
║   ║                ║                  ║          ║         ║ finished parts       ║
╚═══╩════════════════╩══════════════════╩══════════╩═════════╩══════════════════════╝
```

---

## Status Indicators

### During Processing
```
Status: ⏳ Analyzing...
Color: Yellow/Orange
Meaning: Processing in progress, please wait
```

### After Success
```
Status: ✓ Complete - filename.step
Color: Green
Meaning: Analysis finished successfully, results displayed
```

### After Error
```
Status: ✗ Error: [error message]
Color: Red
Meaning: Analysis failed, check file and retry
```

### Ready State
```
Status: Ready
Color: Green
Meaning: Application ready for file selection
```

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open file dialog | No shortcut (use button) |
| Analyze | No shortcut (use button) |
| Scroll tables | Arrow keys or Mouse wheel |
| Copy from table | Ctrl+C (select then copy) |
| Switch tabs | Ctrl+Tab or click tab |

---

## File Types Supported

✅ **Supported:**
- `.step` (STEP format)
- `.stp` (STEP format, alternate extension)

❌ **Not Supported:**
- `.iges`, `.igs` (IGES format)
- `.stl` (STL format)
- `.obj`, `.fbx` (Other 3D formats)
- `.dwg`, `.dxf` (CAD drawings)

**Tip:** Convert other formats to STEP using your CAD software (Fusion 360, SolidWorks, etc.)

---

## Common File Sizes

| Part Complexity | File Size |
|-----------------|-----------|
| Simple (box, cylinder) | 5-20 KB |
| Moderate (2-3 features) | 20-100 KB |
| Complex (many features) | 100-500 KB |
| Very Complex (assemblies) | 500+ KB |

**Tip:** Smaller files analyze faster. Combine related parts into one assembly.

---

## Export Formats Explained

### Text Format (.txt)
```
Best for:
✓ Printing
✓ Sharing via email
✓ Documentation
✓ Human reading

Includes:
• Summary information
• File path and date
• Machinability score
• Number of operations
• Export location
```

### JSON Format (.json)
```
Best for:
✓ Data processing
✓ Integration with other software
✓ Archival/database storage
✓ Automated workflows

Includes:
• Complete structured data
• All operations with parameters
• All tools with specs
• AI recommendations
• Metadata

Can open with:
• Text editors
• Excel (import)
• Python/Java (programmatic)
• Web browsers
```

---

## Troubleshooting Quick Guide

| Problem | Solution |
|---------|----------|
| GUI won't open | Double-click `launch_capp.bat` or run `python capp_app.py` |
| File browser won't open | Check file is `.step` or `.stp` format |
| Analysis fails | Try different file or disable AI recommendations |
| Tables are empty | Verify turning score ≥ 40 |
| Export not working | Check folder permissions, try different location |
| GUI is slow | Close other applications, disable AI |

---

## Tips for Best Results

### ✨ For Accurate Analysis
1. Use high-quality STEP files from CAD
2. Ensure dimensions are in millimeters
3. Include all relevant features in the model
4. Verify geometry before analysis

### ✨ For Better Recommendations
1. Use `llama2` model (more detailed)
2. Enable AI recommendations
3. Use parts with clear cylindrical features
4. Save diverse parts for comparison

### ✨ For Production Use
1. Export results as JSON for archival
2. Keep batch processing records
3. Document any manual adjustments
4. Review recommendations before manufacturing

---

## Advanced Features

### Tab Navigation
- Click any tab to switch views
- All tabs update simultaneously
- Data persists while viewing

### Scrolling
- Use scrollbars for long lists
- Use arrow keys to navigate
- Mouse wheel works in tables

### Column Resizing
- Tables auto-fit window
- Resize window to see more
- Horizontal scroll for wide tables

---

## Save Your Work

### Automatic Saves
- JSON file (if export enabled)
- Location shown in Summary tab

### Manual Saves
- Click "📥 Export Results"
- Choose location and format
- Can save multiple formats

### Recommended Workflow
1. Analyze file
2. Export as JSON (permanent record)
3. Export as TXT (for documentation)
4. Keep both copies for comparison

---

## Performance Stats

| Operation | Time |
|-----------|------|
| Simple geometry analysis | < 2 seconds |
| Process plan generation | < 1 second |
| AI recommendation (phi) | 10-30 seconds |
| AI recommendation (llama2) | 30-60 seconds |
| UI response time | < 100ms |
| Export to file | < 1 second |

**Tip:** Disable AI for instant results, enable for detailed recommendations.

---

## Next Steps

1. ✅ **Launch** the application
2. ✅ **Upload** a STEP file
3. ✅ **Analyze** to generate plan
4. ✅ **Review** results in tables
5. ✅ **Export** for documentation

**That's it!** Enjoy your CAPP system! 🎉

---

**Questions?** Review the comprehensive guide: `CAPP_APP_GUIDE.md`
