import bcrypt
import jwt
import logging
import traceback
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from ..db.mongodb import MongoDB
from ..core.config import settings
from ..models.user import UserCreate, UserLogin, UserResponse

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

    def _get_users_collection(self):
        return MongoDB.get_collection("users")

    def _create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def _get_password_hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    async def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        try:
            users_collection = self._get_users_collection()
            existing_user = await users_collection.find_one({"email": user_data.email})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            hashed_password = self._get_password_hash(user_data.password)
            user_doc = {
                "email": user_data.email,
                "username": user_data.username,
                "full_name": user_data.full_name,
                "hashed_password": hashed_password,
                "role": "user",
                "is_active": True,
                "usersubscription": "free",
                "created_at": datetime.utcnow()
            }
            
            result = await users_collection.insert_one(user_doc)
            access_token = self._create_access_token(data={"sub": user_data.email})
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": str(result.inserted_id),
                    "email": user_data.email,
                    "username": user_data.username,
                    "full_name": user_data.full_name,
                    "role": "user",
                    "is_active": True,
                    "created_at": user_doc["created_at"],
                    "usersubscription": "free"
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )

    async def login_user(self, user_data: UserLogin) -> Dict[str, Any]:
        try:
            users_collection = self._get_users_collection()
            user = await users_collection.find_one({"email": user_data.email})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            if not self._verify_password(user_data.password, user['hashed_password']):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            access_token = self._create_access_token(data={"sub": user_data.email})
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": str(user["_id"]),
                    "email": user["email"],
                    "username": user.get("username"),
                    "full_name": user.get("full_name"),
                    "role": user.get("role", "user"),
                    "is_active": user.get("is_active", True),
                    "created_at": user.get("created_at"),
                    "usersubscription": user.get("usersubscription", "free")
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}"
            )

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        try:
            logger.info(f"🔍 Looking up user by email: {email}")
            users_collection = self._get_users_collection()
            logger.info(f"✅ Users collection obtained: {users_collection is not None}")
            
            user = await users_collection.find_one({"email": email})
            logger.info(f"✅ User lookup result: {user is not None}")
            
            if not user:
                logger.warning(f"❌ User not found for email: {email}")
                return None
            
            logger.info(f"✅ User found - ID: {user.get('_id')}, Email: {user.get('email')}")
            
            # Create UserResponse with detailed logging
            try:
                user_response = UserResponse(
                    id=str(user["_id"]),
                    email=user["email"],
                    username=user.get("username"),
                    full_name=user.get("full_name"),
                    role=user.get("role", "user"),
                    is_active=user.get("is_active", True),
                    created_at=user.get("created_at", datetime.utcnow()),
                    last_login=user.get("last_login"),
                    usersubscription=user.get("usersubscription", "free"),
                    google_id=user.get("google_id"),
                    google_email=user.get("google_email"),
                    google_name=user.get("google_name"),
                    sender_email=user.get("sender_email")
                )
                logger.info(f"✅ UserResponse created successfully")
                return user_response
            except Exception as user_response_error:
                logger.error(f"❌ Error creating UserResponse: {user_response_error}")
                logger.error(f"User data: {user}")
                raise
            
        except Exception as e:
            logger.error(f"❌ Error getting user: {str(e)}")
            logger.error(f"Email: {email}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting user: {str(e)}"
            ) 