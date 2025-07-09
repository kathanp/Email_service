#!/usr/bin/env python3
"""
Quick Test Suite for Email Automation App
Tests critical functionality before production deployment
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class QuickTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}: {message}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_server_health(self):
        """Test if servers are running"""
        print("\n🔍 Testing Server Health...")
        
        # Test backend health
        try:
            response = self.session.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Backend Health Check", True, "Backend server is running")
            else:
                self.log_test("Backend Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection error: {str(e)}")
            
        # Test frontend health
        try:
            response = self.session.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Health Check", True, "Frontend server is running")
            else:
                self.log_test("Frontend Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Frontend Health Check", False, f"Connection error: {str(e)}")
    
    def test_authentication(self):
        """Test user registration and login"""
        print("\n🔐 Testing Authentication...")
        
        test_user = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPassword123!"
        }
        
        # Test registration
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/register", json=test_user, timeout=10)
            if response.status_code == 201:
                data = response.json()
                if "access_token" in data:
                    self.log_test("User Registration", True, "User registered successfully")
                    # Test login with same user
                    response = self.session.post(f"{BASE_URL}/api/auth/login", json=test_user, timeout=10)
                    if response.status_code == 200:
                        self.log_test("User Login", True, "User logged in successfully")
                    else:
                        self.log_test("User Login", False, f"Status: {response.status_code}")
                else:
                    self.log_test("User Registration", False, "No token returned")
            else:
                self.log_test("User Registration", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Authentication", False, f"Error: {str(e)}")
    
    def test_api_endpoints(self):
        """Test critical API endpoints"""
        print("\n🔗 Testing Critical API Endpoints...")
        
        endpoints = [
            ("GET", "/api/stats/summary", "Stats Summary"),
            ("GET", "/api/v1/subscriptions/plans", "Subscription Plans"),
            ("GET", "/api/templates/", "Templates List"),
            ("GET", "/api/senders/", "Senders List"),
        ]
        
        for method, endpoint, description in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{endpoint}", timeout=10)
                    
                if response.status_code in [200, 201, 204]:
                    self.log_test(description, True, f"Status: {response.status_code}")
                elif response.status_code == 401:
                    self.log_test(description, True, "Unauthorized (expected)")
                else:
                    self.log_test(description, False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(description, False, f"Error: {str(e)}")
    
    def run_quick_tests(self):
        """Run quick test suite"""
        print("🚀 Starting Quick Test Suite...")
        print(f"Backend URL: {BASE_URL}")
        print(f"Frontend URL: {FRONTEND_URL}")
        
        self.test_server_health()
        self.test_authentication()
        self.test_api_endpoints()
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("📋 QUICK TEST SUMMARY")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        if failed_tests == 0:
            print("\n🎉 All critical tests passed! Ready for production deployment.")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed. Please check issues before production deployment.")

if __name__ == "__main__":
    test_suite = QuickTestSuite()
    test_suite.run_quick_tests() 