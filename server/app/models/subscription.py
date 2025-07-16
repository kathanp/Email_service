from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, _handler):
        return {"type": "string"}

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"

class UsageStats(BaseModel):
    """Usage statistics for a user."""
    user_id: str
    emails_sent: int = 0
    emails_remaining: int = 0
    total_emails_allowed: int = 0
    templates_used: int = 0
    templates_remaining: int = 0
    total_templates_allowed: int = 0
    sender_emails_used: int = 0
    sender_emails_remaining: int = 0
    total_sender_emails_allowed: int = 0
    current_plan: str = "free"
    usage_percentage: float = 0.0

class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price: float
    billing_cycle: BillingCycle
    features: Dict[str, Any]
    limits: Dict[str, int]

# Define subscription plans
SUBSCRIPTION_PLANS = {
    "free": SubscriptionPlan(
        id="free",
        name="Free",
        price=0.0,
        billing_cycle=BillingCycle.MONTHLY,
        features={
            "email_sends": 100,
            "sender_emails": 1,
            "templates": 5,
            "support": "Community"
        },
        limits={
            "email_sends": 100,
            "sender_emails": 1,
            "templates": 5
        }
    ),
    "starter": SubscriptionPlan(
        id="starter",
        name="Starter",
        price=4.99,
        billing_cycle=BillingCycle.MONTHLY,
        features={
            "email_sends": 1000,
            "sender_emails": 3,
            "templates": 20,
            "support": "Email"
        },
        limits={
            "email_sends": 1000,
            "sender_emails": 3,
            "templates": 20
        }
    ),
    "professional": SubscriptionPlan(
        id="professional",
        name="Professional",
        price=14.99,
        billing_cycle=BillingCycle.MONTHLY,
        features={
            "email_sends": 10000,
            "sender_emails": 10,
            "templates": 100,
            "support": "Priority"
        },
        limits={
            "email_sends": 10000,
            "sender_emails": 10,
            "templates": 100
        }
    ),
    "enterprise": SubscriptionPlan(
        id="enterprise",
        name="Enterprise",
        price=25.99,
        billing_cycle=BillingCycle.MONTHLY,
        features={
            "email_sends": 100000,
            "sender_emails": 50,
            "templates": 500,
            "support": "Dedicated"
        },
        limits={
            "email_sends": 100000,
            "sender_emails": 50,
            "templates": 500
        }
    )
}

class SubscriptionBase(BaseModel):
    user_id: str = Field(..., description="User ID")
    plan_id: str = Field(..., description="Subscription plan ID")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    billing_cycle: BillingCycle = Field(default=BillingCycle.MONTHLY)

class SubscriptionCreate(SubscriptionBase):
    stripe_subscription_id: Optional[str] = Field(None, description="Stripe subscription ID")
    stripe_customer_id: Optional[str] = Field(None, description="Stripe customer ID")

class SubscriptionUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    plan_id: Optional[str] = None
    billing_cycle: Optional[BillingCycle] = None
    stripe_subscription_id: Optional[str] = None

class SubscriptionInDB(SubscriptionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = Field(default=False)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class SubscriptionResponse(SubscriptionBase):
    id: str
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    plan: Optional[str] = None  # Add plan field
    features: Optional[Dict[str, Any]] = None  # Add features field

    model_config = {
        "json_encoders": {ObjectId: str}
    } 