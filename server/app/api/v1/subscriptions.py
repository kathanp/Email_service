from fastapi import APIRouter, Depends, HTTPException, Request
from app.api.deps import get_current_user
from app.services.subscription_service import SubscriptionService
from app.services.payment_method_service import PaymentMethodService
from app.models.subscription import SubscriptionResponse, UsageStats
from app.models.payment_method import PaymentMethodResponse
import stripe
import os
import logging
from datetime import datetime

router = APIRouter(tags=["subscriptions"])
logger = logging.getLogger(__name__)

# Initialize Stripe with proper key handling
stripe_api_key = os.getenv('STRIPE_SECRET_KEY', '')
if not stripe_api_key:
    logger.warning("STRIPE_SECRET_KEY environment variable not set")
else:
    # Clean up the key in case it has line breaks
    stripe_api_key = stripe_api_key.replace('\n', '').replace('\r', '').strip()
    stripe.api_key = stripe_api_key

# Stripe webhook secret
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(current_user = Depends(get_current_user)):
    """Get current user subscription."""
    subscription_service = SubscriptionService()
    subscription_data = await subscription_service.get_current_subscription(current_user.id)
    
    # Get plan features from the available plans
    plans = await subscription_service.get_available_plans()
    current_plan_id = subscription_data.get("plan", "free")
    current_plan = next((p for p in plans if p["id"] == current_plan_id), None)
    
    # Return a properly formatted response that matches the SubscriptionResponse model
    response = SubscriptionResponse(
        id=subscription_data.get("user_id", "unknown"),
        user_id=subscription_data.get("user_id", "unknown"),
        plan_id=current_plan_id,
        status="paid",  # Changed from "active" to "paid" to match PaymentStatus enum
        billing_cycle="monthly",
        stripe_subscription_id=subscription_data.get("stripe_subscription_id"),
        stripe_customer_id=subscription_data.get("stripe_customer_id"),
        created_at=subscription_data.get("created_at", datetime.utcnow()),
        updated_at=subscription_data.get("updated_at", datetime.utcnow()),
        current_period_start=subscription_data.get("current_period_start"),
        current_period_end=subscription_data.get("current_period_end"),
        cancel_at_period_end=subscription_data.get("cancel_at_period_end", False)
    )
    
    # Add plan features to the response (this will be added as extra fields)
    if current_plan:
        response.plan = current_plan_id
        response.features = current_plan["features"]
    
    return response

@router.get("/usage")
async def get_usage_stats(current_user = Depends(get_current_user)):
    """Get usage statistics."""
    subscription_service = SubscriptionService()
    usage_data = await subscription_service.get_usage_stats(current_user.id)
    
    # Create the response with both new and legacy field names for compatibility
    response = {
        "user_id": current_user.id,
        "emails_sent": usage_data.get("emails_sent_total", 0),
        "emails_remaining": usage_data.get("remaining", 0),
        "total_emails_allowed": usage_data.get("limit", 100),
        "templates_used": usage_data.get("templates_created", 0),
        "templates_remaining": usage_data.get("templates_remaining", 3),
        "total_templates_allowed": usage_data.get("templates_limit", 3),
        "sender_emails_used": usage_data.get("senders_used", 0),
        "sender_emails_remaining": usage_data.get("sender_remaining", 1),
        "total_sender_emails_allowed": usage_data.get("sender_limit", 1),
        "current_plan": usage_data.get("current_plan", "free"),
        "usage_percentage": 0.0,
        # Legacy field names for frontend compatibility
        "emails_sent_this_month": usage_data.get("emails_sent_this_billing_period", 0),
        "senders_used": usage_data.get("senders_used", 0),  # This is the key field the frontend needs!
        "templates_created": usage_data.get("templates_created", 0)
    }
    
    return response

@router.get("/plans")
async def get_available_plans():
    """Get available subscription plans."""
    subscription_service = SubscriptionService()
    return await subscription_service.get_available_plans()

@router.post("/create-payment-intent")
async def create_payment_intent(
    request: dict,
    current_user = Depends(get_current_user)
):
    """Create a Stripe payment intent for subscription."""
    try:
        plan_id = request.get("plan")
        billing_cycle = request.get("billing_cycle", "monthly")
        
        if not plan_id:
            raise HTTPException(status_code=400, detail="Plan ID is required")
        
        # Get plan details
        subscription_service = SubscriptionService()
        plans = await subscription_service.get_available_plans()
        
        plan = next((p for p in plans if p["id"] == plan_id), None)
        if not plan:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        # Calculate amount based on billing cycle
        amount = plan["price_monthly"] if billing_cycle == "monthly" else plan["price_yearly"]
        amount_cents = int(amount * 100)  # Convert to cents
        
        # Handle free plan - no payment intent needed
        if plan_id == "free" or amount_cents == 0:
            return {
                "client_secret": None,
                "amount": 0,
                "currency": "usd",
                "is_free_plan": True,
                "plan_id": plan_id,
                "billing_cycle": billing_cycle
            }
        
        # Check minimum charge amount (50 cents for USD)
        if amount_cents < 50:
            raise HTTPException(
                status_code=400, 
                detail=f"Amount ${amount} is below minimum charge amount. Minimum is $0.50 USD."
            )
        
        # Create payment intent with automatic payment methods
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            automatic_payment_methods={
                "enabled": True,
            },
            metadata={
                "user_id": current_user.id,
                "plan_id": plan_id,
                "billing_cycle": billing_cycle
            }
        )
        
        return {
            "client_secret": payment_intent.client_secret,
            "amount": amount_cents,
            "currency": "usd",
            "is_free_plan": False,
            "plan_id": plan_id,
            "billing_cycle": billing_cycle
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/change-plan")
async def change_plan(
    request: dict,
    current_user = Depends(get_current_user)
):
    """Change subscription plan (upgrade/downgrade) without payment for free plans."""
    try:
        new_plan_id = request.get("plan_id")
        billing_cycle = request.get("billing_cycle", "monthly")
        
        if not new_plan_id:
            raise HTTPException(status_code=400, detail="Plan ID is required")
        
        # Get current subscription
        subscription_service = SubscriptionService()
        current_subscription = await subscription_service.get_current_subscription(current_user.id)
        current_plan_id = current_subscription.get("plan_id", "free")
        
        # Get plan details
        plans = await subscription_service.get_available_plans()
        new_plan = next((p for p in plans if p["id"] == new_plan_id), None)
        current_plan = next((p for p in plans if p["id"] == current_plan_id), None)
        
        if not new_plan:
            raise HTTPException(status_code=400, detail="Invalid new plan")
        
        # Handle different scenarios
        if new_plan_id == "free":
            # Downgrade to free - no payment needed
            result = await subscription_service.update_user_subscription(current_user.id, new_plan_id)
            if result["success"]:
                # Get updated subscription and usage stats
                updated_subscription = await subscription_service.get_current_subscription(current_user.id)
                updated_usage = await subscription_service.get_usage_stats(current_user.id)
                
                return {
                    "success": True,
                    "message": f"Successfully downgraded to {new_plan['name']} plan",
                    "plan_id": new_plan_id,
                    "requires_payment": False,
                    "subscription": updated_subscription,
                    "usage_stats": updated_usage
                }
            else:
                if result.get("blocked"):
                    raise HTTPException(
                        status_code=400, 
                        detail={
                            "error": "Downgrade blocked",
                            "reason": result["error"],
                            "violations": result.get("violations", []),
                            "blocked": True
                        }
                    )
                else:
                    raise HTTPException(status_code=500, detail=result["error"])
        
        elif current_plan_id == "free":
            # Upgrade from free - requires payment
            return {
                "success": False,
                "message": "Upgrade from free plan requires payment",
                "requires_payment": True,
                "plan_id": new_plan_id,
                "billing_cycle": billing_cycle,
                "amount": new_plan["price_monthly"] if billing_cycle == "monthly" else new_plan["price_yearly"]
            }
        
        else:
            # Plan change between paid plans - handle through Stripe
            return {
                "success": False,
                "message": "Plan changes between paid plans require payment processing",
                "requires_payment": True,
                "plan_id": new_plan_id,
                "billing_cycle": billing_cycle,
                "amount": new_plan["price_monthly"] if billing_cycle == "monthly" else new_plan["price_yearly"]
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plan-change-preview/{plan_id}")
async def get_plan_change_preview(
    plan_id: str,
    current_user = Depends(get_current_user)
):
    """Get a preview of what would happen with a plan change."""
    try:
        subscription_service = SubscriptionService()
        preview = await subscription_service.get_plan_change_preview(current_user.id, plan_id)
        
        if "error" in preview:
            raise HTTPException(status_code=400, detail=preview["error"])
        
        return preview
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscription-history")
async def get_subscription_history(
    current_user = Depends(get_current_user),
    limit: int = 10
):
    """Get subscription change history for the user."""
    try:
        from ..db.mongodb import MongoDB
        subscription_logs_collection = MongoDB.get_collection("subscription_logs")
        
        if not subscription_logs_collection:
            return {"history": []}
        
        # Get subscription history for the user
        history = await subscription_logs_collection.find(
            {"user_id": current_user.id}
        ).sort("timestamp", -1).limit(limit).to_list(None)
        
        # Format the history
        formatted_history = []
        for entry in history:
            formatted_history.append({
                "id": str(entry["_id"]),
                "old_plan": entry["old_plan"],
                "new_plan": entry["new_plan"],
                "change_type": entry["change_type"],
                "timestamp": entry["timestamp"],
                "source": entry.get("source", "unknown")
            })
        
        return {"history": formatted_history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reactivate-items")
async def reactivate_deactivated_items(
    request: dict,
    current_user = Depends(get_current_user)
):
    """Reactivate items that were deactivated due to plan downgrades."""
    try:
        item_type = request.get("item_type")  # "senders" or "templates"
        item_ids = request.get("item_ids", [])
        
        if not item_type or not item_ids:
            raise HTTPException(status_code=400, detail="Item type and IDs are required")
        
        subscription_service = SubscriptionService()
        
        # Check current plan limits
        current_subscription = await subscription_service.get_current_subscription(current_user.id)
        current_plan = current_subscription.get("plan_id", "free")
        plan_limits = subscription_service.get_plan_features(current_plan)
        
        from ..db.mongodb import MongoDB
        from bson import ObjectId
        
        reactivated_count = 0
        
        if item_type == "senders":
            # Check sender limit
            current_usage = await subscription_service.get_usage_stats(current_user.id)
            sender_limit = plan_limits.get("sender_emails", 1)
            
            if sender_limit != -1 and current_usage["senders_used"] >= sender_limit:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cannot reactivate senders. You've reached your limit of {sender_limit} senders."
                )
            
            senders_collection = MongoDB.get_collection("senders")
            if senders_collection:
                for item_id in item_ids:
                    # Check if sender belongs to user and was deactivated due to plan downgrade
                    sender = await senders_collection.find_one({
                        "_id": ObjectId(item_id),
                        "user_id": current_user.id,
                        "is_active": False,
                        "deactivated_reason": "plan_downgrade"
                    })
                    
                    if sender:
                        # Check if we still have room
                        if sender_limit == -1 or current_usage["senders_used"] < sender_limit:
                            await senders_collection.update_one(
                                {"_id": ObjectId(item_id)},
                                {"$set": {"is_active": True}, "$unset": {"deactivated_reason": ""}}
                            )
                            reactivated_count += 1
                            current_usage["senders_used"] += 1
        
        elif item_type == "templates":
            # Check template limit
            current_usage = await subscription_service.get_usage_stats(current_user.id)
            template_limit = plan_limits.get("templates", 3)
            
            if template_limit != -1 and current_usage["templates_created"] >= template_limit:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cannot reactivate templates. You've reached your limit of {template_limit} templates."
                )
            
            templates_collection = MongoDB.get_collection("templates")
            if templates_collection:
                for item_id in item_ids:
                    # Check if template belongs to user and was deactivated due to plan downgrade
                    template = await templates_collection.find_one({
                        "_id": ObjectId(item_id),
                        "user_id": current_user.id,
                        "is_active": False,
                        "deactivated_reason": "plan_downgrade"
                    })
                    
                    if template:
                        # Check if we still have room
                        if template_limit == -1 or current_usage["templates_created"] < template_limit:
                            await templates_collection.update_one(
                                {"_id": ObjectId(item_id)},
                                {"$set": {"is_active": True}, "$unset": {"deactivated_reason": ""}}
                            )
                            reactivated_count += 1
                            current_usage["templates_created"] += 1
        
        return {
            "success": True,
            "message": f"Reactivated {reactivated_count} {item_type}",
            "reactivated_count": reactivated_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deactivated-items")
async def get_deactivated_items(
    current_user = Depends(get_current_user)
):
    """Get items that were deactivated due to plan downgrades."""
    try:
        from ..db.mongodb import MongoDB
        
        deactivated_items = {
            "senders": [],
            "templates": []
        }
        
        # Get deactivated senders
        senders_collection = MongoDB.get_collection("senders")
        if senders_collection:
            deactivated_senders = await senders_collection.find({
                "user_id": current_user.id,
                "is_active": False,
                "deactivated_reason": "plan_downgrade"
            }).to_list(None)
            
            for sender in deactivated_senders:
                deactivated_items["senders"].append({
                    "id": str(sender["_id"]),
                    "email": sender["email"],
                    "display_name": sender.get("display_name", ""),
                    "deactivated_at": sender.get("updated_at")
                })
        
        # Get deactivated templates
        templates_collection = MongoDB.get_collection("templates")
        if templates_collection:
            deactivated_templates = await templates_collection.find({
                "user_id": current_user.id,
                "is_active": False,
                "deactivated_reason": "plan_downgrade"
            }).to_list(None)
            
            for template in deactivated_templates:
                deactivated_items["templates"].append({
                    "id": str(template["_id"]),
                    "name": template["name"],
                    "subject": template.get("subject", ""),
                    "deactivated_at": template.get("updated_at")
                })
        
        return deactivated_items
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm-payment")
async def confirm_payment(
    request: dict,
    current_user = Depends(get_current_user)
):
    """Confirm payment and update user subscription."""
    try:
        payment_intent_id = request.get("payment_intent_id")
        plan_id = request.get("plan_id")
        billing_cycle = request.get("billing_cycle", "monthly")
        is_free_plan = request.get("is_free_plan", False)
        
        if not plan_id:
            raise HTTPException(status_code=400, detail="Plan ID is required")
        
        # Handle free plan without payment verification
        if is_free_plan or plan_id == "free":
            subscription_service = SubscriptionService()
            result = await subscription_service.update_user_subscription(current_user.id, plan_id)
            
            if not result["success"]:
                if result.get("blocked"):
                    raise HTTPException(
                        status_code=400, 
                        detail={
                            "error": "Downgrade blocked",
                            "reason": result["error"],
                            "violations": result.get("violations", []),
                            "blocked": True
                        }
                    )
                else:
                    raise HTTPException(status_code=500, detail=result["error"])
            
            updated_subscription = await subscription_service.get_current_subscription(current_user.id)
            
            return {
                "success": True,
                "message": f"Successfully changed to {plan_id} plan",
                "subscription": updated_subscription,
                "is_free_plan": True
            }
        
        # Handle paid plans - verify payment
        if not payment_intent_id:
            raise HTTPException(status_code=400, detail="Payment intent ID is required for paid plans")
        
        # Verify payment intent with Stripe
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if payment_intent.status != "succeeded":
                raise HTTPException(status_code=400, detail="Payment not successful")
                
            # Store payment method if available
            if payment_intent.payment_method:
                payment_method_service = PaymentMethodService()
                customer_id = payment_intent.customer
                if customer_id:
                    await payment_method_service.store_payment_method(
                        current_user.id, 
                        payment_intent.payment_method, 
                        customer_id
                    )
                    
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
        
        # Update user subscription
        subscription_service = SubscriptionService()
        result = await subscription_service.update_user_subscription(current_user.id, plan_id)
        
        if not result["success"]:
            if result.get("blocked"):
                raise HTTPException(
                    status_code=400, 
                    detail={
                        "error": "Downgrade blocked",
                        "reason": result["error"],
                        "violations": result.get("violations", []),
                        "blocked": True
                    }
                )
            else:
                raise HTTPException(status_code=500, detail=result["error"])
        
        # Get updated subscription data
        updated_subscription = await subscription_service.get_current_subscription(current_user.id)
        
        return {
            "success": True,
            "message": "Subscription updated successfully",
            "subscription": updated_subscription,
            "is_free_plan": False,
            "payment_intent_id": payment_intent_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        if not STRIPE_WEBHOOK_SECRET:
            logger.warning("Stripe webhook secret not configured")
            return {"status": "webhook secret not configured"}
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            logger.info(f"Payment succeeded: {payment_intent['id']}")
            
            # Extract metadata
            user_id = payment_intent['metadata'].get('user_id')
            plan_id = payment_intent['metadata'].get('plan_id')
            
            if user_id and plan_id:
                # Update user subscription
                subscription_service = SubscriptionService()
                await subscription_service.update_user_subscription(user_id, plan_id)
                logger.info(f"Updated subscription for user {user_id} to plan {plan_id}")
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            logger.warning(f"Payment failed: {payment_intent['id']}")
        
        else:
            logger.info(f"Unhandled event type: {event['type']}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/create")
async def create_subscription(current_user = Depends(get_current_user)):
    """Create a new subscription."""
    subscription_service = SubscriptionService()
    return await subscription_service.create_subscription(current_user.id) 

@router.post("/migrate-billing-cycles")
async def migrate_billing_cycles(current_user = Depends(get_current_user)):
    """Migrate existing users to use billing cycles (admin only)."""
    # Simple admin check - you can enhance this based on your admin system
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        subscription_service = SubscriptionService()
        await subscription_service.migrate_existing_users_billing_cycles()
        return {"success": True, "message": "Billing cycle migration completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@router.get("/payment-methods")
async def get_payment_methods(current_user = Depends(get_current_user)):
    """Get all payment methods for the current user."""
    try:
        payment_method_service = PaymentMethodService()
        payment_methods = await payment_method_service.get_user_payment_methods(current_user.id)
        return {"payment_methods": payment_methods}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment-methods/default")
async def get_default_payment_method(current_user = Depends(get_current_user)):
    """Get the default payment method for the current user."""
    try:
        payment_method_service = PaymentMethodService()
        default_method = await payment_method_service.get_default_payment_method(current_user.id)
        return {"default_payment_method": default_method}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payment-methods/{payment_method_id}/set-default")
async def set_default_payment_method(
    payment_method_id: str,
    current_user = Depends(get_current_user)
):
    """Set a payment method as the default."""
    try:
        payment_method_service = PaymentMethodService()
        result = await payment_method_service.set_default_payment_method(current_user.id, payment_method_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/payment-methods/{payment_method_id}")
async def delete_payment_method(
    payment_method_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a payment method."""
    try:
        payment_method_service = PaymentMethodService()
        result = await payment_method_service.delete_payment_method(current_user.id, payment_method_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-payment-methods")
async def sync_payment_methods(current_user = Depends(get_current_user)):
    """Sync payment methods from Stripe."""
    try:
        # Get current subscription to find Stripe customer ID
        subscription_service = SubscriptionService()
        subscription = await subscription_service.get_current_subscription(current_user.id)
        
        stripe_customer_id = subscription.get("stripe_customer_id")
        if not stripe_customer_id:
            return {"success": False, "message": "No Stripe customer found"}
        
        payment_method_service = PaymentMethodService()
        result = await payment_method_service.sync_stripe_payment_methods(current_user.id, stripe_customer_id)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 