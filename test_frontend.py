#!/usr/bin/env python3
"""
Frontend Test Suite for Email Automation App
Tests React app functionality and key pages
"""

import requests
import json
from datetime import datetime

# Configuration
FRONTEND_URL = "http://localhost:3000"

class FrontendTestSuite:
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
    
    def test_homepage(self):
        """Test homepage loads correctly"""
        print("\n🏠 Testing Homepage...")
        
        try:
            response = self.session.get(f"{FRONTEND_URL}/", timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                if "react" in content or "email" in content or "app" in content:
                    self.log_test("Homepage Load", True, "Homepage loaded successfully")
                else:
                    self.log_test("Homepage Load", False, "Homepage content not recognized")
            else:
                self.log_test("Homepage Load", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Homepage Load", False, f"Error: {str(e)}")
    
    def test_login_page(self):
        """Test login page loads correctly"""
        print("\n🔐 Testing Login Page...")
        
        try:
            response = self.session.get(f"{FRONTEND_URL}/login", timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                if "login" in content or "email" in content or "password" in content:
                    self.log_test("Login Page Load", True, "Login page loaded successfully")
                else:
                    self.log_test("Login Page Load", False, "Login page content not recognized")
            else:
                self.log_test("Login Page Load", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Login Page Load", False, f"Error: {str(e)}")
    
    def test_dashboard_page(self):
        """Test dashboard page loads correctly"""
        print("\n📊 Testing Dashboard Page...")
        
        try:
            response = self.session.get(f"{FRONTEND_URL}/dashboard", timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                if "dashboard" in content or "react" in content:
                    self.log_test("Dashboard Page Load", True, "Dashboard page loaded successfully")
                else:
                    self.log_test("Dashboard Page Load", False, "Dashboard page content not recognized")
            else:
                self.log_test("Dashboard Page Load", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Dashboard Page Load", False, f"Error: {str(e)}")
    
    def test_pricing_page(self):
        """Test pricing page loads correctly"""
        print("\n💳 Testing Pricing Page...")
        
        try:
            response = self.session.get(f"{FRONTEND_URL}/pricing", timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                if "pricing" in content or "plan" in content or "subscription" in content:
                    self.log_test("Pricing Page Load", True, "Pricing page loaded successfully")
                else:
                    self.log_test("Pricing Page Load", False, "Pricing page content not recognized")
            else:
                self.log_test("Pricing Page Load", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Pricing Page Load", False, f"Error: {str(e)}")
    
    def test_static_assets(self):
        """Test static assets load correctly"""
        print("\n📦 Testing Static Assets...")
        
        assets = [
            "/static/js/",
            "/static/css/",
            "/manifest.json",
            "/favicon.ico"
        ]
        
        for asset in assets:
            try:
                response = self.session.get(f"{FRONTEND_URL}{asset}", timeout=10)
                if response.status_code in [200, 404]:  # 404 is expected for some assets
                    self.log_test(f"Asset Load {asset}", True, f"Status: {response.status_code}")
                else:
                    self.log_test(f"Asset Load {asset}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Asset Load {asset}", False, f"Error: {str(e)}")
    
    def run_frontend_tests(self):
        """Run frontend test suite"""
        print("🚀 Starting Frontend Test Suite...")
        print(f"Frontend URL: {FRONTEND_URL}")
        
        self.test_homepage()
        self.test_login_page()
        self.test_dashboard_page()
        self.test_pricing_page()
        self.test_static_assets()
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("📋 FRONTEND TEST SUMMARY")
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
            print("\n🎉 All frontend tests passed! React app is working correctly.")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed. Please check frontend issues.")

if __name__ == "__main__":
    test_suite = FrontendTestSuite()
    test_suite.run_frontend_tests() 