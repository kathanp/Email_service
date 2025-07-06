import asyncio
import sys
import os
sys.path.append('server')

from app.db.mongodb import MongoDB
from bson import ObjectId

async def check_campaigns():
    try:
        await MongoDB.connect()
        campaigns_collection = MongoDB.get_collection('campaigns')
        
        # Get all campaigns
        campaigns = await campaigns_collection.find({}).to_list(length=None)
        print(f'Total campaigns in database: {len(campaigns)}')
        
        if campaigns:
            print('\nCampaign details:')
            for campaign in campaigns:
                print(f'- Name: {campaign.get("name", "N/A")}')
                print(f'  User ID: {campaign.get("user_id", "N/A")}')
                print(f'  Status: {campaign.get("status", "N/A")}')
                print(f'  Total emails: {campaign.get("total_emails", 0)}')
                print(f'  Successful: {campaign.get("successful", 0)}')
                print(f'  Failed: {campaign.get("failed", 0)}')
                print(f'  Created: {campaign.get("created_at", "N/A")}')
                print('---')
        else:
            print('No campaigns found in database.')
            print('This explains why the email count is 0.')
            print('The count will increment when you create and send campaigns.')
        
        await MongoDB.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_campaigns()) 