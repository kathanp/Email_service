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

def _is_development_mode():
    """Check if we're in development mode without database."""
    try:
        MongoDB.get_collection("users")
        return False
    except:
        return True

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current authenticated user."""
    # Check if we're in development mode
    if _is_development_mode():
        logger.info("Development mode: Returning mock user")
        return UserResponse(
            id="dev_user_id",
            email="dev@example.com",
            username="devuser",
            full_name="Development User",
            role="user",
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow(),
            is_active=True,
            google_id=None,
            google_email=None,
            google_name=None,
            sender_email="dev@example.com"
        )
    
    # In production mode, require credentials
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required"
        )
    
    auth_service = AuthService()
    try:
        token_data = verify_token(credentials.credentials)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = await auth_service.get_user_by_email(token_data.email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user: {str(e)}"
        )
