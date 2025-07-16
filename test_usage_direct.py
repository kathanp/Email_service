#!/usr/bin/env python3
"""
Direct Usage Stats Test
This script tests the usage stats function directly from the server side.
"""

import asyncio
import sys
import logging

# Add the server directory to Python path
sys.path.append('server')

from server.app.db.mongodb import MongoDB
from server.app.services.subscription_service import SubscriptionService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_usage_stats_direct():
    """Test usage stats function directly"""
    
    print("🔍 Testing Usage Stats Function Directly")
    print("=" * 50)
    
    try:
        # Connect to MongoDB
        await MongoDB.connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        # Initialize subscription service
        subscription_service = SubscriptionService()
        print("✅ Subscription service initialized")
        
        # Test with the user ID we found in the database
        user_id = "686fe8bfe38cb15aa4df7940"  # One of the user IDs with verified senders
        print(f"\n📊 Testing usage stats for user: {user_id}")
        
        # Call the get_usage_stats function directly
        usage_stats = await subscription_service.get_usage_stats(user_id)
        
        print("\n📋 Usage Stats Result:")
        for key, value in usage_stats.items():
            print(f"  {key}: {value}")
        
        # Check the specific field the frontend is looking for
        senders_used = usage_stats.get('senders_used', 'MISSING')
        print(f"\n🎯 Key Field Check:")
        print(f"  senders_used: {senders_used}")
        
        if isinstance(senders_used, int) and senders_used > 0:
            print(f"✅ Function is returning correct sender count: {senders_used}")
        else:
            print(f"❌ Function is not returning correct sender count: {senders_used}")
            
        return usage_stats
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Close MongoDB connection
        await MongoDB.close_mongo_connection()
        print("✅ MongoDB connection closed")

async def test_all_users():
    """Test usage stats for all users"""
    
    print("\n🔍 Testing All Users")
    print("=" * 30)
    
    try:
        # Connect to MongoDB
        await MongoDB.connect_to_mongo()
        
        # Get all user IDs from senders collection
        senders_collection = MongoDB.get_collection("senders")
        all_senders = await senders_collection.find({}).to_list(length=None)
        
        user_ids = list(set(sender.get("user_id") for sender in all_senders if sender.get("user_id")))
        
        subscription_service = SubscriptionService()
        
        for user_id in user_ids:
            print(f"\n👤 User: {user_id}")
            try:
                usage_stats = await subscription_service.get_usage_stats(user_id)
                senders_used = usage_stats.get('senders_used', 0)
                print(f"   Senders used: {senders_used}")
            except Exception as e:
                print(f"   Error: {e}")
                
    except Exception as e:
        print(f"❌ Error testing all users: {e}")
    finally:
        await MongoDB.close_mongo_connection()

async def main():
    """Main function to run the direct usage stats test"""
    
    print("Direct Usage Stats Test")
    print("This will test the subscription service function directly")
    print("to see what data it's returning without API layers.")
    print()
    
    try:
        # Test single user
        await test_usage_stats_direct()
        
        # Test all users
        await test_all_users()
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 