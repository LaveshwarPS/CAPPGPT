# Ollama Integration Guide

## Quick Start

You now have Ollama integrated into your project! Here's how to use it:

### 1. **Interactive Chatbot REPL** (Easiest)

```powershell
cd 'C:\Users\Adm\Desktop\CAPP-AI project'
& '.\.venv\Scripts\Activate.ps1'
python .\run_chatbot.py
```

Then just type messages and press Enter. Example:
```
You: What is machine learning?
Assistant: [Ollama generates a response...]

You: Explain it in simpler terms
Assistant: [Follows up on your question...]
```

**Available commands in the chatbot:**
- `help` — Show available commands
- `clear` — Clear conversation history
- `exit` or `quit` — Exit the chatbot
- `Ctrl-C` — Force exit

### 2. **Use Ollama in Your Own Python Code**

```python
from chat_ollama import query_ollama, set_model

# Option A: Use default model (phi)
response = query_ollama("What is Python?")
print(response)

# Option B: Specify a different model
response = query_ollama("Explain recursion", model="llama2")
print(response)

# Option C: Set default model for your session
set_model("mistral")
response = query_ollama("Hello!")
print(response)
```

### 3. **Test the Integration**

Run the test script to verify Ollama is working:
```powershell
& '.\.venv\Scripts\Activate.ps1'
python chat_ollama.py
```

Expected output:
```
🤖 Ollama Integration Test
...
✅ Response:
Hello, my name is AI Assistant. How can I assist you today?
```

---

## How It Works

### Architecture

`chat_ollama.py` provides two methods to query Ollama:

1. **HTTP API** (Preferred)
   - Connects to `http://localhost:11434/api/generate`
   - Requires the `requests` library (already installed)
   - Automatically starts if Ollama is running
   - More reliable and faster

2. **CLI (Command-line)** (Fallback)
   - Uses the `ollama run <model>` command
   - Works if the Ollama service isn't running (slower)
   - Falls back automatically if HTTP fails

Both methods have **automatic fallback** — if one fails, the other is tried.

### Model Management

Check installed models:
```powershell
ollama list
```

Pull a new model:
```powershell
ollama pull llama2        # ~4 GB, more powerful
ollama pull mistral       # ~5 GB, very capable
ollama pull neural-chat   # ~4 GB, good for chat
ollama pull phi           # ~1.6 GB (already installed, fast & lightweight)
```

### Configuration

Set defaults via environment variables:

```powershell
# Set default model
$env:OLLAMA_MODEL = "llama2"

# Set HTTP endpoint (for remote Ollama)
$env:OLLAMA_ENDPOINT = "http://remote-server:11434/api/generate"

# Then run your code
python your_script.py
```

Or in Python:
```python
from chat_ollama import set_model
set_model("llama2")
```

---

## Usage Examples

### Example 1: Simple Query

```python
from chat_ollama import query_ollama, OllamaError

try:
    response = query_ollama("What is the capital of France?")
    print(response)
except OllamaError as e:
    print(f"Error: {e}")
```

### Example 2: Chat with History

```python
from chat_ollama import query_ollama

history = []

user_msg = "Tell me about climate change"
history.append(user_msg)

# Build prompt with history for context
prompt = "\n".join(history) + "\nAssistant:"
response = query_ollama(prompt)
print(response)

history.append(response)

# Follow-up question
user_msg = "What can individuals do to help?"
history.append(user_msg)

prompt = "\n".join(history[-5:]) + "\nAssistant:"  # Keep last 5 messages
response = query_ollama(prompt)
print(response)
```

### Example 3: Integration in Your Main Script

You can integrate Ollama into `step_analyzer.py`:

```python
# In step_analyzer.py
import sys
from chat_ollama import query_ollama, OllamaError

def main():
    # ... existing code ...
    
    # Add this after argument parsing
    if "--chat" in sys.argv:
        print("Starting chatbot...")
        from run_chatbot import main as chatbot_main
        chatbot_main()
        return
    
    # ... rest of existing code ...

if __name__ == "__main__":
    main()
```

Then you can run:
```powershell
python step_analyzer.py --chat
```

### Example 4: Analyze STEP Files with AI Commentary

```python
from chat_ollama import query_ollama
from step_analyzer import analyze_step_file

# Analyze the STEP file
result = analyze_step_file("model.step")

# Ask Ollama about the analysis
if result['success']:
    analysis_text = f"""
    Model: {result['file_path']}
    Cylindrical faces: {result['cylindrical_faces']}
    Machinability score: {result['machinability']['3_axis_milling']['score']}/100
    """
    
    prompt = f"Here's a CAD model analysis. Suggest manufacturing methods:\n{analysis_text}"
    recommendation = query_ollama(prompt, model="phi")
    print("AI Recommendation:")
    print(recommendation)
```

---

## Troubleshooting

### Problem: "Could not connect to Ollama at http://localhost:11434"

**Solution:** Make sure Ollama is running:
1. Open the Ollama app (should appear in system tray)
2. Or run in a terminal: `ollama serve`
3. Wait 3-5 seconds for the service to start

### Problem: "Model not found"

**Solution:** Pull the model first:
```powershell
ollama pull phi        # Use phi (default)
ollama pull llama2     # Or another model
ollama list            # Check installed models
```

### Problem: Script times out

**Solution:** Increase timeout or use a faster model:
```python
# Use longer timeout (seconds)
response = query_ollama("Your prompt", timeout=120)

# Or use a faster model
response = query_ollama("Your prompt", model="phi")  # phi is fast & lightweight
```

### Problem: "requests library not found"

**Solution:** Install it:
```powershell
& '.\.venv\Scripts\Activate.ps1'
pip install requests
```

---

## Performance Tips

1. **Use `phi` for speed** — It's ~1.6 GB and responds in seconds
2. **Use `llama2` or `mistral` for quality** — Slower but more capable
3. **Keep context short** — Limit conversation history to last 5–10 messages to avoid token bloat
4. **Batch requests** — If doing many queries, keep the connection alive
5. **Run Ollama in background** — Don't start/stop Ollama between requests

---

## Next Steps

- Integrate `query_ollama` into your STEP analyzer for AI-powered recommendations
- Build a web UI with Streamlit that combines STEP analysis + chatbot
- Experiment with different models (`llama2`, `mistral`, `neural-chat`)
- Use Ollama for natural language queries about your CAD models

---

## References

- **Ollama Docs:** https://github.com/ollama/ollama
- **Available Models:** https://ollama.com/library
- **API Reference:** https://github.com/ollama/ollama/blob/main/docs/api.md

