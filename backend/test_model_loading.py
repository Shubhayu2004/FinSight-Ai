#!/usr/bin/env python3
"""
Test script to verify FinAgent model loading
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

from annual_report_processor.llm_client import FinAgentLLMClient

def test_model_loading():
    """Test if the FinAgent model can be loaded."""
    print("Testing FinAgent model loading...")
    
    # Test with the corrected path
    model_path = "../llm fine tune/l3_finagent_step60/l3_finagent_step60"
    
    print(f"Model path: {model_path}")
    print(f"Path exists: {os.path.exists(model_path)}")
    
    if not os.path.exists(model_path):
        print("❌ Model path does not exist!")
        return False
    
    try:
        # Initialize the client
        client = FinAgentLLMClient(model_path=model_path)
        
        if client.is_available():
            print("✅ FinAgent model loaded successfully!")
            
            # Get model info
            if hasattr(client, 'get_model_info'):
                model_info = client.get_model_info()
                print(f"  - Base model: {model_info['base_model']}")
                print(f"  - Adapter type: {model_info['adapter_type']}")
                print(f"  - Device: {model_info['device']}")
                print(f"  - Status: {model_info['status']}")
            
            # Test a simple query
            test_prompt = "What is the revenue of the company?"
            try:
                response = client.generate_response(test_prompt, max_new_tokens=50)
                print(f"✅ Test query successful: {response[:100]}...")
                return True
            except Exception as e:
                print(f"❌ Test query failed: {e}")
                return False
        else:
            print("❌ FinAgent model not available")
            return False
            
    except Exception as e:
        print(f"❌ Error loading FinAgent model: {e}")
        return False

if __name__ == "__main__":
    success = test_model_loading()
    if success:
        print("\n🎉 FinAgent model is working correctly!")
    else:
        print("\n💥 FinAgent model loading failed!")
        sys.exit(1) 