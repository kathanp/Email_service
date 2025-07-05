"""
Mock subscription service for development without Stripe
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from bson import ObjectId
from app.db.mongodb import MongoDB
from app.models.subscription import SubscriptionPlan, BillingCycle, PaymentStatus, SUBSCRIPTION_PLANS

logger = logging.getLogger(__name__)

class MockSubscriptionService:
    def __init__(self):
        pass
    
    def _get_users_collection(self):
        """Get users collection."""
        return MongoDB.get_collection("users")
    
    async def create_mock_subscription(self, user_id: str, plan: SubscriptionPlan, 
                                     billing_cycle: BillingCycle = BillingCycle.MONTHLY) -> Dict:
        """Create a mock subscription without Stripe."""
        try:
            users_collection = self._get_users_collection()
            
            # Generate mock IDs
            mock_customer_id = f"cus_mock_{user_id}_{datetime.utcnow().timestamp()}"
            mock_subscription_id = f"sub_mock_{user_id}_{datetime.utcnow().timestamp()}"
            
            # Calculate billing dates
            now = datetime.utcnow()
            if billing_cycle == BillingCycle.MONTHLY:
                period_end = now + timedelta(days=30)
            else:
                period_end = now + timedelta(days=365)
            
            # Create subscription data
            subscription_data = {
                "plan": plan,
                "billing_cycle": billing_cycle,
                "status": PaymentStatus.ACTIVE,
                "stripe_customer_id": mock_customer_id,
                "stripe_subscription_id": mock_subscription_id,
                "current_period_start": now,
                "current_period_end": period_end,
                "cancel_at_period_end": False
            }
            
            # Update user
            result = await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"subscription": subscription_data}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Created mock subscription for user {user_id}")
                return {
                    "success": True,
                    "subscription_id": mock_subscription_id,
                    "customer_id": mock_customer_id,
                    "plan": plan,
                    "billing_cycle": billing_cycle,
                    "current_period_start": now,
                    "current_period_end": period_end
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update user"
                }
                
        except Exception as e:
            logger.error(f"Error creating mock subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def add_mock_payment_method(self, user_id: str, card_details: Dict) -> Dict:
        """Add a mock payment method."""
        try:
            users_collection = self._get_users_collection()
            
            # Generate mock payment method ID
            mock_payment_method_id = f"pm_mock_{user_id}_{datetime.utcnow().timestamp()}"
            
            # Create payment method data
            payment_method_data = {
                "id": mock_payment_method_id,
                "type": "card",
                "card": {
                    "brand": card_details.get("brand", "visa"),
                    "last4": card_details.get("last4", "1234"),
                    "exp_month": card_details.get("exp_month", 12),
                    "exp_year": card_details.get("exp_year", 2025)
                },
                "billing_details": {
                    "name": card_details.get("name", "Test User")
                }
            }
            
            # Store payment method in user document
            result = await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"payment_method": payment_method_data}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Added mock payment method for user {user_id}")
                return {
                    "success": True,
                    "payment_method": payment_method_data
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update user"
                }
                
        except Exception as e:
            logger.error(f"Error adding mock payment method: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_mock_payment_method(self, user_id: str) -> Optional[Dict]:
        """Get mock payment method for user."""
        try:
            users_collection = self._get_users_collection()
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
            if user and user.get("payment_method"):
                return user["payment_method"]
            return None
        except Exception as e:
            logger.error(f"Error getting mock payment method: {e}")
            return None

# Create global instance
mock_subscription_service = MockSubscriptionService() 