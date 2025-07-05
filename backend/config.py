"""
Configuration file for the Annual Report Processor
"""

import os
from pathlib import Path

# Base directory (backend folder)
BASE_DIR = Path(__file__).parent

# Model paths
FINAGENT_MODEL_PATH = BASE_DIR / ".." / "llm fine tune" / "l3_finagent_step60" / "l3_finagent_step60"

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
    "finagent": {
        "model_path": str(FINAGENT_MODEL_PATH),
        "device": "auto",
        "max_context_tokens": 4000,
        "max_new_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9
    },
    "openai": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 1000,
        "temperature": 0.3
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

def get_model_path(model_type: str = "finagent") -> str:
    """Get the model path for the specified model type."""
    if model_type == "finagent":
        return str(FINAGENT_MODEL_PATH)
    return LLM_CONFIG.get(model_type, {}).get("model_path", "")

def validate_paths():
    """Validate that all required paths exist."""
    paths_to_check = {
        "FinAgent Model": FINAGENT_MODEL_PATH,
        "Reports Directory": REPORTS_DIR,
        "Cache Directory": CACHE_DIR,
        "Upload Directory": UPLOAD_DIR
    }
    
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
    
    print(f"\nFinAgent Model Path: {FINAGENT_MODEL_PATH}")
    print(f"Reports Directory: {REPORTS_DIR}")
    print(f"Cache Directory: {CACHE_DIR}")
    print(f"Upload Directory: {UPLOAD_DIR}") 