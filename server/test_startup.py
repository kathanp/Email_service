#!/usr/bin/env python3
"""
Test script to check if all backend imports work correctly.
"""

import sys
import os

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports."""
    try:
        print("Testing imports...")
        
        # Test core imports
        from app.core.config import settings
        print("✓ Core config imported")
        
        from app.core.security import create_access_token, verify_password
        print("✓ Core security imported")
        
        # Test models
        from app.models.user import UserResponse, TokenData
        print("✓ User models imported")
        
        from app.models.subscription import SubscriptionResponse, UsageStats
        print("✓ Subscription models imported")
        
        # Test database
        from app.db.mongodb import MongoDB
        print("✓ MongoDB imported")
        
        # Test services
        from app.services.auth_service import AuthService
        print("✓ Auth service imported")
        
        from app.services.subscription_service import SubscriptionService
        print("✓ Subscription service imported")
        
        # Test API
        from app.api.deps import get_current_user
        print("✓ API deps imported")
        
        # Test routes
        from app.routes import auth, customers, senders, templates, files, stats
        print("✓ Routes imported")
        
        # Test main app
        from app.main import app
        print("✓ Main app imported")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 