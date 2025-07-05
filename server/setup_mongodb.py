#!/usr/bin/env python3
"""
MongoDB Atlas Setup Script for Email Bot

This script helps you set up MongoDB Atlas for your Email Bot application.
"""

import os
import sys
from pathlib import Path

def print_header():
    """Print setup header."""
    print("=" * 60)
    print("🗄️  MongoDB Atlas Setup for Email Bot")
    print("=" * 60)
    print()

def print_steps():
    """Print setup steps."""
    print("📋 MongoDB Atlas Setup Steps:")
    print("1. Go to MongoDB Atlas: https://cloud.mongodb.com/")
    print("2. Create a free account or sign in")
    print("3. Create a new cluster (free tier is fine)")
    print("4. Create a database user with read/write permissions")
    print("5. Get your connection string")
    print("6. Add your IP address to the IP whitelist")
    print()

def update_env_file():
    """Update .env file with MongoDB configuration."""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found. Please run setup_google_oauth.py first.")
        return False
    
    print("📝 Current MongoDB configuration:")
    with open(env_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')
        for line in lines:
            if line.startswith('MONGODB_URL='):
                print(f"   {line}")
                break
    
    print("\n🔧 Please provide your MongoDB Atlas connection string:")
    print("Format: mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority")
    
    connection_string = input("MongoDB Connection String: ").strip()
    
    if not connection_string:
        print("❌ Connection string is required.")
        return False
    
    # Update the .env file
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Replace the MongoDB URL
    lines = content.split('\n')
    updated_lines = []
    for line in lines:
        if line.startswith('MONGODB_URL='):
            updated_lines.append(f'MONGODB_URL={connection_string}')
        else:
            updated_lines.append(line)
    
    with open(env_path, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print("✅ MongoDB connection string updated successfully!")
    return True

def test_connection():
    """Test MongoDB connection."""
    print("\n🧪 Testing MongoDB connection...")
    
    try:
        from app.core.config import settings
        from app.db.mongodb import MongoDB
        import asyncio
        
        async def test():
            try:
                await MongoDB.connect_to_mongo()
                print("✅ MongoDB connection successful!")
                await MongoDB.close_mongo_connection()
                return True
            except Exception as e:
                print(f"❌ MongoDB connection failed: {e}")
                return False
        
        return asyncio.run(test())
        
    except ImportError:
        print("❌ Could not import required modules. Make sure you're in the server directory.")
        return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def main():
    """Main setup function."""
    print_header()
    print_steps()
    
    # Change to server directory
    server_dir = Path(__file__).parent
    os.chdir(server_dir)
    
    if update_env_file():
        if test_connection():
            print("\n🎉 MongoDB setup complete!")
            print("🚀 You can now start the backend server.")
        else:
            print("\n⚠️  MongoDB connection failed. Please check your connection string and try again.")
    else:
        print("\n❌ Setup failed. Please try again.")

if __name__ == "__main__":
    main() 