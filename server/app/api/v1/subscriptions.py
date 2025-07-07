from fastapi import APIRouter, Depends, HTTPException, status, Request
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
from ...services.mock_subscription_service import mock_subscription_service
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
        for plan_key, plan_details in SUBSCRIPTION_PLANS.items():
            plans.append({
                "plan_id": plan_details.plan_id,
                "name": plan_details.name,
                "price_monthly": plan_details.price_monthly,
                "price_yearly": plan_details.price_yearly,
                "features": plan_details.features.dict(),
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
    """Get current user's subscription."""
    try:
        from bson import ObjectId
        # Get user's subscription from database
        users_collection = MongoDB.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(current_user.id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get subscription details
        subscription_data = user.get("subscription", {})
        plan = subscription_data.get("plan", SubscriptionPlan.FREE)
        plan_details = SUBSCRIPTION_PLANS[plan]
        
        # Calculate usage
        usage = await calculate_user_usage(current_user.id)
        
        return SubscriptionResponse(
            id=str(user["_id"]),
            user_id=str(user["_id"]),
            plan=plan,
            billing_cycle=subscription_data.get("billing_cycle", BillingCycle.MONTHLY),
            status=subscription_data.get("status", PaymentStatus.ACTIVE),
            current_period_start=subscription_data.get("current_period_start", datetime.utcnow()),
            current_period_end=subscription_data.get("current_period_end", datetime.utcnow()),
            cancel_at_period_end=subscription_data.get("cancel_at_period_end", False),
            stripe_subscription_id=subscription_data.get("stripe_subscription_id"),
            features=plan_details.features,
            usage=usage
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching current subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription"
        )

@router.get("/current/dev", response_model=SubscriptionResponse)
async def get_current_subscription_dev():
    """Development mode: Get mock current subscription (no auth required)."""
    if not _is_development_mode():
        raise HTTPException(status_code=404, detail="Development endpoint not available in production")
    return SubscriptionResponse(
        id="dev_user_id",
        user_id="dev_user_id",
        plan=SubscriptionPlan.PROFESSIONAL,
        billing_cycle=BillingCycle.MONTHLY,
        status=PaymentStatus.ACTIVE,
        current_period_start=datetime.utcnow() - timedelta(days=10),
        current_period_end=datetime.utcnow() + timedelta(days=20),
        cancel_at_period_end=False,
        stripe_subscription_id=None,
        features=SubscriptionFeatures(
            email_limit=10000,
            sender_limit=10,
            template_limit=20
        ),
        usage={
            "emails_sent_this_month": 2500,
            "senders_used": 2,
            "templates_used": 5
        }
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
        
        # Check if we should use mock service (when Stripe keys are not configured)
        use_mock_service = not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY == "test_key"
        
        if use_mock_service:
            # Use mock subscription service
            subscription_result = await mock_subscription_service.create_mock_subscription(
                str(user["_id"]),
                subscription_data.plan,
                subscription_data.billing_cycle
            )
            
            if not subscription_result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create mock subscription: {subscription_result['error']}"
                )
            
            # Update user with subscription details
            update_data = {
                "subscription": {
                    "plan": subscription_data.plan,
                    "billing_cycle": subscription_data.billing_cycle,
                    "status": PaymentStatus.ACTIVE,
                    "stripe_customer_id": subscription_result["customer_id"],
                    "stripe_subscription_id": subscription_result["subscription_id"],
                    "current_period_start": subscription_result["current_period_start"],
                    "current_period_end": subscription_result["current_period_end"],
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
                current_period_start=subscription_result["current_period_start"],
                current_period_end=subscription_result["current_period_end"],
                cancel_at_period_end=False,
                stripe_subscription_id=subscription_result["subscription_id"],
                features=plan_details.features,
                usage=usage
            )
        else:
            # Use real Stripe service
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
        
        subscription = user.get("subscription", {})
        stripe_subscription_id = subscription.get("stripe_subscription_id")
        
        if not stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription to update"
            )
        
        # Update Stripe subscription if plan or billing cycle changed
        if subscription_data.plan or subscription_data.billing_cycle:
            current_plan = subscription.get("plan", SubscriptionPlan.FREE)
            current_billing_cycle = subscription.get("billing_cycle", BillingCycle.MONTHLY)
            
            new_plan = subscription_data.plan or current_plan
            new_billing_cycle = subscription_data.billing_cycle or current_billing_cycle
            
            update_result = await stripe_service.update_subscription(
                stripe_subscription_id,
                new_plan,
                new_billing_cycle
            )
            
            if not update_result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update subscription: {update_result['error']}"
                )
            
            # Update database
            update_data = {
                "subscription.plan": new_plan,
                "subscription.billing_cycle": new_billing_cycle,
                "subscription.current_period_start": update_result.get("current_period_start"),
                "subscription.current_period_end": update_result.get("current_period_end")
            }
            
            await users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": update_data}
            )
        
        # Handle cancellation
        if subscription_data.cancel_at_period_end is not None:
            cancel_result = await stripe_service.cancel_subscription(
                stripe_subscription_id,
                subscription_data.cancel_at_period_end
            )
            
            if not cancel_result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to cancel subscription: {cancel_result['error']}"
                )
            
            await users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"subscription.cancel_at_period_end": cancel_result["cancel_at_period_end"]}}
            )
        
        # Get updated user data
        updated_user = await users_collection.find_one({"_id": user["_id"]})
        updated_subscription = updated_user.get("subscription", {})
        plan_details = SUBSCRIPTION_PLANS[updated_subscription.get("plan", SubscriptionPlan.FREE)]
        usage = await calculate_user_usage(current_user.id)
        
        return SubscriptionResponse(
            id=str(updated_user["_id"]),
            user_id=str(updated_user["_id"]),
            plan=updated_subscription.get("plan", SubscriptionPlan.FREE),
            billing_cycle=updated_subscription.get("billing_cycle", BillingCycle.MONTHLY),
            status=updated_subscription.get("status", PaymentStatus.ACTIVE),
            current_period_start=updated_subscription.get("current_period_start", datetime.utcnow()),
            current_period_end=updated_subscription.get("current_period_end", datetime.utcnow()),
            cancel_at_period_end=updated_subscription.get("cancel_at_period_end", False),
            stripe_subscription_id=updated_subscription.get("stripe_subscription_id"),
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
    """Get user's usage statistics."""
    try:
        usage = await calculate_user_usage(current_user.id)
        return UsageStats(**usage)
    except Exception as e:
        logger.error(f"Error fetching usage stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch usage statistics"
        )

@router.get("/usage/dev", response_model=UsageStats)
async def get_usage_stats_dev():
    """Development mode: Get mock usage stats (no auth required)."""
    if not _is_development_mode():
        raise HTTPException(status_code=404, detail="Development endpoint not available in production")
    return UsageStats(
        emails_sent_this_month=2500,
        emails_sent_total=12000,
        senders_used=2,
        templates_created=5,
        campaigns_created=3
    )

@router.get("/billing", response_model=BillingInfo)
async def get_billing_info(current_user: UserResponse = Depends(get_current_user)):
    """Get user's billing information."""
    try:
        users_collection = MongoDB.get_collection("users")
        user = await users_collection.find_one({"_id": current_user.id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        subscription = user.get("subscription", {})
        stripe_subscription_id = subscription.get("stripe_subscription_id")
        
        if not stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        # Get subscription details from Stripe
        subscription_result = await stripe_service.get_subscription(stripe_subscription_id)
        
        if not subscription_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch billing information"
            )
        
        plan = subscription.get("plan", SubscriptionPlan.FREE)
        plan_details = SUBSCRIPTION_PLANS[plan]
        
        return BillingInfo(
            subscription_id=stripe_subscription_id,
            amount=plan_details.price_monthly if subscription.get("billing_cycle") == BillingCycle.MONTHLY else plan_details.price_yearly,
            currency="usd",
            next_billing_date=subscription_result["current_period_end"],
            payment_method=None  # You can add payment method retrieval here
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
    from ...core.config import settings
    return {"publishable_key": settings.STRIPE_PUBLISHABLE_KEY}

@router.get("/payment-method")
async def get_payment_method(current_user: UserResponse = Depends(get_current_user)):
    """Get user's current payment method."""
    try:
        from bson import ObjectId
        users_collection = MongoDB.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(current_user.id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        subscription = user.get("subscription", {})
        stripe_customer_id = subscription.get("stripe_customer_id")
        
        if not stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No payment method found"
            )
        
        # Get payment methods from Stripe
        payment_methods_result = await stripe_service.get_customer_payment_methods(stripe_customer_id)
        
        if not payment_methods_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch payment method"
            )
        
        payment_methods = payment_methods_result["payment_methods"]
        
        if not payment_methods:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No payment method found"
            )
        
        # Return the first payment method (default)
        payment_method = payment_methods[0]
        
        return {
            "id": payment_method.id,
            "type": payment_method.type,
            "card": {
                "brand": payment_method.card.brand,
                "last4": payment_method.card.last4,
                "exp_month": payment_method.card.exp_month,
                "exp_year": payment_method.card.exp_year
            } if payment_method.card else None,
            "billing_details": payment_method.billing_details
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payment method: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment method"
        )

async def calculate_user_usage(user_id: str) -> dict:
    """Calculate user's current usage statistics."""
    try:
        # Get campaigns collection
        campaigns_collection = MongoDB.get_collection("campaigns")
        
        # Calculate emails sent this month
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        this_month_campaigns = await campaigns_collection.find({
            "user_id": user_id,  # user_id is stored as string
            "created_at": {"$gte": month_start}
        }).to_list(length=None)
        
        emails_sent_this_month = sum(campaign.get("successful", 0) for campaign in this_month_campaigns)
        
        # Calculate total emails sent
        all_campaigns = await campaigns_collection.find({
            "user_id": user_id  # user_id is stored as string
        }).to_list(length=None)
        
        emails_sent_total = sum(campaign.get("successful", 0) for campaign in all_campaigns)
        
        # Get senders count
        senders_collection = MongoDB.get_collection("senders")
        senders_count = await senders_collection.count_documents({"user_id": user_id})  # user_id is stored as string
        
        # Get templates count
        templates_collection = MongoDB.get_collection("templates")
        templates_count = await templates_collection.count_documents({"user_id": user_id})  # user_id is stored as string
        
        # Get campaigns count
        campaigns_count = len(all_campaigns)
        
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