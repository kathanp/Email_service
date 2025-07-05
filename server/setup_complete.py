#!/usr/bin/env python3
"""
Complete Setup Script for Email Bot
This script configures both Google OAuth and AWS SES for the email bot.
"""

import os
import sys

def setup_complete():
    """Complete setup for Email Bot with Google OAuth and AWS SES."""
    print("🚀 Complete Email Bot Setup")
    print("=" * 50)
    
    print("\n📋 This setup configures:")
    print("1. Google OAuth for user authentication")
    print("2. AWS SES for email sending")
    print("3. User's Google email becomes sender email")
    
    print("\n🔧 Step 1: Google OAuth Setup")
    print("-" * 30)
    
    print("\n🌐 Google OAuth Setup Steps:")
    print("1. Go to https://console.developers.google.com/")
    print("2. Create a new project or select existing project")
    print("3. Enable Google+ API (for user info)")
    print("4. Create OAuth 2.0 credentials")
    print("5. Add authorized redirect URI: http://localhost:8000/api/v1/google-auth/callback")
    print("6. Get your Client ID and Client Secret")
    
    print("\n🔑 Please provide your Google OAuth credentials:")
    
    google_client_id = input("Google Client ID: ").strip()
    google_client_secret = input("Google Client Secret: ").strip()
    
    print("\n🔧 Step 2: AWS SES Setup")
    print("-" * 30)
    
    print("\n🌐 AWS SES Setup Steps:")
    print("1. Go to https://aws.amazon.com/ses/")
    print("2. Sign up for AWS (if you don't have an account)")
    print("3. Navigate to Amazon SES in your preferred region")
    print("4. Verify your sender email address (required for sending)")
    print("5. Create an IAM user with SES permissions")
    print("6. Get your Access Key ID and Secret Access Key")
    
    print("\n🔑 Please provide your AWS SES credentials:")
    
    aws_access_key_id = input("AWS Access Key ID: ").strip()
    aws_secret_access_key = input("AWS Secret Access Key: ").strip()
    aws_region = input("AWS Region (e.g., us-east-1): ").strip() or "us-east-1"
    default_sender_email = input("Default Sender Email (for fallback): ").strip()
    
    # Update .env file
    env_file_path = '.env'
    env_content = ""
    
    # Read existing .env file if it exists
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            env_content = f.read()
    
    # Add or update configuration
    config = f"""
# Google OAuth Configuration
GOOGLE_CLIENT_ID={google_client_id}
GOOGLE_CLIENT_SECRET={google_client_secret}
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/google-auth/callback

# AWS Configuration
AWS_ACCESS_KEY_ID={aws_access_key_id}
AWS_SECRET_ACCESS_KEY={aws_secret_access_key}
AWS_REGION={aws_region}
DEFAULT_SENDER_EMAIL={default_sender_email}
"""
    
    # Remove existing config if present
    lines = env_content.split('\n')
    filtered_lines = []
    skip_next = False
    
    for line in lines:
        if line.startswith('# Google OAuth Configuration') or line.startswith('# AWS Configuration'):
            skip_next = True
            continue
        if skip_next and (line.startswith('GOOGLE_') or line.startswith('AWS_') or line.startswith('DEFAULT_SENDER_EMAIL=')):
            continue
        if skip_next and line.strip() == '':
            skip_next = False
            continue
        if not skip_next:
            filtered_lines.append(line)
    
    # Add new config
    env_content = '\n'.join(filtered_lines) + config
    
    # Write updated .env file
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        print(f"\n✅ Configuration saved to {env_file_path}")
        
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        return False
    
    print("\n📝 Next Steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start the server: python -m uvicorn app.main:app --reload")
    print("3. Start the frontend: cd client && npm start")
    print("4. Users can now sign in with Google and send emails via AWS SES")
    
    print("\n🔗 Useful Links:")
    print("- Google Cloud Console: https://console.developers.google.com/")
    print("- AWS SES Console: https://console.aws.amazon.com/ses/")
    print("- Google OAuth Documentation: https://developers.google.com/identity/protocols/oauth2")
    print("- AWS SES Documentation: https://docs.aws.amazon.com/ses/")
    
    print("\n⚠️  Important Notes:")
    print("- Make sure to add the redirect URI to your Google OAuth credentials")
    print("- Verify your sender email in AWS SES console")
    print("- For production, update the redirect URI to your domain")
    print("- Users sign in with Google, emails sent via AWS SES")
    print("- User's Google email becomes the sender email for campaigns")
    
    print("\n🎉 Setup Complete!")
    print("Your Email Bot is ready to use with Google OAuth and AWS SES!")
    
    return True

def verify_setup():
    """Verify complete setup."""
    print("\n🔍 Verifying Complete Setup")
    print("=" * 30)
    
    try:
        from app.core.config import settings
        
        # Check Google OAuth
        google_ok = True
        if not settings.GOOGLE_CLIENT_ID:
            print("❌ Google Client ID not configured")
            google_ok = False
        if not settings.GOOGLE_CLIENT_SECRET:
            print("❌ Google Client Secret not configured")
            google_ok = False
        if not settings.GOOGLE_REDIRECT_URI:
            print("❌ Google Redirect URI not configured")
            google_ok = False
        
        # Check AWS SES
        aws_ok = True
        if not settings.AWS_ACCESS_KEY_ID:
            print("❌ AWS Access Key ID not configured")
            aws_ok = False
        if not settings.AWS_SECRET_ACCESS_KEY:
            print("❌ AWS Secret Access Key not configured")
            aws_ok = False
        if not settings.AWS_REGION:
            print("❌ AWS Region not configured")
            aws_ok = False
        
        if google_ok and aws_ok:
            print("✅ Complete configuration found")
            print(f"   Google Client ID: {settings.GOOGLE_CLIENT_ID[:20]}...")
            print(f"   Google Redirect URI: {settings.GOOGLE_REDIRECT_URI}")
            print(f"   AWS Region: {settings.AWS_REGION}")
            print(f"   Default Sender Email: {settings.DEFAULT_SENDER_EMAIL}")
            return True
        else:
            print("❌ Configuration incomplete")
            return False
        
    except ImportError:
        print("❌ Could not import settings. Make sure .env file is configured.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Complete Email Bot Setup")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_setup()
    else:
        setup_complete() 