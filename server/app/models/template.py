from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    subject: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)
    user_id: Optional[str] = None
    is_default: bool = False

class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    body: Optional[str] = Field(None, min_length=1)
    is_default: Optional[bool] = None

class TemplateInDB(BaseModel):
    id: str
    name: str
    subject: str
    body: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    is_default: bool = False

class TemplateResponse(BaseModel):
    id: str
    name: str
    subject: str
    body: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_default: bool 