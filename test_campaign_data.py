#!/usr/bin/env python3
"""
Test script to check campaign data availability
"""
import asyncio
import sys
import os
sys.path.append('server')

from server.app.db.mongodb import MongoDB
from bson import ObjectId

async def test_campaign_data():
    """Test what data is available for campaigns"""
    try:
        # Connect to MongoDB
        await MongoDB.connect()
        db = MongoDB.get_database()
        
        print("🔍 Checking campaign data availability...")
        
        # Check users
        users = await db.users.find().to_list(length=10)
        print(f"📊 Users found: {len(users)}")
        for user in users:
            print(f"  - User ID: {user['_id']}, Email: {user.get('email', 'N/A')}")
        
        # Check templates
        templates = await db.templates.find().to_list(length=10)
        print(f"📝 Templates found: {len(templates)}")
        for template in templates:
            print(f"  - Template: {template.get('name', 'N/A')} (User: {template.get('user_id', 'N/A')})")
        
        # Check files
        files = await db.files.find().to_list(length=10)
        print(f"📁 Files found: {len(files)}")
        for file in files:
            print(f"  - File: {file.get('filename', 'N/A')} (User: {file.get('user_id', 'N/A')}, Processed: {file.get('processed', False)})")
        
        # Check senders
        senders = await db.senders.find().to_list(length=10)
        print(f"📧 Senders found: {len(senders)}")
        for sender in senders:
            print(f"  - Sender: {sender.get('email', 'N/A')} (User: {sender.get('user_id', 'N/A')}, Status: {sender.get('verification_status', 'N/A')})")
        
        # Check campaigns
        campaigns = await db.campaigns.find().to_list(length=10)
        print(f"🚀 Campaigns found: {len(campaigns)}")
        for campaign in campaigns:
            print(f"  - Campaign: {campaign.get('name', 'N/A')} (User: {campaign.get('user_id', 'N/A')}, Status: {campaign.get('status', 'N/A')})")
        
        print("\n✅ Database check completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Close MongoDB connection
        MongoDB.close_connection()

if __name__ == "__main__":
    asyncio.run(test_campaign_data()) 