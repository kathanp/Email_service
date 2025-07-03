#!/usr/bin/env python3
"""
Add Test Contacts Script
Adds 23 more test contact records to the existing Contacts.xlsx file
"""

import pandas as pd
from pathlib import Path

def add_test_contacts():
    """Add 23 more test contacts to the existing file."""
    
    # Read existing contacts
    contacts_file = Path("input/Contacts.xlsx")
    if not contacts_file.exists():
        print("❌ Error: Contacts.xlsx file not found!")
        return
    
    df = pd.read_excel(contacts_file)
    print(f"📊 Current records: {len(df)}")
    
    # Create 23 more test contacts
    new_contacts = []
    for i in range(4, 27):  # Adding contacts 4-26 (23 total)
        new_contact = {
            'email': 'sale.rrimp@gmail.com',
            'company_name': f'Test Company {i}',
            'contact_name': f'Contact Person {i}'
        }
        new_contacts.append(new_contact)
    
    # Create DataFrame for new contacts
    new_df = pd.DataFrame(new_contacts)
    
    # Combine existing and new contacts
    combined_df = pd.concat([df, new_df], ignore_index=True)
    
    # Save back to Excel file
    combined_df.to_excel(contacts_file, index=False)
    
    print(f"✅ Added {len(new_contacts)} new contacts")
    print(f"📊 Total records now: {len(combined_df)}")
    print(f"📧 All emails will be sent to: sale.rrimp@gmail.com")
    
    # Show first few and last few records
    print("\n📋 First 5 records:")
    print(combined_df.head())
    print("\n📋 Last 5 records:")
    print(combined_df.tail())

if __name__ == "__main__":
    add_test_contacts() 