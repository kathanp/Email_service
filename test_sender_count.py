#!/usr/bin/env python3
"""
Test Sender Count
This script checks if senders are being counted correctly in the database.
"""

import asyncio
import sys
import logging

# Add the server directory to Python path
sys.path.append('server')

from server.app.db.mongodb import MongoDB
from bson import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_sender_count():
    """Test sender count in database."""
    
    print("🔍 Testing Sender Count in Database")
    print("=" * 50)
    
    try:
        # Connect to MongoDB
        await MongoDB.connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        # Get senders collection
        senders_collection = MongoDB.get_collection("senders")
        if senders_collection is None:
            print("❌ Senders collection not available")
            return
            
        print("✅ Senders collection accessed")
        
        # Get all senders
        print("\n📋 All Senders in Database:")
        all_senders_cursor = senders_collection.find({})
        all_senders = await all_senders_cursor.to_list(length=None)
        
        if not all_senders:
            print("   No senders found in database")
            return
            
        print(f"   Total senders in database: {len(all_senders)}")
        
        # Group by user_id
        user_counts = {}
        for sender in all_senders:
            user_id = sender.get("user_id")
            verification_status = sender.get("verification_status", "unknown")
            email = sender.get("email", "unknown")
            
            if user_id not in user_counts:
                user_counts[user_id] = {
                    "total": 0,
                    "pending": 0, 
                    "verified": 0,
                    "failed": 0,
                    "deleted": 0,
                    "other": 0,
                    "emails": []
                }
            
            user_counts[user_id]["total"] += 1
            user_counts[user_id]["emails"].append(f"{email} ({verification_status})")
            
            if verification_status == "pending":
                user_counts[user_id]["pending"] += 1
            elif verification_status == "verified":
                user_counts[user_id]["verified"] += 1
            elif verification_status == "failed":
                user_counts[user_id]["failed"] += 1
            elif verification_status == "deleted":
                user_counts[user_id]["deleted"] += 1
            else:
                user_counts[user_id]["other"] += 1
        
        # Display results per user
        for user_id, counts in user_counts.items():
            print(f"\n👤 User ID: {user_id}")
            print(f"   Total senders: {counts['total']}")
            print(f"   Pending: {counts['pending']}")
            print(f"   Verified: {counts['verified']}")
            print(f"   Failed: {counts['failed']}")
            print(f"   Deleted: {counts['deleted']}")
            print(f"   Other: {counts['other']}")
            print(f"   Emails: {', '.join(counts['emails'])}")
            
            # Test the filter used in usage stats
            non_deleted_count = await senders_collection.count_documents({
                "user_id": user_id,
                "verification_status": {"$ne": "deleted"}
            })
            print(f"   Non-deleted count (usage stats filter): {non_deleted_count}")
            
            # Expected count for usage stats
            expected_count = counts['total'] - counts['deleted']
            print(f"   Expected count: {expected_count}")
            
            if non_deleted_count == expected_count:
                print("   ✅ Count matches expected value")
            else:
                print("   ❌ Count mismatch!")
        
        print("\n" + "=" * 50)
        print("✅ Sender Count Test Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close MongoDB connection
        await MongoDB.close_mongo_connection()
        print("✅ MongoDB connection closed")

async def main():
    """Main function to run the sender count test."""
    
    print("Sender Count Test Script")
    print("This will check the actual sender counts in the database")
    print("and verify the filtering logic used in usage stats.")
    print()
    
    try:
        await test_sender_count()
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 