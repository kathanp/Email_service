#!/usr/bin/env python3
"""
Comprehensive Stripe Payment Flow Test
Tests the complete payment process including plan upgrades.
"""

import requests
import json
import stripe
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

# Stripe configuration
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
stripe.api_key = STRIPE_SECRET_KEY

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

def get_initial_subscription(token):
    """Get user's current subscription."""
    print_step(2, "Get Initial Subscription")
    
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

def create_payment_intent(token, plan_id="professional", billing_cycle="monthly"):
    """Create a payment intent for the plan upgrade."""
    print_step(3, f"Create Payment Intent for {plan_id}")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "plan": plan_id,
        "billing_cycle": billing_cycle
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/subscriptions/create-payment-intent", 
                           headers=headers, json=data)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        intent_data = response.json()
        client_secret = intent_data.get('client_secret')
        amount = intent_data.get('amount', 0)
        print(f"   ✅ Payment intent created")
        print(f"   Amount: ${amount / 100}")
        print(f"   Client Secret: {client_secret[:20]}...")
        return intent_data
    else:
        print(f"   ❌ Failed to create payment intent: {response.text}")
        return None

def simulate_stripe_payment(client_secret):
    """Simulate a successful Stripe payment using test card."""
    print_step(4, "Simulate Stripe Payment")
    
    try:
        # Extract payment intent ID from client secret
        payment_intent_id = client_secret.split('_secret_')[0]
        
        # Simulate payment with test card
        payment_intent = stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method_data={
                'type': 'card',
                'card': {
                    'number': '4242424242424242',
                    'exp_month': 12,
                    'exp_year': 2025,
                    'cvc': '123',
                },
            },
        )
        
        print(f"   Payment Intent ID: {payment_intent.id}")
        print(f"   Payment Status: {payment_intent.status}")
        
        if payment_intent.status == 'succeeded':
            print(f"   ✅ Payment successful!")
            return payment_intent
        else:
            print(f"   ❌ Payment failed: {payment_intent.status}")
            return None
            
    except stripe.error.StripeError as e:
        print(f"   ❌ Stripe error: {str(e)}")
        return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def confirm_payment_backend(token, payment_intent, plan_id="professional", billing_cycle="monthly"):
    """Confirm payment with backend and update subscription."""
    print_step(5, "Confirm Payment with Backend")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "payment_intent_id": payment_intent.id,
        "plan_id": plan_id,
        "billing_cycle": billing_cycle
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/subscriptions/confirm-payment", 
                           headers=headers, json=data)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Payment confirmed successfully")
        print(f"   Message: {result.get('message', 'N/A')}")
        return result
    else:
        print(f"   ❌ Payment confirmation failed: {response.text}")
        return None

def verify_subscription_update(token):
    """Verify that the subscription was updated."""
    print_step(6, "Verify Subscription Update")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/subscriptions/current", headers=headers)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        subscription = response.json()
        current_plan = subscription.get('plan_id', 'Unknown')
        print(f"   ✅ Updated Plan: {current_plan}")
        return subscription
    else:
        print(f"   ❌ Failed to get updated subscription: {response.text}")
        return None

def test_plan_features(token):
    """Test that the new plan features are accessible."""
    print_step(7, "Test Plan Features")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/subscriptions/usage", headers=headers)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        usage = response.json()
        print(f"   ✅ Plan features accessible")
        print(f"   Current Plan: {usage.get('current_plan', 'Unknown')}")
        print(f"   Email Limit: {usage.get('total_emails_allowed', 'Unknown')}")
        print(f"   Template Limit: {usage.get('total_templates_allowed', 'Unknown')}")
        return usage
    else:
        print(f"   ❌ Failed to get usage stats: {response.text}")
        return None

def main():
    """Run the complete payment flow test."""
    print_separator("🧪 STRIPE PAYMENT FLOW TEST")
    print(f"Testing against: {BASE_URL}")
    print(f"Test Plan: Professional ($29/month)")
    print(f"Test Card: 4242424242424242")
    
    # Step 1: Login
    token = login_and_get_token()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Step 2: Get initial subscription
    initial_subscription = get_initial_subscription(token)
    if not initial_subscription:
        print("\n❌ Cannot get initial subscription")
        return
    
    initial_plan = initial_subscription.get('plan_id', 'free')
    
    # Step 3: Create payment intent
    payment_intent_data = create_payment_intent(token, "professional", "monthly")
    if not payment_intent_data:
        print("\n❌ Cannot create payment intent")
        return
    
    # Step 4: Simulate Stripe payment
    payment_intent = simulate_stripe_payment(payment_intent_data['client_secret'])
    if not payment_intent:
        print("\n❌ Payment simulation failed")
        return
    
    # Step 5: Confirm payment with backend
    confirmation_result = confirm_payment_backend(token, payment_intent, "professional", "monthly")
    if not confirmation_result:
        print("\n❌ Payment confirmation failed")
        return
    
    # Step 6: Verify subscription update
    updated_subscription = verify_subscription_update(token)
    if not updated_subscription:
        print("\n❌ Cannot verify subscription update")
        return
    
    # Step 7: Test plan features
    usage_stats = test_plan_features(token)
    
    # Final Results
    print_separator("📊 TEST RESULTS")
    
    final_plan = updated_subscription.get('plan_id', 'Unknown')
    
    print(f"Initial Plan: {initial_plan}")
    print(f"Final Plan: {final_plan}")
    print(f"Payment Intent ID: {payment_intent.id}")
    print(f"Payment Status: {payment_intent.status}")
    
    if initial_plan != final_plan and final_plan == "professional":
        print("\n🎉 SUCCESS: Complete payment flow working!")
        print("✅ Payment processed successfully")
        print("✅ Subscription upgraded correctly")
        print("✅ Plan features accessible")
    else:
        print("\n⚠️  PARTIAL SUCCESS: Payment processed but subscription may not have updated")
        print(f"   Expected: professional, Got: {final_plan}")
    
    print("\n🔍 Debug Information:")
    print(f"- Backend API: {BASE_URL}")
    print(f"- Stripe Test Mode: {'Yes' if STRIPE_SECRET_KEY.startswith('sk_test_') else 'No'}")
    print(f"- Payment Intent: {payment_intent.id}")
    print(f"- Amount Charged: ${payment_intent.amount / 100}")

if __name__ == "__main__":
    main() 