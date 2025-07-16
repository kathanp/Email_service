from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import UserResponse

router = APIRouter(tags=["auth-v1"])

class UserRegister(BaseModel):
    email: str
    password: str
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register a new user."""
    auth_service = AuthService()
    return await auth_service.register_user(user_data)

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """Login user."""
    auth_service = AuthService()
    return await auth_service.login_user(user_data)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.get("/test")
async def test_auth():
    """Test auth endpoint."""
    return {"message": "Auth v1 endpoint working"} 