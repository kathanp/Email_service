import os
#!/usr/bin/env python3
"""
Verify Email Addresses in AWS SES
"""

import boto3
import os
from botocore.exceptions import ClientError

def verify_emails():
    """Verify email addresses in AWS SES."""
    print("🔧 AWS SES Email Verification")
    print("=" * 40)
    
    # AWS credentials from environment variables
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION", "us-east-1")
    
    if not aws_access_key_id or not aws_secret_access_key:
        print("❌ AWS credentials not found in environment variables")
        print("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your .env file")
        return
    
    # Email addresses to verify
    emails_to_verify = [
        "sale.rrimp@gmail.com",
        "patelkathan244@gmail.com"
    ]
    
    try:
        # Create SES client
        ses_client = boto3.client(
            'ses',
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        print("✅ AWS SES client created successfully")
        
        for email in emails_to_verify:
            print(f"\n📧 Processing: {email}")
            
            try:
                # Check if email is already verified
                response = ses_client.get_identity_verification_attributes(
                    Identities=[email]
                )
                
                verification_status = response['VerificationAttributes'].get(email, {}).get('VerificationStatus', 'NotVerified')
                
                if verification_status == 'Success':
                    print(f"   ✅ {email} is already verified")
                elif verification_status == 'Pending':
                    print(f"   ⏳ {email} is pending verification")
                    print(f"   📬 Check your email for verification link")
                else:
                    # Send verification email
                    print(f"   📤 Sending verification email to {email}")
                    ses_client.verify_email_identity(EmailAddress=email)
                    print(f"   ✅ Verification email sent to {email}")
                    print(f"   📬 Please check your email and click the verification link")
                    
            except ClientError as e:
                if e.response['Error']['Code'] == 'AlreadyExists':
                    print(f"   ⏳ {email} verification already in progress")
                else:
                    print(f"   ❌ Error with {email}: {e}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_emails() 