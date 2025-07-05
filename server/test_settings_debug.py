#!/usr/bin/env python3
"""
Debug script to test subscription and payment method functionality
"""

import asyncio
import sys
import os
from bson import ObjectId

# Add the server directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import MongoDB
from app.services.stripe_service import stripe_service
from app.models.subscription import SUBSCRIPTION_PLANS, SubscriptionPlan

async def test_subscription_debug():
    """Test subscription and payment method functionality."""
    
    try:
        # Connect to MongoDB
        await MongoDB.connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        # Get users collection
        users_collection = MongoDB.get_collection("users")
        
        # Find a user with a subscription
        user = await users_collection.find_one({
            "subscription": {"$exists": True, "$ne": {}}
        })
        
        if not user:
            print("❌ No user with subscription found")
            return
        
        print(f"✅ Found user: {user.get('email', 'Unknown')}")
        print(f"   User ID: {user['_id']}")
        
        # Check subscription data
        subscription = user.get("subscription", {})
        print(f"\n📦 Subscription Data:")
        print(f"   Plan: {subscription.get('plan', 'None')}")
        print(f"   Stripe Customer ID: {subscription.get('stripe_customer_id', 'None')}")
        print(f"   Stripe Subscription ID: {subscription.get('stripe_subscription_id', 'None')}")
        print(f"   Status: {subscription.get('status', 'None')}")
        
        # Test payment method retrieval
        stripe_customer_id = subscription.get("stripe_customer_id")
        if stripe_customer_id:
            print(f"\n💳 Testing Payment Method Retrieval:")
            print(f"   Customer ID: {stripe_customer_id}")
            
            payment_methods_result = await stripe_service.get_customer_payment_methods(stripe_customer_id)
            
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
                print(f"   ❌ Failed to get payment methods: {payment_methods_result['error']}")
        else:
            print(f"\n❌ No Stripe Customer ID found")
        
        # Test the payment method endpoint logic
        print(f"\n🔍 Testing Payment Method Endpoint Logic:")
        try:
            from bson import ObjectId
            user_id_str = str(user["_id"])
            print(f"   User ID (string): {user_id_str}")
            
            # Test ObjectId conversion
            user_obj_id = ObjectId(user_id_str)
            print(f"   User ID (ObjectId): {user_obj_id}")
            
            # Test database query
            user_found = await users_collection.find_one({"_id": user_obj_id})
            if user_found:
                print(f"   ✅ User found in database")
                subscription_found = user_found.get("subscription", {})
                stripe_customer_id_found = subscription_found.get("stripe_customer_id")
                print(f"   Stripe Customer ID from query: {stripe_customer_id_found}")
            else:
                print(f"   ❌ User not found in database")
                
        except Exception as e:
            print(f"   ❌ Error in payment method endpoint logic: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await MongoDB.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_subscription_debug()) 