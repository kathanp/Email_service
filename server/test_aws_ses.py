import os
#!/usr/bin/env python3
"""
Test AWS SES Configuration
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def test_aws_ses():
    """Test AWS SES configuration."""
    print("🧪 Testing AWS SES Configuration")
    print("=" * 40)
    
    # AWS credentials
    aws_access_key_id = "os.getenv("AWS_ACCESS_KEY_ID")"
    aws_secret_access_key = "os.getenv("AWS_SECRET_ACCESS_KEY")"
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
        
        print("✅ AWS SES client created successfully")
        
        # Test connection by getting send quota
        print("\n📊 Getting send quota...")
        quota_response = ses_client.get_send_quota()
        print(f"✅ Send quota retrieved successfully!")
        print(f"   Max 24 hour send: {quota_response['Max24HourSend']} emails")
        print(f"   Sent last 24 hours: {quota_response['SentLast24Hours']} emails")
        print(f"   Max send rate: {quota_response['MaxSendRate']} emails/second")
        
        # Check email verification status
        print(f"\n📧 Checking verification status for {sender_email}...")
        verification_response = ses_client.get_identity_verification_attributes(
            Identities=[sender_email]
        )
        
        if sender_email in verification_response['VerificationAttributes']:
            status = verification_response['VerificationAttributes'][sender_email]['VerificationStatus']
            if status == 'Success':
                print(f"✅ {sender_email} is verified and ready to send emails!")
            else:
                print(f"⚠️  {sender_email} is not verified. Status: {status}")
                print("   You need to verify this email in AWS SES console")
                print("   Go to: https://console.aws.amazon.com/ses/")
        else:
            print(f"❌ {sender_email} not found in AWS SES")
            print("   You need to verify this email in AWS SES console")
            print("   Go to: https://console.aws.amazon.com/ses/")
        
        # Test sending a verification email if not verified
        if sender_email not in verification_response['VerificationAttributes'] or \
           verification_response['VerificationAttributes'][sender_email]['VerificationStatus'] != 'Success':
            print(f"\n📧 Sending verification email to {sender_email}...")
            try:
                verify_response = ses_client.verify_email_identity(EmailAddress=sender_email)
                print(f"✅ Verification email sent to {sender_email}")
                print("   Check your email and click the verification link")
            except ClientError as e:
                print(f"❌ Error sending verification email: {e}")
        
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found or invalid")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ AWS SES error: {error_code} - {error_message}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_aws_ses() 