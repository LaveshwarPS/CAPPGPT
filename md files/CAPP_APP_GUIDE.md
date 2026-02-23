# CAPP Professional GUI Application - Quick Start Guide

## 🎯 Overview

**capp_app.py** is a professional GUI application that allows you to:
- Upload STEP files from your computer
- Analyze turning feasibility
- Generate complete process plans
- View results in formatted tables
- Get AI-powered optimization recommendations

---

## 🚀 How to Launch

### Option 1: Direct Command
```powershell
cd "C:\Users\Adm\Desktop\CAPP-AI project"
.\.venv\Scripts\Activate.ps1
python capp_app.py
```

### Option 2: Create a Shortcut (Windows)
1. Right-click on Desktop
2. New → Shortcut
3. Enter: `powershell.exe -NoExit -Command "cd 'C:\Users\Adm\Desktop\CAPP-AI project'; .\.venv\Scripts\Activate.ps1; python capp_app.py"`
4. Name it: "CAPP Planner"
5. Click Finish

---

## 📖 User Interface Guide

### Left Panel: File Upload & Options

#### 1. **File Selection**
   - Click **"📂 Browse & Select STEP File"**
   - Navigate to your STEP file
   - File name appears in the display area
   - Click **"✕ Clear Selection"** to reset

#### 2. **Analysis Options**
   - **🤖 Include AI Optimization** - Enable AI recommendations (default: ON)
   - **💾 Export to JSON** - Save detailed results (default: ON)
   - **AI Model** - Choose between:
     - `phi` (fast, good for quick analysis)
     - `llama2` (detailed, longer processing)
     - `neural-chat` (balanced)

#### 3. **Actions**
   - **🚀 Analyze & Generate Plan** - Start analysis
   - **📥 Export Results** - Save results to file

#### 4. **Status Display**
   - Shows current operation status
   - Green = Ready/Complete
   - Yellow = Processing
   - Red = Error

---

### Right Panel: Results Tabs

#### Tab 1: Operations
Detailed table of all turning operations:
- **Op** - Operation number
- **Name** - Operation name (Face & Center, Finishing, etc.)
- **Type** - Operation type (facing, turning, boring, etc.)
- **Tool** - Tool specification (VNMG 431, etc.)
- **Speed** - Spindle speed in RPM
- **Feed** - Feed rate in mm/rev
- **DOC** - Depth of cut in mm
- **Time** - Estimated time in minutes

#### Tab 2: Tools
Tool specifications required for the process:
- **#** - Tool number
- **Tool Name** - Description (Facing Insert, Turning Insert, etc.)
- **Type/Model** - Tool model number
- **Material** - Tool material (Carbide, High Speed Steel, etc.)
- **Coating** - Surface coating (TiAlN, TiN, etc.)
- **Purpose** - What the tool is used for

#### Tab 3: Summary
Overview of the analysis:
- File information (name, path, date)
- Machinability score (0-100)
- Number of operations and tools
- Total machining time
- Export location

#### Tab 4: AI Recommendations
Optimization suggestions from the AI model:
- Tool selection improvements
- Speed/feed optimization strategies
- Coolant strategy recommendations
- Setup considerations
- Quality improvement tips

---

## 🔄 Complete Workflow

### Step 1: Upload File
```
1. Click "📂 Browse & Select STEP File"
2. Select your STEP file (*.step or *.stp)
3. Confirm file name appears
```

### Step 2: Configure Options
```
1. Toggle AI recommendations (default: ON)
2. Toggle JSON export (default: ON)
3. Select AI model (default: phi)
```

### Step 3: Analyze
```
1. Click "🚀 Analyze & Generate Plan"
2. Wait for processing (status shows progress)
3. Results appear automatically in tables
```

### Step 4: Review Results
```
1. Check "Operations" tab for process plan
2. Check "Tools" tab for tool requirements
3. Check "Summary" tab for overview
4. Check "AI Recommendations" tab for optimization
```

### Step 5: Export (Optional)
```
1. Click "📥 Export Results"
2. Choose save location and format
3. Select .txt for formatted text or .json for raw data
```

---

## 📊 Understanding the Results

### Operations Table

Each row represents one machining operation:

```
Example Operation:
Op:    3
Name:  Finish Turning
Type:  turning
Tool:  Finishing insert (VNMG, R0.4)
Speed: 1,455 RPM          ← Spindle speed
Feed:  0.1 mm/rev         ← Feed per revolution
DOC:   0.5 mm             ← Depth of cut
Time:  10.0 min           ← Estimated machining time
```

**Interpretation:**
- Lower speed + higher feed = faster but rougher finish
- Higher speed + lower feed = slower but better finish
- Multiple operations = sequential turning passes

### Tools Table

Each row represents a required tool:

```
Example Tool:
#:        1
Name:     Facing Insert
Type:     CNMG 432 M0804
Material: Carbide
Coating:  TiAlN
Purpose:  For facing and end turning
```

**Material Codes:**
- **Carbide** = High-speed cutting
- **High Speed Steel (HSS)** = General purpose
- **Ceramic** = High-temperature applications

**Coating Benefits:**
- **TiAlN** = Better wear resistance
- **TiN** = Good general coating
- **Uncoated** = Basic cutting tool

---

## 🎯 Analysis Results Interpretation

### Turning Score (0-100)
- **80-100** = Excellent for turning (use lathe)
- **60-79** = Good for turning (lathe is suitable)
- **40-59** = Marginal (lathe works but not optimal)
- **Below 40** = Not recommended for turning

### Total Machining Time
- **Rough estimate** based on part geometry
- **Actual time** depends on:
  - Material hardness
  - Machine rigidity
  - Operator experience
  - Coolant quality

### AI Recommendations
- **Tool suggestions** = Better surface finish or durability
- **Speed/feed changes** = Faster production or better quality
- **Coolant tips** = Cost reduction or better tool life

---

## ⚙️ Advanced Settings

### Changing AI Model (in code)
Edit `capp_app.py` line ~145:
```python
self.model_var = tk.StringVar(value="phi")  # Change to "llama2" for detailed analysis
```

### Disabling AI by Default
Edit `capp_app.py` line ~141:
```python
self.ai_var = tk.BooleanVar(value=False)  # Change True to False
```

### Disabling JSON Export by Default
Edit `capp_app.py` line ~144:
```python
self.save_var = tk.BooleanVar(value=False)  # Change True to False
```

---

## 🐛 Troubleshooting

### Issue: "Please select a STEP file first"
**Solution:** Click "📂 Browse & Select STEP File" first

### Issue: Analysis takes too long
**Solution:** 
- Use `phi` model (faster)
- Disable AI recommendations
- Check computer performance

### Issue: "Ollama connection error"
**Solution:**
- Make sure Ollama is running: `ollama serve`
- In separate terminal: `ollama serve`

### Issue: Table shows no data
**Solution:**
- Check if part has turning score ≥ 40
- Try disabling AI recommendations
- Select different STEP file

---

## 💾 Export Formats

### Text Format (.txt)
- Human-readable summary
- Good for printing
- Easy to share

### JSON Format (.json)
- Structured data format
- Good for data processing
- Can be opened in Excel/Python

---

## 🎨 Window Management

### Resize Columns
Click and drag column borders in tables

### Expand/Collapse
Resize window to see more data

### Full Screen
Double-click title bar (Windows)

### Copy Data
Select text and Ctrl+C to copy

---

## ✨ Pro Tips

1. **Multiple Files**: Process multiple files in sequence
2. **Compare Results**: Keep multiple result windows open
3. **Export & Archive**: Save JSON files for documentation
4. **AI Tuning**: Try different models for different part types
5. **Documentation**: Export results for quality documentation

---

## 📝 File Outputs

After analysis, you'll have:

1. **Application Window** - Interactive results display
2. **JSON File** (optional) - `{filename}_turning_plan.json`
3. **Exported Report** (optional) - Your chosen format

---

## 🆘 Get Help

For issues or questions:
1. Check the Status label for error messages
2. Review the Summary tab for analysis details
3. Check terminal window for detailed error logs

---

## 🎓 Learning the Interface

1. **Start Simple**: Upload a simple STEP file
2. **Review All Tabs**: Check all 4 tabs to understand results
3. **Compare Models**: Try different AI models
4. **Export Results**: See how results look when exported
5. **Analyze Multiple**: Process several parts to see patterns

---

**Enjoy your CAPP Turning Planner!** 🚀
