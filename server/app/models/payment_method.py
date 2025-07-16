from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
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

class PaymentMethodBase(BaseModel):
    user_id: str
    stripe_payment_method_id: str
    stripe_customer_id: str
    type: str = "card"  # card, bank_account, etc.
    brand: Optional[str] = None  # visa, mastercard, amex, etc.
    last4: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    is_default: bool = False
    billing_details: Optional[Dict[str, Any]] = None

class PaymentMethodCreate(PaymentMethodBase):
    pass

class PaymentMethodUpdate(BaseModel):
    is_default: Optional[bool] = None
    billing_details: Optional[Dict[str, Any]] = None

class PaymentMethodInDB(PaymentMethodBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class PaymentMethodResponse(PaymentMethodBase):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(
        json_encoders={ObjectId: str}
    ) 