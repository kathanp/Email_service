from pydantic import BaseModel, Field, ConfigDict
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

class FileBase(BaseModel):
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type (excel, pdf, etc.)")
    file_size: int = Field(..., description="File size in bytes")
    description: Optional[str] = Field(None, description="File description")

class FileCreate(FileBase):
    user_id: str = Field(..., description="User ID who uploaded the file")
    file_data: bytes = Field(..., description="File binary data")

class FileUpdate(BaseModel):
    description: Optional[str] = Field(None, description="File description")

class FileInDB(FileBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    file_data: bytes
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    processed: bool = Field(default=False)
    contacts_count: Optional[int] = Field(None, description="Number of contacts extracted")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class FileResponse(FileBase):
    id: str
    user_id: str
    upload_date: datetime
    is_active: bool
    processed: bool
    contacts_count: Optional[int]

    model_config = ConfigDict(
        json_encoders={ObjectId: str}
    ) 