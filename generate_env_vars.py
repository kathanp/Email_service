#!/usr/bin/env python3
"""
Environment Variables Generator for Email Bot Deployment

This script helps you generate the environment variables needed for deployment.
"""

import os
import secrets
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key."""
    return secrets.token_hex(32)

def print_env_vars_for_platform(platform_name, domain):
    """Print environment variables formatted for a specific platform."""
    print(f"\n🔧 Environment Variables for {platform_name}:")
    print("=" * 50)
    
    # Generate a secure secret key
    secret_key = generate_secret_key()
    
    # Base environment variables
    env_vars = {
        "GOOGLE_CLIENT_ID": "your-google-client-id-here",
        "GOOGLE_CLIENT_SECRET": "your-google-client-secret-here",
        f"GOOGLE_REDIRECT_URI": f"https://{domain}/api/v1/google-auth/callback",
        "MONGODB_URL": "mongodb+srv://your-username:your-password@your-cluster.mongodb.net/email_bot?retryWrites=true&w=majority",
        "DATABASE_NAME": "email_bot",
        "SECRET_KEY": secret_key,
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "AWS_ACCESS_KEY_ID": "your-aws-access-key-id",
        "AWS_SECRET_ACCESS_KEY": "your-aws-secret-access-key",
        "AWS_REGION": "us-east-1",
        "DEFAULT_SENDER_EMAIL": "your-verified-sender-email@domain.com",
        "CORS_ORIGINS": f"https://{domain},http://localhost:3000",
        "STRIPE_SECRET_KEY": "sk_test_your_stripe_secret_key_here",
        "STRIPE_PUBLISHABLE_KEY": "pk_test_your_stripe_publishable_key_here",
        "STRIPE_WEBHOOK_SECRET": "whsec_your_webhook_secret_here"
    }
    
    if platform_name.lower() == "vercel":
        print("Add these in Vercel Dashboard > Settings > Environment Variables:")
        print()
        for key, value in env_vars.items():
            print(f"{key}={value}")
    
    elif platform_name.lower() == "railway":
        print("Add these in Railway Dashboard > Variables tab:")
        print()
        for key, value in env_vars.items():
            print(f"{key}={value}")
    
    elif platform_name.lower() == "heroku":
        print("Run these commands with Heroku CLI:")
        print()
        for key, value in env_vars.items():
            print(f"heroku config:set {key}={value}")
    
    else:
        print("Environment Variables:")
        print()
        for key, value in env_vars.items():
            print(f"{key}={value}")
    
    print()

def main():
    """Main function."""
    print("🚀 Email Bot Environment Variables Generator")
    print("=" * 50)
    print()
    
    print("This script helps you generate environment variables for deployment.")
    print()
    
    # Get platform choice
    print("Choose your deployment platform:")
    print("1. Vercel")
    print("2. Railway")
    print("3. Heroku")
    print("4. Other")
    print()
    
    choice = input("Enter your choice (1-4): ").strip()
    
    platforms = {
        "1": "Vercel",
        "2": "Railway", 
        "3": "Heroku",
        "4": "Other"
    }
    
    platform = platforms.get(choice, "Other")
    
    # Get domain
    print()
    if platform == "Vercel":
        domain = input("Enter your Vercel domain (e.g., your-app.vercel.app): ").strip()
    elif platform == "Railway":
        domain = input("Enter your Railway domain (e.g., your-app.railway.app): ").strip()
    elif platform == "Heroku":
        domain = input("Enter your Heroku domain (e.g., your-app.herokuapp.com): ").strip()
    else:
        domain = input("Enter your production domain: ").strip()
    
    if not domain:
        print("❌ Domain is required!")
        return
    
    # Print environment variables
    print_env_vars_for_platform(platform, domain)
    
    # Additional instructions
    print("📋 Important Notes:")
    print("1. Replace placeholder values with your actual credentials")
    print("2. Update Google OAuth redirect URI in Google Cloud Console")
    print("3. Make sure your MongoDB cluster allows connections from your deployment platform")
    print("4. Verify your sender email in AWS SES")
    print("5. Test the deployment thoroughly")
    print()
    
    print("🎉 Environment variables generated successfully!")

if __name__ == "__main__":
    main() 