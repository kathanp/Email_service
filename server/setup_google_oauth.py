#!/usr/bin/env python3
"""
Google OAuth Setup Script for Email Bot

This script helps you set up Google OAuth credentials for user authentication.
Follow the steps below to configure Google OAuth for your application.
"""

import os
import sys
from pathlib import Path

def print_header():
    """Print setup header."""
    print("=" * 60)
    print("🔐 Google OAuth Setup for Email Bot")
    print("=" * 60)
    print()

def print_steps():
    """Print setup steps."""
    print("📋 Setup Steps:")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Google+ API (for user info)")
    print("4. Create OAuth 2.0 credentials")
    print("5. Add authorized redirect URI: http://localhost:8000/api/v1/google-auth/callback")
    print("6. Get your Client ID and Client Secret")
    print()

def create_env_file():
    """Create .env file with Google OAuth configuration."""
    env_path = Path(".env")
    
    if env_path.exists():
        print("⚠️  .env file already exists. Backing up to .env.backup")
        backup_path = Path(".env.backup")
        if backup_path.exists():
            backup_path.unlink()
        env_path.rename(backup_path)
    
    print("📝 Creating .env file...")
    
    env_content = """# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/google-auth/callback

# MongoDB Configuration (update with your MongoDB Atlas credentials)
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/email_bot?retryWrites=true&w=majority
DATABASE_NAME=email_bot

# JWT Configuration (change this in production)
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS SES Configuration (for sending emails)
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
DEFAULT_SENDER_EMAIL=your-verified-sender-email@domain.com

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
"""
    
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    print()

def print_next_steps():
    """Print next steps after setup."""
    print("🚀 Next Steps:")
    print("1. Update the .env file with your actual Google OAuth credentials")
    print("2. Update MongoDB connection string with your MongoDB Atlas credentials")
    print("3. Update AWS SES credentials for email sending")
    print("4. Restart the backend server: python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("5. Test Google OAuth login in the frontend")
    print()

def main():
    """Main setup function."""
    print_header()
    print_steps()
    
    # Change to server directory
    server_dir = Path(__file__).parent
    os.chdir(server_dir)
    
    create_env_file()
    print_next_steps()
    
    print("🎉 Setup complete! Follow the steps above to configure your credentials.")
    print("📖 For detailed instructions, see the README.md file.")

if __name__ == "__main__":
    main() 