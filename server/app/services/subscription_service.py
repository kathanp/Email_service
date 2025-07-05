from datetime import datetime
from typing import Dict, Optional
from app.models.subscription import SUBSCRIPTION_PLANS, SubscriptionPlan
from app.db.mongodb import MongoDB
import logging

logger = logging.getLogger(__name__)

class SubscriptionService:
    def __init__(self):
        self.users_collection = MongoDB.get_collection("users")
        self.campaigns_collection = MongoDB.get_collection("campaigns")
        self.senders_collection = MongoDB.get_collection("senders")
        self.templates_collection = MongoDB.get_collection("templates")

    async def get_user_plan(self, user_id: str) -> SubscriptionPlan:
        """Get user's current subscription plan."""
        try:
            user = await self.users_collection.find_one({"_id": user_id})
            if not user:
                return SubscriptionPlan.FREE
            
            subscription_data = user.get("subscription", {})
            return subscription_data.get("plan", SubscriptionPlan.FREE)
        except Exception as e:
            logger.error(f"Error getting user plan: {e}")
            return SubscriptionPlan.FREE

    async def get_plan_limits(self, user_id: str) -> Dict:
        """Get current plan limits for a user."""
        plan = await self.get_user_plan(user_id)
        plan_details = SUBSCRIPTION_PLANS[plan]
        return {
            "plan": plan,
            "email_limit": plan_details.features.email_limit,
            "sender_limit": plan_details.features.sender_limit,
            "template_limit": plan_details.features.template_limit,
            "api_access": plan_details.features.api_access,
            "priority_support": plan_details.features.priority_support,
            "white_label": plan_details.features.white_label,
            "custom_integrations": plan_details.features.custom_integrations
        }

    async def get_current_usage(self, user_id: str) -> Dict:
        """Get current usage for a user."""
        try:
            # Calculate emails sent this month
            now = datetime.utcnow()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            this_month_campaigns = await self.campaigns_collection.find({
                "user_id": user_id,
                "created_at": {"$gte": month_start}
            }).to_list(length=None)
            
            emails_sent_this_month = sum(campaign.get("successful", 0) for campaign in this_month_campaigns)
            
            # Count senders
            senders_count = await self.senders_collection.count_documents({"user_id": user_id})
            
            # Count templates
            templates_count = await self.templates_collection.count_documents({"user_id": user_id})
            
            return {
                "emails_sent_this_month": emails_sent_this_month,
                "senders_count": senders_count,
                "templates_count": templates_count
            }
        except Exception as e:
            logger.error(f"Error calculating usage: {e}")
            return {
                "emails_sent_this_month": 0,
                "senders_count": 0,
                "templates_count": 0
            }

    async def check_email_limit(self, user_id: str, emails_to_send: int) -> Dict:
        """Check if user can send the specified number of emails."""
        try:
            limits = await self.get_plan_limits(user_id)
            usage = await self.get_current_usage(user_id)
            
            if limits["email_limit"] == -1:  # Unlimited
                return {"allowed": True, "reason": "Unlimited plan"}
            
            total_after_send = usage["emails_sent_this_month"] + emails_to_send
            
            if total_after_send <= limits["email_limit"]:
                return {
                    "allowed": True,
                    "reason": "Within limit",
                    "current_usage": usage["emails_sent_this_month"],
                    "limit": limits["email_limit"],
                    "remaining": limits["email_limit"] - usage["emails_sent_this_month"]
                }
            else:
                return {
                    "allowed": False,
                    "reason": f"Would exceed monthly limit of {limits['email_limit']} emails",
                    "current_usage": usage["emails_sent_this_month"],
                    "limit": limits["email_limit"],
                    "attempted": emails_to_send,
                    "would_exceed_by": total_after_send - limits["email_limit"]
                }
        except Exception as e:
            logger.error(f"Error checking email limit: {e}")
            return {"allowed": False, "reason": "Error checking limits"}

    async def check_sender_limit(self, user_id: str) -> Dict:
        """Check if user can add another sender."""
        try:
            limits = await self.get_plan_limits(user_id)
            usage = await self.get_current_usage(user_id)
            
            if limits["sender_limit"] == -1:  # Unlimited
                return {"allowed": True, "reason": "Unlimited plan"}
            
            if usage["senders_count"] < limits["sender_limit"]:
                return {
                    "allowed": True,
                    "reason": "Within limit",
                    "current_count": usage["senders_count"],
                    "limit": limits["sender_limit"],
                    "remaining": limits["sender_limit"] - usage["senders_count"]
                }
            else:
                return {
                    "allowed": False,
                    "reason": f"Maximum {limits['sender_limit']} sender(s) allowed",
                    "current_count": usage["senders_count"],
                    "limit": limits["sender_limit"]
                }
        except Exception as e:
            logger.error(f"Error checking sender limit: {e}")
            return {"allowed": False, "reason": "Error checking limits"}

    async def check_template_limit(self, user_id: str) -> Dict:
        """Check if user can create another template."""
        try:
            limits = await self.get_plan_limits(user_id)
            usage = await self.get_current_usage(user_id)
            
            if limits["template_limit"] == -1:  # Unlimited
                return {"allowed": True, "reason": "Unlimited plan"}
            
            if usage["templates_count"] < limits["template_limit"]:
                return {
                    "allowed": True,
                    "reason": "Within limit",
                    "current_count": usage["templates_count"],
                    "limit": limits["template_limit"],
                    "remaining": limits["template_limit"] - usage["templates_count"]
                }
            else:
                return {
                    "allowed": False,
                    "reason": f"Maximum {limits['template_limit']} template(s) allowed",
                    "current_count": usage["templates_count"],
                    "limit": limits["template_limit"]
                }
        except Exception as e:
            logger.error(f"Error checking template limit: {e}")
            return {"allowed": False, "reason": "Error checking limits"}

    async def get_upgrade_message(self, user_id: str, feature: str) -> str:
        """Get upgrade message for when limits are exceeded."""
        try:
            limits = await self.get_plan_limits(user_id)
            usage = await self.get_current_usage(user_id)
            
            if feature == "emails":
                return f"You've used {usage['emails_sent_this_month']}/{limits['email_limit']} emails this month. Upgrade to send more emails."
            elif feature == "senders":
                return f"You have {usage['senders_count']}/{limits['sender_limit']} sender(s). Upgrade to add more sender emails."
            elif feature == "templates":
                return f"You have {usage['templates_count']}/{limits['template_limit']} template(s). Upgrade to create more templates."
            else:
                return "Upgrade your plan to access this feature."
        except Exception as e:
            logger.error(f"Error getting upgrade message: {e}")
            return "Upgrade your plan to access this feature." 