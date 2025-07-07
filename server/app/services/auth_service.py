from datetime import datetime
from typing import Optional
from bson import ObjectId
from ..db.mongodb import MongoDB
from ..models.user import UserCreate, UserInDB, UserResponse, UserLogin, GoogleUserCreate
from ..core.security import get_password_hash, verify_password, create_access_token
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        logger.info("AuthService initialized")

    def _get_users_collection(self):
        """Get users collection."""
        try:
            logger.info("Getting users collection from MongoDB...")
            collection = MongoDB.get_collection("users")
            if collection:
                logger.info("✅ SUCCESS: Users collection retrieved")
            else:
                logger.warning("⚠️  WARNING: Users collection is None")
            return collection
        except Exception as e:
            logger.error(f"❌ ERROR: Failed to get users collection - {e}")
            logger.warning(f"Database not available: {e}")
            return None

    def _is_development_mode(self):
        """Check if we're in development mode without database."""
        try:
            logger.info("Checking if in development mode...")
            collection = self._get_users_collection()
            is_dev = collection is None
            logger.info(f"Development mode: {is_dev}")
            return is_dev
        except Exception as e:
            logger.error(f"❌ ERROR: Error checking development mode - {e}")
            return True

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user."""
        logger.info("=" * 30)
        logger.info("AUTH SERVICE: register_user called")
        logger.info("=" * 30)
        logger.info(f"Email: {user_data.email}")
        logger.info(f"Username: {user_data.username}")
        logger.info(f"Full name: {user_data.full_name}")
        
        try:
            if self._is_development_mode():
                # Development mode - return mock response
                logger.info("🔄 Development mode: Creating mock user registration")
                mock_user = UserResponse(
                    id="dev_user_123",
                    email=user_data.email,
                    username=user_data.username,
                    full_name=user_data.full_name,
                    role="user",
                    created_at=datetime.utcnow(),
                    last_login=datetime.utcnow(),
                    is_active=True,
                    google_id=None,
                    google_name=None,
                    sender_email=None
                )
                logger.info(f"✅ SUCCESS: Mock user created - ID: {mock_user.id}")
                return mock_user

            logger.info("🔄 Production mode: Creating real user in database")
            users_collection = self._get_users_collection()
            
            # Check if user already exists
            logger.info("Checking if user already exists...")
            existing_user = await users_collection.find_one({"email": user_data.email})
            if existing_user:
                logger.error(f"❌ ERROR: Email already registered - {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Create new user document
            logger.info("Creating new user document...")
            user_dict = user_data.dict()
            
            # Handle password hashing if password is provided
            if user_data.password:
                logger.info("Hashing password...")
                user_dict["hashed_password"] = get_password_hash(user_data.password)
            else:
                logger.info("No password provided, setting hashed_password to None")
                user_dict["hashed_password"] = None
            
            user_dict["created_at"] = datetime.utcnow()
            user_dict["is_active"] = True
            user_dict["settings"] = {}
            
            # Remove plain password from dict
            if "password" in user_dict:
                del user_dict["password"]

            # Insert user into database
            logger.info("Inserting user into database...")
            result = await users_collection.insert_one(user_dict)
            logger.info(f"User inserted with ID: {result.inserted_id}")
            
            # Get the created user
            created_user = await users_collection.find_one({"_id": result.inserted_id})
            
            user_response = UserResponse(
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
            
            logger.info(f"✅ SUCCESS: User registered successfully - ID: {user_response.id}")
            return user_response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ UNEXPECTED ERROR: Error creating user - {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating user: {str(e)}"
            )

    async def register_google_user(self, user_data: GoogleUserCreate) -> UserResponse:
        """Register a new user via Google OAuth."""
        try:
            if self._is_development_mode():
                # Development mode - return mock response
                logger.info("Development mode: Mock Google user registration")
                return UserResponse(
                    id="dev_google_user_123",
                    email=user_data.email,
                    username=None,
                    full_name=user_data.full_name,
                    role="user",
                    created_at=datetime.utcnow(),
                    last_login=datetime.utcnow(),
                    is_active=True,
                    google_id=user_data.google_id,
                    google_name=user_data.google_name,
                    sender_email=None
                )

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
            if self._is_development_mode():
                # Development mode - allow any login with test credentials
                logger.info("Development mode: Mock authentication")
                if email == "test@example.com" and password == "testpass123":
                    return UserInDB(
                        id="dev_user_123",
                        email=email,
                        username="testuser",
                        full_name="Test User",
                        role="user",
                        is_active=True,
                        is_superuser=False,
                        hashed_password=None,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        last_login=datetime.utcnow()
                    )
                return None

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
        logger.info("=" * 30)
        logger.info("AUTH SERVICE: login_user called")
        logger.info("=" * 30)
        logger.info(f"Email: {user_data.email}")
        logger.info(f"Password provided: {'Yes' if user_data.password else 'No'}")
        
        try:
            logger.info("Authenticating user...")
            user = await self.authenticate_user(user_data.email, user_data.password)
            if not user:
                logger.error(f"❌ ERROR: Authentication failed for email: {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )

            logger.info(f"✅ SUCCESS: User authenticated - ID: {user.id}")

            # Update last login (only if database is available)
            if not self._is_development_mode():
                logger.info("Updating last login timestamp...")
                users_collection = self._get_users_collection()
                await users_collection.update_one(
                    {"_id": user.id},
                    {"$set": {"last_login": datetime.utcnow()}}
                )
                logger.info("✅ SUCCESS: Last login updated")
            else:
                logger.info("🔄 Development mode: Skipping last login update")

            # Create access token
            logger.info("Creating access token...")
            access_token = create_access_token(data={"sub": user.email})
            logger.info(f"✅ SUCCESS: Access token created - Length: {len(access_token)}")
            
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

            logger.info(f"✅ SUCCESS: Login completed successfully - User ID: {user.id}")
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_response
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ UNEXPECTED ERROR: Error during login - {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during login: {str(e)}"
            )

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        try:
            if self._is_development_mode():
                # Development mode - return mock user
                logger.info("Development mode: Mock get user by email")
                return UserInDB(
                    id="dev_user_123",
                    email=email,
                    username="testuser",
                    full_name="Test User",
                    role="user",
                    is_active=True,
                    is_superuser=False,
                    hashed_password=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    last_login=datetime.utcnow()
                )

            users_collection = self._get_users_collection()
            user = await users_collection.find_one({"email": email})
            if not user:
                return None
            
            return UserInDB(**user)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting user: {str(e)}"
            )

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID."""
        try:
            if self._is_development_mode():
                # Development mode - return mock user
                logger.info("Development mode: Mock get user by ID")
                return UserInDB(
                    id=user_id,
                    email="test@example.com",
                    username="testuser",
                    full_name="Test User",
                    role="user",
                    is_active=True,
                    is_superuser=False,
                    hashed_password=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    last_login=datetime.utcnow()
                )

            users_collection = self._get_users_collection()
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                return None
            
            return UserInDB(**user)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting user: {str(e)}"
            ) 