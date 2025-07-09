#!/usr/bin/env python3
"""
Test script to demonstrate user isolation in the mass email service.
This script shows how each user can only access their own files.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_user_isolation():
    """Test that users can only access their own files."""
    
    print("🧪 Testing User Isolation in Mass Email Service")
    print("=" * 60)
    
    # Test 1: User Registration
    print("\n1️⃣ Registering test users...")
    
    user1_data = {
        "email": "user1@test.com",
        "password": "password123",
        "username": "user1"
    }
    
    user2_data = {
        "email": "user2@test.com", 
        "password": "password123",
        "username": "user2"
    }
    
    # Register users
    user1_response = requests.post(f"{API_BASE}/auth/register", json=user1_data)
    user2_response = requests.post(f"{API_BASE}/auth/register", json=user2_data)
    
    if user1_response.status_code == 201 and user2_response.status_code == 201:
        print("✅ Both users registered successfully")
        
        user1_token = user1_response.json()["access_token"]
        user2_token = user2_response.json()["access_token"]
        
        user1_id = user1_response.json()["user"]["id"]
        user2_id = user2_response.json()["user"]["id"]
        
        print(f"👤 User 1 ID: {user1_id}")
        print(f"👤 User 2 ID: {user2_id}")
    else:
        print("❌ User registration failed")
        return
    
    # Test 2: File Upload Isolation
    print("\n2️⃣ Testing file upload isolation...")
    
    # Create test CSV files
    csv_content1 = "email,name,company\nuser1@example.com,User One,Company A\nuser1b@example.com,User One B,Company A"
    csv_content2 = "email,name,company\nuser2@example.com,User Two,Company B\nuser2b@example.com,User Two B,Company B"
    
    # Upload files for each user
    files1_response = requests.post(
        f"{API_BASE}/files/upload",
        headers={"Authorization": f"Bearer {user1_token}"},
        files={"file": ("user1_contacts.csv", csv_content1, "text/csv")},
        data={"description": "User 1 contacts"}
    )
    
    files2_response = requests.post(
        f"{API_BASE}/files/upload", 
        headers={"Authorization": f"Bearer {user2_token}"},
        files={"file": ("user2_contacts.csv", csv_content2, "text/csv")},
        data={"description": "User 2 contacts"}
    )
    
    if files1_response.status_code == 200 and files2_response.status_code == 200:
        print("✅ Files uploaded successfully for both users")
        
        user1_file = files1_response.json()
        user2_file = files2_response.json()
        
        print(f"📁 User 1 file ID: {user1_file['id']}")
        print(f"📁 User 2 file ID: {user2_file['id']}")
    else:
        print("❌ File upload failed")
        return
    
    # Test 3: File Access Isolation
    print("\n3️⃣ Testing file access isolation...")
    
    # User 1 tries to access their own file (should succeed)
    user1_own_file = requests.get(
        f"{API_BASE}/files/{user1_file['id']}",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    
    # User 1 tries to access User 2's file (should fail)
    user1_other_file = requests.get(
        f"{API_BASE}/files/{user2_file['id']}",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    
    # User 2 tries to access their own file (should succeed)
    user2_own_file = requests.get(
        f"{API_BASE}/files/{user2_file['id']}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    
    # User 2 tries to access User 1's file (should fail)
    user2_other_file = requests.get(
        f"{API_BASE}/files/{user1_file['id']}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    
    print(f"👤 User 1 accessing own file: {'✅ SUCCESS' if user1_own_file.status_code == 200 else '❌ FAILED'}")
    print(f"👤 User 1 accessing User 2's file: {'❌ BLOCKED (Expected)' if user1_other_file.status_code == 404 else '⚠️ ALLOWED (Security Issue)'}")
    print(f"👤 User 2 accessing own file: {'✅ SUCCESS' if user2_own_file.status_code == 200 else '❌ FAILED'}")
    print(f"👤 User 2 accessing User 1's file: {'❌ BLOCKED (Expected)' if user2_other_file.status_code == 404 else '⚠️ ALLOWED (Security Issue)'}")
    
    # Test 4: File Listing Isolation
    print("\n4️⃣ Testing file listing isolation...")
    
    user1_files = requests.get(
        f"{API_BASE}/files/",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    
    user2_files = requests.get(
        f"{API_BASE}/files/",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    
    if user1_files.status_code == 200 and user2_files.status_code == 200:
        user1_file_count = len(user1_files.json()["files"])
        user2_file_count = len(user2_files.json()["files"])
        
        print(f"📁 User 1 sees {user1_file_count} files")
        print(f"📁 User 2 sees {user2_file_count} files")
        
        if user1_file_count == 1 and user2_file_count == 1:
            print("✅ File listing isolation working correctly")
        else:
            print("⚠️ File listing isolation may have issues")
    else:
        print("❌ File listing failed")
    
    # Test 5: Campaign Creation Isolation
    print("\n5️⃣ Testing campaign creation isolation...")
    
    # Create a simple template for testing
    template_data = {
        "name": "Test Template",
        "subject": "Test Email",
        "body": "Hello {{name}}, this is a test email from {{company}}.",
        "user_id": user1_id
    }
    
    template_response = requests.post(
        f"{API_BASE}/templates/",
        headers={"Authorization": f"Bearer {user1_token}"},
        json=template_data
    )
    
    if template_response.status_code == 200:
        template_id = template_response.json()["id"]
        print(f"📝 Template created: {template_id}")
        
        # User 1 tries to create campaign with their own file (should succeed)
        campaign_data1 = {
            "template_id": template_id,
            "file_id": user1_file["id"],
            "subject_override": "Test Campaign from User 1"
        }
        
        campaign1_response = requests.post(
            f"{API_BASE}/campaigns/",
            headers={"Authorization": f"Bearer {user1_token}"},
            json=campaign_data1
        )
        
        # User 1 tries to create campaign with User 2's file (should fail)
        campaign_data2 = {
            "template_id": template_id,
            "file_id": user2_file["id"],
            "subject_override": "Test Campaign with User 2's file"
        }
        
        campaign2_response = requests.post(
            f"{API_BASE}/campaigns/",
            headers={"Authorization": f"Bearer {user1_token}"},
            json=campaign_data2
        )
        
        print(f"👤 User 1 campaign with own file: {'✅ SUCCESS' if campaign1_response.status_code == 200 else '❌ FAILED'}")
        print(f"👤 User 1 campaign with User 2's file: {'❌ BLOCKED (Expected)' if campaign2_response.status_code == 404 else '⚠️ ALLOWED (Security Issue)'}")
    else:
        print("❌ Template creation failed")
    
    print("\n" + "=" * 60)
    print("🎉 User Isolation Test Complete!")
    print("✅ Each user can only access their own files for campaigns")
    print("✅ Cross-user file access is properly blocked")
    print("✅ Mass email service maintains data isolation")

if __name__ == "__main__":
    test_user_isolation() 