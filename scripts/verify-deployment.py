#!/usr/bin/env python3

"""
Render.com Deployment Verification Script
This script verifies that your application is ready for Render deployment.
"""

import os
import sys
import subprocess
import json

def check_file_exists(filepath, description):
    """Check if a required file exists."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (MISSING)")
        return False

def check_python_dependencies():
    """Check if Python dependencies can be installed."""
    try:
        print("🔍 Checking Python dependencies...")
        result = subprocess.run(['pip', 'check'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Python dependencies are compatible")
            return True
        else:
            print(f"❌ Python dependency issues: {result.stdout}")
            return False
    except Exception as e:
        print(f"⚠️ Could not check Python dependencies: {e}")
        return False

def check_node_dependencies():
    """Check if Node.js dependencies are valid."""
    try:
        print("🔍 Checking Node.js dependencies...")
        if os.path.exists('client/package.json'):
            with open('client/package.json', 'r') as f:
                package_json = json.load(f)
            if 'build' in package_json.get('scripts', {}):
                print("✅ React build script found")
                return True
            else:
                print("❌ React build script missing in package.json")
                return False
        else:
            print("❌ client/package.json not found")
            return False
    except Exception as e:
        print(f"❌ Error checking Node dependencies: {e}")
        return False

def check_environment_template():
    """Check for environment variable template."""
    env_vars_needed = [
        'MONGODB_URL',
        'SECRET_KEY', 
        'JWT_SECRET_KEY',
        'STRIPE_SECRET_KEY',
        'GOOGLE_CLIENT_ID'
    ]
    
    print("🔍 Environment variables needed:")
    for var in env_vars_needed:
        print(f"   • {var}")
    
    return True

def main():
    """Main verification function."""
    print("🚀 Render.com Deployment Verification")
    print("=" * 50)
    
    checks = []
    
    # Check required files
    checks.append(check_file_exists('requirements.txt', 'Python dependencies'))
    checks.append(check_file_exists('render.yaml', 'Render configuration'))
    checks.append(check_file_exists('server/main.py', 'Backend entry point'))
    checks.append(check_file_exists('client/package.json', 'Frontend package.json'))
    checks.append(check_file_exists('client/.env.production', 'Production environment'))
    
    # Check dependencies
    checks.append(check_python_dependencies())
    checks.append(check_node_dependencies())
    
    # Check environment setup
    check_environment_template()
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 All checks passed! Ready for Render deployment.")
        print("\nNext steps:")
        print("1. Push code to GitHub")
        print("2. Follow RENDER_DEPLOYMENT.md guide")
        print("3. Configure environment variables in Render dashboard")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 