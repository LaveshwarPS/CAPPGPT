# 🖥️ TERMINAL-ONLY GUIDE (No GUI, Just Terminal)

## ⭐ QUICK START

Open PowerShell and run:

```powershell
cd "c:\Users\Adm\Desktop\CAPP-AI project"
.\.venv\Scripts\Activate.ps1
python step_analyzer.py
```

That's it! A menu will appear for you to select files and analyze them.

---

## 📋 MAIN TERMINAL WORKFLOW

### Step 1: Activate Virtual Environment
```powershell
cd "c:\Users\Adm\Desktop\CAPP-AI project"
.\.venv\Scripts\Activate.ps1
```

Your prompt will change to:
```
(.venv) PS C:\Users\Adm\Desktop\CAPP-AI project>
```

### Step 2: Run the Analyzer
```powershell
python step_analyzer.py
```

### Step 3: You'll See a Menu
```
📁 Available STEP files:
  1. 5-Turn Speed Servo.step
  2. clo v1 (1).step
  3. head part v1 (1).step
  4. human nose.STEP
  5. smol gear v1.step

🔍 Options:
  • Enter a number to select a file from the list
  • Type 'upload' to upload a new file
  • Type a custom file path

Your choice:
```

### Step 4: Select a File
```
Your choice: 1
```

### Step 5: View Results
The tool will:
- ✅ Analyze the STEP file
- ✅ Show geometry statistics
- ✅ Display surface types
- ✅ Show machinability scores
- ✅ Generate process plan

---

## 🎯 TERMINAL-ONLY COMMANDS

### Basic Analysis
```powershell
python step_analyzer.py
# Interactive menu - select from available files
```

### Analyze Specific File
```powershell
python step_analyzer.py "5-Turn Speed Servo.step"
```

### With AI Recommendations
```powershell
python step_analyzer.py "model.step" --ai-analysis
```

### Interactive Chatbot (Ask Questions)
```powershell
python step_analyzer.py "model.step" --cad-chat
```

### CAPP Turning Process Plan
```powershell
python step_analyzer.py "model.step" --capp-turning
```

### With Multiple Options
```powershell
python step_analyzer.py "model.step" --capp-turning --ai-analysis --save
```

### Using Different AI Model
```powershell
python step_analyzer.py "model.step" --model llama2 --ai-analysis
```

---

## 📂 FILE BROWSER (TERMINAL)

Browse your computer to find STEP files:

```powershell
python browser.py
```

This opens an interactive menu to:
- Navigate folders
- Search for STEP files
- Analyze files directly
- View recent files

---

## 🔄 BATCH PROCESSING (Multiple Files)

Process all STEP files in folder:

```powershell
python batch_optimizer.py
```

With options:
```powershell
python batch_optimizer.py --ai              # With AI analysis
python batch_optimizer.py --model llama2    # Different model
python batch_optimizer.py --no-ai           # Without AI
```

---

## 📊 EXAMPLE TERMINAL SESSION

```powershell
PS C:\Users\Adm\Desktop\CAPP-AI project> .\.venv\Scripts\Activate.ps1

(.venv) PS C:\Users\Adm\Desktop\CAPP-AI project> python step_analyzer.py

🖥️  SYSTEM INFORMATION
==============================
Python executable: C:\Users\Adm\Desktop\CAPP-AI project\.venv\Scripts\python.exe
Python version: 3.13.1
Working directory: C:\Users\Adm\Desktop\CAPP-AI project

📁 Available STEP files:
  1. 5-Turn Speed Servo.step
  2. clo v1 (1).step
  3. head part v1 (1).step
  4. human nose.STEP
  5. smol gear v1.step

Your choice: 1

✅ Selected: 5-Turn Speed Servo.step
📖 Reading STEP file...
🔍 Analyzing geometry...

==================================================
📊 ANALYSIS RESULTS
==================================================

📏 DIMENSIONS:
  • X: 54.60 mm
  • Y: 21.66 mm
  • Z: 44.27 mm

🔍 SURFACE TYPES:
  • Plane: 246
  • Cylinder: 491
  • Sphere: 24
  • Cone: 110
  • Torus: 118

🏭 MACHINABILITY ANALYSIS:

  3-AXIS MILLING:
  • Feasibility: Low (Score: 40/100)

  TURNING (LATHE):
  • Feasibility: Low (Score: 5/100)

  3D PRINTING:
  • Feasibility: High (Score: 100/100)

✅ Analysis completed successfully!

Press Enter to close this window...
```

---

## 🎯 QUICK REFERENCE

| Task | Command |
|------|---------|
| **Basic Analysis** | `python step_analyzer.py` |
| **Specific File** | `python step_analyzer.py model.step` |
| **With AI** | `python step_analyzer.py model.step --ai-analysis` |
| **Chatbot** | `python step_analyzer.py model.step --cad-chat` |
| **Turning Plan** | `python step_analyzer.py model.step --capp-turning` |
| **Browse Files** | `python browser.py` |
| **Batch Process** | `python batch_optimizer.py` |
| **Save Results** | Add `--save` to any command |

---

## 🤖 AI FEATURES (TERMINAL ONLY)

### Get AI Recommendations
```powershell
python step_analyzer.py "model.step" --ai-analysis
```

Output:
```
AI RECOMMENDATIONS:
- Best suited for CNC turning with live tooling
- Recommend HSS tools for roughing
- Feed rate: 0.15-0.25 mm/rev
- Spindle speed: 800-1200 RPM
- Use coolant for extended tool life
```

### Ask Questions About Your Model (Interactive)
```powershell
python step_analyzer.py "model.step" --cad-chat
```

Output:
```
Model loaded and analyzed ✓

You can now ask questions about this CAD model.
Type 'quit' or 'exit' to end the conversation.

You: Can this be machined in a single setup?

AI: Based on the geometry analysis with 491 cylindrical surfaces and 
dimensions of 54.6mm x 21.66mm x 44.27mm, yes this can be machined in a 
single setup on a lathe with live tooling. I recommend a 4-jaw chuck setup 
with a steady rest for support.

You: What tools would you recommend?
```

---

## 💾 SAVE RESULTS

Add `--save` to save output to JSON file:

```powershell
python step_analyzer.py "model.step" --capp-turning --save
```

Creates file like:
```
model_turning_plan.json
```

---

## ⚙️ SETUP ONE TIME

First time only, activate venv:

```powershell
cd "c:\Users\Adm\Desktop\CAPP-AI project"
.\.venv\Scripts\Activate.ps1
```

After that, you can just type:
```powershell
python step_analyzer.py
```

The venv stays active in that PowerShell window.

---

## 🎓 TERMINAL WORKFLOW EXAMPLES

### Example 1: Simple Analysis
```powershell
python step_analyzer.py "5-Turn Speed Servo.step"
# Automatic analysis and display
```

### Example 2: Analysis + AI + Save
```powershell
python step_analyzer.py "gear.step" --ai-analysis --save
# Analyzes, gets AI recommendations, saves to JSON
```

### Example 3: Interactive Chat
```powershell
python step_analyzer.py "servo.step" --cad-chat
# Ask unlimited questions about your model
```

### Example 4: Process Planning
```powershell
python step_analyzer.py "part.step" --capp-turning
# Generate complete 7-step turning process plan
```

### Example 5: Batch All Files
```powershell
python batch_optimizer.py --ai
# Process all STEP files with AI analysis
```

---

## 🆘 TROUBLESHOOTING

### "command not found"
```powershell
# Make sure you activated venv first
.\.venv\Scripts\Activate.ps1
```

### "OCP not found"
```powershell
# Should be installed, but verify:
.\.venv\Scripts\Activate.ps1
# Then run the command
```

### "Ollama not running" (for AI features)
```powershell
# Optional - only if you use --ai-analysis
# Download from https://ollama.com
# Run: ollama serve
# Then use --ai-analysis flag
```

---

## 📝 ALL AVAILABLE FLAGS

```
python step_analyzer.py [FILE] [FLAGS]

FLAGS:
  --ai-analysis       Get AI recommendations (requires Ollama)
  --cad-chat          Start interactive chatbot
  --capp-turning      Generate turning process plan
  --model <name>      Specify AI model (phi, llama2, mistral)
  --save              Save results to JSON file
  --help              Show all options
```

---

## ✨ EXAMPLES BY USE CASE

### I want to analyze one part
```powershell
python step_analyzer.py "my_part.step"
```

### I want AI recommendations
```powershell
python step_analyzer.py "my_part.step" --ai-analysis
```

### I want to ask about my part
```powershell
python step_analyzer.py "my_part.step" --cad-chat
```

### I want a turning process plan
```powershell
python step_analyzer.py "my_part.step" --capp-turning
```

### I want everything (full analysis)
```powershell
python step_analyzer.py "my_part.step" --capp-turning --ai-analysis
```

### I want to process many parts
```powershell
python batch_optimizer.py --ai
```

### I want to browse files first
```powershell
python browser.py
```

---

## 🚀 30-SECOND START

```powershell
# Copy-paste this:
cd "c:\Users\Adm\Desktop\CAPP-AI project" ; .\.venv\Scripts\Activate.ps1 ; python step_analyzer.py
```

Then select a file from the menu!

---

## ✅ TERMINAL-ONLY CHECKLIST

- ✅ No GUI window needed
- ✅ All in PowerShell/terminal
- ✅ Text-based menu system
- ✅ Results in formatted text
- ✅ Can save to JSON if needed
- ✅ AI chatbot works in terminal
- ✅ Supports all features

---

## 💡 TL;DR

```powershell
cd "c:\Users\Adm\Desktop\CAPP-AI project"
.\.venv\Scripts\Activate.ps1
python step_analyzer.py
# Select a file from menu → Results display!
```

That's all you need! 🎉
