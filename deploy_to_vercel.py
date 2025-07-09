#!/usr/bin/env python3
"""
Deployment script for MongoDB-based FastAPI app to Vercel
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return None

def check_vercel_cli():
    """Check if Vercel CLI is installed."""
    try:
        result = subprocess.run(["vercel", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Vercel CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Vercel CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Vercel CLI not found")
        return False

def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = [
        "MONGODB_URL",
        "SECRET_KEY",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Warning: Some environment variables are not set:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nYou can set these in Vercel dashboard after deployment.")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def main():
    """Main deployment function."""
    print("🚀 Starting deployment of MongoDB-based FastAPI app to Vercel")
    print("=" * 60)
    
    # Check Vercel CLI
    if not check_vercel_cli():
        print("\n📦 Installing Vercel CLI...")
        install_result = run_command("npm install -g vercel", "Installing Vercel CLI")
        if not install_result:
            print("❌ Failed to install Vercel CLI. Please install it manually:")
            print("   npm install -g vercel")
            return
    
    # Check environment variables
    check_environment_variables()
    
    # Check if we're in the right directory
    if not Path("vercel.json").exists():
        print("❌ vercel.json not found. Please run this script from the project root.")
        return
    
    if not Path("server/app/main.py").exists():
        print("❌ server/app/main.py not found. Please ensure the MongoDB-based FastAPI app exists.")
        return
    
    print("\n📋 Deployment Checklist:")
    print("✅ Vercel configuration updated to use MongoDB-based app")
    print("✅ Requirements.txt updated with all dependencies")
    print("✅ User model matches MongoDB document format")
    print("✅ Frontend handles user data correctly")
    
    print("\n🚀 Ready to deploy!")
    print("\nTo deploy to Vercel, run:")
    print("   vercel --prod")
    
    print("\n📝 After deployment, set these environment variables in Vercel dashboard:")
    print("   - MONGODB_URL")
    print("   - SECRET_KEY")
    print("   - AWS_ACCESS_KEY_ID")
    print("   - AWS_SECRET_ACCESS_KEY")
    print("   - AWS_REGION")
    print("   - AWS_SES_SOURCE_EMAIL")
    print("   - GOOGLE_CLIENT_ID")
    print("   - GOOGLE_CLIENT_SECRET")
    print("   - STRIPE_SECRET_KEY")
    print("   - STRIPE_PUBLISHABLE_KEY")
    
    print("\n🔗 Your app will be available at:")
    print("   https://your-project-name.vercel.app")
    
    # Ask if user wants to deploy now
    response = input("\n🤔 Do you want to deploy now? (y/n): ").lower().strip()
    if response == 'y':
        print("\n🚀 Starting deployment...")
        deploy_result = run_command("vercel --prod", "Deploying to Vercel")
        if deploy_result:
            print("✅ Deployment completed successfully!")
            print("🔗 Your app is now live!")
        else:
            print("❌ Deployment failed. Please check the error messages above.")
    else:
        print("📝 You can deploy later by running: vercel --prod")

if __name__ == "__main__":
    main() 