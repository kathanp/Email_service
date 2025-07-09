from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
import motor.motor_asyncio
import bcrypt
import jwt
import os
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Email Bot API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://emailbotuser:Xa5EekvEr1cMEGUq@cluster0.wdvicn9.mongodb.net/emailbot?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = os.getenv("DATABASE_NAME", "emailbot")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"

# MongoDB client
client = None
database = None

async def connect_to_mongo():
    global client, database
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        database = client[DATABASE_NAME]
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # Don't raise the exception - allow the app to start without database
        client = None
        database = None

async def close_mongo_connection():
    if client:
        client.close()
        logger.info("MongoDB connection closed")

def get_database():
    """Get database instance, create if not exists."""
    global client, database
    if database is None:
        # Try to reconnect
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
            database = client[DATABASE_NAME]
            logger.info("Reconnected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to reconnect to MongoDB: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )
    return database

async def ensure_database():
    """Ensure database is initialized for each request."""
    try:
        return get_database()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database initialization failed"
        )

def create_access_token(data: dict):
    """Create JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_from_token(request: Request):
    """Extract user from JWT token."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Pydantic models
class UserRegister(BaseModel):
    email: str
    password: str
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    """Register a new user."""
    try:
        db = await ensure_database()
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user document
        user_doc = {
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "hashed_password": hashed_password.decode('utf-8'),
            "is_active": True,
            "is_superuser": False,
            "role": "user",
            "usersubscription": "free",
            "created_at": datetime.utcnow()
        }
        
        # Insert user into database
        result = await db.users.insert_one(user_doc)
        
        # Create access token
        access_token = create_access_token(data={"sub": user_data.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(result.inserted_id),
                "email": user_data.email,
                "username": user_data.username,
                "full_name": user_data.full_name
            },
            "message": "User registered successfully"
        }
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    """Login user."""
    try:
        db = get_database()
        
        # Find user in database
        user = await db.users.find_one({"email": user_data.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not bcrypt.checkpw(user_data.password.encode('utf-8'), user['hashed_password'].encode('utf-8')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user_data.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user.get("username"),
                "full_name": user.get("full_name")
            }
        }
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@app.get("/api/auth/me")
async def get_current_user(request: Request):
    """Get current user information."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user.get("username"),
            "full_name": user.get("full_name"),
            "is_active": user.get("is_active", True),
            "role": user.get("role", "user"),
            "usersubscription": user.get("usersubscription", "free")
        }
        
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )

# ===== BASIC ENDPOINTS =====

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Email Bot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test MongoDB connection
        if client is not None:
            await client.admin.command('ping')
            db_status = "connected"
        else:
            db_status = "disconnected (client not initialized)"
    except Exception as e:
        db_status = f"disconnected (error: {str(e)})"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint."""
    return {
        "message": "Server is working!",
        "timestamp": datetime.utcnow().isoformat()
    }

# ===== FILE MANAGEMENT ENDPOINTS =====

@app.get("/api/files")
async def get_files(request: Request):
    """Get user's files."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        files = await db.files.find({"user_id": str(user["_id"])}).to_list(length=100)
        return {"files": files}
    except Exception as e:
        logger.error(f"Get files error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/files/upload")
async def upload_file(request: Request):
    """Upload a file."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # For now, return a mock response
        return {
            "message": "File upload endpoint",
            "user_id": str(user["_id"])
        }
    except Exception as e:
        logger.error(f"Upload file error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== TEMPLATE ENDPOINTS =====

@app.get("/api/templates")
async def get_templates(request: Request):
    """Get user's templates."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        templates = await db.templates.find({"user_id": str(user["_id"])}).to_list(length=100)
        return {"templates": templates}
    except Exception as e:
        logger.error(f"Get templates error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== SUBSCRIPTION ENDPOINTS =====

@app.get("/api/v1/subscriptions/current")
async def get_current_subscription(request: Request):
    """Get current subscription."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "subscription": user.get("usersubscription", "free"),
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Get subscription error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/subscriptions/usage")
async def get_usage_stats(request: Request):
    """Get usage statistics."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "emails_sent_this_month": 0,
            "emails_sent_total": 0,
            "senders_used": 0,
            "templates_created": 0,
            "campaigns_created": 0
        }
    except Exception as e:
        logger.error(f"Get usage error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize database on startup
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 