from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from ..models.contact import ContactCreate, ContactResponse
from ..services.contact_service import ContactService
from ..core.security import verify_token
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/submit", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def submit_contact_form(contact_data: ContactCreate, request: Request):
    """Submit a new contact form."""
    logger.info("=" * 40)
    logger.info("CONTACT: New contact form submission")
    logger.info("=" * 40)
    logger.info(f"Name: {contact_data.name}")
    logger.info(f"Email: {contact_data.email}")
    logger.info(f"Company: {contact_data.company}")
    logger.info(f"Subject: {contact_data.subject}")
    logger.info(f"Client IP: {request.client.host if request.client else 'unknown'}")
    logger.info(f"User agent: {request.headers.get('user-agent', 'unknown')}")
    
    contact_service = ContactService()
    try:
        logger.info("Calling ContactService.create_contact...")
        result = await contact_service.create_contact(contact_data)
        logger.info(f"✅ SUCCESS: Contact form submitted successfully - ID: {result.id}")
        return result
    except HTTPException as he:
        logger.error(f"❌ HTTP ERROR: Contact submission failed - {he.status_code}: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ UNEXPECTED ERROR: Contact submission failed - {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Contact submission failed: {str(e)}"
        )

@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    skip: int = 0,
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all contact submissions (admin only)."""
    logger.info("CONTACT: Retrieving contact submissions")
    
    # Verify admin access
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Note: You might want to add additional admin role checking here
        
        contact_service = ContactService()
        contacts = await contact_service.get_all_contacts(skip=skip, limit=limit)
        logger.info(f"✅ SUCCESS: Retrieved {len(contacts)} contact submissions")
        return contacts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ERROR: Failed to retrieve contacts - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contacts"
        )

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get a specific contact by ID (admin only)."""
    logger.info(f"CONTACT: Retrieving contact {contact_id}")
    
    # Verify admin access
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        contact_service = ContactService()
        contact = await contact_service.get_contact_by_id(contact_id)
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        logger.info(f"✅ SUCCESS: Retrieved contact {contact_id}")
        return contact
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ERROR: Failed to retrieve contact {contact_id} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contact"
        )

@router.patch("/{contact_id}/status", response_model=ContactResponse)
async def update_contact_status(
    contact_id: str,
    status_update: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update contact status (admin only)."""
    logger.info(f"CONTACT: Updating status for contact {contact_id}")
    
    # Verify admin access
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        new_status = status_update.get("status")
        if not new_status or new_status not in ["new", "in_progress", "resolved"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be one of: new, in_progress, resolved"
            )
        
        contact_service = ContactService()
        updated_contact = await contact_service.update_contact_status(contact_id, new_status)
        
        logger.info(f"✅ SUCCESS: Updated contact {contact_id} status to {new_status}")
        return updated_contact
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ERROR: Failed to update contact {contact_id} status - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update contact status"
        ) 