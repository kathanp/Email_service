from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, validator
from bson import ObjectId
import re

class SenderBase(BaseModel):
    email: str
    display_name: Optional[str] = None
    is_default: bool = False

    @validator('email')
    def validate_email(cls, v):
        if not v:
            raise ValueError('Email is required')
        # Simple email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()

class SenderCreate(SenderBase):
    pass

class SenderUpdate(BaseModel):
    display_name: Optional[str] = None
    is_default: Optional[bool] = None

class SenderInDB(SenderBase):
    id: str
    user_id: str
    verification_status: str  # 'pending', 'verified', 'failed'
    verification_token: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class Sender(SenderBase):
    id: str
    verification_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 