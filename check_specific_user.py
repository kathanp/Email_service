#!/usr/bin/env python3
"""
Script to check if a specific user exists in MongoDB database
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime

# Add the server directory to the path so we can import the config
sys.path.append('server/app')

from core.config import settings

def check_specific_user(email):
    """Check if a specific user exists by email"""
    try:
        # Connect to MongoDB
        client = MongoClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        users_collection = db.users
        
        print(f"🔍 Checking for user: {email}")
        print(f"📊 Database: {settings.DATABASE_NAME}")
        print("=" * 50)
        
        # Find user by email
        user = users_collection.find_one({"email": email})
        
        if user:
            print("✅ User found!")
            print(f"👤 User Details:")
            print(f"   ID: {user.get('_id')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Username: {user.get('username', 'N/A')}")
            print(f"   Full Name: {user.get('full_name', 'N/A')}")
            print(f"   Is Active: {user.get('is_active', 'N/A')}")
            print(f"   Is Verified: {user.get('is_verified', 'N/A')}")
            print(f"   Created At: {user.get('created_at', 'N/A')}")
            print(f"   Updated At: {user.get('updated_at', 'N/A')}")
            
            # Check subscription
            if 'subscription' in user:
                sub = user['subscription']
                print(f"   📦 Subscription:")
                print(f"      Plan: {sub.get('plan', 'N/A')}")
                print(f"      Status: {sub.get('status', 'N/A')}")
                print(f"      Expires: {sub.get('expires_at', 'N/A')}")
            
            # Check usage
            if 'usage' in user:
                usage = user['usage']
                print(f"   📊 Usage:")
                print(f"      Emails Sent: {usage.get('emails_sent', 0)}")
                print(f"      Campaigns Created: {usage.get('campaigns_created', 0)}")
            
            return True
        else:
            print("❌ User not found!")
            print(f"Email '{email}' does not exist in the database.")
            return False
            
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def check_user_by_username(username):
    """Check if a specific user exists by username"""
    try:
        client = MongoClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        users_collection = db.users
        
        print(f"🔍 Checking for username: {username}")
        print("=" * 50)
        
        user = users_collection.find_one({"username": username})
        
        if user:
            print("✅ User found!")
            print(f"👤 User Details:")
            print(f"   ID: {user.get('_id')}")
            print(f"   Email: {user.get('email', 'N/A')}")
            print(f"   Username: {user.get('username')}")
            print(f"   Full Name: {user.get('full_name', 'N/A')}")
            print(f"   Created At: {user.get('created_at', 'N/A')}")
            return True
        else:
            print("❌ User not found!")
            print(f"Username '{username}' does not exist in the database.")
            return False
            
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python check_specific_user.py <email>")
        print("   or: python check_specific_user.py --username <username>")
        sys.exit(1)
    
    if sys.argv[1] == "--username" and len(sys.argv) >= 3:
        username = sys.argv[2]
        check_user_by_username(username)
    else:
        email = sys.argv[1]
        check_specific_user(email) 