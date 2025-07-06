#!/usr/bin/env python3


import os
import sys
from pathlib import Path

def download_fallback_model():
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        # Create models directory (from utils folder)
        models_dir = Path(__file__).parent.parent / "models"
        models_dir.mkdir(exist_ok=True)
        
        print("📥 Downloading fallback model (DialoGPT-medium)...")
        print(f"📁 Cache directory: {models_dir.absolute()}")
        
        # Set cache environment variables
        os.environ['HF_HOME'] = str(models_dir.absolute())
        os.environ['TRANSFORMERS_CACHE'] = str(models_dir.absolute())
        
        model_name = "microsoft/DialoGPT-medium"
        
        # Download tokenizer
        print("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=str(models_dir)
        )
        
        # Download model
        print("Downloading model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=str(models_dir),
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        # Get model size
        model_size = sum(p.numel() for p in model.parameters())
        
        print(f"✅ Fallback model downloaded successfully!")
        print(f"📊 Model parameters: {model_size:,}")
        print(f"📁 Cached in: {models_dir.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to download fallback model: {e}")
        return False

if __name__ == "__main__":
    print("🤖 AI Finance Agent - Fallback Model Downloader")
    print("=" * 50)
    
    success = download_fallback_model()
    
    if success:
        print("\n🎉 Download complete!")
        print("\n💡 The model is now cached locally and will load faster.")
        print("   You can now run: python utils/test_model_loading.py")
    else:
        print("\n❌ Download failed. Check your internet connection.")
        sys.exit(1) 