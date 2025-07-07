from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from bson import ObjectId

class SenderBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None
    is_default: bool = False

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