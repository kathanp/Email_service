from fastapi import APIRouter, Depends, HTTPException, Request
from app.api.deps import get_current_user
from app.services.google_oauth_service import GoogleOAuthService

router = APIRouter(tags=["google-auth"])

@router.get("/authorize")
async def authorize_google(current_user: dict = Depends(get_current_user)):
    """Get Google OAuth authorization URL."""
    oauth_service = GoogleOAuthService()
    return await oauth_service.get_authorization_url(current_user["id"])

@router.get("/callback")
async def google_callback(code: str, state: str, request: Request):
    """Handle Google OAuth callback."""
    oauth_service = GoogleOAuthService()
    return await oauth_service.handle_callback(code, state, request)

@router.get("/status")
async def google_status(current_user: dict = Depends(get_current_user)):
    """Check Google OAuth status."""
    oauth_service = GoogleOAuthService()
    return await oauth_service.get_oauth_status(current_user["id"])

@router.post("/revoke")
async def revoke_google_access(current_user: dict = Depends(get_current_user)):
    """Revoke Google OAuth access."""
    oauth_service = GoogleOAuthService()
    return await oauth_service.revoke_access(current_user["id"])

@router.get("/test")
async def test_google_auth():
    """Test Google Auth endpoint."""
    return {"message": "Google Auth endpoint working"} 