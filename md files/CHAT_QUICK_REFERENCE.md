# 🎯 CAPP Chat Feature - Quick Reference

## ⚡ Quick Start

### 1. Analyze STEP File
```
📂 Browse & Select → Choose .step file → 🚀 Analyze
```

### 2. Go to Chat Tab
```
Click "💬 Chat with AI" tab (Tab 5)
```

### 3. Ask Questions
```
Type question → Ctrl+Enter or 📤 Send
```

## 💬 Example Questions

### Process Optimization
- "What are the optimal spindle speeds for this part?"
- "Can I reduce the number of tool changes?"
- "How can I improve the surface finish?"

### Tool Selection  
- "What tools are best for these cylindrical surfaces?"
- "Can I use a different tool material?"
- "What's the longest tool life option?"

### Design Feedback
- "How can I make this part easier to machine?"
- "Are there any design improvements?"
- "What's the fastest way to make this part?"

### Parameter Optimization
- "Is 0.5 mm/rev feed rate safe?"
- "What depth of cut should I use?"
- "Can I go faster on the roughing pass?"

## 🔧 Setup (First Time)

```powershell
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Pull a model
ollama pull phi

# Terminal 3: Run CAPP
cd "c:\Users\Adm\Desktop\CAPP-AI project"
.\venv312\Scripts\Activate.ps1
python capp_app.py
```

## ✅ Status Indicators

| Indicator | Meaning |
|-----------|---------|
| 🟢 Ollama AI is available | Ready to chat |
| 🔴 Ollama not installed | Install Ollama first |
| ⏳ Thinking... | AI processing response |
| 👤 You | Your message |
| 🤖 AI Assistant | AI response |

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Send message | **Ctrl+Enter** |
| Send message | Click **📤 Send** |
| New line in input | **Shift+Enter** |

## 🎯 Pro Tips

✅ **Be specific** - "Optimal speeds for the 38mm bore"
✅ **Ask why** - "Why are these settings optimal?"
✅ **Follow up** - Ask for alternatives or details
✅ **Copy answers** - Select and copy for documentation
✅ **Try different angles** - Rephrase to get new perspectives

## ⚠️ Common Issues

| Problem | Solution |
|---------|----------|
| Chat disabled | Analyze a STEP file first |
| No response | Start Ollama (`ollama serve`) |
| Timeout | Model is slow, try "phi" instead |
| Can't find Ollama | Install from https://ollama.com |

## 📊 Chat Tips

### For Manufacturing Engineers
- Ask about cutting forces and power requirements
- Get tool recommendations based on material
- Discuss optimal coolant strategies
- Plan tool change sequences

### For Design Engineers
- Get manufacturability feedback
- Identify design improvements
- Understand machining limitations
- Optimize feature ordering

### For Learning
- Understand CAPP principles
- Learn turning operations
- Explore tool selection logic
- Master parameter optimization

## 🚀 Advanced Usage

### Model Selection
```
Left Panel → AI Model dropdown → phi/llama2/neural-chat
```

### Save Responses
```
1. Select AI response text
2. Ctrl+C to copy
3. Paste into document
```

### New Analysis
```
1. Select new STEP file
2. Click "🚀 Analyze"
3. Chat history auto-resets
4. Start new conversation
```

## 📞 Troubleshooting Quick Links

**Chat not working?**
→ See [CHAT_FEATURE_GUIDE.md](CHAT_FEATURE_GUIDE.md) - Troubleshooting section

**Setup issues?**
→ See [PYTHON312_SETUP_COMPLETE.md](PYTHON312_SETUP_COMPLETE.md)

**General help?**
→ See [CHAT_IMPLEMENTATION_SUMMARY.md](CHAT_IMPLEMENTATION_SUMMARY.md)

---

**Status: ✅ Ready to Use**

Just run: `launch_capp.bat` or `python capp_app.py`

Then analyze a STEP file and go to the Chat tab! 🚀
