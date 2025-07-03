#!/usr/bin/env python3
"""
MongoDB Atlas Setup Script
This script helps you configure MongoDB Atlas for the Email Bot project.
"""

import os
import sys

def create_env_file():
    """Create .env file with MongoDB Atlas configuration."""
    
    print("🔧 MongoDB Atlas Setup for Email Bot")
    print("=" * 50)
    
    # Get MongoDB Atlas connection details
    print("\n📋 Please provide your MongoDB Atlas connection details:")
    
    username = input("MongoDB Atlas Username: ").strip()
    password = input("MongoDB Atlas Password: ").strip()
    cluster_name = input("MongoDB Atlas Cluster Name: ").strip()
    
    # Generate MongoDB URL
    mongodb_url = f"mongodb+srv://{username}:{password}@{cluster_name}.mongodb.net/email_bot?retryWrites=true&w=majority"
    
    # Generate secret key
    import secrets
    secret_key = secrets.token_urlsafe(32)
    
    # Create .env content
    env_content = f"""# MongoDB Atlas Configuration
MONGODB_URL={mongodb_url}
DATABASE_NAME=email_bot

# JWT Configuration
SECRET_KEY={secret_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=sale.rrimp@gmail.com
SENDER_PASSWORD=mnuiachbwzesyzwv

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ .env file created successfully!")
        print(f"📁 Location: {os.path.abspath('.env')}")
        
    except Exception as e:
        print(f"\n❌ Error creating .env file: {e}")
        return False
    
    print("\n📝 Next Steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start the server: python -m uvicorn app.main:app --reload")
    print("3. Test the API: http://localhost:8000/docs")
    
    return True

def test_connection():
    """Test MongoDB Atlas connection."""
    print("\n🧪 Testing MongoDB Atlas Connection...")
    
    try:
        from app.core.config import settings
        from app.db.mongodb import MongoDB
        import asyncio
        
        async def test():
            await MongoDB.connect_to_mongo()
            print("✅ MongoDB Atlas connection successful!")
            await MongoDB.close_mongo_connection()
        
        asyncio.run(test())
        return True
        
    except Exception as e:
        print(f"❌ MongoDB Atlas connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your MongoDB Atlas credentials")
        print("2. Ensure your IP is whitelisted in MongoDB Atlas")
        print("3. Verify the cluster name is correct")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_connection()
    else:
        create_env_file() 