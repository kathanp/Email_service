#!/usr/bin/env python3
"""
Test script to verify payment and subscription upgrade flow
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def test_payment_flow():
    print("🧪 Testing Payment and Subscription Upgrade Flow")
    print("=" * 50)
    
    # Step 1: Login with test user
    print("\n1. Logging in with test user...")
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    if login_response.status_code == 200:
        print("✅ User logged in successfully")
        user_data = login_response.json()
        token = user_data.get("access_token")
        user_id = user_data.get("user", {}).get("id")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    # Step 2: Get current subscription (should be free)
    print("\n2. Getting current subscription...")
    headers = {"Authorization": f"Bearer {token}"}
    current_response = requests.get(f"{BASE_URL}/api/v1/subscriptions/current", headers=headers)
    
    if current_response.status_code == 200:
        current_sub = current_response.json()
        print(f"✅ Current plan: {current_sub.get('plan')}")
    else:
        print(f"❌ Failed to get current subscription: {current_response.status_code}")
        print(current_response.text)
        return
    
    # Step 3: Get available plans
    print("\n3. Getting available plans...")
    plans_response = requests.get(f"{BASE_URL}/api/v1/subscriptions/plans", headers=headers)
    
    if plans_response.status_code == 200:
        plans = plans_response.json()
        print(f"✅ Found {len(plans)} plans")
        for plan in plans:
            print(f"   - {plan['id']}: {plan['name']}")
    else:
        print(f"❌ Failed to get plans: {plans_response.status_code}")
        print(plans_response.text)
        return
    
    # Step 4: Upgrade to starter plan
    print("\n4. Upgrading to starter plan...")
    upgrade_data = {"plan": "starter"}
    upgrade_response = requests.post(
        f"{BASE_URL}/api/v1/subscriptions/upgrade", 
        json=upgrade_data, 
        headers=headers
    )
    
    if upgrade_response.status_code == 200:
        upgrade_result = upgrade_response.json()
        print(f"✅ Upgrade successful: {upgrade_result.get('message')}")
    else:
        print(f"❌ Upgrade failed: {upgrade_response.status_code}")
        print(upgrade_response.text)
        return
    
    # Step 5: Verify subscription was updated
    print("\n5. Verifying subscription update...")
    updated_response = requests.get(f"{BASE_URL}/api/v1/subscriptions/current", headers=headers)
    
    if updated_response.status_code == 200:
        updated_sub = updated_response.json()
        print(f"✅ Updated plan: {updated_sub.get('plan')}")
        print(f"✅ Features: {updated_sub.get('features')}")
    else:
        print(f"❌ Failed to get updated subscription: {updated_response.status_code}")
        print(updated_response.text)
        return
    
    print("\n🎉 Payment flow test completed successfully!")

if __name__ == "__main__":
    test_payment_flow() 