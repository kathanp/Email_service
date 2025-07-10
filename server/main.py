from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
import pymongo
from bson import ObjectId
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

# Global MongoDB client for serverless
mongo_client = pymongo.MongoClient(MONGODB_URL)
database = mongo_client[DATABASE_NAME]

def get_database():
    return database

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
def register(user_data: UserRegister):
    """Register a new user."""
    try:
        db = get_database()
        # Check if user already exists
        existing_user = db.users.find_one({"email": user_data.email})
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
        result = db.users.insert_one(user_doc)
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
def login(user_data: UserLogin):
    """Login user."""
    try:
        db = get_database()
        # Find user in database
        user = db.users.find_one({"email": user_data.email})
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
def get_current_user(request: Request):
    """Get current user information."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
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
def root():
    """Root endpoint."""
    return {
        "message": "Email Bot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    try:
        db = get_database()
        db_status = "connected" if db.command("ping") else "disconnected"
    except Exception as e:
        db_status = f"disconnected (error: {str(e)})"
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/test")
def test_endpoint():
    """Test endpoint."""
    return {
        "message": "Server is working!",
        "timestamp": datetime.utcnow().isoformat()
    }

# ===== FILE MANAGEMENT ENDPOINTS =====

@app.get("/api/files")
def get_files(request: Request):
    """Get user's files."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get only files belonging to this user
        files = list(db.files.find({"user_id": str(user["_id"])}))
        
        # Convert ObjectId to string for JSON serialization
        for file in files:
            file["id"] = str(file["_id"])
            del file["_id"]
            # Ensure all dates are serializable
            if "upload_date" in file:
                file["upload_date"] = file["upload_date"].isoformat()
            if "processed_date" in file:
                file["processed_date"] = file["processed_date"].isoformat()
        
        return {"files": files}
    except Exception as e:
        logger.error(f"Get files error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/files/upload")
def upload_file(request: Request):
    """Upload a file."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # For now, return a mock response with user-specific file info
        file_doc = {
            "user_id": str(user["_id"]),
            "filename": "sample_file.xlsx",
            "file_size": 1024,
            "upload_date": datetime.utcnow(),
            "processed": False,
            "contacts_count": 0,
            "file_type": "excel"
        }
        
        result = db.files.insert_one(file_doc)
        file_doc["id"] = str(result.inserted_id)
        del file_doc["_id"]
        file_doc["upload_date"] = file_doc["upload_date"].isoformat()
        
        return {
            "message": "File uploaded successfully",
            "file": file_doc,
            "user_id": str(user["_id"])
        }
    except Exception as e:
        logger.error(f"Upload file error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/files/{file_id}")
def delete_file(request: Request, file_id: str):
    """Delete a user's file."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Ensure the file belongs to the user
        file = db.files.find_one({
            "_id": ObjectId(file_id),
            "user_id": str(user["_id"])
        })
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete the file
        db.files.delete_one({"_id": ObjectId(file_id)})
        
        return {"message": "File deleted successfully"}
    except Exception as e:
        logger.error(f"Delete file error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/files/{file_id}/process")
def process_file(request: Request, file_id: str):
    """Process a user's file."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Ensure the file belongs to the user
        file = db.files.find_one({
            "_id": ObjectId(file_id),
            "user_id": str(user["_id"])
        })
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Mock processing - in real implementation, this would parse the file
        contacts_count = 150  # Mock contact count
        
        # Update file status
        db.files.update_one(
            {"_id": ObjectId(file_id)},
            {
                "$set": {
                    "processed": True,
                    "contacts_count": contacts_count,
                    "processed_date": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "File processed successfully",
            "contacts_count": contacts_count
        }
    except Exception as e:
        logger.error(f"Process file error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/{file_id}/preview")
def preview_file(request: Request, file_id: str):
    """Preview a user's file."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Ensure the file belongs to the user
        file = db.files.find_one({
            "_id": ObjectId(file_id),
            "user_id": str(user["_id"])
        })
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Mock preview data - in real implementation, this would read the file
        mock_contacts = [
            {"name": "John Doe", "email": "john@example.com", "phone": "123-456-7890"},
            {"name": "Jane Smith", "email": "jane@example.com", "phone": "098-765-4321"},
            {"name": "Bob Johnson", "email": "bob@example.com", "phone": "555-123-4567"}
        ]
        
        return {
            "file_id": str(file["_id"]),
            "file_name": file.get("filename", "Unknown"),
            "contacts": mock_contacts,
            "total_contacts": file.get("contacts_count", len(mock_contacts))
        }
    except Exception as e:
        logger.error(f"Preview file error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== TEMPLATE ENDPOINTS =====

@app.get("/api/templates")
def get_templates(request: Request):
    """Get user's templates."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get only templates belonging to this user
        templates = list(db.templates.find({"user_id": str(user["_id"])}))
        
        # Convert ObjectId to string for JSON serialization
        for template in templates:
            template["id"] = str(template["_id"])
            del template["_id"]
            # Ensure all dates are serializable
            if "created_at" in template:
                template["created_at"] = template["created_at"].isoformat()
        
        return {"templates": templates}
    except Exception as e:
        logger.error(f"Get templates error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/templates")
def create_template(request: Request):
    """Create a new template for the user."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Mock template creation
        template_doc = {
            "user_id": str(user["_id"]),
            "name": "Sample Template",
            "subject": "Welcome to our service!",
            "content": "Hello {{name}},\n\nThank you for joining us!\n\nBest regards,\nYour Team",
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = db.templates.insert_one(template_doc)
        template_doc["id"] = str(result.inserted_id)
        del template_doc["_id"]
        template_doc["created_at"] = template_doc["created_at"].isoformat()
        
        return {
            "message": "Template created successfully",
            "template": template_doc
        }
    except Exception as e:
        logger.error(f"Create template error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== SUBSCRIPTION ENDPOINTS =====

@app.get("/api/v1/subscriptions/current")
def get_current_subscription(request: Request):
    """Get current subscription."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
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
def get_usage_stats(request: Request):
    """Get usage statistics."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
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