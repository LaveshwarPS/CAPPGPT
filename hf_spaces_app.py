"""
Hugging Face Spaces - Ollama API Proxy
Provides FastAPI wrapper around Ollama for HF Spaces compatibility.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import subprocess
import time
import os
import sys
import threading
from pathlib import Path

# FastAPI app
app = FastAPI(title="Ollama Cloud API")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama local endpoint
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

def start_ollama_background():
    """Start Ollama in background thread"""
    def run_ollama():
        try:
            print("🚀 Starting Ollama service...")
            subprocess.run(["ollama", "serve"], check=False)
        except Exception as e:
            print(f"Error running Ollama: {e}")
    
    thread = threading.Thread(target=run_ollama, daemon=True)
    thread.start()
    
    # Wait for Ollama to be ready
    print("⏳ Waiting for Ollama to be ready...")
    for attempt in range(60):
        try:
            requests.get("http://localhost:11434/api/version", timeout=2)
            print("✅ Ollama is ready!")
            return True
        except:
            time.sleep(1)
    return False

def pull_model(model: str = "llama2"):
    """Pull model"""
    print(f"📥 Pulling model: {model}...")
    try:
        subprocess.run(["ollama", "pull", model], timeout=3600, capture_output=True)
        print(f"✅ Model ready!")
    except:
        print(f"⚠️ Model pull in progress...")

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# API endpoint
@app.post("/api/generate")
async def generate(request: dict):
    try:
        response = requests.post(OLLAMA_ENDPOINT, json=request, timeout=300)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/version")
def version():
    try:
        response = requests.get("http://localhost:11434/api/version")
        return response.json()
    except:
        return {"version": "unknown"}

if __name__ == "__main__":
    print("🎯 Ollama Cloud Service Starting")
    print("=" * 50)
    
    # Start Ollama
    start_ollama_background()
    time.sleep(3)
    
    # Pull model
    pull_model("llama2")
    
    # Run FastAPI server
    import uvicorn
    print("\n✅ Starting FastAPI server on 0.0.0.0:7860")
    uvicorn.run(app, host="0.0.0.0", port=7860)
