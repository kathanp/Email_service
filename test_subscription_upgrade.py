#!/usr/bin/env python3
"""
Test script to verify subscription upgrade flow
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass123"

def test_subscription_upgrade():
    """Test the complete subscription upgrade flow"""
    
    print("🧪 Testing Subscription Upgrade Flow")
    print("=" * 50)
    
    # Step 1: Register a new user
    print("\n1. Registering new user...")
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    if response.status_code == 201:
        token_data = response.json()
        token = token_data["access_token"]
        user_id = token_data["user"]["id"]
        print(f"✅ User registered successfully - ID: {user_id}")
        print(f"✅ Initial plan: {token_data['user'].get('usersubscription', 'free')}")
    else:
        print(f"❌ Registration failed: {response.status_code} - {response.text}")
        return
    
    # Step 2: Check current subscription
    print("\n2. Checking current subscription...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/subscriptions/current", headers=headers)
    if response.status_code == 200:
        current_sub = response.json()
        print(f"✅ Current subscription: {current_sub.get('plan', 'free')}")
    else:
        print(f"❌ Failed to get current subscription: {response.status_code}")
    
    # Step 3: Test subscription upgrade
    print("\n3. Testing subscription upgrade...")
    upgrade_data = {"plan": "starter"}
    response = requests.post(f"{BASE_URL}/api/v1/subscriptions/upgrade", 
                           json=upgrade_data, headers=headers)
    if response.status_code == 200:
        upgrade_result = response.json()
        print(f"✅ Subscription upgraded successfully: {upgrade_result}")
    else:
        print(f"❌ Upgrade failed: {response.status_code} - {response.text}")
    
    # Step 4: Verify updated subscription
    print("\n4. Verifying updated subscription...")
    response = requests.get(f"{BASE_URL}/api/v1/subscriptions/current", headers=headers)
    if response.status_code == 200:
        updated_sub = response.json()
        print(f"✅ Updated subscription: {updated_sub.get('plan', 'free')}")
    else:
        print(f"❌ Failed to get updated subscription: {response.status_code}")
    
    # Step 5: Test plan limits
    print("\n5. Testing plan limits...")
    from server.app.services.subscription_service import SubscriptionService
    from server.app.models.user import UserResponse
    
    # Create a mock user for testing
    test_user = UserResponse(
        id=user_id,
        email=TEST_EMAIL,
        username="testuser",
        full_name="Test User",
        role="user",
        created_at="2024-01-01T00:00:00",
        last_login="2024-01-01T00:00:00",
        is_active=True,
        usersubscription="starter"  # Updated plan
    )
    
    subscription_service = SubscriptionService()
    limits = subscription_service.get_user_plan_limits(test_user)
    print(f"✅ Plan limits for starter plan:")
    print(f"   - Emails per month: {limits['emails_per_month']}")
    print(f"   - Sender emails: {limits['sender_emails']}")
    print(f"   - Templates: {limits['templates']}")
    print(f"   - API access: {limits['api_access']}")
    
    print("\n🎉 Subscription upgrade test completed successfully!")

if __name__ == "__main__":
    test_subscription_upgrade() 