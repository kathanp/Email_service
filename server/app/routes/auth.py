from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.user import UserCreate, UserLogin, UserResponse, Token
from ..services.auth_service import AuthService
from ..core.security import verify_token
from ..db.mongodb import MongoDB
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, request: Request):
    """Register a new user and return access token."""
    logger.info("=" * 40)
    logger.info("AUTH: User registration attempt")
    logger.info("=" * 40)
    logger.info(f"User email: {user_data.email}")
    logger.info(f"Username: {user_data.username}")
    logger.info(f"Client IP: {request.client.host if request.client else 'unknown'}")
    logger.info(f"User agent: {request.headers.get('user-agent', 'unknown')}")
    
    auth_service = AuthService()
    try:
        logger.info("Calling AuthService.register_user...")
        result = await auth_service.register_user(user_data)
        user_id = result['user'].id if hasattr(result['user'], 'id') else result['user']['id']
        logger.info(f"✅ SUCCESS: User registered successfully - ID: {user_id}")
        return result
    except HTTPException as he:
        logger.error(f"❌ HTTP ERROR: Registration failed - {he.status_code}: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ UNEXPECTED ERROR: Registration failed - {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, request: Request):
    """Login user and return access token."""
    logger.info("=" * 40)
    logger.info("AUTH: User login attempt")
    logger.info("=" * 40)
    logger.info(f"User email: {user_data.email}")
    logger.info(f"Client IP: {request.client.host if request.client else 'unknown'}")
    logger.info(f"User agent: {request.headers.get('user-agent', 'unknown')}")
    
    auth_service = AuthService()
    try:
        logger.info("Calling AuthService.login_user...")
        result = await auth_service.login_user(user_data)
        logger.info(f"✅ SUCCESS: User logged in successfully - Email: {user_data.email}")
        return result
    except HTTPException as he:
        logger.error(f"❌ HTTP ERROR: Login failed - {he.status_code}: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ UNEXPECTED ERROR: Login failed - {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), request: Request = None):
    """Get current authenticated user."""
    logger.info("=" * 40)
    logger.info("AUTH: Get current user attempt")
    logger.info("=" * 40)
    logger.info(f"Client IP: {request.client.host if request and request.client else 'unknown'}")
    logger.info(f"Token length: {len(credentials.credentials) if credentials.credentials else 0}")
    
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
        
        logger.info(f"Token verified for email: {token_data.email}")
        logger.info("Getting user by email...")
        user = await auth_service.get_user_by_email(token_data.email)
        if user is None:
            logger.error(f"❌ ERROR: User not found for email: {token_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        logger.info(f"✅ SUCCESS: User retrieved successfully - ID: {user.id}")
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
        logger.error(f"❌ UNEXPECTED ERROR: Get current user failed - {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user: {str(e)}"
        )

@router.post("/logout")
async def logout(request: Request):
    """Logout user (client should discard token)."""
    logger.info("=" * 40)
    logger.info("AUTH: User logout")
    logger.info("=" * 40)
    logger.info(f"Client IP: {request.client.host if request.client else 'unknown'}")
    logger.info("✅ SUCCESS: User logged out")
    return {"message": "Successfully logged out"}

@router.get("/test-db")
async def test_database_connection():
    """Test MongoDB connection status"""
    try:
        from ..db.mongodb import MongoDB
        from ..core.config import settings
        
        logger.info("Testing MongoDB connection...")
        logger.info(f"MongoDB URL: {settings.MONGODB_URL}")
        logger.info(f"Database name: {settings.DATABASE_NAME}")
        
        collection = MongoDB.get_collection("users")
        if collection is not None:
            # Try to count documents to test actual connection
            count = await collection.count_documents({})
            return {
                "status": "connected",
                "database": settings.DATABASE_NAME,
                "users_count": count,
                "message": "MongoDB connection successful"
            }
        else:
            return {
                "status": "disconnected",
                "database": settings.DATABASE_NAME,
                "message": "MongoDB collection is None"
            }
    except Exception as e:
        return {
            "status": "error",
            "database": settings.DATABASE_NAME,
            "error": str(e),
            "error_type": type(e).__name__
        } 