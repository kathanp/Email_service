from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.models.template import TemplateCreate, TemplateUpdate, TemplateResponse
from app.services.template_service import TemplateService
from app.api.deps import get_current_user
from app.models.user import UserResponse

router = APIRouter()

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