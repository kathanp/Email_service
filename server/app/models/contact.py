from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re

class ContactBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    company: Optional[str] = Field(None, max_length=100)
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=2000)
    
    @validator('email')
    def validate_email(cls, v):
        if not v:
            raise ValueError('Email is required')
        # Simple email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name is required')
        return v.strip()
    
    @validator('subject')
    def validate_subject(cls, v):
        if not v or not v.strip():
            raise ValueError('Subject is required')
        return v.strip()
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message is required')
        return v.strip()

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: str = Field(alias="_id")
    created_at: datetime
    status: str = Field(default="new")  # new, in_progress, resolved
    
    class Config:
        extra = "allow"
        populate_by_name = True

class ContactInDB(ContactBase):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="new") 