from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SubscriptionPlan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class PaymentStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    TRIAL = "trial"

class SubscriptionFeatures(BaseModel):
    email_limit: int
    sender_limit: int
    template_limit: int
    api_access: bool = False
    priority_support: bool = False
    white_label: bool = False
    custom_integrations: bool = False

class SubscriptionPlanDetails(BaseModel):
    plan_id: str
    name: str
    price_monthly: float
    price_yearly: float
    features: SubscriptionFeatures
    stripe_price_id_monthly: str
    stripe_price_id_yearly: str

class SubscriptionCreate(BaseModel):
    plan: SubscriptionPlan
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    stripe_payment_method_id: Optional[str] = None

class SubscriptionUpdate(BaseModel):
    plan: Optional[SubscriptionPlan] = None
    billing_cycle: Optional[BillingCycle] = None
    cancel_at_period_end: Optional[bool] = None

class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    plan: SubscriptionPlan
    billing_cycle: BillingCycle
    status: PaymentStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    stripe_subscription_id: Optional[str] = None
    features: SubscriptionFeatures
    usage: dict

class UsageStats(BaseModel):
    emails_sent_this_month: int
    emails_sent_total: int
    senders_used: int
    templates_created: int
    campaigns_created: int

class BillingInfo(BaseModel):
    subscription_id: str
    amount: float
    currency: str = "usd"
    next_billing_date: datetime
    payment_method: Optional[dict] = None

# Subscription plan configurations
SUBSCRIPTION_PLANS = {
    SubscriptionPlan.FREE: SubscriptionPlanDetails(
        plan_id="free",
        name="Free",
        price_monthly=0.0,
        price_yearly=0.0,
        features=SubscriptionFeatures(
            email_limit=100,
            sender_limit=1,
            template_limit=3,
            api_access=False,
            priority_support=False,
            white_label=False,
            custom_integrations=False
        ),
        stripe_price_id_monthly="",
        stripe_price_id_yearly=""
    ),
    SubscriptionPlan.STARTER: SubscriptionPlanDetails(
        plan_id="starter",
        name="Starter",
        price_monthly=4.99,
        price_yearly=49.99,  # 2 months free would be 49.99 if you want
        features=SubscriptionFeatures(
            email_limit=1000,
            sender_limit=3,
            template_limit=10,
            api_access=False,
            priority_support=False,
            white_label=False,
            custom_integrations=False
        ),
        stripe_price_id_monthly="price_1RhenG4dIfz8S6zvkFNwAJkJ",
        stripe_price_id_yearly="price_1Rhenr4dIfz8S6zvooo5ZyKu"
    ),
    SubscriptionPlan.PROFESSIONAL: SubscriptionPlanDetails(
        plan_id="professional",
        name="Professional",
        price_monthly=14.99,
        price_yearly=149.99,  # 2 months free would be 149.99 if you want
        features=SubscriptionFeatures(
            email_limit=10000,
            sender_limit=10,
            template_limit=50,
            api_access=True,
            priority_support=True,
            white_label=False,
            custom_integrations=False
        ),
        stripe_price_id_monthly="price_1RhepD4dIfz8S6zvNDb8cZ2i",
        stripe_price_id_yearly="price_1Rhepb4dIfz8S6zvz3bTAIKn"
    ),
    SubscriptionPlan.ENTERPRISE: SubscriptionPlanDetails(
        plan_id="enterprise",
        name="Enterprise",
        price_monthly=25.99,
        price_yearly=259.99,  # 2 months free would be 259.99 if you want
        features=SubscriptionFeatures(
            email_limit=50000,
            sender_limit=-1,  # Unlimited
            template_limit=-1,  # Unlimited
            api_access=True,
            priority_support=True,
            white_label=True,
            custom_integrations=True
        ),
        stripe_price_id_monthly="price_1Rheq84dIfz8S6zvs4Sk55zR",
        stripe_price_id_yearly="price_1Rheqq4dIfz8S6zvZtah4C1v"
    )
} 