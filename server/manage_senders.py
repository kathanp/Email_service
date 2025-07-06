#!/usr/bin/env python3
"""
Manage Email Senders
"""

import os
import boto3
from botocore.exceptions import ClientError

def manage_senders():
    """Manage email senders in AWS SES."""
    print("📧 Managing Email Senders")
    print("=" * 40)
    
    # AWS credentials
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    region = "us-east-1"
    
    try:
        # Create SES client
        ses_client = boto3.client(
            'ses',
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        # List verified identities
        print("📋 Listing verified email addresses...")
        response = ses_client.list_identities(
            IdentityType='EmailAddress'
        )
        
        if response['Identities']:
            print("✅ Verified email addresses:")
            for email in response['Identities']:
                print(f"   📧 {email}")
        else:
            print("❌ No verified email addresses found")
            print("   You need to verify at least one email address")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    manage_senders() 