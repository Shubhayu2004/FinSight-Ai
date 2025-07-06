import requests
import json
import time
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   Model available: {data['model_available']}")
            print(f"   Processor available: {data['processor_available']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_model_info():
    print("\n🤖 Testing model info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/model-info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model info retrieved")
            print(f"   Model: {data['model_name']}")
            print(f"   Type: {data['model_type']}")
            print(f"   Device: {data['device']}")
            print(f"   CUDA: {data['cuda_available']}")
            print(f"   Uses PEFT: {data['uses_peft']}")
            return True
        else:
            print(f"❌ Model info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model info error: {e}")
        return False

def test_model():
    print("\n🧠 Testing model with simple query...")
    try:
        response = requests.post(f"{BASE_URL}/test-model")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model test completed")
            print(f"   Success: {data['success']}")
            print(f"   Query: {data['test_query']}")
            print(f"   Response: {data['response'][:100]}...")
            return data['success']
        else:
            print(f"❌ Model test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model test error: {e}")
        return False

def test_upload_pdf():
    """Test PDF upload functionality."""
    print("\n📄 Testing PDF upload...")
    
    # Check if there are any PDF files in the Reports directory
    reports_dir = Path(__file__).parent.parent / "Reports"
    pdf_files = list(reports_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("⚠️  No PDF files found in Reports directory")
        print("   Skipping upload test")
        return None
    
    # Use the first PDF file
    pdf_file = pdf_files[0]
    print(f"📁 Using PDF file: {pdf_file.name}")
    
    try:
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file.name, f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/upload-pdf", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PDF upload successful")
            print(f"   Filename: {data['filename']}")
            return data['filename']
        else:
            print(f"❌ PDF upload failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ PDF upload error: {e}")
        return None

def test_process_report(filename):
    if not filename:
        print("⚠️  Skipping process report test (no filename)")
        return False
    
    print(f"\n⚙️  Testing report processing for: {filename}")
    try:
        data = {"pdf_filename": filename, "force_reprocess": False}
        response = requests.post(f"{BASE_URL}/process-report", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Report processing completed")
            print(f"   Success: {result['success']}")
            print(f"   Total chunks: {result['total_chunks']}")
            print(f"   Sections found: {result['sections_found']}")
            return result['success']
        else:
            print(f"❌ Report processing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Report processing error: {e}")
        return False

def test_query_report(filename):
    """Test report querying."""
    if not filename:
        print("⚠️  Skipping query report test (no filename)")
        return False
    
    print(f"\n❓ Testing report querying for: {filename}")
    try:
        data = {
            "pdf_filename": filename,
            "query": "What is the main business of this company?",
            "company_name": "Test Company"
        }
        response = requests.post(f"{BASE_URL}/query-report", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Report query completed")
            print(f"   Success: {result['success']}")
            print(f"   Query: {result['query']}")
            print(f"   Response: {result['response'][:100]}...")
            return result['success']
        else:
            print(f"❌ Report query failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Report query error: {e}")
        return False

def test_available_sections(filename):
    """Test getting available sections."""
    if not filename:
        print("⚠️  Skipping sections test (no filename)")
        return False
    
    print(f"\n📋 Testing available sections for: {filename}")
    try:
        response = requests.get(f"{BASE_URL}/available-sections/{filename}")
        
        if response.status_code == 200:
            sections = response.json()
            print(f"✅ Available sections retrieved")
            for section_type, section_list in sections.items():
                print(f"   {section_type}: {len(section_list)} sections")
            return True
        else:
            print(f"❌ Available sections failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Available sections error: {e}")
        return False

def test_conversation_history():
    """Test conversation history."""
    print("\n💬 Testing conversation history...")
    try:
        response = requests.get(f"{BASE_URL}/conversation-history")
        
        if response.status_code == 200:
            history = response.json()
            print(f"✅ Conversation history retrieved")
            print(f"   History length: {len(history)}")
            return True
        else:
            print(f"❌ Conversation history failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conversation history error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 AI Finance Agent Backend API Tests")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Model Info", test_model_info),
        ("Model Test", test_model),
        ("PDF Upload", test_upload_pdf),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Get uploaded filename for subsequent tests
    uploaded_filename = results.get("PDF Upload")
    
    # Additional tests that depend on uploaded file
    additional_tests = [
        ("Process Report", lambda: test_process_report(uploaded_filename)),
        ("Query Report", lambda: test_query_report(uploaded_filename)),
        ("Available Sections", lambda: test_available_sections(uploaded_filename)),
        ("Conversation History", test_conversation_history),
    ]
    
    for test_name, test_func in additional_tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 