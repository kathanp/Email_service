#!/usr/bin/env python3
"""
Test Usage API Response
This script tests what the usage API is actually returning.
"""

import requests
import json

# API Configuration
BASE_URL = "http://localhost:8000"

def test_usage_api():
    """Test the usage API with proper authentication"""
    
    # Step 1: Login to get a valid token
    login_data = {
        "email": "patelkathan244@gmail.com",  # From the database test results
        "password": "yourpassword"  # You'll need to replace this
    }
    
    print("🔐 Testing Login...")
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return None
        
        token = login_response.json().get('access_token')
        print(f"✅ Login successful!")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None
    
    # Step 2: Test usage API
    print("\n📊 Testing Usage API...")
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        usage_response = requests.get(f"{BASE_URL}/api/v1/subscriptions/usage", headers=headers)
        
        if usage_response.status_code == 200:
            usage_data = usage_response.json()
            print("✅ Usage API response:")
            print(json.dumps(usage_data, indent=2))
            
            # Check specific fields the frontend is looking for
            print("\n🔍 Frontend Fields Check:")
            print(f"emails_sent_this_month: {usage_data.get('emails_sent_this_month', 'MISSING')}")
            print(f"senders_used: {usage_data.get('senders_used', 'MISSING')}")
            print(f"templates_created: {usage_data.get('templates_created', 'MISSING')}")
            
            return usage_data
        else:
            print(f"❌ Usage API failed: {usage_response.status_code}")
            print(f"Response: {usage_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Usage API error: {e}")
        return None

def main():
    print("Usage API Test")
    print("=" * 50)
    print("This will test the actual API response that the dashboard is receiving.")
    print()
    
    usage_data = test_usage_api()
    
    if usage_data:
        print("\n📋 Summary:")
        senders_used = usage_data.get('senders_used', 0)
        if senders_used > 0:
            print(f"✅ Senders count is working: {senders_used}")
        else:
            print(f"❌ Senders count still showing: {senders_used}")
            print("Check if the server restarted properly with the new code.")
    else:
        print("\n❌ Could not test usage API - check login credentials")

if __name__ == "__main__":
    main() 