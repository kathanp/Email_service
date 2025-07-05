#!/usr/bin/env python3
"""
Stripe Products Setup Script
This script creates the necessary products and prices in Stripe for the subscription plans.
"""

import stripe
import os
from app.core.config import settings
from app.models.subscription import SUBSCRIPTION_PLANS, SubscriptionPlan, BillingCycle

# Set your Stripe secret key
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_products():
    """Create products and prices in Stripe for all subscription plans."""
    
    print("🚀 Setting up Stripe products and prices...")
    
    # Create products and prices for each plan
    for plan_key, plan_details in SUBSCRIPTION_PLANS.items():
        if plan_key == SubscriptionPlan.FREE:
            print(f"⏭️  Skipping FREE plan (no Stripe product needed)")
            continue
            
        print(f"\n📦 Creating product for {plan_details.name} plan...")
        
        try:
            # Create product
            product = stripe.Product.create(
                name=f"Email Bot - {plan_details.name}",
                description=f"Email Bot {plan_details.name} subscription plan",
                metadata={
                    "plan_id": plan_details.plan_id,
                    "email_limit": plan_details.features.email_limit,
                    "sender_limit": plan_details.features.sender_limit,
                    "template_limit": plan_details.features.template_limit
                }
            )
            
            print(f"✅ Created product: {product.name} (ID: {product.id})")
            
            # Create monthly price
            if plan_details.price_monthly > 0:
                monthly_price = stripe.Price.create(
                    product=product.id,
                    unit_amount=int(plan_details.price_monthly * 100),  # Convert to cents
                    currency="usd",
                    recurring={"interval": "month"},
                    metadata={
                        "plan_id": plan_details.plan_id,
                        "billing_cycle": "monthly"
                    }
                )
                print(f"✅ Created monthly price: ${plan_details.price_monthly}/month (ID: {monthly_price.id})")
            
            # Create yearly price
            if plan_details.price_yearly > 0:
                yearly_price = stripe.Price.create(
                    product=product.id,
                    unit_amount=int(plan_details.price_yearly * 100),  # Convert to cents
                    currency="usd",
                    recurring={"interval": "year"},
                    metadata={
                        "plan_id": plan_details.plan_id,
                        "billing_cycle": "yearly"
                    }
                )
                print(f"✅ Created yearly price: ${plan_details.price_yearly}/year (ID: {yearly_price.id})")
            
            # Update the subscription plan with Stripe price IDs
            print(f"📝 Update your config with these price IDs:")
            print(f"   Monthly: {monthly_price.id if plan_details.price_monthly > 0 else 'N/A'}")
            print(f"   Yearly: {yearly_price.id if plan_details.price_yearly > 0 else 'N/A'}")
            
        except Exception as e:
            print(f"❌ Error creating product for {plan_details.name}: {e}")
    
    print("\n🎉 Stripe products setup complete!")
    print("\n📋 Next steps:")
    print("1. Update your config.py with the price IDs above")
    print("2. Test the subscription flow with Stripe test cards")
    print("3. Set up webhooks for subscription events")

def list_existing_products():
    """List existing products in Stripe."""
    print("📋 Existing Stripe products:")
    
    try:
        products = stripe.Product.list(limit=10)
        for product in products.data:
            print(f"   - {product.name} (ID: {product.id})")
            
            # List prices for this product
            prices = stripe.Price.list(product=product.id)
            for price in prices.data:
                interval = price.recurring.interval if price.recurring else "one-time"
                amount = price.unit_amount / 100 if price.unit_amount else 0
                print(f"     Price: ${amount}/{interval} (ID: {price.id})")
                
    except Exception as e:
        print(f"❌ Error listing products: {e}")

if __name__ == "__main__":
    print("🔧 Stripe Products Setup Tool")
    print("=" * 40)
    
    # Check if Stripe key is set
    if settings.STRIPE_SECRET_KEY == "sk_test_your_stripe_secret_key_here":
        print("❌ Please update your Stripe secret key in config.py first!")
        print("   Get your keys from: https://dashboard.stripe.com/apikeys")
        exit(1)
    
    # List existing products
    list_existing_products()
    
    print("\n" + "=" * 40)
    
    # Ask user if they want to create new products
    response = input("Do you want to create new products? (y/n): ").lower().strip()
    
    if response == 'y':
        create_stripe_products()
    else:
        print("⏭️  Skipping product creation") 