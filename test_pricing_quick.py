#!/usr/bin/env python3
"""
Quick Pricing Test - Essential Tests Before Launch

This script tests the critical pricing functionality:
1. User can access pricing plans
2. Payment intent creation works
3. Plan upgrade works (simulated success)
4. Plan verification works
5. Downgrade works

Run: python test_pricing_quick.py
"""

import requests
import json
import time
from datetime import datetime

class QuickPricingTest:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {}
        
    def test_auth(self):
        """Quick auth test"""
        print("🔐 Testing authentication...")
        
        # Try login with default test user
        login_data = {
            "email": "test@example.com", 
            "password": "testpassword"
        }
        
        response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print("   Create a test user first or check your credentials")
            return False
            
    def test_pricing_plans(self):
        """Test fetching pricing plans"""
        print("📋 Testing pricing plans...")
        
        response = requests.get(f"{self.base_url}/api/v1/subscriptions/plans", headers=self.headers)
        
        if response.status_code == 200:
            plans = response.json()
            if len(plans) >= 3:  # Expecting Free, Professional, Enterprise
                print(f"✅ Found {len(plans)} pricing plans")
                return plans
            else:
                print(f"❌ Expected at least 3 plans, got {len(plans)}")
                return None
        else:
            print(f"❌ Failed to fetch plans: {response.status_code}")
            return None
            
    def test_current_subscription(self):
        """Test current subscription endpoint"""
        print("📊 Testing current subscription...")
        
        response = requests.get(f"{self.base_url}/api/v1/subscriptions/current", headers=self.headers)
        
        if response.status_code == 200:
            subscription = response.json()
            plan = subscription.get("plan_id", "unknown")
            print(f"✅ Current plan: {plan}")
            return subscription
        else:
            print(f"❌ Failed to get subscription: {response.status_code}")
            return None
            
    def test_payment_intent(self):
        """Test payment intent creation"""
        print("💳 Testing payment intent creation...")
        
        data = {
            "plan": "professional",
            "billing_cycle": "monthly"
        }
        
        response = requests.post(f"{self.base_url}/api/v1/subscriptions/create-payment-intent", 
                               json=data, headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("client_secret") or result.get("is_free_plan"):
                print("✅ Payment intent created successfully")
                return True
            else:
                print("❌ No client secret or free plan indicator")
                return False
        else:
            print(f"❌ Payment intent failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    def test_plan_upgrade_simulation(self):
        """Simulate successful plan upgrade"""
        print("🚀 Testing plan upgrade (simulated)...")
        
        # Simulate successful payment confirmation
        data = {
            "payment_intent_id": f"pi_test_success_{int(time.time())}",
            "plan_id": "professional",
            "billing_cycle": "monthly",
            "is_free_plan": False
        }
        
        response = requests.post(f"{self.base_url}/api/v1/subscriptions/confirm-payment",
                               json=data, headers=self.headers)
        
        if response.status_code == 200:
            print("✅ Plan upgrade simulation successful")
            time.sleep(1)  # Wait for update
            
            # Verify upgrade
            verification = self.test_current_subscription()
            if verification and verification.get("plan_id") == "professional":
                print("✅ Plan upgrade verified - now on Professional plan")
                return True
            else:
                print("❌ Plan upgrade not reflected in subscription")
                return False
        else:
            print(f"❌ Plan upgrade failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    def test_usage_stats(self):
        """Test usage stats endpoint"""
        print("📈 Testing usage stats...")
        
        response = requests.get(f"{self.base_url}/api/v1/subscriptions/usage", headers=self.headers)
        
        if response.status_code == 200:
            usage = response.json()
            print("✅ Usage stats retrieved successfully")
            print(f"   Emails sent: {usage.get('emails_sent_this_month', 'N/A')}")
            print(f"   Senders used: {usage.get('senders_used', 'N/A')}")
            print(f"   Templates: {usage.get('templates_created', 'N/A')}")
            return True
        else:
            print(f"❌ Usage stats failed: {response.status_code}")
            return False
            
    def test_downgrade(self):
        """Test downgrade to free plan"""
        print("⬇️ Testing downgrade to free...")
        
        data = {
            "plan_id": "free",
            "billing_cycle": "monthly"
        }
        
        response = requests.post(f"{self.base_url}/api/v1/subscriptions/change-plan",
                               json=data, headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Downgrade successful")
                return True
            else:
                print("❌ Downgrade failed")
                return False
        else:
            print(f"❌ Downgrade request failed: {response.status_code}")
            return False
            
    def run_all_tests(self):
        """Run all quick tests"""
        print("🎯 Quick Pricing Tests - Essential Functionality")
        print("=" * 50)
        
        tests_passed = 0
        total_tests = 7
        
        # Run tests
        if self.test_auth():
            tests_passed += 1
            
        if self.test_pricing_plans():
            tests_passed += 1
            
        if self.test_current_subscription():
            tests_passed += 1
            
        if self.test_payment_intent():
            tests_passed += 1
            
        if self.test_plan_upgrade_simulation():
            tests_passed += 1
            
        if self.test_usage_stats():
            tests_passed += 1
            
        if self.test_downgrade():
            tests_passed += 1
            
        # Results
        print("\n" + "=" * 50)
        print("📊 QUICK TEST RESULTS")
        print("=" * 50)
        print(f"Tests Passed: {tests_passed}/{total_tests}")
        print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
        
        if tests_passed == total_tests:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Pricing system is ready for production!")
        else:
            print(f"\n⚠️ {total_tests - tests_passed} tests failed")
            print("❌ Fix issues before launching to production")
            
        print("=" * 50)
        
        return tests_passed == total_tests

if __name__ == "__main__":
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    print(f"🔗 Testing against: {base_url}\n")
    
    tester = QuickPricingTest(base_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1) 