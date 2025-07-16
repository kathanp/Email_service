#!/usr/bin/env python3
"""
Pricing Test Runner

This script runs pricing tests to verify Stripe integration and plan upgrades.

Usage:
    python run_pricing_tests.py              # Quick tests
    python run_pricing_tests.py --full       # Comprehensive tests
    python run_pricing_tests.py --url http://localhost:8000  # Custom URL
"""

import subprocess
import sys
import argparse
import os

def run_quick_tests(base_url="http://localhost:8000"):
    """Run quick pricing tests"""
    print("🚀 Running Quick Pricing Tests...")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, "test_pricing_quick.py", base_url
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running quick tests: {e}")
        return False

def run_comprehensive_tests(base_url="http://localhost:8000"):
    """Run comprehensive pricing tests"""
    print("🔬 Running Comprehensive Pricing Tests...")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, "test_pricing_comprehensive.py", base_url
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running comprehensive tests: {e}")
        return False

def check_server_status(base_url):
    """Check if the server is running"""
    import requests
    
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    parser = argparse.ArgumentParser(description="Run pricing system tests")
    parser.add_argument("--full", action="store_true", help="Run comprehensive tests")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for testing")
    parser.add_argument("--check-only", action="store_true", help="Only check server status")
    
    args = parser.parse_args()
    
    # Check if test files exist
    if not os.path.exists("test_pricing_quick.py"):
        print("❌ test_pricing_quick.py not found!")
        return False
        
    if args.full and not os.path.exists("test_pricing_comprehensive.py"):
        print("❌ test_pricing_comprehensive.py not found!")
        return False
    
    # Check server status
    print(f"🔍 Checking server at {args.url}...")
    if check_server_status(args.url):
        print("✅ Server is running and accessible")
    else:
        print("❌ Server is not accessible!")
        print("   Make sure your FastAPI server is running:")
        print("   cd server && python main.py")
        if not args.check_only:
            return False
    
    if args.check_only:
        return True
    
    print(f"\n🎯 Testing pricing system at: {args.url}")
    
    if args.full:
        # Run comprehensive tests
        success = run_comprehensive_tests(args.url)
    else:
        # Run quick tests
        success = run_quick_tests(args.url)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        print("✅ Pricing system is ready for production deployment!")
    else:
        print("⚠️ Some tests failed!")
        print("❌ Review the issues before deploying to production.")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 