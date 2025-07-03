from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    subject: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)
    user_id: Optional[str] = None

class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    body: Optional[str] = Field(None, min_length=1)

class TemplateInDB(BaseModel):
    id: str
    name: str
    subject: str
    body: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

class TemplateResponse(BaseModel):
    id: str
    name: str
    subject: str
    body: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool 