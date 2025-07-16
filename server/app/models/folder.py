from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class FolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")  # Hex color code

class FolderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")

class FolderInDB(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#007bff"  # Default blue color
    user_id: str
    file_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class FolderResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#007bff"
    file_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 