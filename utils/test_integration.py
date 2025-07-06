#!/usr/bin/env python3
"""
Integration test script for the complete AI Finance Agent system.

This script tests the entire pipeline from model loading to API responses.
"""

import os
import sys
import time
import requests
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_model_loading():
    """Test if the model can be loaded."""
    print("🧠 Testing model loading...")
    try:
        from annual_report_processor.llm_client import FinGPTLLMClient
        
        # Test model loading
        client = FinGPTLLMClient()
        if client.is_available():
            print("✅ Model loaded successfully")
            model_info = client.get_model_info()
            print(f"   Model: {model_info['model_name']}")
            print(f"   Device: {model_info['device']}")
            return True
        else:
            print("❌ Model not available")
            return False
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def test_processor_initialization():
    """Test if the processor can be initialized."""
    print("\n⚙️  Testing processor initialization...")
    try:
        from annual_report_processor import AnnualReportProcessor
        
        processor = AnnualReportProcessor(
            llm_client_type="fingpt",
            max_context_tokens=4000
        )
        print("✅ Processor initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Processor initialization failed: {e}")
        return False

def test_backend_server():
    """Test if the backend server is running."""
    print("\n🌐 Testing backend server...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend server is running")
            print(f"   Status: {data['status']}")
            print(f"   Model available: {data['model_available']}")
            return True
        else:
            print(f"❌ Backend server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running")
        print("   Start it with: python start_backend.py")
        return False
    except Exception as e:
        print(f"❌ Backend server test failed: {e}")
        return False

def test_api_endpoints():
    """Test key API endpoints."""
    print("\n🔌 Testing API endpoints...")
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/model-info", "Model info"),
        ("/uploaded-files", "Uploaded files"),
        ("/conversation-history", "Conversation history")
    ]
    
    results = {}
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description}: OK")
                results[endpoint] = True
            else:
                print(f"❌ {description}: Status {response.status_code}")
                results[endpoint] = False
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
            results[endpoint] = False
    
    return all(results.values())

def test_model_query():
    """Test model query functionality."""
    print("\n❓ Testing model query...")
    try:
        response = requests.post("http://localhost:8000/test-model", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ Model query successful")
                print(f"   Response: {data['response'][:100]}...")
                return True
            else:
                print("❌ Model query failed")
                print(f"   Error: {data['response']}")
                return False
        else:
            print(f"❌ Model query returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model query test failed: {e}")
        return False

def test_file_upload():
    """Test file upload functionality."""
    print("\n📄 Testing file upload...")
    
    # Check if there are any PDF files in Reports directory
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
            response = requests.post("http://localhost:8000/upload-pdf", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ File upload successful")
            print(f"   Filename: {data['filename']}")
            return data['filename']
        else:
            print(f"❌ File upload failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ File upload test failed: {e}")
        return None

def test_report_processing(filename):
    """Test report processing."""
    if not filename:
        print("⚠️  Skipping report processing test (no filename)")
        return False
    
    print(f"\n⚙️  Testing report processing for: {filename}")
    try:
        data = {"pdf_filename": filename, "force_reprocess": False}
        response = requests.post("http://localhost:8000/process-report", json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Report processing successful")
                print(f"   Total chunks: {result['total_chunks']}")
                print(f"   Sections found: {result['sections_found']}")
                return True
            else:
                print("❌ Report processing failed")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Report processing returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Report processing test failed: {e}")
        return False

def test_report_query(filename):
    """Test report querying."""
    if not filename:
        print("⚠️  Skipping report query test (no filename)")
        return False
    
    print(f"\n❓ Testing report querying for: {filename}")
    try:
        data = {
            "pdf_filename": filename,
            "query": "What is the main business of this company?",
            "company_name": "Test Company"
        }
        response = requests.post("http://localhost:8000/query-report", json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Report query successful")
                print(f"   Query: {result['query']}")
                print(f"   Response: {result['response'][:100]}...")
                return True
            else:
                print("❌ Report query failed")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Report query returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Report query test failed: {e}")
        return False

def main():
    """Run complete integration test."""
    print("🧪 AI Finance Agent Integration Test")
    print("=" * 50)
    
    # Test model loading
    model_loaded = test_model_loading()
    
    # Test processor initialization
    processor_ready = test_processor_initialization()
    
    # Test backend server
    server_running = test_backend_server()
    
    if not server_running:
        print("\n⚠️  Backend server is not running. Start it with:")
        print("   python start_backend.py")
        return False
    
    # Test API endpoints
    api_working = test_api_endpoints()
    
    # Test model query
    model_working = test_model_query()
    
    # Test file upload
    uploaded_filename = test_file_upload()
    
    # Test report processing
    processing_working = test_report_processing(uploaded_filename)
    
    # Test report querying
    querying_working = test_report_query(uploaded_filename)
    
    # Summary
    print("\n📊 Integration Test Results")
    print("=" * 30)
    
    tests = [
        ("Model Loading", model_loaded),
        ("Processor Init", processor_ready),
        ("Backend Server", server_running),
        ("API Endpoints", api_working),
        ("Model Query", model_working),
        ("File Upload", uploaded_filename is not None),
        ("Report Processing", processing_working),
        ("Report Querying", querying_working)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! System is working correctly.")
        print("\n🚀 You can now:")
        print("   - Access the API at: http://localhost:8000/docs")
        print("   - Upload and analyze annual reports")
        print("   - Query financial data with the FinGPT model")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure the backend server is running")
        print("   2. Check if models are downloaded: python utils/download_fallback_model.py")
        print("   3. Test model loading: python utils/test_model_loading.py")
        print("   4. Check API endpoints: python utils/test_backend.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 