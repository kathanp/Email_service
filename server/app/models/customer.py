from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId

class CustomerBase(BaseModel):
    email: str = Field(..., description="Customer email address")
    name: Optional[str] = Field(None, description="Customer name")
    phone: Optional[str] = Field(None, description="Customer phone number")
    company: Optional[str] = Field(None, description="Customer company")

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None

class Customer(CustomerBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

class CustomerResponse(Customer):
    pass
