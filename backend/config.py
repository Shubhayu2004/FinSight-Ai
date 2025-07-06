import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# FinGPT model configuration - using open-access models as fallback
# Note: Llama-2-7b-chat-hf requires access approval from Meta
FINGPT_MODEL_NAME = "microsoft/DialoGPT-medium"  # Fallback open model
LLAMA2_MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"  # Requires access approval

# PEFT adapter configuration
PEFT_ADAPTER_NAME = "FinGPT/fingpt-forecaster_dow30_llama2-7b_lora"

# Local model cache configuration
MODEL_CACHE_DIR = BASE_DIR / ".." / "models"  # Local cache directory
USE_LOCAL_CACHE = True  # Whether to use local cache

# Reports directory
REPORTS_DIR = BASE_DIR / ".." / "Reports"

# Cache directory
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Upload directory
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# LLM Configuration
LLM_CONFIG = {
    "fingpt": {
        "model_name": FINGPT_MODEL_NAME,  # Uses fallback model
        "device": "auto",
        "max_context_tokens": 4000,
        "max_new_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "cache_dir": str(MODEL_CACHE_DIR) if USE_LOCAL_CACHE else None
    },
    "llama2": {
        "model_name": LLAMA2_MODEL_NAME,  # Gated model
        "device": "auto",
        "max_context_tokens": 4000,
        "max_new_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "cache_dir": str(MODEL_CACHE_DIR) if USE_LOCAL_CACHE else None
    },
    "huggingface": {
        "model_name": "microsoft/DialoGPT-medium",
        "max_length": 512,
        "temperature": 0.7
    }
}

# PDF Processing Configuration
PDF_CONFIG = {
    "max_pages": 1000,
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "min_section_length": 100
}

# API Configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": True,
    "reload": True
}

def setup_model_cache():
    if USE_LOCAL_CACHE and MODEL_CACHE_DIR.exists():
        os.environ['HF_HOME'] = str(MODEL_CACHE_DIR.absolute())
        os.environ['TRANSFORMERS_CACHE'] = str(MODEL_CACHE_DIR.absolute())
        return True
    return False

def get_model_name(model_type: str = "fingpt") -> str:
    return LLM_CONFIG.get(model_type, {}).get("model_name", FINGPT_MODEL_NAME)

def get_cache_dir(model_type: str = "fingpt") -> str:
    return LLM_CONFIG.get(model_type, {}).get("cache_dir")

def validate_paths():
    paths_to_check = {
        "Reports Directory": REPORTS_DIR,
        "Cache Directory": CACHE_DIR,
        "Upload Directory": UPLOAD_DIR
    }
    
    if USE_LOCAL_CACHE:
        paths_to_check["Model Cache Directory"] = MODEL_CACHE_DIR
    
    missing_paths = []
    for name, path in paths_to_check.items():
        if not path.exists():
            missing_paths.append(f"{name}: {path}")
    
    if missing_paths:
        print("❌ Missing required paths:")
        for path in missing_paths:
            print(f"  - {path}")
        return False
    
    print("✅ All required paths exist")
    return True

if __name__ == "__main__":
    print("Configuration Validation")
    print("=" * 30)
    validate_paths()
    
    print(f"\nFinGPT Model Name: {FINGPT_MODEL_NAME}")
    print(f"Llama-2 Model Name: {LLAMA2_MODEL_NAME}")
    print(f"Model Cache Directory: {MODEL_CACHE_DIR}")
    print(f"Use Local Cache: {USE_LOCAL_CACHE}")
    print(f"Reports Directory: {REPORTS_DIR}")
    print(f"Cache Directory: {CACHE_DIR}")
    print(f"Upload Directory: {UPLOAD_DIR}")
    
    if USE_LOCAL_CACHE:
        setup_model_cache()
        print(f"\n✅ Model cache environment variables set:")
        print(f"   HF_HOME: {os.environ.get('HF_HOME', 'Not set')}")
        print(f"   TRANSFORMERS_CACHE: {os.environ.get('TRANSFORMERS_CACHE', 'Not set')}") 