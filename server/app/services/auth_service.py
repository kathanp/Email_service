from datetime import datetime
from typing import Optional
from bson import ObjectId
from ..db.mongodb import MongoDB
from ..models.user import UserCreate, UserInDB, UserResponse, UserLogin, GoogleUserCreate
from ..core.security import get_password_hash, verify_password, create_access_token
from fastapi import HTTPException, status

class AuthService:
    def __init__(self):
        pass

    def _get_users_collection(self):
        """Get users collection."""
        return MongoDB.get_collection("users")

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user."""
        try:
            users_collection = self._get_users_collection()
            
            # Check if user already exists
            existing_user = await users_collection.find_one({"email": user_data.email})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Create new user document
            user_dict = user_data.dict()
            
            # Handle password hashing if password is provided
            if user_data.password:
                user_dict["hashed_password"] = get_password_hash(user_data.password)
            else:
                user_dict["hashed_password"] = None
            
            user_dict["created_at"] = datetime.utcnow()
            user_dict["is_active"] = True
            user_dict["settings"] = {}
            
            # Remove plain password from dict
            if "password" in user_dict:
                del user_dict["password"]

            # Insert user into database
            result = await users_collection.insert_one(user_dict)
            
            # Get the created user
            created_user = await users_collection.find_one({"_id": result.inserted_id})
            
            return UserResponse(
                id=str(created_user["_id"]),
                email=created_user["email"],
                username=created_user.get("username"),
                full_name=created_user.get("full_name"),
                role=created_user["role"],
                created_at=created_user["created_at"],
                last_login=created_user.get("last_login"),
                is_active=created_user["is_active"],
                google_id=created_user.get("google_id"),
                google_name=created_user.get("google_name"),
                sender_email=created_user.get("sender_email")
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating Google user: {str(e)}"
            )

    async def register_google_user(self, user_data: GoogleUserCreate) -> UserResponse:
        """Register a new user via Google OAuth."""
        try:
            users_collection = self._get_users_collection()
            
            # Check if user already exists by email
            existing_user = await users_collection.find_one({"email": user_data.email})
            if existing_user:
                # Update existing user with Google info
                await users_collection.update_one(
                    {"email": user_data.email},
                    {
                        "$set": {
                            "google_id": user_data.google_id,
                            "google_name": user_data.google_name,
                            "full_name": user_data.full_name or user_data.google_name,
                            "updated_at": datetime.utcnow(),
                            "last_login": datetime.utcnow()
                        }
                    }
                )
                updated_user = await users_collection.find_one({"email": user_data.email})
                return UserResponse(
                    id=str(updated_user["_id"]),
                    email=updated_user["email"],
                    username=updated_user.get("username"),
                    full_name=updated_user.get("full_name"),
                    role=updated_user["role"],
                    created_at=updated_user["created_at"],
                    last_login=updated_user.get("last_login"),
                    is_active=updated_user["is_active"],
                    google_id=updated_user.get("google_id"),
                    google_name=updated_user.get("google_name"),
                    sender_email=updated_user.get("sender_email")  # Keep existing sender email or use AWS SES default
                )

            # Create new user document for Google OAuth
            user_dict = {
                "email": user_data.email,
                "google_id": user_data.google_id,
                "google_name": user_data.google_name,
                "full_name": user_data.full_name or user_data.google_name,
                "username": None,  # No username for Google OAuth users
                "hashed_password": None,  # No password for Google OAuth users
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": datetime.utcnow(),
                "is_active": True,
                "role": "user",
                "settings": {},
                "sender_email": None  # Will use AWS SES default sender email
            }

            # Insert user into database
            result = await users_collection.insert_one(user_dict)
            
            # Get the created user
            created_user = await users_collection.find_one({"_id": result.inserted_id})
            
            return UserResponse(
                id=str(created_user["_id"]),
                email=created_user["email"],
                username=created_user.get("username"),
                full_name=created_user.get("full_name"),
                role=created_user["role"],
                created_at=created_user["created_at"],
                last_login=created_user.get("last_login"),
                is_active=created_user["is_active"],
                google_id=created_user.get("google_id"),
                google_name=created_user.get("google_name"),
                sender_email=created_user.get("sender_email")
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating Google user: {str(e)}"
            )

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate a user with email and password."""
        try:
            users_collection = self._get_users_collection()
            user = await users_collection.find_one({"email": email})
            if not user:
                return None
            
            # Check if user has a password (not Google OAuth only)
            if not user.get("hashed_password"):
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
            users_collection = self._get_users_collection()
            user = await self.authenticate_user(user_data.email, user_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )

            # Update last login
            await users_collection.update_one(
                {"_id": user.id},
                {"$set": {"last_login": datetime.utcnow()}}
            )

            # Create access token
            access_token = create_access_token(data={"sub": user.email})
            
            # Create user response
            user_response = UserResponse(
                id=str(user.id),
                email=user.email,
                username=user.username,
                full_name=user.full_name,
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
            users_collection = self._get_users_collection()
            user = await users_collection.find_one({"email": email})
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
            users_collection = self._get_users_collection()
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                return UserInDB(**user)
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting user: {str(e)}"
            ) 