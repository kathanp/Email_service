#!/usr/bin/env python3
"""
Test Campaign API Endpoint
This script tests the campaign creation API to verify it works properly.
"""

import requests
import json
import sys

# API Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    'LOGIN': f"{BASE_URL}/api/auth/login",
    'CAMPAIGNS': f"{BASE_URL}/api/campaigns",
    'CAMPAIGNS_HISTORY': f"{BASE_URL}/api/campaigns/history",
    'SENDERS': f"{BASE_URL}/api/senders",
    'FILES': f"{BASE_URL}/api/files", 
    'TEMPLATES': f"{BASE_URL}/api/templates"
}

def test_login():
    """Test login and get token"""
    print("🔐 Testing Login...")
    
    # You'll need to replace these with actual test credentials
    login_data = {
        "email": "test@example.com",  # Replace with your test email
        "password": "testpassword"    # Replace with your test password
    }
    
    try:
        response = requests.post(API_ENDPOINTS['LOGIN'], json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Login successful! Token: {token[:20]}...")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login exception: {e}")
        return None

def test_fetch_data(token):
    """Test fetching required data for campaign creation"""
    print("\n📋 Testing Data Fetch...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    results = {}
    
    # Test each endpoint
    for name, url in [
        ('senders', API_ENDPOINTS['SENDERS']), 
        ('files', API_ENDPOINTS['FILES']),
        ('templates', API_ENDPOINTS['TEMPLATES']),
        ('campaign_history', API_ENDPOINTS['CAMPAIGNS_HISTORY'])
    ]:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                results[name] = data
                print(f"✅ {name}: {len(data) if isinstance(data, list) else 'OK'}")
            else:
                print(f"❌ {name}: {response.status_code} - {response.text}")
                results[name] = None
        except Exception as e:
            print(f"❌ {name} exception: {e}")
            results[name] = None
    
    return results

def test_create_campaign(token, senders, files, templates):
    """Test campaign creation"""
    print("\n📧 Testing Campaign Creation...")
    
    if not senders or not files or not templates:
        print("❌ Missing required data for campaign creation")
        return False
    
    # Get first available items
    sender_id = senders[0]['id'] if senders else None
    file_id = files[0]['id'] if files else None 
    template_id = templates[0]['id'] if templates else None
    
    if not all([sender_id, file_id, template_id]):
        print("❌ Missing required IDs for campaign creation")
        print(f"Sender ID: {sender_id}, File ID: {file_id}, Template ID: {template_id}")
        return False
    
    campaign_data = {
        "name": "Test Campaign via API",
        "template_id": template_id,
        "file_id": file_id,
        "subject_override": "Test Subject Override",
        "custom_message": "This is a test campaign created via API"
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Creating campaign with data: {json.dumps(campaign_data, indent=2)}")
        response = requests.post(API_ENDPOINTS['CAMPAIGNS'], 
                               headers=headers, 
                               json=campaign_data)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Campaign created successfully!")
            print(f"Campaign ID: {result.get('id', 'N/A')}")
            print(f"Campaign Name: {result.get('name', 'N/A')}")
            print(f"Status: {result.get('status', 'N/A')}")
            print(f"Total Emails: {result.get('total_emails', 'N/A')}")
            return True
        else:
            print(f"❌ Campaign creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Campaign creation exception: {e}")
        return False

def main():
    """Main test function"""
    print("Campaign API Test")
    print("=" * 50)
    print("Make sure you have:")
    print("1. Server running on localhost:8000")
    print("2. Valid test credentials")
    print("3. At least one verified sender, file, and template")
    print()
    
    # Step 1: Login
    token = test_login()
    if not token:
        print("❌ Cannot proceed without valid token")
        return
    
    # Step 2: Fetch required data
    data = test_fetch_data(token)
    
    # Step 3: Create campaign
    success = test_create_campaign(
        token, 
        data.get('senders'), 
        data.get('files'), 
        data.get('templates')
    )
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Campaign API Test Complete - SUCCESS!")
    else:
        print("❌ Campaign API Test Complete - FAILED!")
    
    print("Check the Campaign History in your web app to see if the campaign appears!")

if __name__ == "__main__":
    main() 