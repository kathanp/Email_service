#!/usr/bin/env python3
"""
Email Campaign Script
Sends emails from Contacts.xlsx and updates total sent count in database
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailCampaignSender:
    def __init__(self):
        self.mongodb_url = os.getenv("MONGODB_URL")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "sale.rrimp@gmail.com"
        self.sender_password = "mnuiachbwzesyzwv"
        self.client = None
        self.db = None
        
    async def connect_to_mongodb(self):
        """Connect to MongoDB Atlas."""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.db = self.client.email_bot
            logger.info("Connected to MongoDB Atlas")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def close_mongodb_connection(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def read_contacts_from_excel(self, file_path):
        """Read contacts from Excel file."""
        try:
            logger.info(f"Reading contacts from: {file_path}")
            df = pd.read_excel(file_path)
            
            # Clean column names
            df.columns = [str(col).strip() for col in df.columns]
            
            # Check if we have the required columns
            required_columns = ['email', 'company_name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}. Available columns: {df.columns.tolist()}")
            
            # Clean data - remove rows with missing email or company_name
            df = df.dropna(subset=['email', 'company_name'])
            df = df[df['email'].str.contains('@', na=False)]
            
            # Convert to list of dictionaries
            contacts = df.to_dict('records')
            logger.info(f"Found {len(contacts)} valid contacts")
            return contacts
            
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            raise
    
    def create_email_content(self, contact):
        """Create personalized email content."""
        subject = f"Partnership Opportunity with {contact.get('company_name', 'Your Company')}"
        
        body = f"""
Dear {contact.get('contact_name', 'Valued Partner')},

I hope this email finds you well. I am reaching out from our team regarding a potential partnership opportunity with {contact.get('company_name', 'your company')}.

We believe there could be significant mutual benefits in exploring a collaboration between our organizations. Your company's reputation and market position align perfectly with our strategic goals.

Would you be interested in scheduling a brief call to discuss potential partnership opportunities? I would be happy to share more details about how we could work together.

Please let me know your availability, and I'll be glad to arrange a meeting at your convenience.

Best regards,
Your Name
Your Company
Email: {self.sender_email}
Phone: Your Phone Number
        """
        
        return subject.strip(), body.strip()
    
    def send_email(self, recipient_email, subject, body, max_retries=3):
        """Send email with retry logic."""
        for attempt in range(max_retries):
            try:
                msg = MIMEMultipart()
                msg['From'] = self.sender_email
                msg['To'] = recipient_email
                msg['Subject'] = subject
                
                msg.attach(MIMEText(body, 'plain'))
                
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(msg)
                
                logger.info(f"✓ Email sent successfully to {recipient_email}")
                return True
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"✗ Final attempt failed for {recipient_email}: {str(e)}")
                    return False
                logger.warning(f"Attempt {attempt + 1} failed, retrying: {str(e)}")
                time.sleep(2 ** attempt)
    
    async def update_campaign_stats(self, total_sent, total_failed):
        """Update campaign statistics in database."""
        try:
            campaign_stats = {
                "date": datetime.utcnow(),
                "total_contacts": total_sent + total_failed,
                "emails_sent": total_sent,
                "emails_failed": total_failed,
                "success_rate": (total_sent / (total_sent + total_failed)) * 100 if (total_sent + total_failed) > 0 else 0
            }
            
            # Insert campaign record
            await self.db.campaigns.insert_one(campaign_stats)
            
            # Update total sent count
            await self.db.stats.update_one(
                {"_id": "email_stats"},
                {
                    "$inc": {
                        "total_emails_sent": total_sent,
                        "total_campaigns": 1
                    },
                    "$set": {"last_updated": datetime.utcnow()}
                },
                upsert=True
            )
            
            logger.info(f"Campaign stats updated: {total_sent} sent, {total_failed} failed")
            
        except Exception as e:
            logger.error(f"Error updating campaign stats: {e}")
    
    async def run_campaign(self, contacts_file_path):
        """Run the complete email campaign."""
        try:
            # Connect to MongoDB
            await self.connect_to_mongodb()
            
            # Read contacts
            contacts = self.read_contacts_from_excel(contacts_file_path)
            
            if not contacts:
                logger.error("No valid contacts found in the file")
                return
            
            successful_emails = 0
            failed_emails = 0
            
            print("\n🚀 Starting Email Campaign...")
            print("=" * 60)
            print(f"📧 Total contacts to process: {len(contacts)}")
            print("=" * 60)
            
            for i, contact in enumerate(contacts, 1):
                try:
                    email = contact.get('email', '').strip()
                    company = contact.get('company_name', 'Unknown Company')
                    
                    if not email or '@' not in email:
                        logger.warning(f"Skipping invalid email: {email}")
                        failed_emails += 1
                        continue
                    
                    print(f"\n📧 Processing email {i}/{len(contacts)}:")
                    print(f"   To: {email}")
                    print(f"   Company: {company}")
                    
                    # Create email content
                    subject, body = self.create_email_content(contact)
                    
                    # Send email
                    success = self.send_email(email, subject, body)
                    
                    if success:
                        successful_emails += 1
                        print("   ✅ Email sent successfully!")
                    else:
                        failed_emails += 1
                        print("   ❌ Failed to send email")
                    
                    print("-" * 60)
                    
                    # Delay between emails to avoid rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing contact {contact}: {str(e)}")
                    failed_emails += 1
                    print(f"   ❌ Error: {str(e)}")
                    print("-" * 60)
            
            # Update campaign statistics
            await self.update_campaign_stats(successful_emails, failed_emails)
            
            # Print summary
            print("\n📊 Email Campaign Summary:")
            print("=" * 60)
            print(f"📧 Total contacts processed: {len(contacts)}")
            print(f"✅ Successfully sent: {successful_emails}")
            print(f"❌ Failed: {failed_emails}")
            print(f"📈 Success rate: {(successful_emails/len(contacts)*100):.1f}%")
            print("=" * 60)
            
            # Get total stats
            stats = await self.db.stats.find_one({"_id": "email_stats"})
            if stats:
                print(f"📊 Total emails sent (all time): {stats.get('total_emails_sent', 0)}")
                print(f"📊 Total campaigns run: {stats.get('total_campaigns', 0)}")
            
        except Exception as e:
            logger.error(f"Error running campaign: {e}")
            raise
        finally:
            await self.close_mongodb_connection()

async def main():
    """Main function to run the email campaign."""
    try:
        # Check if contacts file exists
        contacts_file = Path("input/Contacts.xlsx")
        if not contacts_file.exists():
            print(f"❌ Error: Contacts file not found at {contacts_file}")
            print("Please ensure the file exists in the input/ directory")
            return
        
        # Create and run campaign
        campaign_sender = EmailCampaignSender()
        await campaign_sender.run_campaign(contacts_file)
        
    except Exception as e:
        logger.error(f"Campaign failed: {e}")
        print(f"❌ Campaign failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 