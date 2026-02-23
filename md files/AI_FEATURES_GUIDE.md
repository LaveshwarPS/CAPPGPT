# AI-Enhanced STEP File Analysis

This project combines 3D CAD model analysis with AI-powered recommendations using Ollama.

## 📋 What's New

### 1. **AI-Powered Analysis** (`cad_ai_analyzer.py`)
Analyzes STEP files and generates AI recommendations for:
- ✅ Manufacturing methods and process selection
- ✅ Design optimization suggestions
- ✅ Cost and time estimates for different manufacturing approaches
- ✅ Material recommendations based on part geometry
- ✅ Quality standards and testing considerations

### 2. **Interactive CAD Chatbot** (`cad_chatbot.py`)
Ask questions about your CAD models with AI context awareness:
- ✅ Multi-turn conversation about specific CAD models
- ✅ Maintains geometry and analysis context
- ✅ Manufacturing and design expertise
- ✅ Command system for model switching and analysis review

### 3. **Enhanced CLI** (`step_analyzer.py`)
Updated command-line interface with new flags:
- ✅ `--ai-analysis` - Run AI-powered analysis
- ✅ `--cad-chat` - Start interactive chatbot
- ✅ `--model <name>` - Specify Ollama model
- ✅ `--save` - Save results to JSON file

## 🚀 Quick Start

### Basic STEP Analysis (Existing)
```powershell
python step_analyzer.py
python step_analyzer.py model.step
```

### AI Analysis (NEW)
```powershell
# Run AI analysis with recommendations
python step_analyzer.py model.step --ai-analysis

# Save report to JSON
python step_analyzer.py model.step --ai-analysis --save

# Use custom Ollama model
python step_analyzer.py model.step --ai-analysis --model llama2
```

### Interactive CAD Chatbot (NEW)
```powershell
# Start chatbot for a specific model
python step_analyzer.py model.step --cad-chat

# Use custom model
python step_analyzer.py model.step --cad-chat --model phi

# Without specifying file (select from list)
python step_analyzer.py --cad-chat
```

### Direct Python Usage
```python
# AI Analysis
from cad_ai_analyzer import analyze_with_ai

result = analyze_with_ai("model.step", model="phi", save_report=True)
print(result['summary'])

# CAD Chatbot
from cad_chatbot import interactive_cad_chat

interactive_cad_chat("model.step", model="phi")
```

## 🤖 Ollama Requirements

**Must be installed and running before using AI features.**

### Install Ollama
- Download from: https://ollama.ai
- Or use: `winget install ollama` (Windows)

### Pull Models
```powershell
# Small model (recommended)
ollama pull phi

# Alternative models
ollama pull llama2
ollama pull mistral
```

### Verify Setup
```powershell
ollama --version
ollama list
ollama run phi "Hello"
```

## 📚 File Structure

```
cad_ai_analyzer.py       - AI analysis module
├─ analyze_with_ai()     - Main AI analysis function
├─ generate_ai_recommendations() - Generates 5 types of recommendations
└─ format_analysis_summary() - Formats analysis for prompts

cad_chatbot.py           - Interactive chatbot module
├─ CADChatbot class       - Main chatbot class
├─ ask()                  - Ask questions about models
└─ interactive_cad_chat() - REPL interface

step_analyzer.py         - Enhanced main script
├─ Previous functionality (geometry analysis)
├─ --ai-analysis flag
├─ --cad-chat flag
└─ --model flag

chat_ollama.py           - Ollama integration (existing)
└─ query_ollama()         - Universal query function
```

## 💡 Usage Examples

### Example 1: Full AI Analysis Report
```powershell
python step_analyzer.py gear.step --ai-analysis --save

# Output:
# ✅ Generates complete analysis with:
#    - Manufacturing method recommendations
#    - Design optimization suggestions
#    - Cost/time estimates
#    - Material recommendations
#    - Quality considerations
# 💾 Saves to: gear_ai_analysis.json
```

### Example 2: Interactive CAD Chatbot
```powershell
python step_analyzer.py gear.step --cad-chat

# Example conversation:
You: What manufacturing methods are suitable for this part?
Bot: Based on the geometry with cylindrical faces and complex curves...

You: Can this be 3D printed?
Bot: The 8 cylindrical faces suggest turning is ideal, but 3D printing...

You: What materials would work best?
Bot: Given the geometry and manufacturing constraints...

You: help
Bot: [Shows available commands]

You: analyze
Bot: [Shows current model geometry analysis]

You: exit
```

### Example 3: Python Script Integration
```python
from cad_ai_analyzer import analyze_with_ai
from cad_chatbot import CADChatbot

# Generate AI recommendations
result = analyze_with_ai("model.step", model="phi", save_report=True)
print(result['summary'])

# Start chatbot programmatically
bot = CADChatbot("model.step")
response = bot.ask("What's the best manufacturing method?")
print(response)

# Access model analysis
analysis = bot.get_analysis()
print(f"Cylindrical faces: {analysis.get('cylindrical_faces', 0)}")
```

## ⚙️ Configuration

### Ollama Defaults
- **Endpoint**: `http://localhost:11434`
- **Default Model**: `phi`
- **Timeout**: 60-90 seconds per request

### Environment Variables (Optional)
```powershell
# Set custom model
$env:OLLAMA_MODEL = "llama2"

# Set custom endpoint
$env:OLLAMA_ENDPOINT = "http://192.168.1.100:11434"

# Then run
python step_analyzer.py model.step --ai-analysis
```

## 📊 AI Recommendations Explained

### 1. Manufacturing Methods
Evaluates suitability for:
- 3-Axis CNC Milling
- Turning/Lathe work
- 3D Printing
- Other processes

### 2. Design Optimization
Suggests improvements in:
- Complexity reduction
- Manufacturability
- Cost optimization
- Material efficiency

### 3. Cost & Time Estimates
Provides rough estimates for:
- Different manufacturing methods
- Fast/expensive vs slow/cheap options
- Production timeline

### 4. Material Recommendations
Considers:
- Part function and requirements
- Manufacturing method compatibility
- Cost constraints
- Performance requirements

### 5. Quality Considerations
Covers:
- Tolerance and precision needs
- Stress points in geometry
- Material properties
- Industry standards

## 🔧 Troubleshooting

### Ollama Not Responding
```powershell
# Check if Ollama is running
ollama serve

# In another terminal, test
curl http://localhost:11434/api/tags

# If not working, restart
# Kill Ollama process and restart
```

### Model Timeouts
- Increase timeout with `--timeout` parameter
- Use faster model: `--model phi` (recommended)
- Check system resources
- Ensure no other heavy processes

### Module Not Found
```powershell
# Ensure all files are in same directory:
# - step_analyzer.py ✓
# - cad_ai_analyzer.py ✓
# - cad_chatbot.py ✓
# - chat_ollama.py ✓
```

### ImportError with cad_ai_analyzer
Make sure `chat_ollama.py` and `step_analyzer.py` are in the same directory and properly configured.

## 🎯 Tips & Best Practices

1. **Start with `phi` model** - It's small, fast, and well-suited for CAD analysis
2. **Use `--save` flag** - Keeps records of AI analysis for comparison
3. **Ask follow-up questions** - Chatbot maintains context across messages
4. **Review geometry first** - Basic analysis gives context for AI prompts
5. **Try different models** - Experiment with llama2, mistral for different insights

## 📖 See Also

- `OLLAMA_QUICKSTART.md` - Quick reference
- `OLLAMA_USAGE.md` - Detailed guide
- `START_HERE_OLLAMA.txt` - Getting started
- `README_OLLAMA.txt` - Project overview

## ✅ Verification Checklist

Before using AI features:
- [ ] Ollama installed (`ollama --version`)
- [ ] Model pulled (`ollama list` shows model)
- [ ] Ollama running (`ollama serve` in terminal)
- [ ] Can connect (`curl http://localhost:11434/api/tags`)
- [ ] All .py files in same directory
- [ ] STEP file available for analysis

## 🚀 Next Steps

1. Install/start Ollama
2. Place a STEP file in the project directory
3. Run: `python step_analyzer.py --help`
4. Try: `python step_analyzer.py model.step --ai-analysis`
5. Explore: `python step_analyzer.py model.step --cad-chat`

---

**Happy analyzing! 🎉**
