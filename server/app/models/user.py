from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId
import re

# Remove PyObjectId and use str for id fields

class UserBase(BaseModel):
    email: str
    username: Optional[str] = None  # Made optional for Google OAuth users
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    role: str = Field(default="user", pattern="^(admin|user)$")
    usersubscription: str = Field(default="free", pattern="^(free|starter|professional|enterprise)$")

    @validator('email')
    def validate_email(cls, v):
        if not v:
            raise ValueError('Email is required')
        # Simple email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()

class UserCreate(UserBase):
    password: Optional[str] = None  # Made optional for Google OAuth users

class UserLogin(BaseModel):
    email: str
    password: str

    @validator('email')
    def validate_email(cls, v):
        if not v:
            raise ValueError('Email is required')
        # Simple email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()

class GoogleUserCreate(BaseModel):
    email: str
    google_id: str
    google_name: Optional[str] = None
    full_name: Optional[str] = None

    @validator('email')
    def validate_email(cls, v):
        if not v:
            raise ValueError('Email is required')
        # Simple email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()

class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    role: Optional[str] = None
    usersubscription: Optional[str] = Field(None, pattern="^(free|starter|professional|enterprise)$")
    # Google OAuth fields for login
    google_id: Optional[str] = None
    google_email: Optional[str] = None
    google_name: Optional[str] = None
    # AWS SES sender email (user's email for sending)
    sender_email: Optional[str] = None

    @validator('email')
    def validate_email(cls, v):
        if v is not None:
            # Simple email validation regex
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
            return v.lower()
        return v

class UserInDB(UserBase):
    id: str = Field(alias="_id")
    hashed_password: Optional[str] = None  # Made optional for Google OAuth users
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    # Google OAuth fields for login
    google_id: Optional[str] = None
    google_email: Optional[str] = None
    google_name: Optional[str] = None
    # AWS SES sender email (user's email for sending)
    sender_email: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    # Google OAuth fields for login
    google_id: Optional[str] = None
    google_email: Optional[str] = None
    google_name: Optional[str] = None
    # AWS SES sender email (user's email for sending)
    sender_email: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

class UserResponse(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    usersubscription: str = "free"
    # Google OAuth fields for login
    google_id: Optional[str] = None
    google_email: Optional[str] = None
    google_name: Optional[str] = None
    # AWS SES sender email (user's email for sending)
    sender_email: Optional[str] = None

    model_config = ConfigDict(
        json_encoders={ObjectId: str}
    )

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None