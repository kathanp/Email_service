import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_users():
    """Check if there are any users in the database."""
    try:
        # Get MongoDB URL from environment
        mongodb_url = os.getenv("MONGODB_URL")
        if not mongodb_url:
            print("MONGODB_URL not found in environment variables")
            return
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongodb_url)
        db = client.email_bot  # Use the database name from your config
        
        # Check users collection
        users_collection = db.users
        users_count = await users_collection.count_documents({})
        
        print(f"Total users in database: {users_count}")
        
        if users_count > 0:
            print("\nUser details:")
            async for user in users_collection.find({}):
                print(f"- ID: {user['_id']}")
                print(f"  Name: {user.get('name', 'N/A')}")
                print(f"  Email: {user.get('email', 'N/A')}")
                print(f"  Role: {user.get('role', 'N/A')}")
                print(f"  Created: {user.get('created_at', 'N/A')}")
                print(f"  Active: {user.get('is_active', 'N/A')}")
                print("---")
        else:
            print("No users found in the database.")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"Error checking users: {e}")

if __name__ == "__main__":
    asyncio.run(check_users()) 