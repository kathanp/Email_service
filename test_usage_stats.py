#!/usr/bin/env python3
"""
Test Usage Stats Update
This script tests if the usage stats are being updated correctly after campaign creation.
"""

import requests
import json
import time

# API Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    'LOGIN': f"{BASE_URL}/api/auth/login",
    'USAGE_STATS': f"{BASE_URL}/api/v1/subscriptions/usage",
    'CAMPAIGNS': f"{BASE_URL}/api/campaigns",
    'CAMPAIGNS_HISTORY': f"{BASE_URL}/api/campaigns/history"
}

def test_login_and_get_usage():
    """Test login and get current usage stats"""
    print("🔐 Testing Login and Usage Stats...")
    
    # Login credentials - replace with your test credentials
    login_data = {
        "email": "test@example.com",  # Replace with your actual test email
        "password": "testpassword"    # Replace with your actual test password
    }
    
    try:
        # Step 1: Login
        print("Attempting login...")
        response = requests.post(API_ENDPOINTS['LOGIN'], json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
            
        token = response.json().get('access_token')
        print(f"✅ Login successful! Token: {token[:20]}...")
        
        # Step 2: Get initial usage stats
        headers = {'Authorization': f'Bearer {token}'}
        print("\nGetting initial usage stats...")
        
        usage_response = requests.get(API_ENDPOINTS['USAGE_STATS'], headers=headers)
        if usage_response.status_code == 200:
            usage_data = usage_response.json()
            print("✅ Usage stats retrieved successfully!")
            print(f"📊 Current Usage:")
            print(f"   Emails Sent: {usage_data.get('emails_sent_this_billing_period', 0)}")
            print(f"   Email Limit: {usage_data.get('limit', 'Unknown')}")
            print(f"   Templates Created: {usage_data.get('templates_created', 0)}")
            print(f"   Campaigns Created: {usage_data.get('campaigns_created', 0)}")
            print(f"   Senders Used: {usage_data.get('senders_used', 0)}")
            
            # Check for specific fields that should be tracked
            key_fields = ['emails_sent_this_billing_period', 'templates_created', 'campaigns_created']
            all_zero = all(usage_data.get(field, 0) == 0 for field in key_fields)
            
            if all_zero:
                print("\n⚠️  All usage counts are 0. This might indicate:")
                print("   1. No campaigns have been run yet")
                print("   2. Usage tracking is not working properly")
                print("   3. Email logging is not functioning")
            else:
                print("\n✅ Usage tracking appears to be working - some non-zero values found!")
                
            return token, usage_data
        else:
            print(f"❌ Failed to get usage stats: {usage_response.status_code} - {usage_response.text}")
            return token, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_campaign_history(token):
    """Test campaign history to see if campaigns are being stored"""
    if not token:
        return
        
    print("\n📚 Testing Campaign History...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(API_ENDPOINTS['CAMPAIGNS_HISTORY'], headers=headers)
        if response.status_code == 200:
            campaigns = response.json()
            print(f"✅ Campaign history retrieved: {len(campaigns)} campaigns found")
            
            if campaigns:
                print("Recent campaigns:")
                for i, campaign in enumerate(campaigns[:3]):  # Show first 3
                    print(f"   {i+1}. {campaign.get('name', 'Unknown')} - Status: {campaign.get('status', 'Unknown')}")
                    print(f"      Total Emails: {campaign.get('total_emails', 0)}, Successful: {campaign.get('successful', 0)}")
            else:
                print("   No campaigns in history yet")
                
        else:
            print(f"❌ Failed to get campaign history: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting campaign history: {e}")

def main():
    """Main test function"""
    print("Usage Stats Test Script")
    print("=" * 50)
    print("This script will:")
    print("1. Login to get authentication token")
    print("2. Check current usage statistics")
    print("3. Check campaign history")
    print("4. Provide insights on tracking status")
    print()
    
    # Test login and usage stats
    result = test_login_and_get_usage()
    if not result:
        print("❌ Cannot proceed without successful login")
        return
        
    token, usage_data = result
    
    # Test campaign history
    test_campaign_history(token)
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    if usage_data:
        emails_sent = usage_data.get('emails_sent_this_billing_period', 0)
        campaigns_created = usage_data.get('campaigns_created', 0)
        
        if emails_sent > 0:
            print("✅ Email tracking is working - emails are being counted!")
        else:
            print("⚠️  No emails tracked yet - try creating and running a campaign")
            
        if campaigns_created > 0:
            print("✅ Campaign tracking is working - campaigns are being counted!")
        else:
            print("⚠️  No campaigns tracked yet - try creating a campaign")
            
        print(f"\n💡 Current Stats: {emails_sent} emails sent, {campaigns_created} campaigns created")
    else:
        print("❌ Could not retrieve usage data")
    
    print("\n🔧 If stats are not updating:")
    print("1. Check MongoDB connection")
    print("2. Verify email_logs collection is being populated")
    print("3. Check campaigns collection for new entries")
    print("4. Ensure billing period calculation is correct")

if __name__ == "__main__":
    main() 