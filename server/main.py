from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from datetime import datetime, timedelta
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Email Bot API - Auth Only")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage
users_db = {}

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    """Create JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/api/auth/register")
async def register(request: Request):
    """Register a new user."""
    try:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        username = body.get("username", "")
        full_name = body.get("full_name", "")
        
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        if email in users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user_id = f"user_{len(users_db) + 1}"
        users_db[email] = {
            "id": user_id,
            "email": email,
            "username": username,
            "full_name": full_name,
            "password": password,
            "created_at": datetime.utcnow()
        }
        
        return {
            "id": user_id,
            "email": email,
            "username": username,
            "full_name": full_name,
            "message": "User registered successfully"
        }
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/api/auth/login")
async def login(request: Request):
    """Login user."""
    try:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        if email not in users_db or users_db[email]["password"] != password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = users_db[email]
        access_token = create_access_token(data={"sub": email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "full_name": user["full_name"]
            }
        }
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@app.get("/api/v1/google-auth/login-url")
async def get_google_login_url():
    """Get Google OAuth login URL."""
    try:
        client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback")
        
        if not client_id:
            return {
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=test&redirect_uri=http://localhost:3000/auth/callback&response_type=code&scope=email profile",
                "client_id": "test",
                "message": "Using test client ID"
            }
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=email profile"
        
        return {
            "auth_url": auth_url,
            "client_id": client_id
        }
        
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google OAuth failed: {str(e)}"
        )

@app.get("/api/v1/google-auth/callback")
async def google_auth_callback(code: str):
    """Handle Google OAuth callback."""
    try:
        # Mock implementation - in real app, exchange code for tokens
        return {
            "message": "Google OAuth callback received",
            "code": code,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Google callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google callback failed: {str(e)}"
        )

# ===== BASIC ENDPOINTS =====

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Email Bot API - Auth Only",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/test")
async def test():
    """Test endpoint."""
    return {
        "message": "Auth API is working!",
        "users_count": len(users_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 