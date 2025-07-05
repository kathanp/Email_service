#!/usr/bin/env python3
"""
Test script to simulate subscription creation and debug the process
"""

import asyncio
import sys
import os
from bson import ObjectId

# Add the server directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import MongoDB
from app.services.stripe_service import stripe_service
from app.models.subscription import SUBSCRIPTION_PLANS, SubscriptionPlan, BillingCycle, PaymentStatus
from datetime import datetime

async def test_subscription_creation():
    """Test subscription creation process."""
    
    try:
        # Connect to MongoDB
        await MongoDB.connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        # Get users collection
        users_collection = MongoDB.get_collection("users")
        
        # Find any user
        user = await users_collection.find_one({})
        
        if not user:
            print("❌ No users found in database")
            return
        
        print(f"✅ Found user: {user.get('email', 'Unknown')}")
        print(f"   User ID: {user['_id']}")
        
        # Check if user already has subscription
        existing_subscription = user.get("subscription", {})
        if existing_subscription.get("stripe_subscription_id"):
            print(f"❌ User already has subscription: {existing_subscription.get('stripe_subscription_id')}")
            return
        
        print(f"\n🔄 Testing Subscription Creation Process:")
        
        # Step 1: Create Stripe customer
        print(f"1️⃣ Creating Stripe customer...")
        customer_result = await stripe_service.create_customer(
            str(user["_id"]), 
            user["email"], 
            user.get("full_name")
        )
        
        if customer_result["success"]:
            print(f"   ✅ Customer created: {customer_result['customer_id']}")
            customer_id = customer_result["customer_id"]
        else:
            print(f"   ❌ Failed to create customer: {customer_result['error']}")
            return
        
        # Step 2: Test subscription creation (without payment method for now)
        print(f"\n2️⃣ Testing subscription creation...")
        
        # For testing, we'll create a free subscription first
        plan = SubscriptionPlan.STARTER  # Change this to test different plans
        billing_cycle = BillingCycle.MONTHLY
        
        print(f"   Plan: {plan}")
        print(f"   Billing Cycle: {billing_cycle}")
        
        # Note: For real subscription creation, you need a payment method
        # This is just testing the customer creation part
        print(f"   ⚠️  Note: Real subscription requires payment method")
        
        # Step 3: Update user with customer ID (simulate partial subscription creation)
        print(f"\n3️⃣ Updating user with customer ID...")
        
        update_data = {
            "subscription": {
                "plan": plan,
                "billing_cycle": billing_cycle,
                "status": PaymentStatus.ACTIVE,
                "stripe_customer_id": customer_id,
                "stripe_subscription_id": None,  # Will be set when payment method is added
                "current_period_start": datetime.utcnow(),
                "current_period_end": datetime.utcnow(),
                "cancel_at_period_end": False
            }
        }
        
        result = await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            print(f"   ✅ User updated with customer ID")
        else:
            print(f"   ❌ Failed to update user")
            return
        
        # Step 4: Test payment method retrieval
        print(f"\n4️⃣ Testing payment method retrieval...")
        
        payment_methods_result = await stripe_service.get_customer_payment_methods(customer_id)
        
        if payment_methods_result["success"]:
            payment_methods = payment_methods_result["payment_methods"]
            print(f"   ✅ Found {len(payment_methods)} payment method(s)")
            
            for i, pm in enumerate(payment_methods):
                print(f"   Payment Method {i+1}:")
                print(f"     ID: {pm.id}")
                print(f"     Type: {pm.type}")
                if pm.card:
                    print(f"     Card: {pm.card.brand} •••• {pm.card.last4}")
                    print(f"     Expires: {pm.card.exp_month}/{pm.card.exp_year}")
        else:
            print(f"   ℹ️  No payment methods found (expected for new customer)")
        
        print(f"\n✅ Test completed successfully!")
        print(f"   Customer ID: {customer_id}")
        print(f"   User now has subscription data in database")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await MongoDB.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_subscription_creation()) 