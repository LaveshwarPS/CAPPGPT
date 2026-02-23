# 💬 CAPP AI Chat Feature Guide

## ✨ What's New

Your CAPP application now includes an integrated **AI Chat Interface** that lets you discuss your CAD designs with an AI assistant powered by Ollama!

## 🚀 How to Use

### Step 1: Analyze a STEP File
1. Open the CAPP application
2. Click **"📂 Browse & Select STEP File"**
3. Choose your STEP file
4. Click **"🚀 Analyze & Generate Plan"**
5. Wait for analysis to complete ✓

### Step 2: Switch to Chat Tab
1. Once analysis is complete, click the **"💬 Chat with AI"** tab
2. You'll see the AI assistant greeting with the analysis context

### Step 3: Ask Questions
Type your question about the analyzed part in the text box:

**Example Questions:**
- "What are the optimal cutting speeds for this part?"
- "How can I optimize this turning operation?"
- "What tools would work best for the cylindrical surfaces?"
- "Is there a more efficient way to machine this geometry?"
- "What are the potential challenges with this design?"
- "Can you recommend tool paths for better finish?"

### Step 4: Send Message
- Type your question
- Click **"📤 Send"** button
- OR press **Ctrl+Enter** for quick send
- Wait for AI response (⏳ processing...)

## 🔧 Prerequisites for Chat

### Option 1: Ollama HTTP API (Recommended)
```bash
# 1. Install Ollama from https://ollama.com/
# 2. Run Ollama service
ollama serve

# 3. Pull a model (in another terminal)
ollama pull phi          # Fast & lightweight (4GB)
# OR
ollama pull llama2       # More capable (7B)
# OR
ollama pull neural-chat  # Optimized for chat
```

### Option 2: Ollama CLI
- Ollama installed and available on PATH
- Model pulled (phi, llama2, etc.)

## ✅ Verify Installation

Test that Ollama is working:

```powershell
# Test HTTP API
$response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" `
  -Method Post -Body '{"model":"phi","prompt":"test","stream":false}' -ContentType "application/json"
$response.response

# OR test CLI
ollama run phi "What is CAPP?"
```

## 💡 Tips for Best Results

### Good Questions
✅ "What feeds and speeds should I use?"
✅ "How can I reduce tool changes?"
✅ "What's the optimal operation sequence?"
✅ "Are there any design improvements?"

### Context Matters
- The AI has full context of your analyzed part
- It knows your operations, tools, and process plan
- Ask specific questions about YOUR part

### Model Selection
Choose your AI model in the left panel:
- **phi** (4GB) - Fast, good for quick answers
- **llama2** (7B) - More detailed responses
- **neural-chat** - Optimized for conversation

## 🐛 Troubleshooting

### ❌ "Ollama not installed - Chat features disabled"
**Fix:** Install Ollama from https://ollama.com/

### ❌ "Could not connect to Ollama"
**Fix:** 
1. Make sure Ollama is running (`ollama serve`)
2. Check it's on `http://localhost:11434`
3. Try `ollama pull phi` to ensure a model is available

### ❌ "Request timed out"
**Fix:**
1. Model is slow or busy
2. Try with `phi` model instead of larger models
3. Check your system resources
4. Wait a bit longer (120 second timeout)

### ❌ Chat not responding
**Step-by-step troubleshooting:**
1. Verify file was analyzed (check tabs have data)
2. Check "🟢 Ollama AI is available" message
3. Try a simple question first: "Hello"
4. Check Ollama terminal for errors
5. Restart Ollama service

## 📊 Chat Features

### Conversation History
- Previous messages are displayed in order
- AI maintains context of discussion
- History clears when you analyze a new file

### Auto-Response Handling
- AI thinks about your question (⏳)
- Displays complete response when done
- Can ask follow-up questions

### Copy/Paste
- Select and copy any chat text
- Use responses in documentation

## 🎯 Common Use Cases

### 1. Process Optimization
**You:** "Can you suggest faster cutting speeds?"
**AI:** Analyzes your part geometry and recommends optimized parameters

### 2. Tool Selection
**You:** "What tools would be best for these cylindrical surfaces?"
**AI:** Recommends specific tools based on material and geometry

### 3. Design Feedback
**You:** "Are there any design improvements for manufacturability?"
**AI:** Suggests design changes for easier machining

### 4. Troubleshooting
**You:** "The operation takes too long. How can I speed it up?"
**AI:** Recommends parameter changes, different tools, or operation sequence

### 5. Learning
**You:** "Explain the cutting forces in this operation"
**AI:** Provides detailed technical explanation

## 📝 Chat Best Practices

1. **Be Specific**: "speeds for the 10mm bore" vs "faster speeds"
2. **Ask Why**: "Why are these settings optimal?"
3. **Follow Up**: Ask for more details or alternatives
4. **Verify**: Cross-check AI suggestions with your experience
5. **Document**: Save important recommendations

## 🔐 Privacy Notes

- Chat runs locally (Ollama on your machine)
- No data sent to cloud services
- All processing happens on your computer
- Chat history stored in memory only (cleared on new file)

## 📞 Getting Help

If chat isn't working:
1. Check that Ollama service is running
2. Verify model is pulled: `ollama list`
3. Test Ollama separately: `ollama run phi "test"`
4. Check application error messages
5. Try pulling a fresh model: `ollama pull phi`

---

**Enjoy exploring your CAD designs with AI!** 🚀

## Technical Details

### Supported Models
- phi (4GB) - Fast
- llama2 (7B) - Detailed
- neural-chat - Optimized for chat
- mistral - Creative responses
- Any other Ollama model

### Chat System Architecture
- **Input:** Your questions about analyzed STEP file
- **Context:** Complete analysis results + operation parameters
- **AI Engine:** Local Ollama instance (phi, llama2, etc.)
- **Output:** Detailed technical responses

### Timeout Settings
- Default: 120 seconds per response
- Large models may need more time
- Check Ollama terminal for progress

---
Generated: December 25, 2025
