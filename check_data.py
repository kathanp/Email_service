#!/usr/bin/env python3
"""
Check what data is available for campaigns
"""
import asyncio
import sys
import os
sys.path.append('server')

from server.app.db.mongodb import MongoDB
from bson import ObjectId

async def check_campaign_data():
    """Check what files, templates, and senders are available"""
    try:
        # Connect to MongoDB
        await MongoDB.connect_to_mongo()
        db = MongoDB.get_database()
        
        print("🔍 Checking available data for campaigns...")
        
        # Check files
        files = await db.files.find().to_list(length=20)
        print(f"\n📁 Files found: {len(files)}")
        for file in files:
            print(f"  - ID: {file['_id']}")
            print(f"    Filename: {file.get('filename', 'N/A')}")
            print(f"    User ID: {file.get('user_id', 'N/A')}")
            print(f"    Processed: {file.get('processed', False)}")
            print(f"    Contacts Count: {file.get('contacts_count', 0)}")
            print()
        
        # Check templates
        templates = await db.templates.find().to_list(length=20)
        print(f"📝 Templates found: {len(templates)}")
        for template in templates:
            print(f"  - ID: {template['_id']}")
            print(f"    Name: {template.get('name', 'N/A')}")
            print(f"    Subject: {template.get('subject', 'N/A')}")
            print(f"    User ID: {template.get('user_id', 'N/A')}")
            print(f"    Active: {template.get('is_active', True)}")
            print()
        
        # Check senders
        senders = await db.senders.find().to_list(length=20)
        print(f"📧 Senders found: {len(senders)}")
        for sender in senders:
            print(f"  - ID: {sender['_id']}")
            print(f"    Email: {sender.get('email', 'N/A')}")
            print(f"    Display Name: {sender.get('display_name', 'N/A')}")
            print(f"    User ID: {sender.get('user_id', 'N/A')}")
            print(f"    Verification Status: {sender.get('verification_status', 'N/A')}")
            print(f"    Is Default: {sender.get('is_default', False)}")
            print()
        
        # Check users
        users = await db.users.find().to_list(length=5)
        print(f"👤 Users found: {len(users)}")
        for user in users:
            print(f"  - ID: {user['_id']}")
            print(f"    Email: {user.get('email', 'N/A')}")
            print(f"    Name: {user.get('full_name', 'N/A')}")
            print()
        
        print("✅ Data check completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await MongoDB.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(check_campaign_data()) 