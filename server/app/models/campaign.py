from pydantic import BaseModel, Field, ConfigDict, GetJsonSchemaHandler
from typing import Optional, Any, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: Any, _handler: Any) -> dict[str, Any]:
        return {"type": "string"}

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    template_id: str = Field(..., description="Template ID to use for the campaign")
    file_id: str = Field(..., description="File ID containing contacts")
    subject_override: Optional[str] = Field(None, max_length=200)
    custom_message: Optional[str] = Field(None, description="Additional custom message to append")

class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    subject_override: Optional[str] = Field(None, max_length=200)
    custom_message: Optional[str] = Field(None)

class CampaignInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    user_id: str
    template_id: str
    file_id: str
    subject_override: Optional[str] = None
    custom_message: Optional[str] = None
    status: str = Field(default="pending", pattern="^(pending|sending|completed|failed)$")
    total_emails: int = Field(default=0)
    successful: int = Field(default=0)
    failed: int = Field(default=0)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class CampaignResponse(BaseModel):
    id: str
    name: str
    user_id: str
    template_id: str
    file_id: str
    subject_override: Optional[str] = None
    custom_message: Optional[str] = None
    status: str
    total_emails: int
    successful: int
    failed: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None

    model_config = ConfigDict(
        json_encoders={ObjectId: str}
    )

class CampaignStats(BaseModel):
    total_campaigns: int
    total_emails_sent: int
    successful_emails: int
    failed_emails: int
    average_duration: float
    success_rate: float 