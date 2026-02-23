"""
Configuration for using Ollama from Hugging Face Spaces or other cloud hosts.

This file stores your cloud Ollama endpoint URL.
After deploying to HF Spaces, update this file with your endpoint.
"""

# Default configuration - update these after deploying to HF Spaces
OLLAMA_CLOUD_CONFIG = {
    # Your Hugging Face Spaces URL (e.g., "https://yourusername-ollama-capp.hf.space")
    # Leave empty until you deploy and get the URL
    "endpoint": "https://Laveshps-ollama-capp.hf.space/api/generate",
    
    # Model name to use
    "model": "llama2",
    
    # Request timeout in seconds (increase for slower spaces)
    "timeout": 300,
    
    # Number of retries on failure
    "max_retries": 3,
    
    # Whether to use HTTP (cloud) or local
    "use_cloud": True,
}

# Alternative endpoints (examples)
# For production, use a custom domain or IP
ENDPOINTS = {
    "huggingface_spaces": "",  # Update after deployment
    "local": "http://localhost:11434/api/generate",
    "replicate": "https://api.replicate.com/v1/predictions",  # Alternative
}
