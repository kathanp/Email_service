from pydantic import BaseModel, Field
from typing import Optional
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

class TemplateBase(BaseModel):
    name: str = Field(..., description="Template name")
    subject: str = Field(..., description="Email subject")
    content: str = Field(..., description="Email content")
    description: Optional[str] = Field(None, description="Template description")

class TemplateCreate(TemplateBase):
    user_id: Optional[str] = Field(None, description="User ID who created the template")

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None

class TemplateInDB(TemplateBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class TemplateResponse(TemplateBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_default: Optional[bool] = False
    body: Optional[str] = None  # Add body field for frontend compatibility

    model_config = {
        "json_encoders": {ObjectId: str}
    } 