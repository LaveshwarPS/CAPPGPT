# Hugging Face Spaces Deployment - Quick Start

Your project is now ready to deploy Ollama to the cloud! Here's what was created:

## 📁 New Files Created

### Deployment Files
- **`huggingface_spaces_dockerfile`** - Docker configuration for HF Spaces (contains Ollama)
- **`hf_spaces_app.py`** - Application entry point for HF Spaces (manages Ollama startup)
- **`hf_spaces_requirements.txt`** - Python dependencies for HF Spaces

### Configuration
- **`ollama_cloud_config.py`** - Cloud endpoint configuration (update this with your HF Space URL)

### Testing & Documentation
- **`test_cloud_ollama.py`** - Test script to verify cloud connection
- **`HUGGINGFACE_SPACES_DEPLOYMENT.md`** - Complete deployment guide

### Updated Files
- **`chat_ollama.py`** - Updated to support cloud endpoints via config file

---

## 🚀 Quick Start (4 Steps)

### Step 1: Create HF Spaces Account
- Go to [huggingface.co/spaces](https://huggingface.co/spaces)
- Click **Create new Space**
- Choose **Docker** type, name it `capp-ollama`

### Step 2: Upload Files
Upload to your Space repository:
- `hf_spaces_app.py` → rename as `app.py`
- `hf_spaces_requirements.txt` → rename as `requirements.txt`

> See full guide in `HUGGINGFACE_SPACES_DEPLOYMENT.md` for more details

### Step 3: Get Your URL
Once deployed (3-5 min), HF Spaces gives you a URL like:
```
https://yourusername-capp-ollama.hf.space
```

### Step 4: Update Config
Edit `ollama_cloud_config.py`:
```python
OLLAMA_CLOUD_CONFIG = {
    "endpoint": "https://yourusername-capp-ollama.hf.space",  # ← YOUR URL
    "model": "llama2",
    "timeout": 180,
    "max_retries": 3,
    "use_cloud": True,  # ← ENABLE CLOUD MODE
}
```

---

## ✅ Verify It Works

Run the test script:
```powershell
python test_cloud_ollama.py
```

If successful, you'll see:
```
✅ All tests passed! Cloud Ollama is working.
```

---

## 📊 What Happens After Deployment

Your project uses cloud Ollama automatically:
- ✅ No local Ollama needed on your PC
- ✅ Works from anywhere with internet
- ✅ Others can use the same Space too
- ✅ Runs 24/7 on HF Spaces infrastructure

---

## 💰 Cost & Performance

| Option | Cost | Speed | Notes |
|--------|------|-------|-------|
| **Free (CPU)** | $0 | 30-60s/response | Good for testing |
| **GPU** | $12+/month | 5-10s/response | Faster responses |

Start with Free tier, upgrade later if needed.

---

## 🔧 File Reference

| File | Purpose |
|------|---------|
| `ollama_cloud_config.py` | Where to set your cloud endpoint |
| `chat_ollama.py` | Already updated - checks config automatically |
| `test_cloud_ollama.py` | Verify connection works |
| `HUGGINGFACE_SPACES_DEPLOYMENT.md` | Full troubleshooting guide |

---

## 🎯 Next Steps

1. Create HF Spaces account (free)
2. Create a Space with Docker type
3. Upload the files
4. Update `ollama_cloud_config.py` with your URL
5. Run `test_cloud_ollama.py` to verify
6. Use your CAPP app normally - it will use cloud Ollama!

---

## ❓ Troubleshooting

**Can't connect?**
→ See `HUGGINGFACE_SPACES_DEPLOYMENT.md` - Troubleshooting section

**Slow responses?**
→ Normal on CPU. Upgrade to GPU in HF Spaces settings for faster responses.

**Space stuck building?**
→ Check HF Space logs, may take 10-15 minutes first time pulling the Ollama image.

---

**Questions?** Check `HUGGINGFACE_SPACES_DEPLOYMENT.md` for detailed instructions on every step.
