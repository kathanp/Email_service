#!/usr/bin/env python3

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_test_email():
    """Send a test email to verify the email service is working."""
    
    # Email configuration
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = "sale.rrimp@gmail.com"
    password = "mnuiachbwzesyzwv"
    recipient_email = "sale.rrimp@gmail.com"  # Sending to self for testing
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "Test Email from Email Bot"
        
        # Email body
        body = """
        Hello!
        
        This is a test email from your Email Bot application.
        
        If you receive this email, it means:
        ✅ SMTP connection is working
        ✅ Email credentials are valid
        ✅ Email service is functional
        
        Best regards,
        Email Bot System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print("Connecting to SMTP server...")
        with smtplib.SMTP(smtp_server, port, timeout=30) as server:
            server.starttls()
            print("Logging in...")
            server.login(sender_email, password)
            print("Sending email...")
            server.send_message(msg)
        
        print("✅ Test email sent successfully!")
        print(f"📧 Email sent to: {recipient_email}")
        print(f"📧 Email sent from: {sender_email}")
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Email Service...")
    print("=" * 50)
    send_test_email()
    print("=" * 50) 