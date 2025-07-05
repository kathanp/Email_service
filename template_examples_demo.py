#!/usr/bin/env python3
"""
Demonstration of email templates using email, company_name, contact_name variables
"""

import pandas as pd
from io import StringIO

def demonstrate_templates():
    """Demonstrate how templates work with contact data."""
    
    # Sample contact data (your structure)
    contacts_data = """email,company_name,contact_name
john.doe@company1.com,Acme Corporation,John Doe
jane.smith@company2.com,Tech Solutions Inc,Jane Smith
bob.johnson@company3.com,Global Industries,Bob Johnson
sarah.wilson@company4.com,Innovation Labs,Sarah Wilson
mike.brown@company5.com,Digital Dynamics,Mike Brown"""
    
    df = pd.read_csv(StringIO(contacts_data))
    
    # Example templates
    templates = {
        "Professional Introduction": {
            "subject": "Partnership Opportunity with {COMPANY_NAME}",
            "body": """Dear {CONTACT_NAME},

I hope this email finds you well. My name is Alex Johnson, and I'm reaching out from Business Solutions Corp regarding a potential partnership opportunity with {COMPANY_NAME}.

I've been following {COMPANY_NAME}'s impressive work in the industry and believe there could be significant mutual benefits in exploring a collaboration between our organizations.

Our company specializes in digital transformation and we've successfully partnered with companies similar to {COMPANY_NAME} to deliver exceptional results.

Would you be interested in scheduling a brief 15-minute call to discuss how we might work together? I'd be happy to share more details about our services and explore potential synergies.

Please let me know your availability, and I'll be glad to arrange a meeting at your convenience.

Best regards,
Alex Johnson
Senior Business Development Manager
Business Solutions Corp
Email: alex.johnson@businesssolutions.com
Phone: +1 (555) 123-4567"""
        },
        
        "Service Offer": {
            "subject": "Exclusive Service Offer for {COMPANY_NAME}",
            "body": """Hello {CONTACT_NAME},

I hope you're having a great day! I'm reaching out because I believe {COMPANY_NAME} could benefit from our specialized services.

Based on my research of {COMPANY_NAME}, I think our AI-powered analytics platform could help you achieve 40% increase in operational efficiency. We've helped similar companies in your industry increase their productivity by an average of 35%.

Here's what we offer:
• Real-time data analytics and insights
• Custom dashboard creation
• Predictive modeling capabilities
• 24/7 technical support

I'd love to schedule a quick call to discuss how we can help {COMPANY_NAME} achieve its goals. Would you be available for a 20-minute conversation this week?

Looking forward to hearing from you!

Best regards,
Maria Rodriguez
Sales Director
DataTech Solutions"""
        },
        
        "Event Invitation": {
            "subject": "Exclusive Invitation for {COMPANY_NAME} - Tech Innovation Summit 2024",
            "body": """Dear {CONTACT_NAME},

I hope this message finds you well. I'm excited to extend a special invitation to {COMPANY_NAME} for our upcoming Tech Innovation Summit 2024.

Tech Innovation Summit 2024 is a premier industry event that brings together leaders and innovators in technology. Given {COMPANY_NAME}'s reputation and expertise, we believe your team would find tremendous value in attending.

Event Details:
📅 Date: March 15-17, 2024
📍 Location: San Francisco Convention Center
⏰ Time: 9:00 AM - 6:00 PM daily
🎯 Focus: AI, Cloud Computing, Digital Transformation

This exclusive event will feature:
• Keynote presentations from industry leaders
• Networking opportunities with peers
• Interactive workshops and sessions
• Exclusive insights and trends

As a special offer for {COMPANY_NAME}, we're extending a 25% discount on registration.

Would you be interested in learning more about this opportunity? I'd be happy to provide additional details and answer any questions you might have.

Best regards,
David Chen
Event Director
Tech Innovation Summit"""
        }
    }
    
    print("📧 Email Template Examples with Contact Data")
    print("=" * 60)
    print(f"📋 Contact Data Structure: {list(df.columns)}")
    print(f"👥 Number of contacts: {len(df)}")
    print("=" * 60)
    
    # Show how each template would be personalized for each contact
    for template_name, template in templates.items():
        print(f"\n🎯 Template: {template_name}")
        print("-" * 40)
        
        # Show example for first contact
        first_contact = df.iloc[0]
        
        # Replace variables in template
        personalized_subject = template["subject"].replace("{COMPANY_NAME}", first_contact["company_name"])
        personalized_body = template["body"].replace("{CONTACT_NAME}", first_contact["contact_name"])
        personalized_body = personalized_body.replace("{COMPANY_NAME}", first_contact["company_name"])
        
        print(f"📧 To: {first_contact['email']}")
        print(f"🏢 Company: {first_contact['company_name']}")
        print(f"👤 Contact: {first_contact['contact_name']}")
        print(f"📝 Subject: {personalized_subject}")
        print(f"📄 Body Preview: {personalized_body[:200]}...")
        print("-" * 40)
    
    # Show validation example
    print(f"\n✅ Template Variable Validation")
    print("-" * 40)
    print("Template variables used:")
    for template_name, template in templates.items():
        variables = []
        if "{CONTACT_NAME}" in template["body"]:
            variables.append("CONTACT_NAME")
        if "{COMPANY_NAME}" in template["body"]:
            variables.append("COMPANY_NAME")
        print(f"• {template_name}: {', '.join(variables)}")
    
    print(f"\n📋 Contact file columns: {list(df.columns)}")
    print("✅ All template variables are available in the contact file!")
    print("✅ These templates will pass validation and can be sent successfully.")
    
    # Show what happens with missing variables
    print(f"\n❌ Example: What happens with missing variables")
    print("-" * 40)
    print("If a template uses {PHONE_NUMBER} but contact file only has:")
    print("email, company_name, contact_name")
    print("❌ Validation would fail and prevent campaign from being sent")
    print("💡 Solution: Add 'phone_number' column to contact file")

if __name__ == "__main__":
    demonstrate_templates() 