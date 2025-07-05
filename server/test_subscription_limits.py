#!/usr/bin/env python3
"""
Test Subscription Limits for Free Plan
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the server directory to the Python path
sys.path.append(os.path.dirname(__file__))

from app.services.subscription_service import SubscriptionService
from app.db.mongodb import MongoDB
from bson import ObjectId

async def test_subscription_limits():
    """Test subscription limits for Free plan users."""
    print("🧪 Testing Subscription Limits for Free Plan")
    print("=" * 50)
    
    # Initialize MongoDB connection first
    await MongoDB.connect_to_mongo()
    
    # Initialize services
    subscription_service = SubscriptionService()
    
    # Test user ID (you can replace this with a real user ID)
    test_user_id = "507f1f77bcf86cd799439011"  # Example ObjectId
    
    try:
        print(f"📋 Testing limits for user: {test_user_id}")
        print()
        
        # Test 1: Get user plan
        print("1️⃣ Testing Plan Detection")
        plan = await subscription_service.get_user_plan(test_user_id)
        print(f"   User plan: {plan}")
        print()
        
        # Test 2: Get plan limits
        print("2️⃣ Testing Plan Limits")
        limits = await subscription_service.get_plan_limits(test_user_id)
        print(f"   Email limit: {limits['email_limit']}")
        print(f"   Sender limit: {limits['sender_limit']}")
        print(f"   Template limit: {limits['template_limit']}")
        print()
        
        # Test 3: Get current usage
        print("3️⃣ Testing Current Usage")
        usage = await subscription_service.get_current_usage(test_user_id)
        print(f"   Emails sent this month: {usage['emails_sent_this_month']}")
        print(f"   Senders used: {usage['senders_count']}")
        print(f"   Templates created: {usage['templates_count']}")
        print()
        
        # Test 4: Test email limits
        print("4️⃣ Testing Email Limits")
        test_emails = [50, 100, 150]
        for email_count in test_emails:
            result = await subscription_service.check_email_limit(test_user_id, email_count)
            print(f"   Trying to send {email_count} emails: {'✅ Allowed' if result['allowed'] else '❌ Blocked'}")
            if not result['allowed']:
                print(f"      Reason: {result['reason']}")
        print()
        
        # Test 5: Test sender limits
        print("5️⃣ Testing Sender Limits")
        result = await subscription_service.check_sender_limit(test_user_id)
        print(f"   Adding new sender: {'✅ Allowed' if result['allowed'] else '❌ Blocked'}")
        if not result['allowed']:
            print(f"      Reason: {result['reason']}")
        print()
        
        # Test 6: Test template limits
        print("6️⃣ Testing Template Limits")
        result = await subscription_service.check_template_limit(test_user_id)
        print(f"   Creating new template: {'✅ Allowed' if result['allowed'] else '❌ Blocked'}")
        if not result['allowed']:
            print(f"      Reason: {result['reason']}")
        print()
        
        # Test 7: Test upgrade messages
        print("7️⃣ Testing Upgrade Messages")
        for feature in ['emails', 'senders', 'templates']:
            message = await subscription_service.get_upgrade_message(test_user_id, feature)
            print(f"   {feature.capitalize()}: {message}")
        print()
        
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close MongoDB connection
        await MongoDB.close_mongo_connection()

async def test_with_real_user():
    """Test with a real user from the database."""
    print("\n🔍 Testing with Real User from Database")
    print("=" * 40)
    
    try:
        # Initialize MongoDB connection
        await MongoDB.connect_to_mongo()
        
        # Get a real user from the database
        users_collection = MongoDB.get_collection("users")
        user = await users_collection.find_one()
        
        if user:
            user_id = str(user["_id"])
            print(f"Found user: {user.get('email', 'Unknown')} (ID: {user_id})")
            
            subscription_service = SubscriptionService()
            
            # Test limits for this user
            limits = await subscription_service.get_plan_limits(user_id)
            usage = await subscription_service.get_current_usage(user_id)
            
            print(f"Plan: {limits['plan']}")
            print(f"Email usage: {usage['emails_sent_this_month']}/{limits['email_limit']}")
            print(f"Sender usage: {usage['senders_count']}/{limits['sender_limit']}")
            print(f"Template usage: {usage['templates_count']}/{limits['template_limit']}")
            
            # Test if they can send 50 emails
            email_check = await subscription_service.check_email_limit(user_id, 50)
            print(f"Can send 50 emails: {'✅ Yes' if email_check['allowed'] else '❌ No'}")
            
        else:
            print("No users found in database")
            
    except Exception as e:
        print(f"❌ Error testing with real user: {e}")
    finally:
        # Close MongoDB connection
        await MongoDB.close_mongo_connection()

if __name__ == "__main__":
    print("🚀 Starting Subscription Limits Test")
    print("=" * 50)
    
    # Run the tests
    asyncio.run(test_subscription_limits())
    asyncio.run(test_with_real_user())
    
    print("\n🎉 Test completed!") 