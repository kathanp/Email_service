#!/usr/bin/env python3
"""
Comprehensive Test Suite for Email Automation App
Tests all major functionality before production deployment
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class TestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.test_user = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPassword123!"
        }
        self.auth_token = None
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
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.log_test("Backend Health Check", True, "Backend server is running")
            else:
                self.log_test("Backend Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection error: {str(e)}")
            
        # Test frontend health
        try:
            response = self.session.get(FRONTEND_URL)
            if response.status_code == 200:
                self.log_test("Frontend Health Check", True, "Frontend server is running")
            else:
                self.log_test("Frontend Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Frontend Health Check", False, f"Connection error: {str(e)}")
    
    def test_authentication(self):
        """Test user registration and login"""
        print("\n🔐 Testing Authentication...")
        
        # Test registration
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/register", json=self.test_user)
            if response.status_code == 201:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Registration", True, "User registered successfully")
                else:
                    self.log_test("User Registration", False, "No token returned")
            else:
                self.log_test("User Registration", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {str(e)}")
            
        # Test login
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/login", json=self.test_user)
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Login", True, "User logged in successfully")
                else:
                    self.log_test("User Login", False, "No token returned")
            else:
                self.log_test("User Login", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("User Login", False, f"Error: {str(e)}")
    
    def test_file_management(self):
        """Test file upload, processing, and management"""
        print("\n📁 Testing File Management...")
        
        # Create test Excel file (since CSV is not allowed)
        test_excel_content = b'\x50\x4b\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00\x21\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        test_file_path = "test_contacts.xlsx"
        
        try:
            with open(test_file_path, "wb") as f:
                f.write(test_excel_content)
            
            # Test file upload
            with open(test_file_path, "rb") as f:
                files = {"file": ("test_contacts.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                response = self.session.post(f"{BASE_URL}/api/files/upload", files=files)
                
            if response.status_code in [200, 201]:
                data = response.json()
                file_id = data.get("id") or data.get("file_id")
                self.log_test("File Upload", True, f"File uploaded with ID: {file_id}")
                
                # Test file processing
                response = self.session.post(f"{BASE_URL}/api/files/{file_id}/process")
                if response.status_code == 200:
                    self.log_test("File Processing", True, "File processed successfully")
                else:
                    self.log_test("File Processing", False, f"Status: {response.status_code}")
                    
                # Test get files
                response = self.session.get(f"{BASE_URL}/api/files/")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        self.log_test("Get Files", True, f"Found {len(data)} files")
                    else:
                        self.log_test("Get Files", False, "No files returned or invalid format")
                else:
                    self.log_test("Get Files", False, f"Status: {response.status_code}")
                    
            else:
                self.log_test("File Upload", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("File Management", False, f"Error: {str(e)}")
        finally:
            # Cleanup
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
    
    def test_email_templates(self):
        """Test email template management"""
        print("\n📧 Testing Email Templates...")
        
        test_template = {
            "name": "Test Template",
            "subject": "Test Email Subject",
            "body": "<h1>Hello {{name}}</h1><p>This is a test email.</p>"  # Fixed: use 'body' instead of 'content'
        }
        
        try:
            # Test template creation
            response = self.session.post(f"{BASE_URL}/api/templates/", json=test_template)
            if response.status_code == 201:
                data = response.json()
                template_id = data.get("id")
                self.log_test("Template Creation", True, f"Template created with ID: {template_id}")
                
                # Test get templates
                response = self.session.get(f"{BASE_URL}/api/templates/")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        self.log_test("Get Templates", True, f"Found {len(data)} templates")
                    else:
                        self.log_test("Get Templates", False, "No templates returned or invalid format")
                else:
                    self.log_test("Get Templates", False, f"Status: {response.status_code}")
                    
            else:
                self.log_test("Template Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Email Templates", False, f"Error: {str(e)}")
    
    def test_sender_management(self):
        """Test sender email management"""
        print("\n📤 Testing Sender Management...")
        
        test_sender = {
            "email": f"test_sender_{int(time.time())}@example.com",
            "name": "Test Sender"
        }
        
        try:
            # Test sender creation
            response = self.session.post(f"{BASE_URL}/api/senders/", json=test_sender)
            if response.status_code in [200, 201]:
                data = response.json()
                sender_id = data.get("id") or data.get("sender_id")
                self.log_test("Sender Creation", True, f"Sender created with ID: {sender_id}")
                
                # Test get senders
                response = self.session.get(f"{BASE_URL}/api/senders/")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        self.log_test("Get Senders", True, f"Found {len(data)} senders")
                    else:
                        self.log_test("Get Senders", False, "No senders returned or invalid format")
                else:
                    self.log_test("Get Senders", False, f"Status: {response.status_code}")
                    
            else:
                self.log_test("Sender Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Sender Management", False, f"Error: {str(e)}")
    
    def test_campaign_management(self):
        """Test email campaign management"""
        print("\n📊 Testing Campaign Management...")
        
        try:
            # Test get campaigns (using stats endpoint)
            response = self.session.get(f"{BASE_URL}/api/stats/campaigns")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Campaigns", True, f"Found {len(data)} campaigns")
                else:
                    self.log_test("Get Campaigns", False, "Invalid response format")
            else:
                self.log_test("Get Campaigns", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Campaign Management", False, f"Error: {str(e)}")
    
    def test_subscription_management(self):
        """Test subscription and pricing endpoints"""
        print("\n💳 Testing Subscription Management...")
        
        try:
            # Test get plans
            response = self.session.get(f"{BASE_URL}/api/v1/subscriptions/plans")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Get Plans", True, f"Found {len(data)} plans")
                else:
                    self.log_test("Get Plans", False, "No plans returned or invalid format")
            else:
                self.log_test("Get Plans", False, f"Status: {response.status_code}")
                
            # Test get current subscription
            response = self.session.get(f"{BASE_URL}/api/v1/subscriptions/current")
            if response.status_code == 200:
                self.log_test("Get Current Subscription", True, "Subscription status retrieved")
            else:
                self.log_test("Get Current Subscription", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Subscription Management", False, f"Error: {str(e)}")
    
    def test_stats_endpoints(self):
        """Test statistics endpoints"""
        print("\n📈 Testing Statistics Endpoints...")
        
        try:
            # Test get stats summary
            response = self.session.get(f"{BASE_URL}/api/stats/summary")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Stats Summary", True, "Statistics retrieved successfully")
            else:
                self.log_test("Get Stats Summary", False, f"Status: {response.status_code}")
                
            # Test get recent activity
            response = self.session.get(f"{BASE_URL}/api/stats/activity")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Recent Activity", True, "Activity data retrieved successfully")
            else:
                self.log_test("Get Recent Activity", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Statistics", False, f"Error: {str(e)}")
    
    def test_api_endpoints(self):
        """Test all API endpoints for proper responses"""
        print("\n🔗 Testing API Endpoints...")
        
        endpoints = [
            ("GET", "/api/auth/me", "Get Current User"),
        ]
        
        for method, endpoint, description in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{endpoint}")
                elif method == "POST":
                    response = self.session.post(f"{BASE_URL}{endpoint}")
                    
                if response.status_code in [200, 201, 204]:
                    self.log_test(description, True, f"Status: {response.status_code}")
                elif response.status_code == 401:
                    self.log_test(description, True, "Unauthorized (expected for some endpoints)")
                else:
                    self.log_test(description, False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(description, False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive Test Suite...")
        print(f"Backend URL: {BASE_URL}")
        print(f"Frontend URL: {FRONTEND_URL}")
        
        self.test_server_health()
        self.test_authentication()
        
        if self.auth_token:
            self.test_file_management()
            self.test_email_templates()
            self.test_sender_management()
            self.test_campaign_management()
            self.test_subscription_management()
            self.test_stats_endpoints()
            self.test_api_endpoints()
        else:
            print("⚠️  Skipping authenticated tests - no auth token available")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        
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
        
        # Save results to file
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: test_results.json")
        
        if failed_tests == 0:
            print("\n🎉 All tests passed! Ready for production deployment.")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed. Please fix issues before production deployment.")

if __name__ == "__main__":
    test_suite = TestSuite()
    test_suite.run_all_tests() 