#!/usr/bin/env python3
"""
Test AWS SES Email Sending
"""

import os
import boto3
from botocore.exceptions import ClientError

def test_ses_email():
    """Test sending an email via AWS SES."""
    print("🧪 Testing AWS SES Email Sending")
    print("=" * 40)
    
    # AWS credentials
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    region = "us-east-1"
    sender_email = "sale.rrimp@gmail.com"
    recipient_email = "patelkathan244@gmail.com"
    
    try:
        # Create SES client
        ses_client = boto3.client(
            'ses',
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        # Test email content
        subject = "Test Email from AWS SES"
        body = """
        This is a test email sent from AWS SES.
        
        If you receive this email, your AWS SES setup is working correctly!
        
        Best regards,
        Email Bot Team
        """
        
        # Send email
        response = ses_client.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [recipient_email]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Text': {
                        'Data': body
                    }
                }
            }
        )
        
        print(f"✅ Test email sent successfully!")
        print(f"📧 From: {sender_email}")
        print(f"📧 To: {recipient_email}")
        print(f"📧 Subject: {subject}")
        print(f"📧 Message ID: {response['MessageId']}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'MessageRejected':
            print(f"❌ Email rejected: {e}")
        elif error_code == 'MailFromDomainNotVerified':
            print(f"❌ Sender domain not verified: {e}")
        else:
            print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_ses_email() 