# Deploy Ollama to Hugging Face Spaces

This guide walks you through deploying Ollama (Llama 2) to Hugging Face Spaces and connecting your CAPP project to it.

## Step 1: Create a Hugging Face Account

1. Go to [huggingface.co](https://huggingface.co)
2. Sign up or log in
3. Go to **Spaces** (top menu bar)
4. Click **Create new Space**

## Step 2: Create a New Space

Fill in the creation form:
- **Space name**: `capp-ollama` (or any name you prefer)
- **Space type**: `Docker`
- **Visibility**: `Private` (recommended) or `Public`
- **Hardware**: `CPU` (free tier, but slow) or upgrade to GPU

> **⚠️ Note**: Free tier is CPU-only and will be slow (~30-60s per response). For better performance, upgrade to GPU ($10-20/month).

Click **Create Space**

## Step 3: Upload Files

You'll see an empty Space repository. Add these files:

### Option A: Via Hugging Face Web UI (Easiest)
1. In the Space, click **Files** → **Upload files**
2. Upload these files from your `CAPP-AI project` folder:
   - `hf_spaces_app.py` (rename to `app.py` when uploading)
   - `requirements.txt`
   - Optionally: `chat_ollama.py`

### Option B: Via Git Clone & Push (Advanced)
```powershell
# Clone the space repository
git clone https://huggingface.co/spaces/your-username/capp-ollama
cd capp-ollama

# Copy files
Copy-Item ../path/to/hf_spaces_app.py -Destination app.py
Copy-Item ../path/to/requirements.txt -Destination requirements.txt

# Commit and push
git add .
git commit -m "Add Ollama setup"
git push
```

## Step 4: Create/Update requirements.txt

The Space needs these Python packages. Create or update `requirements.txt`:

```
requests>=2.28.0
ollama>=0.0.1
```

> The Dockerfile already includes Ollama binary, this is for Python dependencies.

## Step 5: Wait for Deployment

HF Spaces will automatically build and deploy your Space:
1. You'll see a build log in the Space
2. Wait for the build to complete (2-5 minutes)
3. Look for "✅ Ollama is ready!" in the logs

## Step 6: Get Your Space URL

Once deployed, HF Spaces gives you a public URL like:
- `https://yourusername-capp-ollama.hf.space`

This is your cloud Ollama endpoint.

## Step 7: Update Your Project Configuration

Update **`ollama_cloud_config.py`** in your CAPP project:

```python
OLLAMA_CLOUD_CONFIG = {
    # Your Hugging Face Spaces URL
    "endpoint": "https://yourusername-capp-ollama.hf.space",
    
    "model": "llama2",
    "timeout": 180,
    "max_retries": 3,
    "use_cloud": True,  # ← IMPORTANT: Enable cloud mode
}
```

## Step 8: Connect from Your PC

Now your CAPP app will use the cloud Ollama. Test it:

```python
from chat_ollama import query_ollama, ollama_health_check

# Check if cloud Ollama is running
if ollama_health_check():
    print("✓ Connected to cloud Ollama!")
    response = query_ollama("Hello, what's your name?", timeout=180)
    print(response)
else:
    print("✗ Cannot reach cloud Ollama")
```

## Troubleshooting

### Space stuck building
- Check the build logs in the Space
- May take 10-15 minutes first time (pulling Ollama Docker image)

### "Connection refused" error
- Wait a few minutes after deployment
- Check HF Space status (should show "Running")
- Verify URL is correct in `ollama_cloud_config.py`

### Very slow responses (30-60s)
- This is normal on CPU. Messages from the model appear slowly.
- Consider upgrading to GPU for faster responses

### Timeout errors
- CPU Spaces are slow; increase `timeout` in config:
  ```python
  "timeout": 300,  # Increase to 300s for CPU
  ```

### Model not found error
- The Space auto-pulls `llama2` on first start
- This takes 5-10 minutes. Wait and try again.
- Check Space logs to see pull progress

## Optional: Use Environment Variables

Instead of editing `ollama_cloud_config.py`, you can set environment variables:

```powershell
# PowerShell
$env:OLLAMA_USE_CLOUD = "true"
$env:OLLAMA_ENDPOINT = "https://yourusername-capp-ollama.hf.space/api/generate"
$env:OLLAMA_TIMEOUT = "300"

# Then run your app
python capp_app.py
```

## Optional: Custom Domain (Advanced)

If you have a custom domain, you can set it up with HF Spaces for a cleaner URL:
1. In Space settings → **Repository settings**
2. Add your custom domain
3. Update DNS records (instructions provided)

## Monitoring Your Space

Hugging Face Spaces automatically:
- Restarts on crashes
- Handles traffic spikes
- Logs all activity

View logs anytime by clicking **Logs** in the Space.

## Cost Breakdown

| Tier | Cost | Speed | Notes |
|------|------|-------|-------|
| Free (CPU) | $0/month | 30-60s/response | Great for testing |
| Standard GPU | $12/month | 5-10s/response | T4 GPU, recommended |
| Advanced GPU | $40/month | 1-3s/response | A100 GPU |

## Next Steps

1. Deploy to HF Spaces now (follow steps 1-6)
2. Update your config (step 7)
3. Test connection from your CAPP app (step 8)
4. Your local PC no longer needs to run Ollama!

**Your app will now work wherever you are, as long as you have internet!**
