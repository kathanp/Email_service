#!/usr/bin/env python3
"""
Test script to create mock subscription and payment method
"""

import asyncio
import sys
import os
from bson import ObjectId

# Add the server directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import MongoDB
from app.services.mock_subscription_service import mock_subscription_service
from app.models.subscription import SubscriptionPlan, BillingCycle

async def test_mock_subscription():
    """Test mock subscription creation."""
    
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
        
        user_id = str(user["_id"])
        
        # Step 1: Create mock subscription
        print(f"\n1️⃣ Creating mock subscription...")
        
        subscription_result = await mock_subscription_service.create_mock_subscription(
            user_id=user_id,
            plan=SubscriptionPlan.STARTER,
            billing_cycle=BillingCycle.MONTHLY
        )
        
        if subscription_result["success"]:
            print(f"   ✅ Mock subscription created!")
            print(f"   Subscription ID: {subscription_result['subscription_id']}")
            print(f"   Customer ID: {subscription_result['customer_id']}")
        else:
            print(f"   ❌ Failed to create subscription: {subscription_result['error']}")
            return
        
        # Step 2: Add mock payment method
        print(f"\n2️⃣ Adding mock payment method...")
        
        card_details = {
            "brand": "visa",
            "last4": "4242",
            "exp_month": 12,
            "exp_year": 2025,
            "name": "Test User"
        }
        
        payment_result = await mock_subscription_service.add_mock_payment_method(
            user_id=user_id,
            card_details=card_details
        )
        
        if payment_result["success"]:
            print(f"   ✅ Mock payment method added!")
            payment_method = payment_result["payment_method"]
            print(f"   Payment Method ID: {payment_method['id']}")
            print(f"   Card: {payment_method['card']['brand']} •••• {payment_method['card']['last4']}")
            print(f"   Expires: {payment_method['card']['exp_month']}/{payment_method['card']['exp_year']}")
        else:
            print(f"   ❌ Failed to add payment method: {payment_result['error']}")
        
        # Step 3: Verify data in database
        print(f"\n3️⃣ Verifying data in database...")
        
        updated_user = await users_collection.find_one({"_id": user["_id"]})
        
        if updated_user.get("subscription"):
            subscription = updated_user["subscription"]
            print(f"   ✅ Subscription found:")
            print(f"     Plan: {subscription.get('plan')}")
            print(f"     Status: {subscription.get('status')}")
            print(f"     Customer ID: {subscription.get('stripe_customer_id')}")
            print(f"     Subscription ID: {subscription.get('stripe_subscription_id')}")
        else:
            print(f"   ❌ No subscription found")
        
        if updated_user.get("payment_method"):
            payment_method = updated_user["payment_method"]
            print(f"   ✅ Payment method found:")
            print(f"     ID: {payment_method.get('id')}")
            print(f"     Type: {payment_method.get('type')}")
            if payment_method.get('card'):
                card = payment_method['card']
                print(f"     Card: {card.get('brand')} •••• {card.get('last4')}")
        else:
            print(f"   ❌ No payment method found")
        
        print(f"\n🎉 Test completed successfully!")
        print(f"   You can now test the Settings page with this mock data")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await MongoDB.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_mock_subscription()) 