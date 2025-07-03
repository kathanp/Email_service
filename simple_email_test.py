#!/usr/bin/env python3

import smtplib
import pandas as pd
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

def send_email(recipient_email, subject, body):
    """Send email to a recipient."""
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = "sale.rrimp@gmail.com"
    password = "mnuiachbwzesyzwv"
    
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(smtp_server, port, timeout=30) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
        
        print(f"✅ Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {recipient_email}: {str(e)}")
        return False

def create_email_content(contact_info):
    """Create email content for the contact."""
    subject = f"Exclusive Corporate Rates - Red Roof Inn Moss Point for {contact_info['company_name']}"
    
    body = f"""Dear Sir/Madam,

I trust this letter finds you well. I am writing to introduce the exclusive corporate rates available at Red Roof Inn, Moss Point, designed specifically for {contact_info['company_name']}'s contractors and workforce.

We understand that business travelers have unique requirements, and we are committed to providing exceptional accommodations at competitive rates. Our partnership with CLC Lodging enables us to offer particularly attractive pricing for both short-term and extended stays.

Our Corporate Rate Structure:
Red Roof Inn, Moss Point
- Weekly Rates: $370 (Single Bed) / $420 (Double Bed) including tax
- Monthly Rates: $50 (Single Bed) / $57 (Double Bed) per night including tax, for stays of one month or longer

Distinguished Amenities:
- Complimentary hot breakfast featuring scrambled eggs and sausage gravy
- Newly renovated rooms with modern furniture
- Complimentary Tesla and EV charging stations
- High-speed Wi-Fi
- 24/7 coffee service in the lobby
- Strategic location in Moss Point
- Business-friendly facilities
- Corporate rewards program

For companies with specific room requirements and employee headcounts, we are happy to discuss custom rate negotiations to better accommodate your needs. Our flexible pricing structure allows us to provide even more competitive rates for larger groups or longer-term commitments.

As a CLC Lodging partner, we are positioned to provide superior accommodations at highly competitive rates. We welcome the opportunity to discuss how we can tailor our services to meet your specific requirements.

For reservations or inquiries, please contact:
Kathan Patel
General Manager
Tel: +1(228) 460-0615
Email: Redroofinn1101@gmail.com or Sale.rrimp@gmail.com

We look forward to establishing a lasting partnership with {contact_info['company_name']} and serving as your preferred accommodation provider.

Best regards,
Kathan Patel
General Manager
Red Roof Inn, Moss Point"""
    
    return subject, body

def test_email_campaign():
    """Test the email campaign with the dummy Excel file."""
    
    print("🧪 Testing Email Campaign with Excel File...")
    print("=" * 60)
    
    # Check if the Excel file exists
    excel_file = Path("input/Contacts.xlsx")
    if not excel_file.exists():
        print(f"❌ Excel file not found at: {excel_file}")
        return
    
    print(f"📁 Found Excel file: {excel_file}")
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file)
        print(f"📊 Found {len(df)} contacts in the file")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Convert to list of dictionaries
        contacts = df.to_dict('records')
        
        successful_emails = 0
        failed_emails = 0
        
        print("\n🚀 Starting email campaign...")
        print("=" * 60)
        
        for i, contact in enumerate(contacts, 1):
            try:
                # Create email content
                subject, body = create_email_content(contact)
                
                print(f"\n📧 Processing email {i}/{len(contacts)}:")
                print(f"   To: {contact.get('email', 'No email')}")
                print(f"   Company: {contact.get('company_name', 'No company')}")
                print(f"   Contact: {contact.get('contact_name', 'No name')}")
                
                # Send email
                success = send_email(contact['email'], subject, body)
                
                if success:
                    successful_emails += 1
                else:
                    failed_emails += 1
                
                # Add delay between emails
                if i < len(contacts):
                    print("   ⏳ Waiting 2 seconds before next email...")
                    time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Error processing contact {i}: {str(e)}")
                failed_emails += 1
        
        print("\n📊 Campaign Results:")
        print("=" * 60)
        print(f"✅ Successfully sent: {successful_emails}")
        print(f"❌ Failed: {failed_emails}")
        print(f"📧 Total processed: {len(contacts)}")
        print("=" * 60)
        
        if successful_emails > 0:
            print("🎉 Email campaign completed successfully!")
            print("📧 Check your email inbox for the test emails.")
        else:
            print("⚠️  No emails were sent successfully.")
            
    except Exception as e:
        print(f"❌ Error during email campaign: {str(e)}")

if __name__ == "__main__":
    test_email_campaign() 