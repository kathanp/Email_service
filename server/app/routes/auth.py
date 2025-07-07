from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.user import UserCreate, UserLogin, UserResponse, Token
from ..services.auth_service import AuthService
from ..core.security import verify_token
import os
from datetime import datetime, timedelta
import jwt
from ..core.config import settings

router = APIRouter()
security = HTTPBearer()

def _is_development_mode():
    """Check if we're in development mode without database."""
    mongodb_url = os.getenv("MONGODB_URL", "")
    if not mongodb_url or "localhost" in mongodb_url or "127.0.0.1" in mongodb_url:
        return True
    try:
        from ..db.mongodb import MongoDB
        database = MongoDB.get_database()
        if not database:
            return True
        database.command('ping')
        return False
    except Exception:
        return True

def _create_dev_token(email: str) -> str:
    """Create a mock JWT token for development."""
    payload = {
        "sub": email,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

@router.post("/register/dev", response_model=Token)
async def register_dev(user_data: UserCreate):
    """Development mode: Register a new user (no database required)."""
    if not _is_development_mode():
        raise HTTPException(status_code=404, detail="Development endpoint not available in production")
    
    # Create mock user response
    mock_user = UserResponse(
        id="dev_user_id",
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        role="user",
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow(),
        is_active=True
    )
    
    # Create mock token
    token = _create_dev_token(user_data.email)
    
    return Token(
        access_token=token,
        token_type="bearer",
        user=mock_user
    )

@router.post("/login/dev", response_model=Token)
async def login_dev(user_data: UserLogin):
    """Development mode: Login user (no database required)."""
    if not _is_development_mode():
        raise HTTPException(status_code=404, detail="Development endpoint not available in production")
    
    # Accept any email/password in development mode
    mock_user = UserResponse(
        id="dev_user_id",
        email=user_data.email,
        username=user_data.email.split('@')[0],
        full_name=user_data.email.split('@')[0].replace('.', ' ').title(),
        role="user",
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow(),
        is_active=True
    )
    
    # Create mock token
    token = _create_dev_token(user_data.email)
    
    return Token(
        access_token=token,
        token_type="bearer",
        user=mock_user
    )

@router.get("/me/dev", response_model=UserResponse)
async def get_current_user_dev(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Development mode: Get current user (no database required)."""
    if not _is_development_mode():
        raise HTTPException(status_code=404, detail="Development endpoint not available in production")
    
    try:
        # Verify the token
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("email")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Return mock user data
        return UserResponse(
            id="dev_user_id",
            email=email,
            username=email.split('@')[0],
            full_name=email.split('@')[0].replace('.', ' ').title(),
            role="user",
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow(),
            is_active=True
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user."""
    auth_service = AuthService()
    try:
        user = await auth_service.register_user(user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user and return access token."""
    auth_service = AuthService()
    try:
        result = await auth_service.login_user(user_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
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

@router.post("/logout")
async def logout():
    """Logout user (client should remove token)."""
    return {"message": "Successfully logged out"} 