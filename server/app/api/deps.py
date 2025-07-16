from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..services.auth_service import AuthService
from ..core.security import verify_token
from ..models.user import UserResponse
from ..db.mongodb import MongoDB
from datetime import datetime
import logging

security = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current authenticated user."""
    logger.info("=" * 30)
    logger.info("AUTH: Get current user attempt")
    logger.info("=" * 30)
    logger.info(f"Credentials: {credentials}")
    logger.info(f"Token length: {len(credentials.credentials) if credentials and credentials.credentials else 0}")
    
    # In production mode, require credentials
    if not credentials or not credentials.credentials:
        logger.error("❌ ERROR: No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required"
        )
    
    # Check for invalid token values
    if credentials.credentials in ['undefined', 'null', '']:
        logger.error(f"❌ ERROR: Invalid token value: '{credentials.credentials}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    auth_service = AuthService()
    try:
        logger.info("Verifying token...")
        token_data = verify_token(credentials.credentials)
        if token_data is None:
            logger.error("❌ ERROR: Invalid token - verify_token returned None")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        logger.info(f"✅ SUCCESS: Token verified for email: {token_data.email}")
        user = await auth_service.get_user_by_email(token_data.email)
        if user is None:
            logger.error(f"❌ ERROR: User not found for email: {token_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        logger.info(f"✅ SUCCESS: User found - ID: {user.id}")
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            created_at=user.created_at,
            last_login=user.last_login,
            is_active=user.is_active,
            google_id=user.google_id,
            google_email=user.google_email,
            google_name=user.google_name,
            sender_email=user.sender_email
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ERROR: Unexpected error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user: {str(e)}"
        )