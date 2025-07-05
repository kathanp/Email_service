#!/usr/bin/env python3
"""
AWS SES Setup Script for Email Bot
This script helps you configure AWS SES for mass email sending.
"""

import os
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def create_aws_credentials():
    """Create AWS credentials file for centralized SES management."""
    print("🔧 AWS SES Setup for Email Bot (Centralized)")
    print("=" * 50)
    
    print("\n📋 This setup configures AWS SES for centralized email sending.")
    print("All users will share the same AWS SES account managed by the application.")
    
    print("\n🌐 AWS SES Setup Steps:")
    print("1. Go to https://aws.amazon.com/ses/")
    print("2. Sign up for AWS (if you don't have an account)")
    print("3. Navigate to Amazon SES in your preferred region")
    print("4. Verify your sender email address (required for sending)")
    print("5. Create an IAM user with SES permissions")
    print("6. Get your Access Key ID and Secret Access Key")
    
    print("\n🔑 Please provide your AWS credentials:")
    
    access_key_id = input("AWS Access Key ID: ").strip()
    secret_access_key = input("AWS Secret Access Key: ").strip()
    region = input("AWS Region (e.g., us-east-1): ").strip() or "us-east-1"
    default_sender_email = input("Default Sender Email: ").strip()
    
    # Test AWS credentials
    print("\n🧪 Testing AWS credentials...")
    
    try:
        ses_client = boto3.client(
            'ses',
            region_name=region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key
        )
        
        # Test connection by getting send quota
        response = ses_client.get_send_quota()
        print("✅ AWS credentials are valid!")
        print(f"📊 Send quota: {response['Max24HourSend']} emails per day")
        print(f"📈 Send rate: {response['MaxSendRate']} emails per second")
        
    except NoCredentialsError:
        print("❌ AWS credentials not found or invalid")
        return False
    except ClientError as e:
        print(f"❌ AWS SES error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Update .env file
    env_file_path = '.env'
    env_content = ""
    
    # Read existing .env file if it exists
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            env_content = f.read()
    
    # Add or update AWS configuration
    aws_config = f"""
# AWS Configuration
AWS_ACCESS_KEY_ID={access_key_id}
AWS_SECRET_ACCESS_KEY={secret_access_key}
AWS_REGION={region}
DEFAULT_SENDER_EMAIL={default_sender_email}
"""
    
    # Remove existing AWS config if present
    lines = env_content.split('\n')
    filtered_lines = []
    skip_next = False
    
    for line in lines:
        if line.startswith('# AWS Configuration'):
            skip_next = True
            continue
        if skip_next and (line.startswith('AWS_') or line.startswith('DEFAULT_SENDER_EMAIL=')):
            continue
        if skip_next and line.strip() == '':
            skip_next = False
            continue
        if not skip_next:
            filtered_lines.append(line)
    
    # Add new AWS config
    env_content = '\n'.join(filtered_lines) + aws_config
    
    # Write updated .env file
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        print(f"\n✅ AWS configuration saved to {env_file_path}")
        
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        return False
    
    print("\n📝 Next Steps:")
    print("1. Verify your sender email in AWS SES console")
    print("2. If in sandbox mode, verify recipient emails too")
    print("3. Request production access if needed for mass sending")
    print("4. Install dependencies: pip install -r requirements.txt")
    print("5. Start the server: python -m uvicorn app.main:app --reload")
    
    print("\n🔗 Useful Links:")
    print("- AWS SES Console: https://console.aws.amazon.com/ses/")
    print("- SES Documentation: https://docs.aws.amazon.com/ses/")
    print("- Pricing: https://aws.amazon.com/ses/pricing/")
    
    return True

def verify_email_setup():
    """Verify email setup with AWS SES."""
    print("\n📧 Email Verification Setup")
    print("=" * 30)
    
    try:
        from app.core.config import settings
        
        ses_client = boto3.client(
            'ses',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        # Check if sender email is verified
        try:
            response = ses_client.get_identity_verification_attributes(
                Identities=[settings.DEFAULT_SENDER_EMAIL]
            )
            
            if settings.DEFAULT_SENDER_EMAIL in response['VerificationAttributes']:
                status = response['VerificationAttributes'][settings.DEFAULT_SENDER_EMAIL]['VerificationStatus']
                if status == 'Success':
                    print(f"✅ Sender email {settings.DEFAULT_SENDER_EMAIL} is verified")
                else:
                    print(f"⚠️  Sender email {settings.DEFAULT_SENDER_EMAIL} is not verified")
                    print("   Please check your email and click the verification link")
            else:
                print(f"❌ Sender email {settings.DEFAULT_SENDER_EMAIL} not found")
                
        except ClientError as e:
            print(f"❌ Error checking email verification: {e}")
            
    except ImportError:
        print("❌ Could not import settings. Make sure .env file is configured.")
    except Exception as e:
        print(f"❌ Error: {e}")

def manage_sender_emails():
    """Manage multiple sender emails for different companies."""
    print("\n📧 Sender Email Management")
    print("=" * 30)
    
    try:
        from app.core.config import settings
        
        ses_client = boto3.client(
            'ses',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        while True:
            print("\nOptions:")
            print("1. Add new sender email")
            print("2. Verify domain (recommended for companies)")
            print("3. List verified identities")
            print("4. Check verification status")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                email = input("Enter email address to verify: ").strip()
                try:
                    response = ses_client.verify_email_identity(EmailAddress=email)
                    print(f"✅ Verification email sent to {email}")
                    print("   Check the email and click the verification link")
                except ClientError as e:
                    print(f"❌ Error: {e}")
                    
            elif choice == "2":
                domain = input("Enter domain to verify (e.g., company.com): ").strip()
                try:
                    response = ses_client.verify_domain_identity(Domain=domain)
                    print(f"✅ Domain verification initiated for {domain}")
                    print("   Add the following TXT record to your DNS:")
                    print(f"   Name: _amazonses.{domain}")
                    print(f"   Value: {response['VerificationToken']}")
                except ClientError as e:
                    print(f"❌ Error: {e}")
                    
            elif choice == "3":
                try:
                    response = ses_client.list_identities(IdentityType='EmailAddress')
                    print("\n📧 Verified Email Addresses:")
                    for email in response['Identities']:
                        status_response = ses_client.get_identity_verification_attributes(Identities=[email])
                        status = status_response['VerificationAttributes'][email]['VerificationStatus']
                        print(f"   {email} - {status}")
                        
                    domain_response = ses_client.list_identities(IdentityType='Domain')
                    print("\n🌐 Verified Domains:")
                    for domain in domain_response['Identities']:
                        status_response = ses_client.get_identity_verification_attributes(Identities=[domain])
                        status = status_response['VerificationAttributes'][domain]['VerificationStatus']
                        print(f"   {domain} - {status}")
                        
                except ClientError as e:
                    print(f"❌ Error: {e}")
                    
            elif choice == "4":
                identity = input("Enter email or domain to check: ").strip()
                try:
                    response = ses_client.get_identity_verification_attributes(Identities=[identity])
                    if identity in response['VerificationAttributes']:
                        status = response['VerificationAttributes'][identity]['VerificationStatus']
                        print(f"   {identity} - {status}")
                    else:
                        print(f"   {identity} - Not found")
                except ClientError as e:
                    print(f"❌ Error: {e}")
                    
            elif choice == "5":
                break
            else:
                print("Invalid option. Please try again.")
                
    except ImportError:
        print("❌ Could not import settings. Make sure .env file is configured.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 AWS SES Setup for Email Bot")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "verify":
            verify_email_setup()
        elif sys.argv[1] == "manage":
            manage_sender_emails()
        else:
            print("Usage: python setup_aws_ses.py [verify|manage]")
    else:
        create_aws_credentials() 