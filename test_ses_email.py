#!/usr/bin/env python3
"""
Simple AWS SES Email Test Script
This script tests the AWS SES integration to verify email sending capability.
"""

import asyncio
import sys
import os
from datetime import datetime
import logging

# Add the server directory to Python path
sys.path.append('server')

from server.app.services.ses_manager import SESManager
from server.app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ses_email():
    """Test AWS SES email sending functionality."""
    
    print("🔍 Testing AWS SES Email Functionality")
    print("=" * 50)
    
    # Initialize SES Manager
    try:
        ses_manager = SESManager()
        print("✅ SES Manager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize SES Manager: {e}")
        return False
    
    # Check SES health
    print("\n📋 Checking SES Health...")
    try:
        health = await ses_manager.check_health()
        print(f"Health Status: {health}")
        
        if health['status'] != 'healthy':
            print("❌ SES is not healthy!")
            return False
        else:
            print("✅ SES is healthy")
    except Exception as e:
        print(f"❌ Failed to check SES health: {e}")
        return False
    
    # Get SES quota
    print("\n📊 Checking SES Quota...")
    try:
        quota = await ses_manager.get_send_quota()
        if quota['success']:
            print(f"✅ SES Quota: {quota['quota']}")
        else:
            print(f"❌ Failed to get quota: {quota['error']}")
    except Exception as e:
        print(f"❌ Error getting quota: {e}")
    
    # Test email sending
    print("\n📧 Testing Email Send...")
    
    # You can modify these values for testing
    test_email_data = {
        'to_email': 'test@example.com',  # Replace with your test email
        'sender_email': 'noreply@yourdomain.com',  # Replace with your verified sender
        'subject': f'Test Email - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        'body': 'This is a test email to verify AWS SES integration.',
        'html_body': '''
        <html>
        <body>
            <h2>AWS SES Test Email</h2>
            <p>This is a test email to verify AWS SES integration.</p>
            <p>Sent at: {}</p>
            <p>If you received this email, AWS SES is working correctly!</p>
        </body>
        </html>
        '''.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        'user_id': 'test_user_123'
    }
    
    print(f"Sending test email from: {test_email_data['sender_email']}")
    print(f"Sending test email to: {test_email_data['to_email']}")
    
    try:
        result = await ses_manager.send_email(
            to_email=test_email_data['to_email'],
            subject=test_email_data['subject'],
            body=test_email_data['body'],
            sender_email=test_email_data['sender_email'],
            html_body=test_email_data['html_body'],
            user_id=test_email_data['user_id']
        )
        
        print(f"\n📬 Email Send Result:")
        print(f"Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"✅ Email sent successfully!")
            print(f"Message ID: {result.get('message_id', 'N/A')}")
            print(f"Response: {result.get('response', 'N/A')}")
        else:
            print(f"❌ Email send failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print(f"Details: {result.get('details', 'No details')}")
            
    except Exception as e:
        print(f"❌ Exception during email send: {e}")
        return False
    
    # Test bulk email sending (with small batch)
    print("\n📬 Testing Bulk Email Send...")
    
    test_emails = [
        'test1@example.com',  # Replace with your test emails
        'test2@example.com',
    ]
    
    try:
        bulk_results = await ses_manager.send_bulk_emails(
            emails=test_emails,
            sender_email=test_email_data['sender_email'],
            user_id=test_email_data['user_id']
        )
        
        print(f"\n📮 Bulk Email Results:")
        print(f"Total sent: {bulk_results.get('total_sent', 0)}")
        print(f"Total failed: {bulk_results.get('total_failed', 0)}")
        print(f"Success rate: {bulk_results.get('success_rate', 0)}%")
        
        if bulk_results.get('failed_emails'):
            print(f"Failed emails: {bulk_results['failed_emails']}")
            
    except Exception as e:
        print(f"❌ Exception during bulk email send: {e}")
    
    print("\n" + "=" * 50)
    print("✅ SES Test Complete!")
    
    return True

async def main():
    """Main function to run the SES test."""
    
    print("AWS SES Email Test Script")
    print("Make sure your AWS credentials are properly configured!")
    print("Update the test email addresses in the script before running.")
    print()
    
    try:
        await test_ses_email()
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 