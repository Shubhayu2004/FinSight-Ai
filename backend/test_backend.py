#!/usr/bin/env python3
"""
Test script for FinSight AI Backend
Run this to verify all components are working correctly.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_company_search():
    """Test company search functionality"""
    try:
        # Test search for "Reliance"
        response = requests.get(f"{BASE_URL}/api/company/search?q=Reliance")
        companies = response.json()
        print(f"✅ Company search: Found {len(companies)} companies for 'Reliance'")
        if companies:
            print(f"   First result: {companies[0]}")
        return True
    except Exception as e:
        print(f"❌ Company search failed: {e}")
        return False

def test_llm_status():
    """Test LLM status"""
    try:
        response = requests.get(f"{BASE_URL}/api/llm/status")
        status = response.json()
        print(f"✅ LLM status: {status}")
        return status.get('loaded', False)
    except Exception as e:
        print(f"❌ LLM status check failed: {e}")
        return False

def test_chat():
    """Test chat functionality"""
    try:
        # Test a simple question
        data = {
            "symbol": "RELIANCE",
            "question": "What is the company's main business?",
            "context": "Reliance Industries Ltd. is a diversified conglomerate with interests in energy, petrochemicals, natural gas, retail, telecommunications, mass media, and textiles."
        }
        
        response = requests.post(f"{BASE_URL}/api/chat/ask", json=data)
        result = response.json()
        print(f"✅ Chat test: {result.get('answer', 'No answer')[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def test_report_upload():
    """Test report upload endpoint (without actual file)"""
    try:
        # Test URL parsing
        response = requests.get(f"{BASE_URL}/api/report/parse-url?url=https://example.com")
        result = response.json()
        print(f"✅ Report parsing: {result.get('text_length', 0)} characters extracted")
        return True
    except Exception as e:
        print(f"❌ Report parsing test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing FinSight AI Backend...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Company Search", test_company_search),
        ("LLM Status", test_llm_status),
        ("Chat Functionality", test_chat),
        ("Report Parsing", test_report_upload),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Backend is ready.")
    else:
        print("⚠️  Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main() 