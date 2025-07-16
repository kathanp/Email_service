from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..models.sender import SenderCreate, Sender
from ..services.sender_service import SenderService
from ..api.deps import get_current_user
from ..models.user import UserResponse

router = APIRouter(tags=["senders"])

@router.post("/", response_model=dict)
async def add_sender(
    sender_data: SenderCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Add a new sender email for the current user."""
    sender_service = SenderService()
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
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all sender emails for the current user."""
    sender_service = SenderService()
    senders = await sender_service.get_user_senders(str(current_user.id))
    return senders

@router.delete("/{sender_id}", response_model=dict)
async def delete_sender(
    sender_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a sender email for the current user."""
    sender_service = SenderService()
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
    current_user: UserResponse = Depends(get_current_user)
):
    """Set a sender as default for the current user."""
    sender_service = SenderService()
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
    current_user: UserResponse = Depends(get_current_user)
):
    """Get the default sender for the current user."""
    sender_service = SenderService()
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
    current_user: UserResponse = Depends(get_current_user)
):
    """Resend verification email for a sender."""
    sender_service = SenderService()
    result = await sender_service.resend_verification(str(current_user.id), sender_id)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

@router.post("/{sender_id}/verify", response_model=dict)
async def verify_sender_manually(
    sender_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Manually verify a sender email (called when user confirms verification)."""
    sender_service = SenderService()
    result = await sender_service.verify_sender_manually(str(current_user.id), sender_id)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

@router.get("/{sender_id}/status", response_model=dict)
async def check_verification_status(
    sender_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Check verification status of a sender email with AWS SES."""
    sender_service = SenderService()
    result = await sender_service.check_verification_status(str(current_user.id), sender_id)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        ) 