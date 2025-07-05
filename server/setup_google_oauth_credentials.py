#!/usr/bin/env python3
"""
Google OAuth Setup Script for Email Bot
This script helps you configure Google OAuth for user authentication.
"""

import os
import json

def setup_google_oauth():
    """Setup Google OAuth credentials."""
    print("🔧 Google OAuth Setup for Email Bot")
    print("=" * 50)
    
    print("\n📋 This setup configures Google OAuth for user authentication.")
    print("Each user will log in with their Google account and use their Gmail as sender.")
    
    print("\n🌐 Google OAuth Setup Steps:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable Google+ API (or Google Identity API)")
    print("4. Go to 'Credentials' section")
    print("5. Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("6. Choose 'Web application'")
    print("7. Add authorized redirect URI: http://localhost:8000/api/v1/google-auth/callback")
    print("8. Copy the Client ID and Client Secret")
    
    print("\n🔑 Please provide your Google OAuth credentials:")
    
    client_id = input("Google Client ID: ").strip()
    client_secret = input("Google Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Client ID and Client Secret are required!")
        return False
    
    # Update config file
    config_file = "app/core/config.py"
    
    try:
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Replace empty Google credentials
        content = content.replace(
            'GOOGLE_CLIENT_ID: str = ""',
            f'GOOGLE_CLIENT_ID: str = "{client_id}"'
        )
        content = content.replace(
            'GOOGLE_CLIENT_SECRET: str = ""',
            f'GOOGLE_CLIENT_SECRET: str = "{client_secret}"'
        )
        
        with open(config_file, 'w') as f:
            f.write(content)
        
        print(f"\n✅ Google OAuth credentials saved to {config_file}")
        
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        return False
    
    print("\n📝 Next Steps:")
    print("1. Restart the backend server")
    print("2. Test Google login in the frontend")
    print("3. Each user will use their Gmail as sender email")
    print("4. No need for AWS SES verification per user")
    
    print("\n🔗 Useful Links:")
    print("- Google Cloud Console: https://console.cloud.google.com/")
    print("- Google OAuth Documentation: https://developers.google.com/identity/protocols/oauth2")
    
    return True

if __name__ == "__main__":
    setup_google_oauth() 