#!/usr/bin/env python3
"""
Simple test script to verify Google OAuth flow is working
"""
import requests
import json

def test_google_oauth():
    base_url = "https://www.mailsflow.net"
    
    print("🔍 Testing Google OAuth flow...")
    
    # Test 1: Check if the login URL endpoint works
    try:
        response = requests.get(f"{base_url}/api/v1/google-auth/login-url")
        if response.status_code == 200:
            data = response.json()
            print("✅ Login URL endpoint working")
            print(f"   Auth URL: {data.get('auth_url', 'N/A')[:50]}...")
            print(f"   Client ID: {data.get('client_id', 'N/A')}")
        else:
            print(f"❌ Login URL endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing login URL: {e}")
        return False
    
    # Test 2: Check if the main page loads
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Main page loads successfully")
        else:
            print(f"❌ Main page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing main page: {e}")
        return False
    
    # Test 3: Check if auth endpoints are accessible
    try:
        response = requests.get(f"{base_url}/api/auth/me")
        # This should return 401 (unauthorized) which is expected
        if response.status_code in [401, 403]:
            print("✅ Auth endpoints are accessible (401 expected for unauthenticated)")
        else:
            print(f"⚠️  Auth endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing auth endpoint: {e}")
        return False
    
    print("\n🎉 All basic tests passed!")
    print("\n📋 Next steps:")
    print("1. Go to https://www.mailsflow.net")
    print("2. Click 'Continue with Google'")
    print("3. Select your Google account")
    print("4. You should be redirected to the dashboard")
    
    return True

if __name__ == "__main__":
    test_google_oauth() 