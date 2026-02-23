"""
Quick test script to verify connection to cloud Ollama on HF Spaces

Run this after deploying to HF Spaces to check if everything works.
"""

import sys
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from chat_ollama import ollama_health_check, query_ollama, get_available_models, OllamaError

def test_cloud_ollama():
    """Test cloud Ollama connection"""
    print("=" * 70)
    print("🔍 Testing Cloud Ollama Connection")
    print("=" * 70)
    print()
    
    # Check config
    try:
        from ollama_cloud_config import OLLAMA_CLOUD_CONFIG
        endpoint = OLLAMA_CLOUD_CONFIG.get("endpoint", "")
        use_cloud = OLLAMA_CLOUD_CONFIG.get("use_cloud", False)
        
        print("📋 Configuration:")
        print(f"  Endpoint: {endpoint if endpoint else '(not set)'}")
        print(f"  Cloud mode: {use_cloud}")
        print(f"  Model: {OLLAMA_CLOUD_CONFIG.get('model', 'N/A')}")
        print()
        
        if not endpoint:
            print("❌ ERROR: Endpoint not configured in ollama_cloud_config.py")
            print("   Please update OLLAMA_CLOUD_CONFIG['endpoint'] with your HF Spaces URL")
            return False
            
        if not use_cloud:
            print("⚠️  Cloud mode is disabled. Set use_cloud=True in ollama_cloud_config.py")
            return False
    
    except ImportError:
        print("❌ ERROR: Cannot load ollama_cloud_config.py")
        return False
    
    # Health check
    print("🔌 Checking connection...")
    if ollama_health_check():
        print("✅ Connection successful!")
    else:
        print("❌ Cannot reach cloud Ollama")
        print("   - Verify your endpoint URL is correct")
        print("   - Check HF Space deployment is running")
        print("   - Wait a few minutes if just deployed")
        return False
    
    print()
    
    # List available models
    print("📚 Available models:")
    try:
        models = get_available_models()
        if models:
            for model in models:
                print(f"  • {model}")
        else:
            print("  (No models yet - still loading)")
    except Exception as e:
        print(f"  (Could not list: {e})")
    
    print()
    
    # Test simple query
    print("💬 Testing model query...")
    test_prompt = "Say 'Hello from cloud Ollama!' in one sentence."
    
    try:
        print(f"   Prompt: {test_prompt}")
        print("   ⏳ Waiting for response (this may take 30-60s on CPU)...")
        
        start = time.time()
        response = query_ollama(test_prompt, timeout=180)
        elapsed = time.time() - start
        
        print(f"\n✅ Response received in {elapsed:.1f}s:")
        print("-" * 70)
        print(response)
        print("-" * 70)
        return True
        
    except OllamaError as e:
        print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_cloud_ollama()
    
    print()
    print("=" * 70)
    if success:
        print("✅ All tests passed! Cloud Ollama is working.")
        print("   Your CAPP project can now use cloud Ollama.")
    else:
        print("❌ Tests failed. Please check the errors above.")
        print("   See HUGGINGFACE_SPACES_DEPLOYMENT.md for troubleshooting.")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
