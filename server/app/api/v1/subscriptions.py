from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import os

from ..deps import get_current_user
from ...models.user import UserResponse
from ...models.subscription import (
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse, 
    SubscriptionPlan, BillingCycle, PaymentStatus, UsageStats, BillingInfo,
    SUBSCRIPTION_PLANS, SubscriptionFeatures
)
from ...services.stripe_service import stripe_service
from ...core.config import settings
from ...db.mongodb import MongoDB

router = APIRouter()
logger = logging.getLogger(__name__)

def _is_development_mode():
    mongodb_url = os.getenv("MONGODB_URL", "")
    if not mongodb_url or "localhost" in mongodb_url or "127.0.0.1" in mongodb_url:
        return True
    try:
        database = MongoDB.get_database()
        if not database:
            return True
        database.command('ping')
        return False
    except Exception:
        return True

@router.get("/plans", response_model=List[dict])
async def get_subscription_plans():
    """Get available subscription plans."""
    try:
        plans = []
        for plan_id, plan_details in SUBSCRIPTION_PLANS.items():
            plans.append({
                "id": plan_id,
                "name": plan_details.name,
                "price_monthly": plan_details.price_monthly,
                "price_yearly": plan_details.price_yearly,
                "features": {
                    "email_limit": plan_details.features.email_limit,
                    "sender_limit": plan_details.features.sender_limit,
                    "template_limit": plan_details.features.template_limit,
                    "api_access": plan_details.features.api_access,
                    "priority_support": plan_details.features.priority_support,
                    "white_label": plan_details.features.white_label,
                    "custom_integrations": plan_details.features.custom_integrations
                },
                "stripe_price_id_monthly": plan_details.stripe_price_id_monthly,
                "stripe_price_id_yearly": plan_details.stripe_price_id_yearly
            })
        return plans
    except Exception as e:
        logger.error(f"Error fetching subscription plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription plans"
        )

@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(current_user: UserResponse = Depends(get_current_user)):
    """Get current subscription for the authenticated user."""
    try:
        from bson import ObjectId
        users_collection = MongoDB.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(current_user.id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check both subscription object and usersubscription field
        subscription_data = user.get("subscription", {})
        user_subscription = user.get("usersubscription", "free")
        
        # If no subscription object but has usersubscription field, use that
        if not subscription_data and user_subscription:
            plan = user_subscription
            plan_details = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS[SubscriptionPlan.FREE])
            usage = await calculate_user_usage(current_user.id)
            
            return SubscriptionResponse(
                id=current_user.id,
                user_id=current_user.id,
                plan=plan,
                billing_cycle=BillingCycle.MONTHLY,
                status=PaymentStatus.ACTIVE,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
                cancel_at_period_end=False,
                stripe_subscription_id=None,
                features=plan_details.features,
                usage=usage
            )
        
        if not subscription_data:
            # Return free plan for users without subscription
            plan_details = SUBSCRIPTION_PLANS[SubscriptionPlan.FREE]
            usage = await calculate_user_usage(current_user.id)
            
            return SubscriptionResponse(
                id=current_user.id,
                user_id=current_user.id,
                plan=SubscriptionPlan.FREE,
                billing_cycle=BillingCycle.MONTHLY,
                status=PaymentStatus.ACTIVE,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
                cancel_at_period_end=False,
                stripe_subscription_id=None,
                features=plan_details.features,
                usage=usage
            )
        
        # Get plan details
        plan = subscription_data.get("plan", SubscriptionPlan.FREE)
        plan_details = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS[SubscriptionPlan.FREE])
        usage = await calculate_user_usage(current_user.id)
        
        return SubscriptionResponse(
            id=current_user.id,
            user_id=current_user.id,
            plan=plan,
            billing_cycle=subscription_data.get("billing_cycle", BillingCycle.MONTHLY),
            status=subscription_data.get("status", PaymentStatus.ACTIVE),
            current_period_start=subscription_data.get("current_period_start", datetime.utcnow()),
            current_period_end=subscription_data.get("current_period_end", datetime.utcnow() + timedelta(days=30)),
            cancel_at_period_end=subscription_data.get("cancel_at_period_end", False),
            stripe_subscription_id=subscription_data.get("stripe_subscription_id"),
            features=plan_details.features,
            usage=usage
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription"
        )

@router.post("/create", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new subscription for the user."""
    try:
        from bson import ObjectId
        users_collection = MongoDB.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(current_user.id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user already has a subscription
        existing_subscription = user.get("subscription", {})
        if existing_subscription.get("stripe_subscription_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active subscription"
            )
        
        # Create or get Stripe customer
        customer_result = await stripe_service.create_customer(
            str(user["_id"]), 
            user["email"], 
            user.get("full_name")
        )
        
        if not customer_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create customer: {customer_result['error']}"
            )
        
        # Create Stripe subscription
        subscription_result = await stripe_service.create_subscription(
            customer_result["customer_id"],
            subscription_data.plan,
            subscription_data.billing_cycle,
            subscription_data.stripe_payment_method_id
        )
        
        if not subscription_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create subscription: {subscription_result['error']}"
            )
        
        # Update user with subscription details
        update_data = {
            "subscription": {
                "plan": subscription_data.plan,
                "billing_cycle": subscription_data.billing_cycle,
                "status": PaymentStatus.ACTIVE,
                "stripe_customer_id": customer_result["customer_id"],
                "stripe_subscription_id": subscription_result.get("subscription_id"),
                "current_period_start": subscription_result.get("current_period_start", datetime.utcnow()),
                "current_period_end": subscription_result.get("current_period_end", datetime.utcnow()),
                "cancel_at_period_end": False
            }
        }
        
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": update_data}
        )
        
        # Get updated user data
        updated_user = await users_collection.find_one({"_id": user["_id"]})
        plan_details = SUBSCRIPTION_PLANS[subscription_data.plan]
        usage = await calculate_user_usage(current_user.id)
        
        return SubscriptionResponse(
            id=str(updated_user["_id"]),
            user_id=str(updated_user["_id"]),
            plan=subscription_data.plan,
            billing_cycle=subscription_data.billing_cycle,
            status=PaymentStatus.ACTIVE,
            current_period_start=subscription_result.get("current_period_start", datetime.utcnow()),
            current_period_end=subscription_result.get("current_period_end", datetime.utcnow()),
            cancel_at_period_end=False,
            stripe_subscription_id=subscription_result.get("subscription_id"),
            features=plan_details.features,
            usage=usage
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )

@router.put("/update", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_data: SubscriptionUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update user's subscription."""
    try:
        users_collection = MongoDB.get_collection("users")
        user = await users_collection.find_one({"_id": current_user.id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        subscription_data_user = user.get("subscription", {})
        if not subscription_data_user.get("stripe_subscription_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription found"
            )
        
        # Update subscription in Stripe
        update_result = await stripe_service.update_subscription(
            subscription_data_user["stripe_subscription_id"],
            subscription_data
        )
        
        if not update_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update subscription: {update_result['error']}"
            )
        
        # Update user subscription data
        update_data = {}
        if subscription_data.plan:
            update_data["subscription.plan"] = subscription_data.plan
        if subscription_data.billing_cycle:
            update_data["subscription.billing_cycle"] = subscription_data.billing_cycle
        if subscription_data.cancel_at_period_end is not None:
            update_data["subscription.cancel_at_period_end"] = subscription_data.cancel_at_period_end
        
        if update_data:
            await users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": update_data}
            )
        
        # Get updated user data
        updated_user = await users_collection.find_one({"_id": user["_id"]})
        plan_details = SUBSCRIPTION_PLANS[subscription_data.plan or updated_user["subscription"]["plan"]]
        usage = await calculate_user_usage(current_user.id)
        
        return SubscriptionResponse(
            id=str(updated_user["_id"]),
            user_id=str(updated_user["_id"]),
            plan=subscription_data.plan or updated_user["subscription"]["plan"],
            billing_cycle=subscription_data.billing_cycle or updated_user["subscription"]["billing_cycle"],
            status=updated_user["subscription"]["status"],
            current_period_start=updated_user["subscription"]["current_period_start"],
            current_period_end=updated_user["subscription"]["current_period_end"],
            cancel_at_period_end=subscription_data.cancel_at_period_end or updated_user["subscription"]["cancel_at_period_end"],
            stripe_subscription_id=updated_user["subscription"]["stripe_subscription_id"],
            features=plan_details.features,
            usage=usage
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription"
        )

@router.get("/usage", response_model=UsageStats)
async def get_usage_stats(current_user: UserResponse = Depends(get_current_user)):
    """Get usage statistics for the current user."""
    try:
        usage = await calculate_user_usage(current_user.id)
        return UsageStats(**usage)
    except Exception as e:
        logger.error(f"Error fetching usage stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch usage statistics"
        )

@router.get("/billing", response_model=BillingInfo)
async def get_billing_info(current_user: UserResponse = Depends(get_current_user)):
    """Get billing information for the current user."""
    try:
        from bson import ObjectId
        users_collection = MongoDB.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(current_user.id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        subscription_data = user.get("subscription", {})
        
        if not subscription_data or not subscription_data.get("stripe_subscription_id"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        # Get billing info from Stripe
        billing_result = await stripe_service.get_billing_info(
            subscription_data["stripe_subscription_id"]
        )
        
        if not billing_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch billing info: {billing_result['error']}"
            )
        
        return BillingInfo(
            subscription_id=subscription_data["stripe_subscription_id"],
            amount=billing_result["amount"],
            currency=billing_result["currency"],
            next_billing_date=billing_result["next_billing_date"],
            payment_method=billing_result.get("payment_method")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching billing info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch billing information"
        )

@router.get("/stripe-key")
async def get_stripe_publishable_key():
    """Get Stripe publishable key for frontend."""
    return {"publishable_key": settings.STRIPE_PUBLISHABLE_KEY}

@router.get("/payment-method")
async def get_payment_method(current_user: UserResponse = Depends(get_current_user)):
    """Get user's payment method."""
    try:
        from bson import ObjectId
        users_collection = MongoDB.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(current_user.id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        subscription_data = user.get("subscription", {})
        
        if not subscription_data or not subscription_data.get("stripe_customer_id"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No payment method found"
            )
        
        # Get payment method from Stripe
        payment_method_result = await stripe_service.get_payment_method(
            subscription_data["stripe_customer_id"]
        )
        
        if not payment_method_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch payment method: {payment_method_result['error']}"
            )
        
        return payment_method_result["payment_method"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payment method: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment method"
        )

@router.post("/upgrade", response_model=dict)
async def upgrade_subscription(
    plan: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Upgrade user subscription after successful Stripe payment."""
    try:
        from ..services.subscription_service import SubscriptionService
        subscription_service = SubscriptionService()
        
        # Validate plan
        valid_plans = ["starter", "professional", "enterprise"]
        if plan not in valid_plans:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan. Must be one of: {', '.join(valid_plans)}"
            )
        
        # Update user subscription
        success = await subscription_service.update_user_subscription(current_user.id, plan)
        
        if success:
            return {
                "success": True,
                "message": f"Successfully upgraded to {plan} plan",
                "plan": plan
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update subscription"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error upgrading subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Subscription upgrade failed: {str(e)}"
        )

async def calculate_user_usage(user_id: str) -> dict:
    """Calculate user's current usage statistics."""
    try:
        # Get campaigns collection
        campaigns_collection = MongoDB.get_collection("campaigns")
        templates_collection = MongoDB.get_collection("templates")
        senders_collection = MongoDB.get_collection("senders")
        
        # Calculate emails sent this month
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        campaigns = await campaigns_collection.find({
            "user_id": user_id,
            "created_at": {"$gte": month_start}
        }).to_list(length=None)
        
        emails_sent_this_month = sum(campaign.get("successful", 0) for campaign in campaigns)
        emails_sent_total = sum(campaign.get("successful", 0) for campaign in await campaigns_collection.find({"user_id": user_id}).to_list(length=None))
        
        # Count templates
        templates_count = await templates_collection.count_documents({
            "user_id": user_id,
            "is_active": True
        })
        
        # Count senders
        senders_count = await senders_collection.count_documents({
            "user_id": user_id
        })
        
        # Count campaigns
        campaigns_count = await campaigns_collection.count_documents({
            "user_id": user_id
        })
        
        return {
            "emails_sent_this_month": emails_sent_this_month,
            "emails_sent_total": emails_sent_total,
            "senders_used": senders_count,
            "templates_created": templates_count,
            "campaigns_created": campaigns_count
        }
    except Exception as e:
        logger.error(f"Error calculating user usage: {e}")
        return {
            "emails_sent_this_month": 0,
            "emails_sent_total": 0,
            "senders_used": 0,
            "templates_created": 0,
            "campaigns_created": 0
        } 