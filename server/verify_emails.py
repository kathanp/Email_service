#!/usr/bin/env python3
"""
Verify Email Addresses in AWS SES
"""

import os
import boto3
from botocore.exceptions import ClientError

def verify_email(email_address):
    """Verify an email address in AWS SES."""
    print(f"📧 Verifying {email_address} in AWS SES...")
    
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
        
        # Send verification email
        response = ses_client.verify_email_identity(
            EmailAddress=email_address
        )
        
        print(f"✅ Verification email sent to {email_address}")
        print("📬 Please check your email and click the verification link")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'MessageRejected':
            print(f"❌ Email verification failed: {e}")
        else:
            print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Verify the sender email
    sender_email = "sale.rrimp@gmail.com"
    verify_email(sender_email) 