#!/usr/bin/env python3
"""
Test script for FinSight AI Backend Components
Tests all four main components: company_data, report_extractor, technical_data, and chatbot
"""

import requests
import json
import time
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComponentTester:
    """Test all backend components"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}
    
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        try:
            logger.info("Testing health check...")
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Health check passed: {data}")
                self.test_results['health_check'] = {'status': 'PASS', 'data': data}
                return True
            else:
                logger.error(f"Health check failed: {response.status_code}")
                self.test_results['health_check'] = {'status': 'FAIL', 'error': response.text}
                return False
                
        except Exception as e:
            logger.error(f"Health check error: {e}")
            self.test_results['health_check'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def test_system_status(self) -> bool:
        """Test system status endpoint"""
        try:
            logger.info("Testing system status...")
            response = self.session.get(f"{self.base_url}/status")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"System status: {data}")
                self.test_results['system_status'] = {'status': 'PASS', 'data': data}
                return True
            else:
                logger.error(f"System status failed: {response.status_code}")
                self.test_results['system_status'] = {'status': 'FAIL', 'error': response.text}
                return False
                
        except Exception as e:
            logger.error(f"System status error: {e}")
            self.test_results['system_status'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def test_company_data(self) -> bool:
        """Test company data component"""
        try:
            logger.info("Testing company data component...")
            
            # Test company search
            response = self.session.get(f"{self.base_url}/api/company/search?q=RELIANCE&limit=5")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Company search successful: {len(data.get('companies', []))} results")
            else:
                logger.error(f"Company search failed: {response.status_code}")
                return False
            
            # Test company details
            response = self.session.get(f"{self.base_url}/api/company/RELIANCE")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Company details retrieved: {data.get('name', 'N/A')}")
            else:
                logger.error(f"Company details failed: {response.status_code}")
                return False
            
            # Test all companies list
            response = self.session.get(f"{self.base_url}/api/company/list/all")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"All companies list: {len(data)} companies")
            else:
                logger.error(f"All companies list failed: {response.status_code}")
                return False
            
            self.test_results['company_data'] = {'status': 'PASS'}
            return True
            
        except Exception as e:
            logger.error(f"Company data test error: {e}")
            self.test_results['company_data'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def test_report_extractor(self) -> bool:
        """Test report extractor component"""
        try:
            logger.info("Testing report extractor component...")
            
            # Test report fetch (this might fail if no reports are available)
            response = self.session.post(f"{self.base_url}/api/reports/fetch/RELIANCE")
            if response.status_code in [200, 404]:  # 404 is expected if no reports found
                data = response.json()
                logger.info(f"Report fetch response: {data.get('success', False)}")
            else:
                logger.error(f"Report fetch failed: {response.status_code}")
                return False
            
            # Test report sections (this might fail if no reports are available)
            response = self.session.get(f"{self.base_url}/api/reports/RELIANCE/sections")
            if response.status_code in [200, 404]:  # 404 is expected if no reports found
                data = response.json()
                logger.info(f"Report sections response: {data}")
            else:
                logger.error(f"Report sections failed: {response.status_code}")
                return False
            
            self.test_results['report_extractor'] = {'status': 'PASS'}
            return True
            
        except Exception as e:
            logger.error(f"Report extractor test error: {e}")
            self.test_results['report_extractor'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def test_technical_data(self) -> bool:
        """Test technical data component"""
        try:
            logger.info("Testing technical data component...")
            
            # Test company overview
            response = self.session.get(f"{self.base_url}/api/technical/RELIANCE/overview")
            if response.status_code in [200, 404]:  # 404 is expected if API key not configured
                data = response.json()
                logger.info(f"Company overview response: {data}")
            else:
                logger.error(f"Company overview failed: {response.status_code}")
                return False
            
            # Test technical indicators
            response = self.session.get(f"{self.base_url}/api/technical/RELIANCE/indicators")
            if response.status_code in [200, 404]:  # 404 is expected if API key not configured
                data = response.json()
                logger.info(f"Technical indicators response: {data}")
            else:
                logger.error(f"Technical indicators failed: {response.status_code}")
                return False
            
            # Test financial ratios
            response = self.session.get(f"{self.base_url}/api/technical/RELIANCE/fundamentals")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Financial ratios retrieved: P/E={data.get('pe_ratio', 'N/A')}")
            else:
                logger.error(f"Financial ratios failed: {response.status_code}")
                return False
            
            # Test investment recommendation
            response = self.session.get(f"{self.base_url}/api/technical/RELIANCE/recommendation")
            if response.status_code in [200, 404]:  # 404 is expected if technical analysis fails
                data = response.json()
                logger.info(f"Investment recommendation: {data.get('recommendation', 'N/A')}")
            else:
                logger.error(f"Investment recommendation failed: {response.status_code}")
                return False
            
            self.test_results['technical_data'] = {'status': 'PASS'}
            return True
            
        except Exception as e:
            logger.error(f"Technical data test error: {e}")
            self.test_results['technical_data'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def test_chatbot(self) -> bool:
        """Test chatbot component"""
        try:
            logger.info("Testing chatbot component...")
            
            # Test chatbot status
            response = self.session.get(f"{self.base_url}/api/chat/status")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Chatbot status: LLM loaded={data.get('llm_loaded', False)}")
            else:
                logger.error(f"Chatbot status failed: {response.status_code}")
                return False
            
            # Test session creation
            session_data = {
                "company_symbol": "RELIANCE",
                "company_name": "Reliance Industries Ltd."
            }
            response = self.session.post(f"{self.base_url}/api/chat/session/create", json=session_data)
            if response.status_code == 200:
                data = response.json()
                session_id = data.get('id')
                logger.info(f"Chat session created: {session_id}")
            else:
                logger.error(f"Session creation failed: {response.status_code}")
                return False
            
            # Test asking a question
            chat_request = {
                "session_id": session_id,
                "message": "What is the current stock price of Reliance?",
                "company_symbol": "RELIANCE",
                "include_context": True
            }
            response = self.session.post(f"{self.base_url}/api/chat/ask", json=chat_request)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Chat response received: {len(data.get('message', {}).get('content', ''))} characters")
            else:
                logger.error(f"Chat request failed: {response.status_code}")
                return False
            
            # Test session retrieval
            response = self.session.get(f"{self.base_url}/api/chat/session/{session_id}")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Session retrieved: {len(data.get('messages', []))} messages")
            else:
                logger.error(f"Session retrieval failed: {response.status_code}")
                return False
            
            # Clean up session
            response = self.session.delete(f"{self.base_url}/api/chat/session/{session_id}")
            if response.status_code == 200:
                logger.info("Session cleaned up successfully")
            else:
                logger.warning(f"Session cleanup failed: {response.status_code}")
            
            self.test_results['chatbot'] = {'status': 'PASS'}
            return True
            
        except Exception as e:
            logger.error(f"Chatbot test error: {e}")
            self.test_results['chatbot'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all component tests"""
        logger.info("Starting FinSight AI Backend Component Tests")
        logger.info("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("System Status", self.test_system_status),
            ("Company Data", self.test_company_data),
            ("Report Extractor", self.test_report_extractor),
            ("Technical Data", self.test_technical_data),
            ("Chatbot", self.test_chatbot)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\nRunning {test_name} test...")
            try:
                if test_func():
                    passed += 1
                    logger.info(f"✅ {test_name} test PASSED")
                else:
                    logger.error(f"❌ {test_name} test FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name} test ERROR: {e}")
        
        logger.info("\n" + "=" * 50)
        logger.info(f"Test Results: {passed}/{total} tests passed")
        
        # Print detailed results
        logger.info("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = result.get('status', 'UNKNOWN')
            if status == 'PASS':
                logger.info(f"✅ {test_name}: PASS")
            elif status == 'FAIL':
                logger.error(f"❌ {test_name}: FAIL - {result.get('error', 'Unknown error')}")
            else:
                logger.error(f"❌ {test_name}: ERROR - {result.get('error', 'Unknown error')}")
        
        return {
            'passed': passed,
            'total': total,
            'success_rate': passed / total if total > 0 else 0,
            'results': self.test_results
        }

def main():
    """Main test function"""
    tester = ComponentTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\nTest results saved to test_results.json")
    
    if results['success_rate'] >= 0.8:
        logger.info("🎉 Most tests passed! Backend is ready for development.")
    elif results['success_rate'] >= 0.5:
        logger.warning("⚠️  Some tests failed. Check the logs for details.")
    else:
        logger.error("💥 Many tests failed. Backend needs attention.")

if __name__ == "__main__":
    main() 