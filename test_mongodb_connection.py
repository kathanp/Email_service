#!/usr/bin/env python3
"""
Test MongoDB connection with current configuration
"""

import asyncio
import sys
import os

# Add the server directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from app.core.config import settings
from app.db.mongodb import MongoDB

async def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    print("=" * 50)
    print("Testing MongoDB Connection")
    print("=" * 50)
    
    try:
        print(f"📊 MongoDB URL: {settings.MONGODB_URL}")
        print(f"📊 Database Name: {settings.DATABASE_NAME}")
        
        # Initialize MongoDB connection
        print("\n🔍 Initializing MongoDB connection...")
        await MongoDB.connect_to_mongo()
        
        # Test connection by getting a collection
        print("🔍 Testing collection access...")
        collection = MongoDB.get_collection("users")
        
        if collection is None:
            print("❌ ERROR: Collection is None - connection failed")
            return False
        
        # Test basic operation
        print("🔍 Testing document count...")
        count = await collection.count_documents({})
        print(f"✅ SUCCESS: Found {count} documents in users collection")
        
        # Test insert operation
        print("🔍 Testing insert operation...")
        test_doc = {"test": "connection", "timestamp": "2024-01-01"}
        result = await collection.insert_one(test_doc)
        print(f"✅ SUCCESS: Inserted document with ID: {result.inserted_id}")
        
        # Clean up test document
        await collection.delete_one({"_id": result.inserted_id})
        print("✅ SUCCESS: Cleaned up test document")
        
        # Close connection
        await MongoDB.close_mongo_connection()
        
        print("\n🎉 MongoDB connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: MongoDB connection failed")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_mongodb_connection())
    sys.exit(0 if result else 1) 