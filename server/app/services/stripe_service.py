import stripe
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.subscription import SubscriptionPlan, BillingCycle, PaymentStatus, SUBSCRIPTION_PLANS

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    def __init__(self):
        self.stripe = stripe
        
    async def create_customer(self, user_id: str, email: str, name: str = None) -> Dict:
        """Create a Stripe customer for a user."""
        try:
            customer = self.stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    "user_id": user_id
                }
            )
            
            logger.info(f"Created Stripe customer {customer.id} for user {user_id}")
            return {
                "success": True,
                "customer_id": customer.id,
                "customer": customer
            }
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def attach_payment_method(self, payment_method_id: str, customer_id: str) -> Dict:
        """Attach a payment method to a customer."""
        try:
            payment_method = self.stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            
            logger.info(f"Attached payment method {payment_method_id} to customer {customer_id}")
            return {
                "success": True,
                "payment_method": payment_method
            }
        except Exception as e:
            logger.error(f"Error attaching payment method: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def create_subscription(self, customer_id: str, plan: SubscriptionPlan, 
                                billing_cycle: BillingCycle, payment_method_id: str = None) -> Dict:
        """Create a subscription for a customer."""
        try:
            plan_details = SUBSCRIPTION_PLANS[plan]
            
            # Get the appropriate price ID
            if billing_cycle == BillingCycle.MONTHLY:
                price_id = plan_details.stripe_price_id_monthly
            else:
                price_id = plan_details.stripe_price_id_yearly
            
            # If free plan, return success without creating Stripe subscription
            if plan == SubscriptionPlan.FREE:
                return {
                    "success": True,
                    "subscription_id": None,
                    "plan": plan,
                    "billing_cycle": billing_cycle,
                    "features": plan_details.features
                }
            
            # Attach payment method to customer if provided
            if payment_method_id:
                attach_result = await self.attach_payment_method(payment_method_id, customer_id)
                if not attach_result["success"]:
                    return {
                        "success": False,
                        "error": f"Failed to attach payment method: {attach_result['error']}"
                    }
            
            # Create subscription parameters
            subscription_params = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "metadata": {
                    "plan": plan,
                    "billing_cycle": billing_cycle
                }
            }
            
            # Add payment method if provided
            if payment_method_id:
                subscription_params["default_payment_method"] = payment_method_id
            
            # Create the subscription
            subscription = self.stripe.Subscription.create(**subscription_params)
            
            logger.info(f"Created subscription {subscription.id} for customer {customer_id}")
            
            # Get current period dates with fallback
            try:
                current_period_start = datetime.fromtimestamp(subscription.current_period_start)
            except (AttributeError, TypeError):
                current_period_start = datetime.utcnow()
                
            try:
                current_period_end = datetime.fromtimestamp(subscription.current_period_end)
            except (AttributeError, TypeError):
                # Set end date to 30 days from now for monthly, 365 for yearly
                if billing_cycle == BillingCycle.MONTHLY:
                    current_period_end = current_period_start + timedelta(days=30)
                else:
                    current_period_end = current_period_start + timedelta(days=365)
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "plan": plan,
                "billing_cycle": billing_cycle,
                "features": plan_details.features,
                "current_period_start": current_period_start,
                "current_period_end": current_period_end,
                "status": subscription.status
            }
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_subscription(self, subscription_id: str, plan: SubscriptionPlan, 
                                billing_cycle: BillingCycle) -> Dict:
        """Update an existing subscription."""
        try:
            plan_details = SUBSCRIPTION_PLANS[plan]
            
            # Get the appropriate price ID
            if billing_cycle == BillingCycle.MONTHLY:
                price_id = plan_details.stripe_price_id_monthly
            else:
                price_id = plan_details.stripe_price_id_yearly
            
            # Update the subscription
            subscription = self.stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription.items.data[0].id,
                    "price": price_id
                }],
                metadata={
                    "plan": plan,
                    "billing_cycle": billing_cycle
                }
            )
            
            logger.info(f"Updated subscription {subscription_id}")
            return {
                "success": True,
                "subscription_id": subscription.id,
                "plan": plan,
                "billing_cycle": billing_cycle,
                "features": plan_details.features,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "status": subscription.status
            }
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_subscription(self, subscription_id: str, cancel_at_period_end: bool = True) -> Dict:
        """Cancel a subscription."""
        try:
            if cancel_at_period_end:
                subscription = self.stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = self.stripe.Subscription.cancel(subscription_id)
            
            logger.info(f"Cancelled subscription {subscription_id}")
            return {
                "success": True,
                "subscription_id": subscription.id,
                "status": subscription.status,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_subscription(self, subscription_id: str) -> Dict:
        """Get subscription details."""
        try:
            subscription = self.stripe.Subscription.retrieve(subscription_id)
            
            return {
                "success": True,
                "subscription": subscription,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        except Exception as e:
            logger.error(f"Error retrieving subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_payment_intent(self, amount: int, currency: str = "usd", 
                                  customer_id: str = None) -> Dict:
        """Create a payment intent for one-time payments."""
        try:
            payment_intent = self.stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                automatic_payment_methods={"enabled": True}
            )
            
            return {
                "success": True,
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret
            }
        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_customer_payment_methods(self, customer_id: str) -> Dict:
        """Get payment methods for a customer."""
        try:
            payment_methods = self.stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            
            return {
                "success": True,
                "payment_methods": payment_methods.data
            }
        except Exception as e:
            logger.error(f"Error getting payment methods: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_setup_intent(self, customer_id: str) -> Dict:
        """Create a setup intent for adding payment methods."""
        try:
            setup_intent = self.stripe.SetupIntent.create(
                customer=customer_id,
                payment_method_types=["card"]
            )
            
            return {
                "success": True,
                "setup_intent_id": setup_intent.id,
                "client_secret": setup_intent.client_secret
            }
        except Exception as e:
            logger.error(f"Error creating setup intent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_invoices(self, customer_id: str, limit: int = 10) -> Dict:
        """Get invoices for a customer."""
        try:
            invoices = self.stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
            
            return {
                "success": True,
                "invoices": invoices.data
            }
        except Exception as e:
            logger.error(f"Error getting invoices: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Create global instance
stripe_service = StripeService() 