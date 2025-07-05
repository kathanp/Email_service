from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from typing import Dict, Optional
from datetime import datetime
from app.api.deps import get_current_user
from app.models.user import UserResponse, GoogleUserCreate
from app.services.google_oauth_service import GoogleOAuthService
from app.services.auth_service import AuthService
from app.core.security import create_access_token
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
google_service = GoogleOAuthService()

def get_auth_service():
    return AuthService()

@router.get("/login-url")
async def get_google_login_url():
    """Get Google OAuth login URL."""
    try:
        result = google_service.get_authorization_url()
        
        if result['success']:
            return {
                "success": True,
                "authorization_url": result['authorization_url']
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result['error']
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate login URL: {str(e)}"
        )

@router.get("/callback")
async def google_oauth_callback(
    code: str,
    state: Optional[str] = None,
    error: Optional[str] = None
):
    """Handle Google OAuth callback for user login."""
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}"
        )
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is required"
        )
    
    try:
        # Exchange code for tokens and user info
        token_result = await google_service.exchange_code_for_tokens(code)
        
        if not token_result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=token_result['error']
            )
        
        user_info = token_result['user_info']
        google_email = user_info.get('email')
        google_id = user_info.get('id')
        google_name = user_info.get('name')
        
        if not google_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        # Create or update user using the auth service
        google_user_data = GoogleUserCreate(
            email=google_email,
            google_id=google_id,
            google_name=google_name,
            full_name=google_name
        )
        
        auth_service = get_auth_service()
        user_response = await auth_service.register_google_user(google_user_data)
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": user_response.email})
        
        # Redirect to frontend with token
        return RedirectResponse(
            url=f"http://localhost:3000/google-login-success?token={access_token}",
            status_code=302
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Google OAuth callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete login: {str(e)}"
        )

@router.get("/status")
async def get_google_auth_status(current_user: UserResponse = Depends(get_current_user)):
    """Get Google OAuth status for current user."""
    try:
        # Get user from auth service
        auth_service = get_auth_service()
        user = await auth_service.get_user_by_id(current_user.id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        is_google_user = bool(
            user.google_id and 
            user.google_email
        )
        
        return {
            "is_google_user": is_google_user,
            "google_email": user.google_email,
            "google_name": user.google_name,
            "sender_email": user.sender_email,
            "connected_at": user.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Google auth status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Google auth status: {str(e)}"
        )

@router.post("/disconnect")
async def disconnect_google_auth(current_user: UserResponse = Depends(get_current_user)):
    """Disconnect Google OAuth for current user."""
    try:
        auth_service = get_auth_service()
        users_collection = auth_service._get_users_collection()
        
        update_data = {
            "google_id": None,
            "google_email": None,
            "google_name": None,
            "sender_email": None,
            "updated_at": datetime.utcnow()
        }
        
        result = await users_collection.update_one(
            {"_id": current_user.id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to disconnect Google OAuth"
            )
        
        return {"message": "Google OAuth disconnected successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting Google OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect Google OAuth: {str(e)}"
        ) 