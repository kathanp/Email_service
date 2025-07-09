from typing import Dict, Any, Optional
from ..db.mongodb import MongoDB
from ..models.user import UserResponse
import logging

logger = logging.getLogger(__name__)

class SubscriptionService:
    def __init__(self):
        self.plan_limits = {
            "free": {
                "emails_per_month": 100,
                "sender_emails": 1,
                "templates": 3,
                "api_access": False,
                "priority_support": False,
                "white_label": False,
                "custom_integrations": False
            },
            "starter": {
                "emails_per_month": 1000,
                "sender_emails": 3,
                "templates": 10,
                "api_access": False,
                "priority_support": False,
                "white_label": False,
                "custom_integrations": False
            },
            "professional": {
                "emails_per_month": 10000,
                "sender_emails": 10,
                "templates": 50,
                "api_access": True,
                "priority_support": True,
                "white_label": False,
                "custom_integrations": False
            },
            "enterprise": {
                "emails_per_month": 50000,
                "sender_emails": -1,  # Unlimited
                "templates": -1,  # Unlimited
                "api_access": True,
                "priority_support": True,
                "white_label": True,
                "custom_integrations": True
            }
        }

    def get_user_plan_limits(self, user: UserResponse) -> Dict[str, Any]:
        """Get the limits for a user's current plan."""
        plan = user.usersubscription or "free"
        return self.plan_limits.get(plan, self.plan_limits["free"])

    async def check_email_limit(self, user: UserResponse) -> Dict[str, Any]:
        """Check if user can send more emails this month."""
        try:
            plan_limits = self.get_user_plan_limits(user)
            emails_per_month = plan_limits["emails_per_month"]
            
            if emails_per_month == -1:  # Unlimited
                return {"can_send": True, "remaining": -1, "limit": -1}
            
            # Get current month's email count
            from datetime import datetime, timedelta
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            email_logs_collection = MongoDB.get_collection("email_logs")
            if email_logs_collection:
                sent_count = await email_logs_collection.count_documents({
                    "user_id": user.id,
                    "sent_at": {"$gte": start_of_month},
                    "status": "sent"
                })
                
                remaining = max(0, emails_per_month - sent_count)
                can_send = remaining > 0
                
                return {
                    "can_send": can_send,
                    "remaining": remaining,
                    "limit": emails_per_month,
                    "used": sent_count
                }
            else:
                # If collection not available, assume can send
                return {"can_send": True, "remaining": emails_per_month, "limit": emails_per_month, "used": 0}
                
        except Exception as e:
            logger.error(f"Error checking email limit: {e}")
            return {"can_send": True, "remaining": 100, "limit": 100, "used": 0}

    async def check_sender_email_limit(self, user: UserResponse) -> Dict[str, Any]:
        """Check if user can add more sender emails."""
        try:
            plan_limits = self.get_user_plan_limits(user)
            sender_emails_limit = plan_limits["sender_emails"]
            
            if sender_emails_limit == -1:  # Unlimited
                return {"can_add": True, "remaining": -1, "limit": -1}
            
            # Get current sender email count
            senders_collection = MongoDB.get_collection("senders")
            if senders_collection:
                current_count = await senders_collection.count_documents({
                    "user_id": user.id,
                    "is_active": True
                })
                
                remaining = max(0, sender_emails_limit - current_count)
                can_add = remaining > 0
                
                return {
                    "can_add": can_add,
                    "remaining": remaining,
                    "limit": sender_emails_limit,
                    "current": current_count
                }
            else:
                # If collection not available, assume can add
                return {"can_add": True, "remaining": sender_emails_limit, "limit": sender_emails_limit, "current": 0}
                
        except Exception as e:
            logger.error(f"Error checking sender email limit: {e}")
            return {"can_add": True, "remaining": 1, "limit": 1, "current": 0}

    async def check_template_limit(self, user: UserResponse) -> Dict[str, Any]:
        """Check if user can create more templates."""
        try:
            plan_limits = self.get_user_plan_limits(user)
            templates_limit = plan_limits["templates"]
            
            if templates_limit == -1:  # Unlimited
                return {"can_create": True, "remaining": -1, "limit": -1}
            
            # Get current template count
            templates_collection = MongoDB.get_collection("templates")
            if templates_collection:
                current_count = await templates_collection.count_documents({
                    "user_id": user.id,
                    "is_active": True
                })
                
                remaining = max(0, templates_limit - current_count)
                can_create = remaining > 0
                
                return {
                    "can_create": can_create,
                    "remaining": remaining,
                    "limit": templates_limit,
                    "current": current_count
                }
            else:
                # If collection not available, assume can create
                return {"can_create": True, "remaining": templates_limit, "limit": templates_limit, "current": 0}
                
        except Exception as e:
            logger.error(f"Error checking template limit: {e}")
            return {"can_create": True, "remaining": 3, "limit": 3, "current": 0}

    def check_api_access(self, user: UserResponse) -> bool:
        """Check if user has API access."""
        plan_limits = self.get_user_plan_limits(user)
        return plan_limits["api_access"]

    def check_priority_support(self, user: UserResponse) -> bool:
        """Check if user has priority support."""
        plan_limits = self.get_user_plan_limits(user)
        return plan_limits["priority_support"]

    async def update_user_subscription(self, user_id: str, new_plan: str) -> bool:
        """Update user's subscription plan."""
        try:
            if new_plan not in self.plan_limits:
                logger.error(f"Invalid plan: {new_plan}")
                return False
            
            users_collection = MongoDB.get_collection("users")
            if users_collection:
                from bson import ObjectId
                result = await users_collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"usersubscription": new_plan}}
                )
                
                if result.modified_count > 0:
                    logger.info(f"Updated user {user_id} subscription to {new_plan}")
                    return True
                else:
                    logger.error(f"Failed to update user {user_id} subscription")
                    return False
            else:
                logger.error("Users collection not available")
                return False
                
        except Exception as e:
            logger.error(f"Error updating user subscription: {e}")
            return False

    def get_plan_features(self, plan: str) -> Dict[str, Any]:
        """Get features for a specific plan."""
        return self.plan_limits.get(plan, self.plan_limits["free"])

    def get_all_plans(self) -> Dict[str, Dict[str, Any]]:
        """Get all available plans with their features."""
        return self.plan_limits 