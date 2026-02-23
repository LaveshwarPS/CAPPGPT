# Using Ollama in Your Code - Summary

## ✅ What You Have Now

1. **`chat_ollama.py`** — Core module to query Ollama models
   - Supports HTTP API (fast, preferred)
   - Supports CLI fallback (if HTTP unavailable)
   - Automatic error handling and model management

2. **`run_chatbot.py`** — Interactive REPL chatbot
   - Multi-turn conversation with history
   - Command support (`help`, `clear`, `exit`)
   - Model selection via CLI argument

3. **`example_ollama.py`** — 5 working examples
   - Simple queries
   - Custom model selection
   - Conversation with history
   - Error handling
   - Default model configuration

4. **`OLLAMA_USAGE.md`** — Full documentation with troubleshooting

---

## 🚀 How to Use It

### Quick Test (30 seconds)

```powershell
cd 'C:\Users\Adm\Desktop\CAPP-AI project'
& '.\.venv\Scripts\Activate.ps1'
python run_chatbot.py
```

Then type a message like "Hello, how are you?" and press Enter.

### In Your Code (3 lines)

```python
from chat_ollama import query_ollama

response = query_ollama("What is Python?")
print(response)
```

### Advanced: Custom Model & Error Handling

```python
from chat_ollama import query_ollama, OllamaError, set_model

set_model("llama2")  # Use a more powerful model

try:
    response = query_ollama("Explain machine learning", timeout=120)
    print(response)
except OllamaError as e:
    print(f"Ollama error: {e}")
```

---

## 📋 Common Tasks

### Run the Interactive Chatbot

```powershell
python run_chatbot.py              # Default model (phi)
python run_chatbot.py --model llama2   # Specify model
```

### Pull Additional Models

```powershell
ollama pull llama2      # More powerful, slower (~4 GB)
ollama pull mistral     # Very capable (~5 GB)
ollama pull neural-chat # Good for chat (~4 GB)
ollama list             # See what you have
```

### Use a Different Default Model

In your Python code:
```python
from chat_ollama import set_model
set_model("llama2")
```

Or via environment variable:
```powershell
$env:OLLAMA_MODEL = "llama2"
python your_script.py
```

### Increase Timeout (for slower systems)

```python
response = query_ollama("Your prompt", timeout=120)  # 2 minutes
```

---

## 🔧 Integration Examples

### 1. Enhance STEP File Analysis with AI

```python
from step_analyzer import analyze_step_file
from chat_ollama import query_ollama

# Analyze the model
result = analyze_step_file("gear.step")

# Ask AI for recommendations
if result['success']:
    prompt = f"""
    I have a CAD part with:
    - {result['cylindrical_faces']} cylindrical faces
    - Machinability score: {result['machinability']['3_axis_milling']['score']}/100
    
    What manufacturing process would you recommend?
    """
    recommendation = query_ollama(prompt)
    print(recommendation)
```

### 2. Add `--chat` Flag to step_analyzer.py

Edit `step_analyzer.py` and add near the top:

```python
import sys

def analyze_step_file(file_path: str = None):
    # Add this at the beginning of the function:
    if "--chat" in sys.argv:
        from run_chatbot import main as chatbot_main
        chatbot_main()
        return {'success': True}
    
    # ... rest of existing code ...
```

Then use it:
```powershell
python step_analyzer.py --chat
```

### 3. Build a Streamlit UI with Ollama Chat

Create `streamlit_app.py`:

```python
import streamlit as st
from chat_ollama import query_ollama, OllamaError, set_model

st.title("📊 CAD Analysis + 🤖 Ollama Chat")

col1, col2 = st.columns(2)

with col1:
    st.header("STEP File Analysis")
    # Add STEP file analysis code here

with col2:
    st.header("💬 AI Assistant")
    
    user_input = st.text_input("Ask the AI something:")
    if st.button("Ask"):
        try:
            response = query_ollama(user_input)
            st.write(response)
        except OllamaError as e:
            st.error(f"Error: {e}")
```

Run with: `streamlit run streamlit_app.py`

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Could not connect to Ollama" | Start Ollama: `ollama serve` (in another terminal) |
| "Model not found" | Pull a model: `ollama pull phi` |
| Timeout errors | Use a faster model (phi) or increase timeout |
| Slow responses | phi is fastest; llama2/mistral are slower but better quality |
| "requests library not found" | Install: `pip install requests` |

---

## 📚 Files in Your Project

- `chat_ollama.py` — Core Ollama wrapper (use this in your code)
- `run_chatbot.py` — Interactive chatbot REPL
- `example_ollama.py` — 5 working examples
- `OLLAMA_USAGE.md` — Detailed documentation
- `THIS_FILE` — Quick reference

---

## 🎯 What's Next

1. **Try the chatbot** — `python run_chatbot.py`
2. **Run the examples** — `python example_ollama.py`
3. **Integrate into your script** — Add 3 lines to use Ollama
4. **Experiment with models** — `ollama pull llama2; ollama list`
5. **Build a UI** — Use Streamlit to combine STEP analysis + Ollama chat

---

## 📖 Quick API Reference

```python
from chat_ollama import query_ollama, set_model, OllamaError

# Single query
response = query_ollama("Your prompt")

# Specify model
response = query_ollama("Your prompt", model="llama2")

# Set default for session
set_model("phi")

# Error handling
try:
    response = query_ollama("Prompt", timeout=60)
except OllamaError as e:
    print(f"Error: {e}")
```

---

**Enjoy using Ollama! 🚀**
