from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from typing import Dict, Optional
from datetime import datetime
from app.api.deps import get_current_user
from app.models.user import User
from app.services.gmail_oauth_service import GmailOAuthService
from app.services.auth_service import AuthService
from app.db.mongodb import get_database

router = APIRouter()
gmail_service = GmailOAuthService()
auth_service = AuthService()

@router.get("/auth-url")
async def get_gmail_auth_url(current_user: User = Depends(get_current_user)):
    """Get Gmail OAuth authorization URL."""
    try:
        result = gmail_service.get_authorization_url(state=str(current_user.id))
        
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
            detail=f"Failed to generate authorization URL: {str(e)}"
        )

@router.get("/callback")
async def gmail_oauth_callback(
    code: str,
    state: Optional[str] = None,
    error: Optional[str] = None
):
    """Handle Gmail OAuth callback."""
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
        # Exchange code for tokens
        token_result = await gmail_service.exchange_code_for_tokens(code)
        
        if not token_result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=token_result['error']
            )
        
        # Update user with Gmail tokens
        db = get_database()
        user_id = state  # The state parameter contains the user ID
        
        update_data = {
            "gmail_access_token": token_result['access_token'],
            "gmail_refresh_token": token_result['refresh_token'],
            "gmail_token_expires_at": datetime.utcnow().timestamp() + token_result['expires_in'],
            "sender_email": token_result['user_email'],
            "updated_at": datetime.utcnow()
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        result = db.users.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Redirect to frontend with success
        return RedirectResponse(
            url=f"http://localhost:3000/gmail-success?email={token_result['user_email']}",
            status_code=302
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete OAuth: {str(e)}"
        )

@router.get("/status")
async def get_gmail_status(current_user: User = Depends(get_current_user)):
    """Get Gmail OAuth status for current user."""
    try:
        db = get_database()
        user = db.users.find_one({"_id": current_user.id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        is_connected = bool(
            user.get('gmail_access_token') and 
            user.get('gmail_refresh_token') and 
            user.get('sender_email')
        )
        
        # Check if token is expired
        token_expired = False
        if is_connected and user.get('gmail_token_expires_at'):
            token_expired = gmail_service.is_token_expired(
                datetime.fromtimestamp(user['gmail_token_expires_at'])
            )
        
        return {
            "is_connected": is_connected and not token_expired,
            "sender_email": user.get('sender_email'),
            "token_expired": token_expired,
            "connected_at": user.get('updated_at')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Gmail status: {str(e)}"
        )

@router.post("/disconnect")
async def disconnect_gmail(current_user: User = Depends(get_current_user)):
    """Disconnect Gmail OAuth for current user."""
    try:
        db = get_database()
        
        update_data = {
            "gmail_access_token": None,
            "gmail_refresh_token": None,
            "gmail_token_expires_at": None,
            "sender_email": None,
            "updated_at": datetime.utcnow()
        }
        
        result = db.users.update_one(
            {"_id": current_user.id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"success": True, "message": "Gmail disconnected successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect Gmail: {str(e)}"
        )

@router.post("/refresh-token")
async def refresh_gmail_token(current_user: User = Depends(get_current_user)):
    """Refresh Gmail access token."""
    try:
        db = get_database()
        user = db.users.find_one({"_id": current_user.id})
        
        if not user or not user.get('gmail_refresh_token'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Gmail refresh token found"
            )
        
        # Refresh the token
        refresh_result = gmail_service.refresh_access_token(user['gmail_refresh_token'])
        
        if not refresh_result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=refresh_result['error']
            )
        
        # Update user with new token
        update_data = {
            "gmail_access_token": refresh_result['access_token'],
            "gmail_token_expires_at": refresh_result['expires_in'],
            "updated_at": datetime.utcnow()
        }
        
        db.users.update_one(
            {"_id": current_user.id},
            {"$set": update_data}
        )
        
        return {"success": True, "message": "Token refreshed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh token: {str(e)}"
        )

@router.post("/send-test")
async def send_test_email(
    to_email: str,
    current_user: User = Depends(get_current_user)
):
    """Send a test email using Gmail."""
    try:
        db = get_database()
        user = db.users.find_one({"_id": current_user.id})
        
        if not user or not user.get('gmail_access_token'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gmail not connected. Please connect your Gmail account first."
            )
        
        # Check if token is expired and refresh if needed
        access_token = user['gmail_access_token']
        if user.get('gmail_token_expires_at'):
            if gmail_service.is_token_expired(
                datetime.fromtimestamp(user['gmail_token_expires_at'])
            ):
                refresh_result = gmail_service.refresh_access_token(user['gmail_refresh_token'])
                if refresh_result['success']:
                    access_token = refresh_result['access_token']
                    # Update the token in database
                    db.users.update_one(
                        {"_id": current_user.id},
                        {"$set": {
                            "gmail_access_token": access_token,
                            "gmail_token_expires_at": refresh_result['expires_in'],
                            "updated_at": datetime.utcnow()
                        }}
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to refresh Gmail token"
                    )
        
        # Send test email
        result = await gmail_service.send_email(
            access_token=access_token,
            to_email=to_email,
            subject="Test Email from Email Bot",
            body="This is a test email sent from your Email Bot application using Gmail.",
            user_id=str(current_user.id)
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Test email sent successfully",
                "message_id": result['message_id']
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to send email: {result['error_message']}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test email: {str(e)}"
        ) 