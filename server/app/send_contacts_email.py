#!/usr/bin/env python3
"""
Send emails to contacts from input/Contacts.xlsx
"""

import pandas as pd
import asyncio
import sys
import os
import time
import logging
from datetime import datetime
from pathlib import Path

# Add the server directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from app.services.gmail_oauth_service import GmailOAuthService
from app.core.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'email_campaign_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ContactEmailSender:
    def __init__(self):
        self.contacts_file = "../../input/Contacts.xlsx"
        self.gmail_service = GmailOAuthService()
        
    def load_contacts(self):
        """Load contacts from Excel file."""
        try:
            logger.info(f"Loading contacts from {self.contacts_file}")
            df = pd.read_excel(self.contacts_file)
            
            # Validate required columns
            required_columns = ['email', 'company_name', 'contact_name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Clean and validate data
            contacts = []
            for index, row in df.iterrows():
                email = str(row['email']).strip()
                company_name = str(row['company_name']).strip()
                contact_name = str(row['contact_name']).strip()
                
                # Basic email validation
                if '@' in email and '.' in email:
                    contacts.append({
                        'email': email,
                        'company_name': company_name,
                        'contact_name': contact_name,
                        'row_index': index + 1
                    })
                else:
                    logger.warning(f"Invalid email format in row {index + 1}: {email}")
            
            logger.info(f"Loaded {len(contacts)} valid contacts from {len(df)} total rows")
            return contacts
            
        except Exception as e:
            logger.error(f"Error loading contacts: {e}")
            raise
    
    def create_email_content(self, contact):
        """Create personalized email content for a contact."""
        subject = f"Exclusive Corporate Partnership Opportunity - {contact['company_name']}"
        
        body = f"""Dear {contact['contact_name']},

I trust this letter finds you well. I am writing to introduce the exclusive corporate rates available at Red Roof Inn, Moss Point, designed specifically for {contact['company_name']}'s contractors and workforce.

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

We look forward to establishing a lasting partnership with {contact['company_name']} and serving as your preferred accommodation provider.

Best regards,
Kathan Patel
General Manager
Red Roof Inn, Moss Point

---
This email was sent from your Email Bot application.
        """
        
        html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
        .header {{ background: #d32f2f; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .rates {{ background: #f5f5f5; padding: 15px; margin: 15px 0; border-left: 4px solid #d32f2f; }}
        .amenities {{ background: #e8f5e8; padding: 15px; margin: 15px 0; border-left: 4px solid #4caf50; }}
        .contact {{ background: #fff3e0; padding: 15px; margin: 15px 0; border-left: 4px solid #ff9800; }}
        .footer {{ background: #f8f9fa; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Red Roof Inn, Moss Point</h1>
        <h2>Exclusive Corporate Partnership Opportunity</h2>
    </div>
    
    <div class="content">
        <p>Dear {contact['contact_name']},</p>
        
        <p>I trust this letter finds you well. I am writing to introduce the exclusive corporate rates available at Red Roof Inn, Moss Point, designed specifically for <strong>{contact['company_name']}</strong>'s contractors and workforce.</p>
        
        <p>We understand that business travelers have unique requirements, and we are committed to providing exceptional accommodations at competitive rates. Our partnership with CLC Lodging enables us to offer particularly attractive pricing for both short-term and extended stays.</p>
        
        <div class="rates">
            <h3>Our Corporate Rate Structure:</h3>
            <p><strong>Red Roof Inn, Moss Point</strong></p>
            <ul>
                <li><strong>Weekly Rates:</strong> $370 (Single Bed) / $420 (Double Bed) including tax</li>
                <li><strong>Monthly Rates:</strong> $50 (Single Bed) / $57 (Double Bed) per night including tax, for stays of one month or longer</li>
            </ul>
        </div>
        
        <div class="amenities">
            <h3>Distinguished Amenities:</h3>
            <ul>
                <li>Complimentary hot breakfast featuring scrambled eggs and sausage gravy</li>
                <li>Newly renovated rooms with modern furniture</li>
                <li>Complimentary Tesla and EV charging stations</li>
                <li>High-speed Wi-Fi</li>
                <li>24/7 coffee service in the lobby</li>
                <li>Strategic location in Moss Point</li>
                <li>Business-friendly facilities</li>
                <li>Corporate rewards program</li>
            </ul>
        </div>
        
        <p>For companies with specific room requirements and employee headcounts, we are happy to discuss custom rate negotiations to better accommodate your needs. Our flexible pricing structure allows us to provide even more competitive rates for larger groups or longer-term commitments.</p>
        
        <p>As a CLC Lodging partner, we are positioned to provide superior accommodations at highly competitive rates. We welcome the opportunity to discuss how we can tailor our services to meet your specific requirements.</p>
        
        <div class="contact">
            <h3>For reservations or inquiries, please contact:</h3>
            <p><strong>Kathan Patel</strong><br>
            General Manager<br>
            Tel: +1(228) 460-0615<br>
            Email: <a href="mailto:Redroofinn1101@gmail.com">Redroofinn1101@gmail.com</a> or <a href="mailto:Sale.rrimp@gmail.com">Sale.rrimp@gmail.com</a></p>
        </div>
        
        <p>We look forward to establishing a lasting partnership with <strong>{contact['company_name']}</strong> and serving as your preferred accommodation provider.</p>
        
        <p>Best regards,<br>
        <strong>Kathan Patel</strong><br>
        General Manager<br>
        Red Roof Inn, Moss Point</p>
    </div>
    
    <div class="footer">
        <p>This email was sent from your Email Bot application.</p>
    </div>
</body>
</html>
        """
        
        return subject, body, html_body
    
    async def send_email_via_smtp(self, contact, subject, body):
        """Send email via Gmail SMTP."""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = settings.SENDER_EMAIL
            msg['To'] = contact['email']
            msg['Subject'] = subject
            
            # Add text and HTML parts
            text_part = MIMEText(body, 'plain')
            html_part = MIMEText(self.create_email_content(contact)[2], 'html')
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send via SMTP
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=30) as server:
                server.starttls()
                server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"SMTP error for {contact['email']}: {e}")
            return False
    
    async def send_emails_to_contacts(self, contacts, use_smtp=True):
        """Send emails to all contacts."""
        logger.info(f"Starting email campaign to {len(contacts)} contacts")
        logger.info(f"Using {'SMTP' if use_smtp else 'Gmail OAuth'} for sending")
        
        successful = 0
        failed = 0
        start_time = datetime.now()
        
        for i, contact in enumerate(contacts, 1):
            try:
                logger.info(f"Processing contact {i}/{len(contacts)}: {contact['email']} ({contact['company_name']})")
                
                # Create email content
                subject, body, html_body = self.create_email_content(contact)
                
                # Send email
                if use_smtp:
                    success = await self.send_email_via_smtp(contact, subject, body)
                else:
                    # Note: Gmail OAuth would require user authentication first
                    logger.warning("Gmail OAuth requires user authentication. Using SMTP instead.")
                    success = await self.send_email_via_smtp(contact, subject, body)
                
                if success:
                    successful += 1
                    logger.info(f"✅ Email sent successfully to {contact['email']}")
                else:
                    failed += 1
                    logger.error(f"❌ Failed to send email to {contact['email']}")
                
                # Rate limiting - wait 2 seconds between emails
                if i < len(contacts):
                    logger.info("⏳ Waiting 2 seconds before next email...")
                    await asyncio.sleep(2)
                
            except Exception as e:
                failed += 1
                logger.error(f"❌ Error processing contact {i}: {e}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Summary
        logger.info("=" * 60)
        logger.info("📊 EMAIL CAMPAIGN SUMMARY")
        logger.info("=" * 60)
        logger.info(f"📧 Total contacts processed: {len(contacts)}")
        logger.info(f"✅ Successfully sent: {successful}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"⏱️  Total duration: {duration:.2f} seconds")
        logger.info(f"📈 Success rate: {(successful/len(contacts)*100):.1f}%")
        logger.info("=" * 60)
        
        return successful, failed

async def main():
    """Main function to run the email campaign."""
    print("🧪 Email Campaign to Contacts")
    print("=" * 50)
    
    try:
        # Initialize sender
        sender = ContactEmailSender()
        
        # Load contacts
        contacts = sender.load_contacts()
        
        if not contacts:
            print("❌ No valid contacts found!")
            return
        
        print(f"📋 Loaded {len(contacts)} contacts from input/Contacts.xlsx")
        print()
        
        # Show first few contacts
        print("📧 First 5 contacts:")
        for i, contact in enumerate(contacts[:5], 1):
            print(f"  {i}. {contact['contact_name']} ({contact['email']}) - {contact['company_name']}")
        if len(contacts) > 5:
            print(f"  ... and {len(contacts) - 5} more contacts")
        print()
        
        # Confirm before sending
        confirm = input("Do you want to send emails to all contacts? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("❌ Email campaign cancelled.")
            return
        
        print()
        print("🚀 Starting email campaign...")
        print("=" * 50)
        
        # Send emails
        successful, failed = await sender.send_emails_to_contacts(contacts, use_smtp=True)
        
        print()
        if successful > 0:
            print(f"🎉 Email campaign completed! {successful} emails sent successfully.")
            print("📧 Check your email logs for detailed results.")
        else:
            print("⚠️  No emails were sent successfully. Check the logs for errors.")
        
    except Exception as e:
        logger.error(f"Campaign error: {e}")
        print(f"❌ Error during email campaign: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 