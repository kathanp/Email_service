#!/usr/bin/env python3
"""
Email Bot Deployment Setup Script

This script helps you set up your Email Bot for deployment on platforms like Vercel, Railway, Heroku, etc.
"""

import os
import sys
from pathlib import Path

def print_header():
    """Print setup header."""
    print("=" * 60)
    print("🚀 Email Bot Deployment Setup")
    print("=" * 60)
    print()

def create_env_template():
    """Create .env.template file for deployment reference."""
    print("📝 Creating .env.template file...")
    
    template_content = """# Copy this file to .env and fill in your actual values
# For production deployment, set these as environment variables in your hosting platform

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/google-auth/callback

# MongoDB Configuration
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/email_bot?retryWrites=true&w=majority
DATABASE_NAME=email_bot

# JWT Configuration
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS SES Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
DEFAULT_SENDER_EMAIL=your-verified-sender-email@domain.com

# CORS Configuration (comma-separated for production)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
"""
    
    with open(".env.template", "w") as f:
        f.write(template_content)
    
    print("✅ Created .env.template file")
    print()

def print_deployment_instructions():
    """Print deployment instructions for different platforms."""
    print("🌐 Deployment Instructions:")
    print()
    
    print("📋 For Vercel:")
    print("1. Go to vercel.com and create a new project")
    print("2. Connect your GitHub repository")
    print("3. In project settings, go to 'Environment Variables'")
    print("4. Add each variable from .env.template")
    print("5. Update GOOGLE_REDIRECT_URI to your Vercel domain")
    print("6. Deploy!")
    print()
    
    print("📋 For Railway:")
    print("1. Go to railway.app and create a new project")
    print("2. Connect your GitHub repository")
    print("3. Go to 'Variables' tab")
    print("4. Add each variable from .env.template")
    print("5. Update GOOGLE_REDIRECT_URI to your Railway domain")
    print("6. Deploy!")
    print()
    
    print("📋 For Heroku:")
    print("1. Install Heroku CLI")
    print("2. Create app: heroku create your-app-name")
    print("3. Add variables: heroku config:set KEY=value")
    print("4. Update GOOGLE_REDIRECT_URI to your Heroku domain")
    print("5. Deploy: git push heroku main")
    print()

def print_google_oauth_setup():
    """Print Google OAuth setup instructions."""
    print("🔐 Google OAuth Setup for Production:")
    print()
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Select your project")
    print("3. Go to 'APIs & Services' > 'Credentials'")
    print("4. Edit your OAuth 2.0 Client ID")
    print("5. Add your production domain to 'Authorized redirect URIs':")
    print("   - For Vercel: https://your-app.vercel.app/api/v1/google-auth/callback")
    print("   - For Railway: https://your-app.railway.app/api/v1/google-auth/callback")
    print("   - For Heroku: https://your-app.herokuapp.com/api/v1/google-auth/callback")
    print("6. Save the changes")
    print()

def print_environment_variables():
    """Print the environment variables that need to be set."""
    print("🔧 Required Environment Variables:")
    print()
    
    variables = [
        ("GOOGLE_CLIENT_ID", "Your Google OAuth Client ID"),
        ("GOOGLE_CLIENT_SECRET", "Your Google OAuth Client Secret"),
        ("GOOGLE_REDIRECT_URI", "Your production callback URL"),
        ("MONGODB_URL", "Your MongoDB connection string"),
        ("DATABASE_NAME", "Your database name (default: email_bot)"),
        ("SECRET_KEY", "JWT secret key (generate with: openssl rand -hex 32)"),
        ("AWS_ACCESS_KEY_ID", "Your AWS SES access key"),
        ("AWS_SECRET_ACCESS_KEY", "Your AWS SES secret key"),
        ("DEFAULT_SENDER_EMAIL", "Your verified sender email"),
        ("CORS_ORIGINS", "Comma-separated list of allowed origins"),
        ("STRIPE_SECRET_KEY", "Your Stripe secret key"),
        ("STRIPE_PUBLISHABLE_KEY", "Your Stripe publishable key"),
        ("STRIPE_WEBHOOK_SECRET", "Your Stripe webhook secret")
    ]
    
    for var, description in variables:
        print(f"  {var}: {description}")
    
    print()

def print_next_steps():
    """Print next steps after setup."""
    print("🚀 Next Steps:")
    print("1. Copy .env.template to .env and fill in your local values")
    print("2. Set up Google OAuth redirect URIs for production")
    print("3. Deploy to your chosen platform")
    print("4. Add environment variables in your hosting platform")
    print("5. Test the deployment")
    print()

def main():
    """Main setup function."""
    print_header()
    
    # Create .env.template
    create_env_template()
    
    # Print deployment instructions
    print_deployment_instructions()
    
    # Print Google OAuth setup
    print_google_oauth_setup()
    
    # Print environment variables
    print_environment_variables()
    
    # Print next steps
    print_next_steps()
    
    print("🎉 Setup complete! Follow the instructions above to deploy your app.")
    print("📖 For detailed instructions, see the DEPLOYMENT_GUIDE.md file.")

if __name__ == "__main__":
    main() 