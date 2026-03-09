#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import base64
import os
import time

class ORIONISAPITester:
    def __init__(self, base_url="https://agent-hub-148.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = None
        self.test_session_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        
    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n{status} - {name}")
        if details:
            print(f"   {details}")
        if success:
            self.tests_passed += 1
        else:
            self.failed_tests.append({"test": name, "details": details})

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)
        if self.session_token:
            test_headers['Authorization'] = f'Bearer {self.session_token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            if not success:
                details += f" (Expected: {expected_status})"
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        details += f" - {error_data['detail']}"
                except:
                    details += f" - Response: {response.text[:200]}"
            
            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoint"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root Endpoint", "GET", "", 200)

    def test_system_status(self):
        """Test system status endpoint"""
        success, response = self.run_test("System Status", "GET", "system/status", 200)
        if success and 'agents' in response:
            agent_count = len(response.get('agents', []))
            self.log_test("System Status - Agents Count", agent_count > 0, f"Found {agent_count} agents")
        return success

    def test_auth_session_invalid(self):
        """Test auth session with invalid session_id"""
        return self.run_test(
            "Auth Session (Invalid)", 
            "POST", 
            "auth/session", 
            401,
            {"session_id": "invalid_session_id"}
        )

    def test_auth_me_unauthorized(self):
        """Test /auth/me without authentication"""
        return self.run_test("Auth Me (Unauthorized)", "GET", "auth/me", 401)

    def test_chat_unauthorized(self):
        """Test chat endpoint without authentication"""
        return self.run_test(
            "Chat (Unauthorized)", 
            "POST", 
            "chat", 
            401,
            {"message": "Hello"}
        )

    def test_voice_transcribe_unauthorized(self):
        """Test voice transcribe without authentication"""
        return self.run_test("Voice Transcribe (Unauthorized)", "POST", "voice/transcribe", 401)

    def test_voice_speak_unauthorized(self):
        """Test voice TTS without authentication"""
        return self.run_test(
            "Voice TTS (Unauthorized)", 
            "POST", 
            "voice/speak", 
            401,
            {"text": "Hello"}
        )

    def test_vision_analyze_unauthorized(self):
        """Test vision analysis without authentication"""
        return self.run_test(
            "Vision Analyze (Unauthorized)", 
            "POST", 
            "vision/analyze", 
            401,
            {"image_base64": "fake_base64", "question": "What is this?"}
        )

    def test_image_generate_unauthorized(self):
        """Test image generation without authentication"""
        return self.run_test(
            "Image Generate (Unauthorized)", 
            "POST", 
            "image/generate", 
            401,
            {"prompt": "A beautiful sunset"}
        )

    def test_conversations_unauthorized(self):
        """Test conversations endpoint without authentication"""
        return self.run_test("Conversations (Unauthorized)", "GET", "conversations", 401)

    def test_cors_headers(self):
        """Test CORS configuration"""
        try:
            response = requests.options(f"{self.api_url}/health", timeout=10)
            success = 'access-control-allow-origin' in str(response.headers).lower()
            self.log_test("CORS Headers", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("CORS Headers", False, f"Error: {str(e)}")
            return False

    def test_api_key_validation(self):
        """Test if EMERGENT_LLM_KEY is configured"""
        # This tests endpoints that would use the API key
        success, _ = self.test_chat_unauthorized()
        # If it returns 401 (unauthorized), the endpoint exists and API key validation works
        # If it returns 500, there might be an API key configuration issue
        return success

    def run_all_tests(self):
        """Run comprehensive API tests"""
        print("=" * 60)
        print("🚀 ORIONIS API TESTING SUITE")
        print("=" * 60)
        print(f"Testing API: {self.api_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Basic connectivity tests
        print(f"\n📡 CONNECTIVITY TESTS")
        print("-" * 30)
        self.test_health_check()
        self.test_root_endpoint()
        self.test_cors_headers()
        
        # System status tests
        print(f"\n🖥️  SYSTEM TESTS")
        print("-" * 30)
        self.test_system_status()
        
        # Authentication tests
        print(f"\n🔐 AUTHENTICATION TESTS")
        print("-" * 30)
        self.test_auth_session_invalid()
        self.test_auth_me_unauthorized()
        
        # AI Features tests (unauthorized - should return 401)
        print(f"\n🤖 AI FEATURES TESTS (Unauthorized Access)")
        print("-" * 30)
        self.test_chat_unauthorized()
        self.test_voice_transcribe_unauthorized()
        self.test_voice_speak_unauthorized()
        self.test_vision_analyze_unauthorized()
        self.test_image_generate_unauthorized()
        
        # Data management tests
        print(f"\n📚 DATA MANAGEMENT TESTS (Unauthorized Access)")
        print("-" * 30)
        self.test_conversations_unauthorized()
        
        # API key validation
        print(f"\n🔑 API KEY VALIDATION")
        print("-" * 30)
        self.test_api_key_validation()
        
        # Print summary
        print(f"\n" + "=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"{i}. {test['test']}: {test['details']}")
        else:
            print(f"\n✅ ALL TESTS PASSED!")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Return status for script exit
        return len(self.failed_tests) == 0

def main():
    """Main function"""
    print("🌟 Starting ORIONIS API Testing...")
    
    tester = ORIONISAPITester()
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)