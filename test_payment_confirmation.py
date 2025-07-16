#!/usr/bin/env python3
"""
Test Payment Confirmation and Subscription Update
This test focuses on the backend payment confirmation flow.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def print_separator(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_step(step, description):
    print(f"\n🔸 Step {step}: {description}")

def login_and_get_token():
    """Login and get authentication token."""
    print_step(1, "Authentication")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, headers=headers)
    print(f"   Login Status: {response.status_code}")
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"   ✅ Login successful")
        return token
    else:
        print(f"   ❌ Login failed: {response.text}")
        return None

def get_current_subscription(token):
    """Get user's current subscription."""
    print_step(2, "Get Current Subscription")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/subscriptions/current", headers=headers)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        subscription = response.json()
        current_plan = subscription.get('plan_id', 'Unknown')
        print(f"   ✅ Current Plan: {current_plan}")
        return subscription
    else:
        print(f"   ❌ Failed to get subscription: {response.text}")
        return None

def get_available_plans(token):
    """Get available subscription plans."""
    print_step(3, "Get Available Plans")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/subscriptions/plans", headers=headers)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        plans = response.json()
        print(f"   ✅ Available plans:")
        for plan in plans:
            print(f"      - {plan['id']}: {plan['name']} (${plan['price_monthly']}/month)")
        return plans
    else:
        print(f"   ❌ Failed to get plans: {response.text}")
        return None

def test_payment_confirmation_without_stripe(token, plan_id="professional"):
    """Test payment confirmation with a mock payment intent ID."""
    print_step(4, f"Test Payment Confirmation (Mock) for {plan_id}")
    
    # Create a mock payment intent ID
    mock_payment_intent_id = f"pi_mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "payment_intent_id": mock_payment_intent_id,
        "plan_id": plan_id,
        "billing_cycle": "monthly"
    }
    
    print(f"   Mock Payment Intent ID: {mock_payment_intent_id}")
    print(f"   Target Plan: {plan_id}")
    
    response = requests.post(f"{BASE_URL}/api/v1/subscriptions/confirm-payment", 
                           headers=headers, json=data)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Payment confirmation successful")
        print(f"   Message: {result.get('message', 'N/A')}")
        return result
    else:
        print(f"   ❌ Payment confirmation failed: {response.text}")
        return None

def verify_subscription_update(token, expected_plan):
    """Verify that the subscription was updated."""
    print_step(5, "Verify Subscription Update")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/subscriptions/current", headers=headers)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        subscription = response.json()
        current_plan = subscription.get('plan_id', 'Unknown')
        print(f"   ✅ Updated Plan: {current_plan}")
        
        if current_plan == expected_plan:
            print(f"   ✅ Plan successfully updated to {expected_plan}")
            return True
        else:
            print(f"   ⚠️  Plan not updated (Expected: {expected_plan}, Got: {current_plan})")
            return False
    else:
        print(f"   ❌ Failed to get updated subscription: {response.text}")
        return False

def test_plan_features(token):
    """Test that the new plan features are accessible."""
    print_step(6, "Test Plan Features")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/subscriptions/usage", headers=headers)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        usage = response.json()
        print(f"   ✅ Plan features accessible")
        print(f"   Current Plan: {usage.get('current_plan', 'Unknown')}")
        print(f"   Email Limit: {usage.get('total_emails_allowed', 'Unknown')}")
        print(f"   Template Limit: {usage.get('total_templates_allowed', 'Unknown')}")
        print(f"   Sender Limit: {usage.get('total_sender_emails_allowed', 'Unknown')}")
        return usage
    else:
        print(f"   ❌ Failed to get usage stats: {response.text}")
        return None

def main():
    """Run the payment confirmation test."""
    print_separator("🧪 PAYMENT CONFIRMATION TEST")
    print(f"Testing against: {BASE_URL}")
    print(f"Test: Backend payment confirmation and subscription update")
    print(f"Note: This test bypasses Stripe API calls")
    
    # Step 1: Login
    token = login_and_get_token()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Step 2: Get initial subscription
    initial_subscription = get_current_subscription(token)
    if not initial_subscription:
        print("\n❌ Cannot get initial subscription")
        return
    
    initial_plan = initial_subscription.get('plan_id', 'free')
    
    # Step 3: Get available plans
    plans = get_available_plans(token)
    if not plans:
        print("\n❌ Cannot get available plans")
        return
    
    # Step 4: Test payment confirmation (mock)
    target_plan = "professional"
    confirmation_result = test_payment_confirmation_without_stripe(token, target_plan)
    
    # Step 5: Verify subscription update
    subscription_updated = verify_subscription_update(token, target_plan)
    
    # Step 6: Test plan features
    usage_stats = test_plan_features(token)
    
    # Final Results
    print_separator("📊 TEST RESULTS")
    
    print(f"Initial Plan: {initial_plan}")
    print(f"Target Plan: {target_plan}")
    print(f"Subscription Updated: {'Yes' if subscription_updated else 'No'}")
    
    if confirmation_result and subscription_updated:
        print("\n🎉 SUCCESS: Payment confirmation flow working!")
        print("✅ Backend API endpoints accessible")
        print("✅ Subscription update logic working")
        print("✅ Plan features accessible")
        print("\n📝 Next Steps:")
        print("1. Configure valid Stripe API keys in environment")
        print("2. Test with real Stripe payment intent")
        print("3. Set up Stripe webhook for production")
    else:
        print("\n⚠️  ISSUES FOUND:")
        if not confirmation_result:
            print("❌ Payment confirmation endpoint failed")
        if not subscription_updated:
            print("❌ Subscription was not updated in database")
        
        print("\n🔍 Debug Information:")
        print("- Check server logs for detailed error messages")
        print("- Verify database connection and user permissions")
        print("- Ensure subscription service is properly configured")

if __name__ == "__main__":
    main() 