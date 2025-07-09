#!/usr/bin/env python3
"""
Script to check user records in MongoDB database
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime

# Add the server directory to the path so we can import the config
sys.path.append('server/app')

from core.config import settings

def check_users():
    """Check all users in the database"""
    try:
        # Connect to MongoDB
        client = MongoClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        users_collection = db.users
        
        print(f"🔍 Checking users in database: {settings.DATABASE_NAME}")
        print(f"📊 MongoDB URL: {settings.MONGODB_URL}")
        print("=" * 60)
        
        # Get total count
        total_users = users_collection.count_documents({})
        print(f"📈 Total users in database: {total_users}")
        
        if total_users == 0:
            print("❌ No users found in database")
            return
        
        # Get all users
        users = list(users_collection.find({}))
        
        print(f"\n👥 User Records ({len(users)} found):")
        print("-" * 60)
        
        for i, user in enumerate(users, 1):
            print(f"\n👤 User #{i}:")
            print(f"   ID: {user.get('_id')}")
            print(f"   Email: {user.get('email', 'N/A')}")
            print(f"   Username: {user.get('username', 'N/A')}")
            print(f"   Full Name: {user.get('full_name', 'N/A')}")
            print(f"   Is Active: {user.get('is_active', 'N/A')}")
            print(f"   Is Verified: {user.get('is_verified', 'N/A')}")
            print(f"   Created At: {user.get('created_at', 'N/A')}")
            print(f"   Updated At: {user.get('updated_at', 'N/A')}")
            
            # Check if user has subscription info
            if 'subscription' in user:
                sub = user['subscription']
                print(f"   📦 Subscription:")
                print(f"      Plan: {sub.get('plan', 'N/A')}")
                print(f"      Status: {sub.get('status', 'N/A')}")
                print(f"      Expires: {sub.get('expires_at', 'N/A')}")
            
            # Check if user has usage info
            if 'usage' in user:
                usage = user['usage']
                print(f"   📊 Usage:")
                print(f"      Emails Sent: {usage.get('emails_sent', 0)}")
                print(f"      Campaigns Created: {usage.get('campaigns_created', 0)}")
            
            print("-" * 40)
        
        # Check other collections
        print(f"\n📋 Other Collections:")
        collections = db.list_collection_names()
        for collection in collections:
            if collection != 'users':
                count = db[collection].count_documents({})
                print(f"   {collection}: {count} documents")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return False
    
    return True

def check_recent_users():
    """Check only recent users (last 24 hours)"""
    try:
        client = MongoClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        users_collection = db.users
        
        # Get users created in the last 24 hours
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        recent_users = list(users_collection.find({
            "created_at": {"$gte": yesterday}
        }).sort("created_at", -1))
        
        print(f"\n🕐 Recent Users (last 24 hours): {len(recent_users)}")
        print("-" * 40)
        
        for user in recent_users:
            created_at = user.get('created_at', 'Unknown')
            if isinstance(created_at, datetime):
                created_at = created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            
            print(f"📧 {user.get('email', 'N/A')} - Created: {created_at}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error checking recent users: {e}")

if __name__ == "__main__":
    print("🔍 MongoDB User Checker")
    print("=" * 60)
    
    # Check all users
    success = check_users()
    
    if success:
        # Check recent users
        check_recent_users()
    
    print("\n✅ Check complete!") 