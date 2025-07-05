#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from email_service import EmailMicroservice

def test_email_campaign():
    """Test the email campaign with the dummy Excel file."""
    
    print("🧪 Testing Email Campaign with Excel File...")
    print("=" * 60)
    
    # Initialize the email service
    try:
        service = EmailMicroservice()
        print("✅ Email service initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing email service: {str(e)}")
        return
    
    # Check if the Excel file exists
    excel_file = Path("input/Contacts.xlsx")
    if not excel_file.exists():
        print(f"❌ Excel file not found at: {excel_file}")
        return
    
    print(f"📁 Found Excel file: {excel_file}")
    
    # Process the contacts and send emails
    try:
        print("\n🚀 Starting email campaign...")
        successful, failed = service.process_contacts(excel_file)
        
        print("\n📊 Campaign Results:")
        print("=" * 60)
        print(f"✅ Successfully sent: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📧 Total processed: {successful + failed}")
        print("=" * 60)
        
        if successful > 0:
            print("🎉 Email campaign completed successfully!")
            print("📧 Check your email inbox for the test emails.")
        else:
            print("⚠️  No emails were sent successfully.")
            
    except Exception as e:
        print(f"❌ Error during email campaign: {str(e)}")

if __name__ == "__main__":
    test_email_campaign() 