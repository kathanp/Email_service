#!/usr/bin/env python3
"""
Check Email Verification Status
"""

import os
import boto3
from botocore.exceptions import ClientError

def check_verification():
    """Check if the email is verified."""
    print("🔍 Checking Email Verification Status")
    print("=" * 40)
    
    # AWS credentials
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    region = "us-east-1"
    sender_email = "sale.rrimp@gmail.com"
    
    try:
        # Create SES client
        ses_client = boto3.client(
            'ses',
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        # Check verification status
        print(f"📧 Checking verification status for {sender_email}...")
        verification_response = ses_client.get_identity_verification_attributes(
            Identities=[sender_email]
        )
        
        if sender_email in verification_response['VerificationAttributes']:
            status = verification_response['VerificationAttributes'][sender_email]['VerificationStatus']
            if status == 'Success':
                print(f"✅ {sender_email} is verified and ready to send emails!")
                print("🎉 You can now send email campaigns successfully!")
                return True
            else:
                print(f"⚠️  {sender_email} is not verified yet. Status: {status}")
                print("   Please check your email and click the verification link")
                return False
        else:
            print(f"❌ {sender_email} not found in AWS SES")
            print("   Please check your email and click the verification link")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_verification() 