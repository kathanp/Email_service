import stripe
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from ..db.mongodb import MongoDB
from ..models.payment_method import PaymentMethodInDB, PaymentMethodResponse
from ..core.config import settings

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentMethodService:
    def __init__(self):
        self.stripe = stripe

    async def store_payment_method(self, user_id: str, stripe_payment_method_id: str, stripe_customer_id: str) -> Dict[str, Any]:
        """Store payment method information from Stripe."""
        try:
            # Get payment method details from Stripe
            payment_method = self.stripe.PaymentMethod.retrieve(stripe_payment_method_id)
            
            # Extract card details
            card_details = payment_method.get('card', {})
            billing_details = payment_method.get('billing_details', {})
            
            payment_methods_collection = MongoDB.get_collection("payment_methods")
            if not payment_methods_collection:
                return {"success": False, "error": "Database not available"}

            # Check if this is the user's first payment method
            existing_methods_count = await payment_methods_collection.count_documents({
                "user_id": user_id,
                "is_active": True
            })
            is_default = existing_methods_count == 0

            # Create payment method record
            payment_method_data = {
                "user_id": user_id,
                "stripe_payment_method_id": stripe_payment_method_id,
                "stripe_customer_id": stripe_customer_id,
                "type": payment_method.get('type', 'card'),
                "brand": card_details.get('brand'),
                "last4": card_details.get('last4'),
                "exp_month": card_details.get('exp_month'),
                "exp_year": card_details.get('exp_year'),
                "is_default": is_default,
                "billing_details": billing_details,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True
            }

            result = await payment_methods_collection.insert_one(payment_method_data)
            
            logger.info(f"Stored payment method for user {user_id}: {card_details.get('brand')} ending in {card_details.get('last4')}")
            
            return {
                "success": True,
                "payment_method_id": str(result.inserted_id),
                "message": "Payment method stored successfully"
            }

        except Exception as e:
            logger.error(f"Error storing payment method: {e}")
            return {
                "success": False,
                "error": f"Failed to store payment method: {str(e)}"
            }

    async def get_user_payment_methods(self, user_id: str) -> List[PaymentMethodResponse]:
        """Get all active payment methods for a user."""
        try:
            payment_methods_collection = MongoDB.get_collection("payment_methods")
            if not payment_methods_collection:
                return []

            # Get all active payment methods for the user
            payment_methods = await payment_methods_collection.find({
                "user_id": user_id,
                "is_active": True
            }).sort("created_at", -1).to_list(None)

            result = []
            for pm in payment_methods:
                result.append(PaymentMethodResponse(
                    id=str(pm["_id"]),
                    user_id=pm["user_id"],
                    stripe_payment_method_id=pm["stripe_payment_method_id"],
                    stripe_customer_id=pm["stripe_customer_id"],
                    type=pm.get("type", "card"),
                    brand=pm.get("brand"),
                    last4=pm.get("last4"),
                    exp_month=pm.get("exp_month"),
                    exp_year=pm.get("exp_year"),
                    is_default=pm.get("is_default", False),
                    billing_details=pm.get("billing_details"),
                    created_at=pm["created_at"],
                    updated_at=pm["updated_at"],
                    is_active=pm["is_active"]
                ))

            return result

        except Exception as e:
            logger.error(f"Error getting user payment methods: {e}")
            return []

    async def get_default_payment_method(self, user_id: str) -> Optional[PaymentMethodResponse]:
        """Get the default payment method for a user."""
        try:
            payment_methods_collection = MongoDB.get_collection("payment_methods")
            if not payment_methods_collection:
                return None

            # Get the default payment method
            payment_method = await payment_methods_collection.find_one({
                "user_id": user_id,
                "is_default": True,
                "is_active": True
            })

            if payment_method:
                return PaymentMethodResponse(
                    id=str(payment_method["_id"]),
                    user_id=payment_method["user_id"],
                    stripe_payment_method_id=payment_method["stripe_payment_method_id"],
                    stripe_customer_id=payment_method["stripe_customer_id"],
                    type=payment_method.get("type", "card"),
                    brand=payment_method.get("brand"),
                    last4=payment_method.get("last4"),
                    exp_month=payment_method.get("exp_month"),
                    exp_year=payment_method.get("exp_year"),
                    is_default=payment_method.get("is_default", False),
                    billing_details=payment_method.get("billing_details"),
                    created_at=payment_method["created_at"],
                    updated_at=payment_method["updated_at"],
                    is_active=payment_method["is_active"]
                )

            return None

        except Exception as e:
            logger.error(f"Error getting default payment method: {e}")
            return None

    async def set_default_payment_method(self, user_id: str, payment_method_id: str) -> Dict[str, Any]:
        """Set a payment method as the default for a user."""
        try:
            payment_methods_collection = MongoDB.get_collection("payment_methods")
            if not payment_methods_collection:
                return {"success": False, "error": "Database not available"}

            from bson import ObjectId

            # First, unset all other payment methods as default
            await payment_methods_collection.update_many(
                {"user_id": user_id, "is_active": True},
                {"$set": {"is_default": False, "updated_at": datetime.utcnow()}}
            )

            # Set the specified payment method as default
            result = await payment_methods_collection.update_one(
                {"_id": ObjectId(payment_method_id), "user_id": user_id, "is_active": True},
                {"$set": {"is_default": True, "updated_at": datetime.utcnow()}}
            )

            if result.modified_count > 0:
                logger.info(f"Set payment method {payment_method_id} as default for user {user_id}")
                return {"success": True, "message": "Default payment method updated"}
            else:
                return {"success": False, "error": "Payment method not found"}

        except Exception as e:
            logger.error(f"Error setting default payment method: {e}")
            return {"success": False, "error": str(e)}

    async def delete_payment_method(self, user_id: str, payment_method_id: str) -> Dict[str, Any]:
        """Soft delete a payment method."""
        try:
            payment_methods_collection = MongoDB.get_collection("payment_methods")
            if not payment_methods_collection:
                return {"success": False, "error": "Database not available"}

            from bson import ObjectId

            # Soft delete the payment method
            result = await payment_methods_collection.update_one(
                {"_id": ObjectId(payment_method_id), "user_id": user_id},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )

            if result.modified_count > 0:
                logger.info(f"Deleted payment method {payment_method_id} for user {user_id}")
                return {"success": True, "message": "Payment method deleted"}
            else:
                return {"success": False, "error": "Payment method not found"}

        except Exception as e:
            logger.error(f"Error deleting payment method: {e}")
            return {"success": False, "error": str(e)}

    async def sync_stripe_payment_methods(self, user_id: str, stripe_customer_id: str) -> Dict[str, Any]:
        """Sync payment methods from Stripe for a customer."""
        try:
            # Get payment methods from Stripe
            stripe_payment_methods = self.stripe.PaymentMethod.list(
                customer=stripe_customer_id,
                type="card"
            )

            synced_count = 0
            for stripe_pm in stripe_payment_methods.data:
                # Check if we already have this payment method stored
                payment_methods_collection = MongoDB.get_collection("payment_methods")
                existing = await payment_methods_collection.find_one({
                    "stripe_payment_method_id": stripe_pm.id,
                    "user_id": user_id
                })

                if not existing:
                    # Store new payment method
                    result = await self.store_payment_method(user_id, stripe_pm.id, stripe_customer_id)
                    if result["success"]:
                        synced_count += 1

            logger.info(f"Synced {synced_count} payment methods for user {user_id}")
            return {"success": True, "synced_count": synced_count}

        except Exception as e:
            logger.error(f"Error syncing Stripe payment methods: {e}")
            return {"success": False, "error": str(e)} 