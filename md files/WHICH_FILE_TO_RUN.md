# 🎯 WHICH FILE SHOULD YOU RUN?

## ⭐ QUICK ANSWER

**Just double-click this file:**
```
launch_capp.bat
```

That's it! The GUI will open automatically. ✨

---

## 📋 Complete File Guide

### **PRIMARY FILES (Use These)**

#### 1. **launch_capp.bat** ⭐⭐⭐ (BEST FOR BEGINNERS)
**What it does:** One-click launch of the professional GUI app
**Location:** `c:\Users\Adm\Desktop\CAPP-AI project\launch_capp.bat`
**How to use:** Double-click it
**Result:** GUI app opens instantly
**Best for:** Most users - simple, fast, complete

```
📂 Double-click → GUI Opens → Upload STEP file → Analyze → View Results
```

---

#### 2. **capp_app.py** ⭐⭐⭐ (GUI APPLICATION)
**What it does:** Professional GUI for STEP analysis with AI
**Location:** `c:\Users\Adm\Desktop\CAPP-AI project\capp_app.py`
**How to use:** 
```bash
cd "c:\Users\Adm\Desktop\CAPP-AI project"
.\venv312\Scripts\Activate.ps1
python capp_app.py
```
**Features:**
- Upload STEP files
- 4 tabs: Operations, Tools, Summary, AI Recommendations
- Export results
- Optional AI optimization
- Professional table display

**Best for:** Graphical analysis, visual presentation

---

#### 3. **step_analyzer.py** ⭐⭐ (COMMAND LINE)
**What it does:** Terminal-based STEP file analysis
**Location:** `c:\Users\Adm\Desktop\CAPP-AI project\step_analyzer.py`
**How to use:**
```bash
cd "c:\Users\Adm\Desktop\CAPP-AI project"
.\venv312\Scripts\Activate.ps1
python step_analyzer.py
```
**Features:**
- Interactive file selection menu
- Geometry analysis
- Machinability scoring
- Optional AI analysis (`--ai-analysis`)
- Optional chatbot (`--cad-chat`)

**Best for:** Terminal users, scripting, automation

---

#### 4. **browser.py** ⭐ (FILE BROWSER)
**What it does:** Interactive terminal file browser
**Location:** `c:\Users\Adm\Desktop\CAPP-AI project\browser.py`
**How to use:**
```bash
python browser.py
```
**Features:**
- Browse your computer
- Find STEP files
- Analyze inline
- Recent files

**Best for:** Finding and analyzing files in bulk

---

#### 5. **batch_optimizer.py** ⭐ (BATCH PROCESSING)
**What it does:** Process multiple STEP files at once
**Location:** `c:\Users\Adm\Desktop\CAPP-AI project\batch_optimizer.py`
**How to use:**
```bash
python batch_optimizer.py
python batch_optimizer.py --ai
python batch_optimizer.py --model llama2
```
**Features:**
- Process entire folders
- Generate statistics
- Export summary reports
- AI-powered analysis

**Best for:** Processing multiple parts

---

### **SECONDARY FILES (Utilities)**

#### 6. **run_chatbot.py**
**What it does:** Start interactive CAD chatbot
**How to use:** `python run_chatbot.py`
**Best for:** Asking questions about CAD models

---

#### 7. **test_ai_features.py**
**What it does:** Test if AI/Ollama is working
**How to use:** `python test_ai_features.py`
**Best for:** Troubleshooting, verifying setup

---

#### 8. **REFERENCE_CARD.py**
**What it does:** Display helpful command reference
**How to use:** `python REFERENCE_CARD.py`
**Best for:** Learning available commands

---

## 🗂️ WHICH FILE FOR WHICH TASK?

| Task | Use This File | Command |
|------|---------------|---------|
| **Analyze 1 STEP file (GUI)** | `capp_app.py` | `python capp_app.py` |
| **Analyze 1 STEP file (Terminal)** | `step_analyzer.py` | `python step_analyzer.py` |
| **Upload file & get results** | `launch_capp.bat` | Double-click |
| **Browse & analyze multiple** | `browser.py` | `python browser.py` |
| **Process entire folder** | `batch_optimizer.py` | `python batch_optimizer.py` |
| **Ask about your model** | `run_chatbot.py` | `python run_chatbot.py` |
| **Test AI/Ollama setup** | `test_ai_features.py` | `python test_ai_features.py` |
| **One-click launch** | `launch_capp.bat` | Double-click ⭐ |

---

## 🚀 RECOMMENDED WORKFLOWS

### Workflow 1: Complete Beginner
```
1. Double-click launch_capp.bat
2. Click "Browse & Select STEP File"
3. Choose your model
4. Click "Analyze"
5. View results in tabs
6. Click "Export Results" if needed
```

### Workflow 2: Terminal User
```bash
cd "c:\Users\Adm\Desktop\CAPP-AI project"
.\venv312\Scripts\Activate.ps1
python step_analyzer.py
# Select file from menu
# Results display automatically
```

### Workflow 3: Process Multiple Files
```bash
python batch_optimizer.py
# Analyzes all STEP files in folder
# Creates summary report
```

### Workflow 4: Interactive Q&A
```bash
python step_analyzer.py model.step --cad-chat
# Ask questions about your CAD model
```

### Workflow 5: With AI Optimization
```bash
python step_analyzer.py model.step --ai-analysis
# Get AI-powered recommendations
```

---

## ⚠️ IMPORTANT ACTIVATION STEP

**Always activate the virtual environment first:**

```powershell
cd "c:\Users\Adm\Desktop\CAPP-AI project"
.\venv312\Scripts\Activate.ps1
```

The prompt will change to:
```
(.venv) PS C:\Users\Adm\Desktop\CAPP-AI project>
```

Then run your file.

---

## ✅ QUICK START (3 STEPS)

### Option A: One-Click (EASIEST)
```
1. Navigate to: C:\Users\Adm\Desktop\CAPP-AI project
2. Double-click: launch_capp.bat
3. Done! GUI opens
```

### Option B: Manual Launch
```powershell
1. Open PowerShell
2. cd "c:\Users\Adm\Desktop\CAPP-AI project"
3. .\venv312\Scripts\Activate.ps1
4. python capp_app.py
```

---

## 🎯 MAIN ENTRY POINTS SUMMARY

```
┌─────────────────────────────────────────────────┐
│     YOUR APPLICATION HAS 3 MAIN ENTRY POINTS    │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. launch_capp.bat (GUI via batch file)      │
│     └─ Use this: Double-click               │
│                                                 │
│  2. capp_app.py (GUI via Python)              │
│     └─ Use this: python capp_app.py          │
│                                                 │
│  3. step_analyzer.py (Terminal interface)     │
│     └─ Use this: python step_analyzer.py     │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🔧 TROUBLESHOOTING

### "Python not found"
**Solution:**
```powershell
.\venv312\Scripts\Activate.ps1
python step_analyzer.py
```

### "OCP libraries not installed"
**Solution:** Use `launch_capp.bat` (it activates virtual environment automatically)

### "Ollama not running"
**For AI features only:**
```bash
# Install Ollama from https://ollama.com
# Run: ollama serve
# Then run your file
```

### "Port 11434 already in use"
**Solution:** Ollama already running, this is fine! Just use the app.

---

## 📊 FILE RELATIONSHIP

```
launch_capp.bat (launcher)
    ↓
capp_app.py (main GUI)
    ├─→ step_analyzer.py (geometry analysis)
    ├─→ capp_turning_planner.py (process planning)
    ├─→ cad_ai_analyzer.py (AI recommendations)
    └─→ chat_ollama.py (Ollama integration)

step_analyzer.py (terminal interface)
    ├─→ capp_turning_planner.py
    ├─→ cad_ai_analyzer.py
    └─→ cad_chatbot.py

browser.py (file browser)
    └─→ step_analyzer.py

batch_optimizer.py (batch processing)
    └─→ step_analyzer.py (multiple times)
```

---

## ✨ FEATURES BY FILE

| File | Analysis | AI | Chat | Export | GUI |
|------|----------|----|----|--------|-----|
| capp_app.py | ✅ | ✅ | ✅ | ✅ | ✅ |
| step_analyzer.py | ✅ | ✅ | ✅ | ✅ | ❌ |
| browser.py | ✅ | ❌ | ❌ | ❌ | ❌ |
| batch_optimizer.py | ✅ | ✅ | ❌ | ✅ | ❌ |
| run_chatbot.py | ✅ | ✅ | ✅ | ❌ | ❌ |

---

## 🎓 LEARNING PATH

1. **Start here:** Read `00_START_HERE.md`
2. **Try GUI:** Double-click `launch_capp.bat`
3. **Learn features:** Read `CAPP_APP_GUIDE.md`
4. **Use terminal:** Run `python step_analyzer.py`
5. **Batch process:** Run `python batch_optimizer.py`
6. **Advanced AI:** Run `python step_analyzer.py model.step --cad-chat`

---

## 💡 MY RECOMMENDATION

**For most users:** 
👉 **Double-click `launch_capp.bat`** 👈

It's the easiest, fastest, and most professional way to use your CAPP system!

---

## 📝 COMMAND CHEAT SHEET

```bash
# GUI Application (RECOMMENDED)
double-click launch_capp.bat

# Terminal Interface
python step_analyzer.py

# File Browser
python browser.py

# Batch Processing
python batch_optimizer.py

# With AI Analysis
python step_analyzer.py model.step --ai-analysis

# Interactive Chatbot
python step_analyzer.py model.step --cad-chat

# Test AI Setup
python test_ai_features.py

# Batch with AI
python batch_optimizer.py --ai
```

---

**🎯 TL;DR: Double-click `launch_capp.bat` and start analyzing! 🚀**

