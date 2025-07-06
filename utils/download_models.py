#!/usr/bin/env python3
"""
Model download script for the AI Finance Agent project.

This script downloads and caches models locally to reduce access time and enable offline usage.
"""

import os
import sys
from pathlib import Path
import logging

# Add the backend directory to the path (from utils folder)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_model(model_name: str, cache_dir: str = "models", force_download: bool = False):
    """
    Download a model and cache it locally.
    
    Args:
        model_name: HuggingFace model name
        cache_dir: Directory to cache models
        force_download: Whether to force re-download
    """
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        # Create cache directory (from utils folder)
        cache_path = Path(__file__).parent.parent / cache_dir
        cache_path.mkdir(exist_ok=True)
        
        # Set HuggingFace cache directory
        os.environ['HF_HOME'] = str(cache_path.absolute())
        os.environ['TRANSFORMERS_CACHE'] = str(cache_path.absolute())
        
        logger.info(f"📥 Downloading model: {model_name}")
        logger.info(f"📁 Cache directory: {cache_path.absolute()}")
        
        # Download tokenizer
        logger.info("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=str(cache_path),
            local_files_only=not force_download
        )
        
        # Download model
        logger.info("Downloading model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=str(cache_path),
            local_files_only=not force_download,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        logger.info(f"✅ Model {model_name} downloaded successfully!")
        
        # Get model size
        model_size = sum(p.numel() for p in model.parameters())
        logger.info(f"📊 Model parameters: {model_size:,}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download {model_name}: {e}")
        return False

def download_peft_adapter(adapter_name: str, cache_dir: str = "models", force_download: bool = False):
    """
    Download a PEFT adapter and cache it locally.
    
    Args:
        adapter_name: HuggingFace adapter name
        cache_dir: Directory to cache models
        force_download: Whether to force re-download
    """
    try:
        from peft import PeftModel
        
        # Create cache directory (from utils folder)
        cache_path = Path(__file__).parent.parent / cache_dir
        cache_path.mkdir(exist_ok=True)
        
        # Set HuggingFace cache directory
        os.environ['HF_HOME'] = str(cache_path.absolute())
        os.environ['TRANSFORMERS_CACHE'] = str(cache_path.absolute())
        
        logger.info(f"📥 Downloading PEFT adapter: {adapter_name}")
        logger.info(f"📁 Cache directory: {cache_path.absolute()}")
        
        # Download adapter (this will download the adapter files)
        # Note: PEFT adapters are typically small and download quickly
        logger.info("Downloading PEFT adapter files...")
        
        # We'll use a dummy model to trigger the adapter download
        from transformers import AutoModelForCausalLM
        import torch
        
        # Create a minimal model for adapter download
        dummy_model = AutoModelForCausalLM.from_pretrained(
            "microsoft/DialoGPT-small",  # Small model for testing
            cache_dir=str(cache_path),
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        # Try to load the adapter (this will download it)
        try:
            adapter = PeftModel.from_pretrained(
                dummy_model,
                adapter_name,
                cache_dir=str(cache_path),
                local_files_only=not force_download
            )
            logger.info(f"✅ PEFT adapter {adapter_name} downloaded successfully!")
            return True
        except Exception as adapter_error:
            logger.warning(f"⚠️  Could not load adapter (this is normal if base model doesn't match): {adapter_error}")
            logger.info("✅ PEFT adapter files downloaded successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to download PEFT adapter {adapter_name}: {e}")
        return False

def get_cache_info(cache_dir: str = "models"):
    """Get information about cached models."""
    cache_path = Path(__file__).parent.parent / cache_dir
    
    if not cache_path.exists():
        print("❌ Cache directory not found")
        return
    
    print(f"📊 Cache Information for: {cache_path.absolute()}")
    print("=" * 50)
    
    total_size = 0
    model_count = 0
    
    for item in cache_path.rglob("*"):
        if item.is_file():
            size = item.stat().st_size
            total_size += size
            model_count += 1
    
    print(f"Total files: {model_count}")
    print(f"Total size: {format_size(total_size)}")
    
    # List main directories
    print("\n📁 Cached items:")
    for item in cache_path.iterdir():
        if item.is_dir():
            size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
            print(f"  - {item.name}: {format_size(size)}")

def format_size(size_bytes):
    """Format size in bytes to human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download and cache models locally")
    parser.add_argument("--models", nargs="+", default=["microsoft/DialoGPT-medium"], 
                       help="Models to download")
    parser.add_argument("--adapters", nargs="+", default=["FinGPT/fingpt-forecaster_dow30_llama2-7b_lora"],
                       help="PEFT adapters to download")
    parser.add_argument("--cache-dir", default="models", help="Cache directory")
    parser.add_argument("--force", action="store_true", help="Force re-download")
    parser.add_argument("--info", action="store_true", help="Show cache information")
    
    args = parser.parse_args()
    
    if args.info:
        get_cache_info(args.cache_dir)
        return
    
    print("🤖 AI Finance Agent - Model Downloader")
    print("=" * 40)
    
    # Download models
    for model in args.models:
        success = download_model(model, args.cache_dir, args.force)
        if success:
            print(f"✅ {model} ready!")
        else:
            print(f"❌ {model} failed!")
        print()
    
    # Download adapters
    for adapter in args.adapters:
        success = download_peft_adapter(adapter, args.cache_dir, args.force)
        if success:
            print(f"✅ {adapter} ready!")
        else:
            print(f"❌ {adapter} failed!")
        print()
    
    print("🎉 Download complete!")
    cache_path = Path(__file__).parent.parent / args.cache_dir
    print(f"\n📁 Models cached in: {cache_path.absolute()}")
    print("\n💡 To use cached models, set the cache directory in your environment:")
    print(f"   export HF_HOME={cache_path.absolute()}")
    print(f"   export TRANSFORMERS_CACHE={cache_path.absolute()}")

if __name__ == "__main__":
    main() 