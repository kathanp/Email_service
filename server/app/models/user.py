from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None  # Made optional for Google OAuth users
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    role: str = Field(default="user", regex="^(admin|user)$")

class UserCreate(UserBase):
    password: Optional[str] = None  # Made optional for Google OAuth users

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleUserCreate(BaseModel):
    email: EmailStr
    google_id: str
    google_name: Optional[str] = None
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    role: Optional[str] = None
    # Google OAuth fields for login
    google_id: Optional[str] = None
    google_email: Optional[str] = None
    google_name: Optional[str] = None
    # AWS SES sender email (user's email for sending)
    sender_email: Optional[str] = None

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
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

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

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

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class UserResponse(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    # Google OAuth fields for login
    google_id: Optional[str] = None
    google_email: Optional[str] = None
    google_name: Optional[str] = None
    # AWS SES sender email (user's email for sending)
    sender_email: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
