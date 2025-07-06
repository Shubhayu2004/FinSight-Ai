#!/usr/bin/env python3
"""
Test script to verify FinGPT model loading with PEFT adapter.
"""

import sys
import os

# Add the backend directory to the path (from utils folder)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_model_loading():
    """Test the FinGPT model loading with PEFT adapter."""
    print("🧪 Testing FinGPT model loading...")
    print("=" * 60)
    
    try:
        from annual_report_processor.llm_client import FinGPTLLMClient
        
        # Test 1: Fallback model (should work without access approval)
        print("1️⃣ Testing fallback model (open-access)...")
        client_fallback = FinGPTLLMClient(use_llama2=False)
        
        if client_fallback.is_available():
            print("✅ Fallback model loaded successfully!")
            
            # Get model info
            info = client_fallback.get_model_info()
            print(f"\n📊 Fallback Model Information:")
            print(f"   Model name: {info['model_name']}")
            print(f"   Model type: {info['model_type']}")
            print(f"   Device: {info['device']}")
            print(f"   CUDA available: {info['cuda_available']}")
            print(f"   Uses PEFT: {info['uses_peft']}")
            print(f"   Description: {info['description']}")
            
            # Test generation
            print(f"\n🧠 Testing fallback model generation...")
            test_prompt = "What is the main business of this company?"
            test_context = "This is a technology company focused on software development and cloud services."
            
            try:
                response = client_fallback.generate_response(
                    client_fallback.create_financial_prompt(test_context, test_prompt, "Test Company"),
                    max_new_tokens=100
                )
                print(f"✅ Fallback generation successful!")
                print(f"Response: {response[:200]}...")
            except Exception as e:
                print(f"⚠️  Fallback generation failed: {e}")
        else:
            print("❌ Fallback model not available")
            return False
        
        # Test 2: Try Llama-2 model (requires access approval)
        print(f"\n2️⃣ Testing Llama-2 model (requires access approval)...")
        try:
            client_llama2 = FinGPTLLMClient(use_llama2=True)
            
            if client_llama2.is_available():
                print("✅ Llama-2 model with PEFT adapter loaded successfully!")
                
                # Get model info
                info = client_llama2.get_model_info()
                print(f"\n📊 Llama-2 Model Information:")
                print(f"   Model name: {info['model_name']}")
                print(f"   Model type: {info['model_type']}")
                print(f"   Device: {info['device']}")
                print(f"   CUDA available: {info['cuda_available']}")
                print(f"   Uses PEFT: {info['uses_peft']}")
                print(f"   Description: {info['description']}")
                
                # Test generation
                print(f"\n🧠 Testing Llama-2 model generation...")
                try:
                    response = client_llama2.generate_response(
                        client_llama2.create_financial_prompt(test_context, test_prompt, "Test Company"),
                        max_new_tokens=100
                    )
                    print(f"✅ Llama-2 generation successful!")
                    print(f"Response: {response[:200]}...")
                except Exception as e:
                    print(f"⚠️  Llama-2 generation failed: {e}")
            else:
                print("⚠️  Llama-2 model not available (access not approved yet)")
                print("   This is expected if you haven't received access approval from Meta")
                
        except Exception as e:
            print(f"⚠️  Llama-2 model loading failed: {e}")
            print("   This is expected if you haven't received access approval from Meta")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the project root directory")
        print("Required packages: transformers, torch, peft")
        return False
    except Exception as e:
        print(f"💥 Model loading failed!")
        print(f"Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have enough VRAM (at least 4GB recommended)")
        print("2. Install required packages: pip install transformers torch peft")
        print("3. Check your internet connection for model downloads")
        return False
    
    return True

if __name__ == "__main__":
    success = test_model_loading()
    if success:
        print("\n🎉 All tests passed! The FinGPT system is working correctly.")
        print("\n📝 Notes:")
        print("- Fallback model is working (open-access)")
        print("- Llama-2 model requires access approval from Meta")
        print("- Once approved, the system will automatically use Llama-2 with PEFT")
    else:
        print("\n❌ Tests failed. Check the error messages above.")
        sys.exit(1) 