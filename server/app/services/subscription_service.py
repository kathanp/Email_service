from typing import Dict, Any, Optional
from ..db.mongodb import MongoDB
from ..models.user import UserResponse
import logging
from datetime import datetime, timedelta

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

    async def get_user_billing_period(self, user_id: str) -> Dict[str, Any]:
        """Get the current billing period for a user based on their subscription history."""
        try:
            # Check if user has a billing cycle record
            billing_cycles_collection = MongoDB.get_collection("billing_cycles")
            if billing_cycles_collection is not None:
                # Get the most recent billing cycle for the user
                billing_cycle = await billing_cycles_collection.find_one(
                    {"user_id": user_id},
                    sort=[("period_start", -1)]
                )
                
                if billing_cycle:
                    period_start = billing_cycle["period_start"]
                    period_end = billing_cycle["period_end"]
                    
                    # Check if current billing period is still active
                    now = datetime.utcnow()
                    if now <= period_end:
                        return {
                            "period_start": period_start,
                            "period_end": period_end,
                            "billing_cycle": billing_cycle.get("billing_cycle", "monthly"),
                            "plan_id": billing_cycle.get("plan_id", "free")
                        }
            
            # If no billing cycle found or expired, use user account creation date
            users_collection = MongoDB.get_collection("users")
            if users_collection is not None:
                from bson import ObjectId
                user = await users_collection.find_one({"_id": ObjectId(user_id)})
                
                if user:
                    # Use account creation date as the base for billing cycle
                    account_created = user.get("created_at", datetime.utcnow())
                    current_plan = user.get("usersubscription", "free")
                    
                    # Calculate current billing period based on account creation date
                    now = datetime.utcnow()
                    
                    # For monthly billing, find the current month cycle
                    # Start from account creation and add months until we reach current period
                    period_start = account_created.replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    # Find the current billing period
                    while period_start + timedelta(days=30) < now:
                        period_start = period_start + timedelta(days=30)
                    
                    period_end = period_start + timedelta(days=30)
                    
                    # Create billing cycle record for future use
                    await self._create_billing_cycle_record(user_id, current_plan, "monthly", period_start, period_end)
                    
                    return {
                        "period_start": period_start,
                        "period_end": period_end,
                        "billing_cycle": "monthly",
                        "plan_id": current_plan
                    }
            
            # Fallback to current month if all else fails
            now = datetime.utcnow()
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                period_end = period_start.replace(year=now.year + 1, month=1)
            else:
                period_end = period_start.replace(month=now.month + 1)
            
            return {
                "period_start": period_start,
                "period_end": period_end,
                "billing_cycle": "monthly",
                "plan_id": "free"
            }
            
        except Exception as e:
            logger.error(f"Error getting user billing period: {e}")
            # Fallback to current month
            now = datetime.utcnow()
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                period_end = period_start.replace(year=now.year + 1, month=1)
            else:
                period_end = period_start.replace(month=now.month + 1)
            
            return {
                "period_start": period_start,
                "period_end": period_end,
                "billing_cycle": "monthly",
                "plan_id": "free"
            }

    async def _create_billing_cycle_record(self, user_id: str, plan_id: str, billing_cycle: str, period_start: datetime, period_end: datetime):
        """Create a billing cycle record for tracking user's billing periods."""
        try:
            billing_cycles_collection = MongoDB.get_collection("billing_cycles")
            if billing_cycles_collection is not None:
                billing_record = {
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "billing_cycle": billing_cycle,
                    "period_start": period_start,
                    "period_end": period_end,
                    "created_at": datetime.utcnow()
                }
                
                await billing_cycles_collection.insert_one(billing_record)
                logger.info(f"Created billing cycle record for user {user_id}: {period_start} to {period_end}")
                
        except Exception as e:
            logger.error(f"Error creating billing cycle record: {e}")

    async def _create_new_billing_cycle(self, user_id: str, new_plan: str, billing_cycle: str = "monthly"):
        """Create a new billing cycle when user changes plans."""
        try:
            # Start new billing cycle immediately
            now = datetime.utcnow()
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Calculate period end based on billing cycle
            if billing_cycle == "yearly":
                period_end = period_start + timedelta(days=365)
            else:  # monthly
                period_end = period_start + timedelta(days=30)
            
            # Create the billing cycle record
            await self._create_billing_cycle_record(user_id, new_plan, billing_cycle, period_start, period_end)
            
            logger.info(f"Created new billing cycle for user {user_id} with plan {new_plan}: {period_start} to {period_end}")
            
        except Exception as e:
            logger.error(f"Error creating new billing cycle: {e}")

    async def migrate_existing_users_billing_cycles(self):
        """Migration method to initialize billing cycles for existing users."""
        try:
            logger.info("Starting billing cycle migration for existing users...")
            
            users_collection = MongoDB.get_collection("users")
            billing_cycles_collection = MongoDB.get_collection("billing_cycles")
            
            if users_collection is None or billing_cycles_collection is None:
                logger.error("Required collections not available for migration")
                return
            
            # Get all users
            users = await users_collection.find({}).to_list(None)
            migrated_count = 0
            
            for user in users:
                user_id = str(user["_id"])
                
                # Check if user already has a billing cycle record
                existing_billing_cycle = await billing_cycles_collection.find_one({"user_id": user_id})
                
                if not existing_billing_cycle:
                    # Create initial billing cycle based on account creation date
                    account_created = user.get("created_at", datetime.utcnow())
                    current_plan = user.get("usersubscription", "free")
                    
                    # Calculate current billing period based on account creation date
                    now = datetime.utcnow()
                    period_start = account_created.replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    # Find the current billing period
                    while period_start + timedelta(days=30) < now:
                        period_start = period_start + timedelta(days=30)
                    
                    period_end = period_start + timedelta(days=30)
                    
                    # Create billing cycle record
                    await self._create_billing_cycle_record(user_id, current_plan, "monthly", period_start, period_end)
                    migrated_count += 1
                    
                    logger.info(f"Migrated user {user_id} with billing cycle {period_start} to {period_end}")
            
            logger.info(f"Billing cycle migration completed. Migrated {migrated_count} users.")
            
        except Exception as e:
            logger.error(f"Error during billing cycle migration: {e}")

    def get_user_plan_limits(self, user: UserResponse) -> Dict[str, Any]:
        """Get the limits for a user's current plan."""
        plan = user.usersubscription or "free"
        return self.plan_limits.get(plan, self.plan_limits["free"])

    async def check_email_limit(self, user: UserResponse) -> Dict[str, Any]:
        """Check if user can send more emails in their current billing period."""
        try:
            plan_limits = self.get_user_plan_limits(user)
            emails_per_month = plan_limits["emails_per_month"]
            
            if emails_per_month == -1:  # Unlimited
                return {"can_send": True, "remaining": -1, "limit": -1}
            
            # Get user's current billing period
            billing_period = await self.get_user_billing_period(user.id)
            period_start = billing_period["period_start"]
            period_end = billing_period["period_end"]
            
            email_logs_collection = MongoDB.get_collection("email_logs")
            if email_logs_collection is not None:
                # Count emails sent in current billing period
                sent_count = await email_logs_collection.count_documents({
                    "user_id": user.id,
                    "sent_at": {
                        "$gte": period_start,
                        "$lt": period_end
                    },
                    "status": "sent"
                })
                
                remaining = max(0, emails_per_month - sent_count)
                can_send = remaining > 0
                
                logger.info(f"User {user.id} email limit check: {sent_count}/{emails_per_month} used in billing period {period_start} to {period_end}")
                
                return {
                    "can_send": can_send,
                    "remaining": remaining,
                    "limit": emails_per_month,
                    "used": sent_count,
                    "billing_period_start": period_start,
                    "billing_period_end": period_end
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
            if senders_collection is not None:
                # Use user.id as string (don't convert to ObjectId since it's stored as string)
                current_count = await senders_collection.count_documents({
                    "user_id": user.id,  # user.id is already a string
                    "verification_status": {"$ne": "deleted"}  # Count all non-deleted senders
                })
                
                remaining = max(0, sender_emails_limit - current_count)
                can_add = remaining > 0
                
                logger.info(f"User {user.id} sender limit check: {current_count}/{sender_emails_limit} used, can_add: {can_add}")
                
                return {
                    "can_add": can_add,
                    "remaining": remaining,
                    "limit": sender_emails_limit,
                    "current": current_count
                }
            else:
                # If collection not available, assume can add
                logger.warning("Senders collection not available, allowing sender addition")
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
            if templates_collection is not None:
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

    async def update_user_subscription(self, user_id: str, new_plan: str) -> Dict[str, Any]:
        """Update user's subscription plan."""
        try:
            if new_plan not in self.plan_limits:
                logger.error(f"Invalid plan: {new_plan}")
                return {
                    "success": False,
                    "error": "Invalid plan selected",
                    "blocked": False
                }
            
            # Get current subscription and usage before updating
            current_subscription = await self.get_current_subscription(user_id)
            current_plan = current_subscription.get("plan_id", "free")
            
            # Check if this is a downgrade and handle limit violations
            if await self._is_downgrade(current_plan, new_plan):
                downgrade_result = await self._handle_downgrade_limits(user_id, current_plan, new_plan)
                if not downgrade_result["allowed"]:
                    logger.warning(f"Downgrade blocked for user {user_id}: {downgrade_result['reason']}")
                    return {
                        "success": False,
                        "error": downgrade_result["reason"],
                        "blocked": True,
                        "violations": downgrade_result["violations"]
                    }
            
            users_collection = MongoDB.get_collection("users")
            if users_collection is not None:
                from bson import ObjectId
                result = await users_collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"usersubscription": new_plan}}
                )
                
                if result.modified_count > 0:
                    logger.info(f"Updated user {user_id} subscription from {current_plan} to {new_plan}")
                    
                    # Create new billing cycle record for the new plan
                    await self._create_new_billing_cycle(user_id, new_plan)
                    
                    # Log the subscription change
                    await self._log_subscription_change(user_id, current_plan, new_plan)
                    
                    # Send notification about plan change
                    await self._notify_plan_change(user_id, current_plan, new_plan)
                    
                    return {
                        "success": True,
                        "message": f"Successfully updated subscription from {current_plan} to {new_plan}",
                        "blocked": False
                    }
                else:
                    logger.error(f"Failed to update user {user_id} subscription")
                    return {
                        "success": False,
                        "error": "Failed to update subscription in database",
                        "blocked": False
                    }
            else:
                logger.error("Users collection not available")
                return {
                    "success": False,
                    "error": "Database not available",
                    "blocked": False
                }
                
        except Exception as e:
            logger.error(f"Error updating user subscription: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "blocked": False
            }

    async def _is_downgrade(self, current_plan: str, new_plan: str) -> bool:
        """Check if the plan change is a downgrade."""
        plan_hierarchy = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
        current_tier = plan_hierarchy.get(current_plan, 0)
        new_tier = plan_hierarchy.get(new_plan, 0)
        return new_tier < current_tier

    async def _handle_downgrade_limits(self, user_id: str, current_plan: str, new_plan: str) -> Dict[str, Any]:
        """Handle downgrade limit violations by blocking downgrades that exceed limits."""
        try:
            new_limits = self.plan_limits.get(new_plan, self.plan_limits["free"])
            current_usage = await self.get_usage_stats(user_id)
            
            violations = []
            warnings = []
            
            # Check email limit (monthly)
            if new_limits["emails_per_month"] != -1:
                if current_usage["emails_sent_this_month"] > new_limits["emails_per_month"]:
                    violations.append(f"You have sent {current_usage['emails_sent_this_month']} emails this month, which exceeds the {new_plan} plan limit of {new_limits['emails_per_month']} emails/month")
            
            # Check sender emails limit
            if new_limits["sender_emails"] != -1:
                if current_usage["senders_used"] > new_limits["sender_emails"]:
                    violations.append(f"You have {current_usage['senders_used']} sender emails, which exceeds the {new_plan} plan limit of {new_limits['sender_emails']} senders")
            
            # Check templates limit
            if new_limits["templates"] != -1:
                if current_usage["templates_created"] > new_limits["templates"]:
                    violations.append(f"You have {current_usage['templates_created']} templates, which exceeds the {new_plan} plan limit of {new_limits['templates']} templates")
            
            # If there are violations, BLOCK the downgrade
            if violations:
                logger.warning(f"Downgrade BLOCKED for user {user_id}: {violations}")
                
                # Create helpful message for the user
                violation_message = "Cannot downgrade because your current usage exceeds the target plan limits:\n\n" + "\n".join(f"• {v}" for v in violations)
                violation_message += f"\n\nTo downgrade to {new_plan}, please reduce your usage first or consider a higher tier plan."
                
                return {
                    "allowed": False,  # BLOCK the downgrade
                    "violations": violations,
                    "warnings": warnings,
                    "reason": violation_message,
                    "blocked": True
                }
            
            return {
                "allowed": True,
                "violations": [],
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"Error handling downgrade limits: {e}")
            return {
                "allowed": False,  # Block downgrade on error for safety
                "violations": [],
                "warnings": [f"Could not verify limits: {str(e)}"],
                "reason": "Unable to verify your current usage. Please try again later or contact support.",
                "blocked": True
            }

    async def _auto_handle_violations(self, user_id: str, new_limits: Dict, current_usage: Dict):
        """Automatically handle some limit violations during downgrade."""
        try:
            # Handle sender emails limit violation
            if new_limits["sender_emails"] != -1 and current_usage["senders_used"] > new_limits["sender_emails"]:
                await self._deactivate_excess_senders(user_id, new_limits["sender_emails"])
            
            # Handle templates limit violation
            if new_limits["templates"] != -1 and current_usage["templates_created"] > new_limits["templates"]:
                await self._deactivate_excess_templates(user_id, new_limits["templates"])
            
            logger.info(f"Auto-handled limit violations for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error auto-handling violations: {e}")

    async def _deactivate_excess_senders(self, user_id: str, max_senders: int):
        """Deactivate excess sender emails when downgrading."""
        try:
            senders_collection = MongoDB.get_collection("senders")
            if senders_collection is not None:
                # Get all active senders for the user, ordered by creation date (keep newest)
                senders = await senders_collection.find({
                    "user_id": user_id,
                    "is_active": True
                }).sort("created_at", -1).to_list(None)
                
                if len(senders) > max_senders:
                    # Deactivate excess senders (oldest ones)
                    excess_senders = senders[max_senders:]
                    for sender in excess_senders:
                        await senders_collection.update_one(
                            {"_id": sender["_id"]},
                            {"$set": {"is_active": False, "deactivated_reason": "plan_downgrade"}}
                        )
                    
                    logger.info(f"Deactivated {len(excess_senders)} excess senders for user {user_id}")
                    
        except Exception as e:
            logger.error(f"Error deactivating excess senders: {e}")

    async def _deactivate_excess_templates(self, user_id: str, max_templates: int):
        """Deactivate excess templates when downgrading."""
        try:
            templates_collection = MongoDB.get_collection("templates")
            if templates_collection is not None:
                # Get all active templates for the user, ordered by creation date (keep newest)
                templates = await templates_collection.find({
                    "user_id": user_id,
                    "is_active": True
                }).sort("created_at", -1).to_list(None)
                
                if len(templates) > max_templates:
                    # Deactivate excess templates (oldest ones)
                    excess_templates = templates[max_templates:]
                    for template in excess_templates:
                        await templates_collection.update_one(
                            {"_id": template["_id"]},
                            {"$set": {"is_active": False, "deactivated_reason": "plan_downgrade"}}
                        )
                    
                    logger.info(f"Deactivated {len(excess_templates)} excess templates for user {user_id}")
                    
        except Exception as e:
            logger.error(f"Error deactivating excess templates: {e}")

    async def _log_subscription_change(self, user_id: str, old_plan: str, new_plan: str):
        """Log subscription changes for audit purposes."""
        try:
            subscription_logs_collection = MongoDB.get_collection("subscription_logs")
            if subscription_logs_collection is not None:
                log_entry = {
                    "user_id": user_id,
                    "old_plan": old_plan,
                    "new_plan": new_plan,
                    "change_type": "upgrade" if await self._is_upgrade(old_plan, new_plan) else "downgrade",
                    "timestamp": datetime.utcnow(),
                    "source": "user_initiated"
                }
                
                await subscription_logs_collection.insert_one(log_entry)
                logger.info(f"Logged subscription change for user {user_id}: {old_plan} → {new_plan}")
                
        except Exception as e:
            logger.error(f"Error logging subscription change: {e}")

    async def _is_upgrade(self, current_plan: str, new_plan: str) -> bool:
        """Check if the plan change is an upgrade."""
        plan_hierarchy = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
        current_tier = plan_hierarchy.get(current_plan, 0)
        new_tier = plan_hierarchy.get(new_plan, 0)
        return new_tier > current_tier

    async def _notify_plan_change(self, user_id: str, old_plan: str, new_plan: str):
        """Send notification about plan change."""
        try:
            # Get user email
            users_collection = MongoDB.get_collection("users")
            if users_collection is not None:
                from bson import ObjectId
                user = await users_collection.find_one({"_id": ObjectId(user_id)})
                
                if user:
                    user_email = user.get("email")
                    change_type = "upgraded" if await self._is_upgrade(old_plan, new_plan) else "downgraded"
                    
                    # Here you would integrate with your email service
                    # For now, just log the notification
                    logger.info(f"Notification: User {user_email} {change_type} from {old_plan} to {new_plan}")
                    
                    # You can add actual email sending logic here
                    # await self._send_plan_change_email(user_email, old_plan, new_plan, change_type)
                    
        except Exception as e:
            logger.error(f"Error sending plan change notification: {e}")

    async def get_plan_change_preview(self, user_id: str, new_plan: str) -> Dict[str, Any]:
        """Get a preview of what would happen with a plan change."""
        try:
            current_subscription = await self.get_current_subscription(user_id)
            current_plan = current_subscription.get("plan_id", "free")
            
            if current_plan == new_plan:
                return {
                    "is_same_plan": True,
                    "message": "You are already on this plan"
                }
            
            new_limits = self.plan_limits.get(new_plan, self.plan_limits["free"])
            current_usage = await self.get_usage_stats(user_id)
            
            is_upgrade = await self._is_upgrade(current_plan, new_plan)
            is_downgrade = await self._is_downgrade(current_plan, new_plan)
            
            preview = {
                "current_plan": current_plan,
                "new_plan": new_plan,
                "is_upgrade": is_upgrade,
                "is_downgrade": is_downgrade,
                "current_usage": current_usage,
                "new_limits": new_limits,
                "changes": [],
                "warnings": [],
                "benefits": [],
                "blocked": False,
                "block_reason": None
            }
            
            # Check if downgrade would be blocked
            if is_downgrade:
                downgrade_result = await self._handle_downgrade_limits(user_id, current_plan, new_plan)
                if not downgrade_result["allowed"]:
                    preview["blocked"] = True
                    preview["block_reason"] = downgrade_result["reason"]
                    preview["violations"] = downgrade_result["violations"]
                    return preview
            
            # Compare limits and highlight changes
            current_limits = self.plan_limits.get(current_plan, self.plan_limits["free"])
            
            # Email limits
            if new_limits["emails_per_month"] != current_limits["emails_per_month"]:
                if new_limits["emails_per_month"] == -1:
                    preview["benefits"].append("Unlimited monthly emails")
                elif current_limits["emails_per_month"] == -1:
                    preview["changes"].append(f"Monthly emails: Unlimited → {new_limits['emails_per_month']:,}")
                else:
                    change = new_limits["emails_per_month"] - current_limits["emails_per_month"]
                    if change > 0:
                        preview["benefits"].append(f"Monthly emails: {current_limits['emails_per_month']:,} → {new_limits['emails_per_month']:,} (+{change:,})")
                    else:
                        preview["changes"].append(f"Monthly emails: {current_limits['emails_per_month']:,} → {new_limits['emails_per_month']:,} ({change:,})")
                        if current_usage["emails_sent_this_month"] > new_limits["emails_per_month"]:
                            preview["warnings"].append(f"You've already sent {current_usage['emails_sent_this_month']} emails this month, which exceeds the new limit of {new_limits['emails_per_month']}")
            
            # Sender emails
            if new_limits["sender_emails"] != current_limits["sender_emails"]:
                if new_limits["sender_emails"] == -1:
                    preview["benefits"].append("Unlimited sender emails")
                elif current_limits["sender_emails"] == -1:
                    preview["changes"].append(f"Sender emails: Unlimited → {new_limits['sender_emails']}")
                else:
                    change = new_limits["sender_emails"] - current_limits["sender_emails"]
                    if change > 0:
                        preview["benefits"].append(f"Sender emails: {current_limits['sender_emails']} → {new_limits['sender_emails']} (+{change})")
                    else:
                        preview["changes"].append(f"Sender emails: {current_limits['sender_emails']} → {new_limits['sender_emails']} ({change})")
                        if current_usage["senders_used"] > new_limits["sender_emails"]:
                            excess = current_usage["senders_used"] - new_limits["sender_emails"]
                            preview["warnings"].append(f"You have {current_usage['senders_used']} sender emails, but the new plan allows only {new_limits['sender_emails']}. {excess} will be deactivated.")
            
            # Templates
            if new_limits["templates"] != current_limits["templates"]:
                if new_limits["templates"] == -1:
                    preview["benefits"].append("Unlimited templates")
                elif current_limits["templates"] == -1:
                    preview["changes"].append(f"Templates: Unlimited → {new_limits['templates']}")
                else:
                    change = new_limits["templates"] - current_limits["templates"]
                    if change > 0:
                        preview["benefits"].append(f"Templates: {current_limits['templates']} → {new_limits['templates']} (+{change})")
                    else:
                        preview["changes"].append(f"Templates: {current_limits['templates']} → {new_limits['templates']} ({change})")
                        if current_usage["templates_created"] > new_limits["templates"]:
                            excess = current_usage["templates_created"] - new_limits["templates"]
                            preview["warnings"].append(f"You have {current_usage['templates_created']} templates, but the new plan allows only {new_limits['templates']}. {excess} will be deactivated.")
            
            # Feature changes
            feature_changes = []
            if new_limits["api_access"] != current_limits["api_access"]:
                if new_limits["api_access"]:
                    preview["benefits"].append("API access enabled")
                else:
                    preview["changes"].append("API access will be disabled")
            
            if new_limits["priority_support"] != current_limits["priority_support"]:
                if new_limits["priority_support"]:
                    preview["benefits"].append("Priority support enabled")
                else:
                    preview["changes"].append("Priority support will be disabled")
            
            return preview
            
        except Exception as e:
            logger.error(f"Error getting plan change preview: {e}")
            return {
                "error": f"Could not generate preview: {str(e)}"
            }

    def get_plan_features(self, plan: str) -> Dict[str, Any]:
        """Get features for a specific plan."""
        return self.plan_limits.get(plan, self.plan_limits["free"])

    def get_all_plans(self) -> Dict[str, Dict[str, Any]]:
        """Get all available plans with their features."""
        return self.plan_limits

    async def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get usage statistics for the current billing period."""
        try:
            # Get billing period
            billing_period = await self.get_user_billing_period(user_id)
            period_start = billing_period["period_start"]
            period_end = billing_period["period_end"]
            
            # Get usage collections
            email_logs_collection = MongoDB.get_collection("email_logs")
            if email_logs_collection is not None:
                # Count emails sent in current period
                emails_sent = await email_logs_collection.count_documents({
                    "user_id": user_id,
                    "sent_at": {
                        "$gte": period_start,
                        "$lt": period_end
                    },
                    "status": "sent"
                })
            else:
                emails_sent = 0
            
            # Get templates collection
            templates_collection = MongoDB.get_collection("templates")
            if templates_collection is not None:
                templates_created = await templates_collection.count_documents({
                    "user_id": user_id,
                    "created_at": {
                        "$gte": period_start,
                        "$lt": period_end
                    }
                })
            else:
                templates_created = 0
            
            # Get files collection  
            files_collection = MongoDB.get_collection("files")
            if files_collection is not None:
                files_uploaded = await files_collection.count_documents({
                    "user_id": user_id,
                    "created_at": {
                        "$gte": period_start,
                        "$lt": period_end
                    }
                })
            else:
                files_uploaded = 0
            
            # Get campaigns collection
            campaigns_collection = MongoDB.get_collection("campaigns")
            if campaigns_collection is not None:
                campaigns_created = await campaigns_collection.count_documents({
                    "user_id": user_id
                })
            else:
                campaigns_created = 0
            
            # Get actual senders count from senders collection
            senders_collection = MongoDB.get_collection("senders")
            if senders_collection is not None:
                senders_used = await senders_collection.count_documents({
                    "user_id": user_id,
                    "verification_status": {"$ne": "deleted"}  # Count all non-deleted senders
                })
            else:
                senders_used = 0
            
            # Calculate remaining limits
            email_limit = self.plan_limits.get(billing_period["plan_id"], self.plan_limits["free"])["emails_per_month"]
            sender_limit = self.plan_limits.get(billing_period["plan_id"], self.plan_limits["free"])["sender_emails"]
            template_limit = self.plan_limits.get(billing_period["plan_id"], self.plan_limits["free"])["templates"]
            
            emails_remaining = max(0, email_limit - emails_sent) if email_limit != -1 else -1
            senders_remaining = max(0, sender_limit - senders_used) if sender_limit != -1 else -1
            templates_remaining = max(0, template_limit - templates_created) if template_limit != -1 else -1
            
            return {
                "emails_sent_total": emails_sent,
                "emails_sent_this_month": emails_sent, # Keep same key for compatibility
                "emails_sent_this_billing_period": emails_sent,
                "senders_used": senders_used,
                "templates_created": templates_created,
                "campaigns_created": campaigns_created,
                "files_uploaded": files_uploaded,  # Keep files count separate
                "current_plan": billing_period["plan_id"],
                "limit": email_limit,
                "remaining": emails_remaining,
                "sender_limit": sender_limit,
                "sender_remaining": senders_remaining,
                "templates_limit": template_limit,
                "templates_remaining": templates_remaining,
                "billing_period_start": period_start,
                "billing_period_end": period_end
            }
            
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {
                "emails_sent_total": 0,
                "emails_sent_this_month": 0,  # Keep for compatibility
                "emails_sent_this_billing_period": 0,
                "senders_used": 0,
                "templates_created": 0,
                "campaigns_created": 0,
                "current_plan": "free",
                "limit": 100,
                "remaining": 100,
                "sender_limit": 1,
                "sender_remaining": 1,
                "templates_limit": 3,
                "templates_remaining": 3,
                "billing_period_start": datetime.utcnow(),
                "billing_period_end": datetime.utcnow() + timedelta(days=30)
            }

    async def get_available_plans(self):
        """Async method to get all available plans for API endpoint."""
        plans = [
            {
                "id": "free",
                "name": "Free",
                "price_monthly": 0,
                "price_yearly": 0,
                "features": {
                    "email_limit": 100,
                    "sender_limit": 1,
                    "template_limit": 3,
                    "api_access": False,
                    "priority_support": False,
                    "white_label": False,
                    "custom_integrations": False
                }
            },
            {
                "id": "starter",
                "name": "Starter",
                "price_monthly": 4.99,
                "price_yearly": 49.99,
                "features": {
                    "email_limit": 1000,
                    "sender_limit": 3,
                    "template_limit": 10,
                    "api_access": False,
                    "priority_support": False,
                    "white_label": False,
                    "custom_integrations": False
                }
            },
            {
                "id": "professional",
                "name": "Professional",
                "price_monthly": 14.99,
                "price_yearly": 149.99,
                "features": {
                    "email_limit": 10000,
                    "sender_limit": 10,
                    "template_limit": 50,
                    "api_access": True,
                    "priority_support": True,
                    "white_label": False,
                    "custom_integrations": False
                }
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price_monthly": 25.99,
                "price_yearly": 259.99,
                "features": {
                    "email_limit": 50000,
                    "sender_limit": -1,  # Unlimited
                    "template_limit": -1,  # Unlimited
                    "api_access": True,
                    "priority_support": True,
                    "white_label": True,
                    "custom_integrations": True
                }
            }
        ]
        return plans

    async def get_current_subscription(self, user_id: str) -> Dict[str, Any]:
        """Get the current subscription for a user."""
        try:
            users_collection = MongoDB.get_collection("users")
            if users_collection is not None:
                from bson import ObjectId
                user = await users_collection.find_one({"_id": ObjectId(user_id)})
                
                if user:
                    current_plan = user.get("usersubscription", "free")
                    plan_limits = self.plan_limits.get(current_plan, self.plan_limits["free"])
                    
                    # Get billing period information
                    billing_period = await self.get_user_billing_period(user_id)
                    
                    return {
                        "id": str(user.get("_id", "unknown")),
                        "user_id": user_id,
                        "plan_id": current_plan,
                        "plan": current_plan,
                        "status": "active",
                        "billing_cycle": billing_period.get("billing_cycle", "monthly"),
                        "limits": plan_limits,
                        "stripe_subscription_id": None,
                        "stripe_customer_id": None,
                        "created_at": user.get("created_at", datetime.utcnow()),
                        "updated_at": datetime.utcnow(),
                        "current_period_start": billing_period.get("period_start"),
                        "current_period_end": billing_period.get("period_end"),
                        "cancel_at_period_end": False
                    }
                else:
                    return {
                        "id": "unknown",
                        "user_id": user_id,
                        "plan_id": "free",
                        "plan": "free",
                        "status": "active",
                        "billing_cycle": "monthly",
                        "limits": self.plan_limits["free"],
                        "stripe_subscription_id": None,
                        "stripe_customer_id": None,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "current_period_start": None,
                        "current_period_end": None,
                        "cancel_at_period_end": False
                    }
            else:
                logger.error("Users collection not available")
                return {
                    "id": "unknown",
                    "user_id": user_id,
                    "plan_id": "free",
                    "plan": "free",
                    "status": "active",
                    "billing_cycle": "monthly",
                    "limits": self.plan_limits["free"],
                    "stripe_subscription_id": None,
                    "stripe_customer_id": None,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "current_period_start": None,
                    "current_period_end": None,
                    "cancel_at_period_end": False
                }
                
        except Exception as e:
            logger.error(f"Error getting current subscription: {e}")
            return {
                "id": "error",
                "user_id": user_id,
                "plan_id": "free",
                "plan": "free", 
                "status": "unknown",
                "billing_cycle": "monthly",
                "limits": self.plan_limits["free"],
                "stripe_subscription_id": None,
                "stripe_customer_id": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "current_period_start": datetime.utcnow(),
                "current_period_end": datetime.utcnow() + timedelta(days=30),
                "cancel_at_period_end": False
            }

    async def get_upgrade_message(self, user_id: str, resource_type: str) -> str:
        """Get upgrade message for specific resource type."""
        try:
            current_subscription = await self.get_current_subscription(user_id)
            current_plan = current_subscription.get("plan", "free")
            
            # Define upgrade paths
            upgrade_paths = {
                "free": "starter",
                "starter": "professional", 
                "professional": "enterprise",
                "enterprise": "enterprise"  # Already at highest tier
            }
            
            next_plan = upgrade_paths.get(current_plan, "starter")
            
            # Resource-specific messages
            messages = {
                "emails": f"Upgrade to {next_plan.title()} plan for more monthly email quota.",
                "senders": f"Upgrade to {next_plan.title()} plan to add more sender emails.",
                "templates": f"Upgrade to {next_plan.title()} plan to create more templates."
            }
            
            base_message = messages.get(resource_type, "Upgrade your plan for higher limits.")
            
            if current_plan == "enterprise":
                return "You're already on our highest tier! Contact support if you need custom limits."
            
            return f"{base_message} Visit the Pricing page to upgrade now."
            
        except Exception as e:
            logger.error(f"Error getting upgrade message: {e}")
            return "Please upgrade your plan for higher limits. Visit the Pricing page for more details."

    async def create_subscription(self, user_id: str) -> Dict[str, Any]:
        """Create a new subscription record for a user."""
        try:
            users_collection = MongoDB.get_collection("users") 
            if users_collection is not None:
                from bson import ObjectId
                user = await users_collection.find_one({"_id": ObjectId(user_id)})
                
                if user:
                    # Set default plan to free if not specified
                    current_plan = user.get("usersubscription", "free")
                    
                    # Update user with subscription if not set
                    if not user.get("usersubscription"):
                        await users_collection.update_one(
                            {"_id": ObjectId(user_id)},
                            {"$set": {"usersubscription": "free"}}
                        )
                    
                    # Create billing cycle
                    await self._create_new_billing_cycle(user_id, current_plan)
                    
                    return {
                        "success": True,
                        "plan": current_plan,
                        "message": f"Subscription initialized with {current_plan} plan"
                    }
                else:
                    return {
                        "success": False,
                        "error": "User not found"
                    }
            else:
                return {
                    "success": False,
                    "error": "Database not available"
                }
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            } 