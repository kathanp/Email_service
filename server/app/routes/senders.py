from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.sender import SenderCreate, Sender
from app.services.sender_service import SenderService
from app.api.deps import get_current_user
from app.models.user import UserResponse

router = APIRouter(tags=["senders"])

@router.post("/", response_model=dict)
async def add_sender(
    sender_data: SenderCreate,
    current_user: UserResponse = Depends(get_current_user),
    sender_service: SenderService = Depends()
):
    """Add a new sender email for the current user."""
    result = await sender_service.add_sender(str(current_user.id), sender_data)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

@router.get("/", response_model=List[dict])
async def get_user_senders(
    current_user: UserResponse = Depends(get_current_user),
    sender_service: SenderService = Depends()
):
    """Get all sender emails for the current user."""
    senders = await sender_service.get_user_senders(str(current_user.id))
    return senders

@router.delete("/{sender_id}", response_model=dict)
async def delete_sender(
    sender_id: str,
    current_user: UserResponse = Depends(get_current_user),
    sender_service: SenderService = Depends()
):
    """Delete a sender email for the current user."""
    result = await sender_service.delete_sender(str(current_user.id), sender_id)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

@router.post("/{sender_id}/set-default", response_model=dict)
async def set_default_sender(
    sender_id: str,
    current_user: UserResponse = Depends(get_current_user),
    sender_service: SenderService = Depends()
):
    """Set a sender as default for the current user."""
    result = await sender_service.set_default_sender(str(current_user.id), sender_id)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

@router.get("/default", response_model=dict)
async def get_default_sender(
    current_user: UserResponse = Depends(get_current_user),
    sender_service: SenderService = Depends()
):
    """Get the default sender for the current user."""
    sender = await sender_service.get_default_sender(str(current_user.id))
    
    if sender:
        return sender
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No default sender found"
        )

@router.post("/{sender_id}/resend-verification", response_model=dict)
async def resend_verification(
    sender_id: str,
    current_user: UserResponse = Depends(get_current_user),
    sender_service: SenderService = Depends()
):
    """Resend verification email for a sender."""
    result = await sender_service.resend_verification(str(current_user.id), sender_id)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        ) 