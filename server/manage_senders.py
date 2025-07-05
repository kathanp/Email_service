import os
#!/usr/bin/env python3
"""
Manage Multiple Verified Sender Emails in AWS SES
Option A2: Multiple Verified Senders
"""

import boto3
from botocore.exceptions import ClientError
import json

def manage_senders():
    """Manage multiple verified sender emails in AWS SES."""
    print("🔧 AWS SES Multiple Sender Management")
    print("=" * 50)
    
    # AWS credentials
    aws_access_key_id = "os.getenv("AWS_ACCESS_KEY_ID")"
    aws_secret_access_key = "os.getenv("AWS_SECRET_ACCESS_KEY")"
    region = "us-east-1"
    
    # List of sender emails to manage
    sender_emails = [
        "sale.rrimp@gmail.com",
        "patelkathan244@gmail.com",
        "redroofinn1101@gmail.com",
        "kathan.patel@example.com",  # Add more business emails as needed
        "support@yourbusiness.com"   # Add more business emails as needed
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
        print(f"📧 Managing {len(sender_emails)} sender emails\n")
        
        verified_senders = []
        pending_senders = []
        unverified_senders = []
        
        for email in sender_emails:
            print(f"📧 Processing: {email}")
            
            try:
                # Check verification status
                response = ses_client.get_identity_verification_attributes(
                    Identities=[email]
                )
                
                verification_status = response['VerificationAttributes'].get(email, {}).get('VerificationStatus', 'NotVerified')
                
                if verification_status == 'Success':
                    print(f"   ✅ VERIFIED - {email}")
                    verified_senders.append(email)
                elif verification_status == 'Pending':
                    print(f"   ⏳ PENDING - {email}")
                    print(f"      📬 Check email for verification link")
                    pending_senders.append(email)
                else:
                    print(f"   ❌ NOT VERIFIED - {email}")
                    print(f"      📤 Sending verification email...")
                    
                    try:
                        ses_client.verify_email_identity(EmailAddress=email)
                        print(f"      ✅ Verification email sent to {email}")
                        pending_senders.append(email)
                    except ClientError as e:
                        if e.response['Error']['Code'] == 'AlreadyExists':
                            print(f"      ⏳ Verification already in progress")
                            pending_senders.append(email)
                        else:
                            print(f"      ❌ Error: {e}")
                            unverified_senders.append(email)
                            
            except Exception as e:
                print(f"   ❌ Error checking {email}: {e}")
                unverified_senders.append(email)
            
            print()
        
        # Summary
        print("📊 VERIFICATION SUMMARY")
        print("=" * 30)
        print(f"✅ Verified: {len(verified_senders)}")
        print(f"⏳ Pending: {len(pending_senders)}")
        print(f"❌ Unverified: {len(unverified_senders)}")
        
        if verified_senders:
            print(f"\n✅ READY TO USE:")
            for email in verified_senders:
                print(f"   - {email}")
        
        if pending_senders:
            print(f"\n⏳ PENDING VERIFICATION:")
            for email in pending_senders:
                print(f"   - {email}")
            print("   📬 Check your emails and click verification links")
        
        if unverified_senders:
            print(f"\n❌ NEEDS ATTENTION:")
            for email in unverified_senders:
                print(f"   - {email}")
        
        # Save verified senders to a file for the application
        if verified_senders:
            with open('verified_senders.json', 'w') as f:
                json.dump(verified_senders, f, indent=2)
            print(f"\n💾 Verified senders saved to 'verified_senders.json'")
        
        print(f"\n🎯 NEXT STEPS:")
        print("1. Check emails for verification links")
        print("2. Click verification links")
        print("3. Wait 2-3 minutes for AWS to process")
        print("4. Run this script again to check status")
        print("5. Once verified, users can choose from these sender emails")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    manage_senders() 