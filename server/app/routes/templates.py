from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from ..models.template import TemplateCreate, TemplateUpdate, TemplateResponse
from ..services.template_service import TemplateService
from ..api.deps import get_current_user
from ..models.user import UserResponse
from ..db.mongodb import MongoDB
import logging
import os

router = APIRouter()
logger = logging.getLogger(__name__)

def _is_development_mode():
    """Check if we're in development mode without database."""
    # Check if we're running locally without proper MongoDB credentials
    mongodb_url = os.getenv("MONGODB_URL", "")
    if not mongodb_url or "localhost" in mongodb_url or "127.0.0.1" in mongodb_url:
        return True
    
    # Check if MongoDB client is connected
    try:
        database = MongoDB.get_database()
        if not database:
            return True
        # Try a simple operation
        database.command('ping')
        return False
    except Exception as e:
        logger.info(f"Development mode detected: {str(e)}")
        return True

@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new email template."""
    template_service = TemplateService()
    # Set the user_id from the authenticated user
    template_data.user_id = current_user.id
    return await template_service.create_template(template_data)

@router.get("/", response_model=List[TemplateResponse])
async def get_user_templates(current_user: UserResponse = Depends(get_current_user)):
    """Get all templates created by the current user."""
    template_service = TemplateService()
    return await template_service.get_user_templates(current_user.id)

@router.get("/dev", response_model=List[TemplateResponse])
async def get_user_templates_dev():
    """Get templates for development mode (no auth required)."""
    if not _is_development_mode():
        raise HTTPException(status_code=404, detail="Development endpoint not available in production")
    
    # Development mode - return mock templates
    logger.info("Development mode: Mock templates")
    from datetime import datetime
    return [
        TemplateResponse(
            id="template_1",
            name="Welcome Template",
            subject="Welcome to our platform!",
            content="<h1>Welcome {{name}}!</h1><p>Thank you for joining us.</p>",
            category="welcome",
            user_id="dev_user_id",
            is_default=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
            body=""
        ),
        TemplateResponse(
            id="template_2",
            name="Newsletter Template",
            subject="Monthly Newsletter",
            content="<h1>Monthly Newsletter</h1><p>Here's what's new this month.</p>",
            category="newsletter",
            user_id="dev_user_id",
            is_default=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
            body=""
        )
    ]

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific template by ID."""
    template_service = TemplateService()
    return await template_service.get_template_by_id(template_id, current_user.id)

@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template_data: TemplateUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a template."""
    template_service = TemplateService()
    return await template_service.update_template(template_id, current_user.id, template_data)

@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a template."""
    template_service = TemplateService()
    return await template_service.delete_template(template_id, current_user.id)

@router.post("/{template_id}/set-default", response_model=TemplateResponse)
async def set_template_as_default(
    template_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Set a template as the default template for the current user."""
    template_service = TemplateService()
    return await template_service.set_template_as_default(template_id, current_user.id)

@router.get("/categories/list")
async def get_template_categories():
    """Get list of available template categories."""
    return {
        "categories": [
            {"value": "general", "label": "General"},
            {"value": "welcome", "label": "Welcome"},
            {"value": "partnership", "label": "Partnership"},
            {"value": "follow-up", "label": "Follow-up"},
            {"value": "promotional", "label": "Promotional"},
            {"value": "newsletter", "label": "Newsletter"},
            {"value": "support", "label": "Support"},
            {"value": "sales", "label": "Sales"}
        ]
    } 