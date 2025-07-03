from datetime import datetime
from typing import Optional
from bson import ObjectId
from app.db.mongodb import MongoDB
from app.models.user import UserCreate, UserInDB, UserResponse, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token
from fastapi import HTTPException, status

class AuthService:
    def __init__(self):
        self.users_collection = MongoDB.get_collection("users")

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user."""
        try:
            # Check if user already exists
            existing_user = await self.users_collection.find_one({"email": user_data.email})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Create new user document
            user_dict = user_data.dict()
            user_dict["hashed_password"] = get_password_hash(user_data.password)
            user_dict["created_at"] = datetime.utcnow()
            user_dict["is_active"] = True
            user_dict["settings"] = {}
            
            # Remove plain password from dict
            del user_dict["password"]

            # Insert user into database
            result = await self.users_collection.insert_one(user_dict)
            
            # Get the created user
            created_user = await self.users_collection.find_one({"_id": result.inserted_id})
            
            return UserResponse(
                id=str(created_user["_id"]),
                name=created_user["name"],
                email=created_user["email"],
                role=created_user["role"],
                created_at=created_user["created_at"],
                is_active=created_user["is_active"]
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating user: {str(e)}"
            )

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate a user with email and password."""
        try:
            user = await self.users_collection.find_one({"email": email})
            if not user:
                return None
            
            if not verify_password(password, user["hashed_password"]):
                return None
            
            if not user.get("is_active", True):
                return None

            return UserInDB(**user)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error authenticating user: {str(e)}"
            )

    async def login_user(self, user_data: UserLogin) -> dict:
        """Login a user and return access token."""
        try:
            user = await self.authenticate_user(user_data.email, user_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )

            # Update last login
            await self.users_collection.update_one(
                {"_id": user.id},
                {"$set": {"last_login": datetime.utcnow()}}
            )

            # Create access token
            access_token = create_access_token(data={"sub": user.email})
            
            # Create user response
            user_response = UserResponse(
                id=str(user.id),
                name=user.name,
                email=user.email,
                role=user.role,
                created_at=user.created_at,
                last_login=user.last_login,
                is_active=user.is_active
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_response
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during login: {str(e)}"
            )

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        try:
            user = await self.users_collection.find_one({"email": email})
            if user:
                return UserInDB(**user)
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting user: {str(e)}"
            )

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID."""
        try:
            user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                return UserInDB(**user)
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting user: {str(e)}"
            ) 