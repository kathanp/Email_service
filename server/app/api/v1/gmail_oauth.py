from fastapi import APIRouter, Depends, HTTPException, Request
from app.api.deps import get_current_user
from app.services.gmail_oauth_service import GmailOAuthService

router = APIRouter(tags=["gmail-oauth"])

@router.get("/authorize")
async def authorize_gmail(current_user: dict = Depends(get_current_user)):
    """Get Gmail OAuth authorization URL."""
    oauth_service = GmailOAuthService()
    return await oauth_service.get_authorization_url(current_user["id"])

@router.get("/callback")
async def gmail_callback(code: str, state: str, request: Request):
    """Handle Gmail OAuth callback."""
    oauth_service = GmailOAuthService()
    return await oauth_service.handle_callback(code, state, request)

@router.get("/status")
async def gmail_status(current_user: dict = Depends(get_current_user)):
    """Check Gmail OAuth status."""
    oauth_service = GmailOAuthService()
    return await oauth_service.get_oauth_status(current_user["id"])

@router.post("/revoke")
async def revoke_gmail_access(current_user: dict = Depends(get_current_user)):
    """Revoke Gmail OAuth access."""
    oauth_service = GmailOAuthService()
    return await oauth_service.revoke_access(current_user["id"]) 