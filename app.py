"""
Hugging Face Spaces Ollama API Wrapper
This runs the Ollama service and exposes it via an API
"""
import subprocess
import time
import os
import signal
import sys
from pathlib import Path

# Start Ollama service in background
def start_ollama():
    """Start Ollama service"""
    print("🚀 Starting Ollama service...")
    
    # Create .ollama directory if it doesn't exist
    ollama_dir = Path.home() / ".ollama"
    ollama_dir.mkdir(exist_ok=True)
    
    # Start ollama in background
    proc = subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if os.name != 'nt' else None
    )
    
    # Wait for Ollama to be ready
    print("⏳ Waiting for Ollama to be ready...")
    for attempt in range(30):
        try:
            import requests
            resp = requests.get("http://localhost:11434/api/version", timeout=2)
            if resp.status_code == 200:
                print("✅ Ollama is ready!")
                return proc
        except Exception:
            pass
        time.sleep(1)
    
    print("❌ Ollama failed to start")
    return proc

def pull_model(model: str = "llama2"):
    """Pull a model (runs once at startup)"""
    print(f"📥 Pulling model: {model}...")
    
    try:
        result = subprocess.run(
            ["ollama", "pull", model],
            capture_output=True,
            timeout=3600,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Model '{model}' ready")
        else:
            print(f"⚠️ Model pull warning: {result.stderr[:100]}")
    except Exception as e:
        print(f"⚠️ Could not pull model: {e}")

if __name__ == "__main__":
    # Pull model on startup (only if not already present)
    model_to_pull = os.getenv("OLLAMA_MODEL", "llama2")
    print(f"🎯 Target model: {model_to_pull}")
    
    # Start Ollama
    ollama_process = start_ollama()
    
    # Try to pull model
    try:
        pull_model(model_to_pull)
    except KeyboardInterrupt:
        pass
    
    print("\n🌐 Ollama API is running at: http://0.0.0.0:11434")
    print("📚 API Documentation: https://github.com/ollama/ollama/blob/main/docs/api.md")
    print("\nTo query the model from outside Spaces, use the public URL provided by Hugging Face")
    print("Keep this process running in Spaces (it will auto-restart if it crashes)")
    
    # Keep process alive
    try:
        ollama_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Ollama...")
        if os.name == 'nt':
            ollama_process.terminate()
        else:
            os.killpg(os.getpgid(ollama_process.pid), signal.SIGTERM)
        sys.exit(0)
