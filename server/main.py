from fastapi import FastAPI, Request, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, Depends
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import jwt
import json

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info("=" * 50)
logger.info("EMAIL BOT API STARTING UP - FULL VERSION")
logger.info("=" * 50)
logger.info(f"Environment: {'production' if os.getenv('VERCEL_ENV') else 'development'}")
logger.info(f"Python version: {os.sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")

app = FastAPI(
    title="Email Bot API - Full Version",
    description="Email automation and customer management API",
    version="1.0.0"
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses."""
    start_time = time.time()
    
    # Log request details
    logger.info(f"REQUEST: {request.method} {request.url}")
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Client IP: {client_ip}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response details
        logger.info(f"RESPONSE: {response.status_code} - {process_time:.3f}s")
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"ERROR: {request.method} {request.url} - {str(e)} - {process_time:.3f}s")
        raise

# Configure CORS with detailed logging
logger.info("Configuring CORS...")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS configured successfully")

# Simple data storage (in memory for now)
users_db = {}
templates_db = {}
customers_db = {}
senders_db = {}
campaigns_db = {}
files_db = {}

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return {"email": email}
    except jwt.PyJWTError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """Get current user from token."""
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    email = token_data["email"]
    if email not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return users_db[email]

# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/api/auth/register")
async def register(request: Request):
    """Register a new user."""
    logger.info("=" * 40)
    logger.info("AUTH: User registration attempt")
    logger.info("=" * 40)
    
    try:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        username = body.get("username", "")
        full_name = body.get("full_name", "")
        
        logger.info(f"User email: {email}")
        logger.info(f"Username: {username}")
        
        if not email or not password:
            logger.error("❌ ERROR: Missing email or password")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        if email in users_db:
            logger.error(f"❌ ERROR: Email already registered - {email}")
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
            "hashed_password": password,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        logger.info(f"✅ SUCCESS: User registered successfully - ID: {user_id}")
        
        return {
            "id": user_id,
            "email": email,
            "username": username,
            "full_name": full_name,
            "role": "user",
            "created_at": users_db[email]["created_at"],
            "is_active": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ UNEXPECTED ERROR: Registration failed - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/api/auth/login")
async def login(request: Request):
    """Login user and return access token."""
    logger.info("=" * 40)
    logger.info("AUTH: User login attempt")
    logger.info("=" * 40)
    
    try:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        
        logger.info(f"User email: {email}")
        
        if not email or not password:
            logger.error("❌ ERROR: Missing email or password")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        if email not in users_db or users_db[email]["hashed_password"] != password:
            logger.error(f"❌ ERROR: Invalid credentials for email: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        user = users_db[email]
        logger.info(f"✅ SUCCESS: User authenticated - ID: {user['id']}")
        
        access_token = create_access_token(data={"sub": email})
        logger.info(f"✅ SUCCESS: Access token created - Length: {len(access_token)}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": "user",
                "created_at": user["created_at"],
                "is_active": user["is_active"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ UNEXPECTED ERROR: Login failed - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user."""
    logger.info("=" * 40)
    logger.info("AUTH: Get current user attempt")
    logger.info("=" * 40)
    
    logger.info(f"✅ SUCCESS: User retrieved successfully - ID: {current_user['id']}")
    
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "role": "user",
        "created_at": current_user["created_at"],
        "is_active": current_user["is_active"]
    }

# ===== STATS ENDPOINTS =====

@app.get("/api/stats/summary")
async def get_stats_summary(current_user: dict = Depends(get_current_user)):
    """Get user statistics summary."""
    logger.info("STATS: Summary requested")
    
    user_id = current_user["id"]
    
    # Count user's data
    user_templates = len([t for t in templates_db.values() if t.get("user_id") == user_id])
    user_customers = len([c for c in customers_db.values() if c.get("user_id") == user_id])
    user_campaigns = len([c for c in campaigns_db.values() if c.get("user_id") == user_id])
    user_senders = len([s for s in senders_db.values() if s.get("user_id") == user_id])
    
    return {
        "templates_count": user_templates,
        "customers_count": user_customers,
        "campaigns_count": user_campaigns,
        "senders_count": user_senders,
        "emails_sent": 0,  # Mock data
        "emails_delivered": 0,  # Mock data
        "emails_bounced": 0,  # Mock data
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/stats/activity")
async def get_stats_activity(current_user: dict = Depends(get_current_user)):
    """Get user activity statistics."""
    logger.info("STATS: Activity requested")
    
    return {
        "recent_activity": [
            {
                "id": "1",
                "type": "campaign_sent",
                "description": "Campaign 'Welcome Series' sent to 150 recipients",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "completed"
            },
            {
                "id": "2",
                "type": "template_created",
                "description": "Template 'Newsletter Template' created",
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "status": "completed"
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

# ===== TEMPLATES ENDPOINTS =====

@app.get("/api/templates")
async def get_templates(current_user: dict = Depends(get_current_user)):
    """Get all templates for user."""
    logger.info("TEMPLATES: Get all templates")
    
    user_id = current_user["id"]
    user_templates = [t for t in templates_db.values() if t.get("user_id") == user_id]
    
    return {
        "templates": user_templates,
        "count": len(user_templates)
    }

@app.post("/api/templates")
async def create_template(request: Request, current_user: dict = Depends(get_current_user)):
    """Create a new template."""
    logger.info("TEMPLATES: Create template")
    
    try:
        body = await request.json()
        template_id = f"template_{len(templates_db) + 1}"
        
        template = {
            "id": template_id,
            "user_id": current_user["id"],
            "name": body.get("name", "Untitled Template"),
            "subject": body.get("subject", ""),
            "content": body.get("content", ""),
            "html_content": body.get("html_content", ""),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        templates_db[template_id] = template
        
        return template
    except Exception as e:
        logger.error(f"❌ ERROR: Create template failed - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )

# ===== CUSTOMERS ENDPOINTS =====

@app.get("/api/customers")
async def get_customers(current_user: dict = Depends(get_current_user)):
    """Get all customers for user."""
    logger.info("CUSTOMERS: Get all customers")
    
    user_id = current_user["id"]
    user_customers = [c for c in customers_db.values() if c.get("user_id") == user_id]
    
    return {
        "customers": user_customers,
        "count": len(user_customers)
    }

@app.post("/api/customers")
async def create_customer(request: Request, current_user: dict = Depends(get_current_user)):
    """Create a new customer."""
    logger.info("CUSTOMERS: Create customer")
    
    try:
        body = await request.json()
        customer_id = f"customer_{len(customers_db) + 1}"
        
        customer = {
            "id": customer_id,
            "user_id": current_user["id"],
            "email": body.get("email", ""),
            "name": body.get("name", ""),
            "phone": body.get("phone", ""),
            "company": body.get("company", ""),
            "created_at": datetime.utcnow().isoformat()
        }
        
        customers_db[customer_id] = customer
        
        return customer
    except Exception as e:
        logger.error(f"❌ ERROR: Create customer failed - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create customer: {str(e)}"
        )

# ===== SENDERS ENDPOINTS =====

@app.get("/api/senders")
async def get_senders(current_user: dict = Depends(get_current_user)):
    """Get all senders for user."""
    logger.info("SENDERS: Get all senders")
    
    user_id = current_user["id"]
    user_senders = [s for s in senders_db.values() if s.get("user_id") == user_id]
    
    return {
        "senders": user_senders,
        "count": len(user_senders)
    }

@app.post("/api/senders")
async def create_sender(request: Request, current_user: dict = Depends(get_current_user)):
    """Create a new sender."""
    logger.info("SENDERS: Create sender")
    
    try:
        body = await request.json()
        sender_id = f"sender_{len(senders_db) + 1}"
        
        sender = {
            "id": sender_id,
            "user_id": current_user["id"],
            "email": body.get("email", ""),
            "display_name": body.get("display_name", ""),
            "is_default": body.get("is_default", False),
            "verification_status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        senders_db[sender_id] = sender
        
        return sender
    except Exception as e:
        logger.error(f"❌ ERROR: Create sender failed - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sender: {str(e)}"
        )

# ===== CAMPAIGNS ENDPOINTS =====

@app.get("/api/campaigns")
async def get_campaigns(current_user: dict = Depends(get_current_user)):
    """Get all campaigns for user."""
    logger.info("CAMPAIGNS: Get all campaigns")
    
    user_id = current_user["id"]
    user_campaigns = [c for c in campaigns_db.values() if c.get("user_id") == user_id]
    
    return {
        "campaigns": user_campaigns,
        "count": len(user_campaigns)
    }

@app.post("/api/campaigns")
async def create_campaign(request: Request, current_user: dict = Depends(get_current_user)):
    """Create a new campaign."""
    logger.info("CAMPAIGNS: Create campaign")
    
    try:
        body = await request.json()
        campaign_id = f"campaign_{len(campaigns_db) + 1}"
        
        campaign = {
            "id": campaign_id,
            "user_id": current_user["id"],
            "name": body.get("name", "Untitled Campaign"),
            "subject": body.get("subject", ""),
            "template_id": body.get("template_id", ""),
            "sender_email": body.get("sender_email", ""),
            "status": "draft",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        campaigns_db[campaign_id] = campaign
        
        return campaign
    except Exception as e:
        logger.error(f"❌ ERROR: Create campaign failed - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

# ===== FILES ENDPOINTS =====

@app.get("/api/files")
async def get_files(current_user: dict = Depends(get_current_user)):
    """Get all files for user."""
    logger.info("FILES: Get all files")
    
    user_id = current_user["id"]
    user_files = [f for f in files_db.values() if f.get("user_id") == user_id]
    
    return {
        "files": user_files,
        "count": len(user_files)
    }

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload a file."""
    logger.info("FILES: Upload file")
    
    try:
        file_id = f"file_{len(files_db) + 1}"
        
        file_info = {
            "id": file_id,
            "user_id": current_user["id"],
            "filename": file.filename,
            "content_type": file.content_type,
            "size": 0,  # Mock size
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        files_db[file_id] = file_info
        
        return file_info
    except Exception as e:
        logger.error(f"❌ ERROR: Upload file failed - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

# ===== SUBSCRIPTIONS ENDPOINTS =====

@app.get("/api/v1/subscriptions/current")
async def get_current_subscription(current_user: dict = Depends(get_current_user)):
    """Get current subscription."""
    logger.info("SUBSCRIPTIONS: Get current subscription")
    
    return {
        "subscription": {
            "id": "sub_123",
            "status": "active",
            "plan": "pro",
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "cancel_at_period_end": False
        }
    }

# ===== GOOGLE OAUTH ENDPOINTS =====

@app.get("/api/v1/google-auth/login-url")
async def get_google_login_url():
    """Get Google OAuth login URL."""
    logger.info("GOOGLE OAUTH: Get login URL")
    
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/google-auth/callback")
    
    if not client_id:
        logger.error("❌ ERROR: Google Client ID not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=email profile"
    
    return {
        "auth_url": auth_url,
        "client_id": client_id
    }

@app.get("/api/v1/google-auth/callback")
async def google_auth_callback(code: str):
    """Handle Google OAuth callback."""
    logger.info("GOOGLE OAUTH: Callback received")
    
    # Mock implementation - in real app, exchange code for tokens
    return {
        "message": "Google OAuth callback received",
        "code": code
    }

# ===== BASIC ENDPOINTS =====

@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("ROOT: Root endpoint accessed")
    return {
        "message": "Email Bot API - Full Version",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "production" if os.getenv('VERCEL_ENV') else "development"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("HEALTH: Health check endpoint accessed")
    
    return {
        "status": "healthy", 
        "mode": "full-version",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Full version with all endpoints working!"
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint."""
    logger.info("TEST: Test endpoint accessed")
    return {
        "message": "Full backend with all endpoints is working!",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/debug")
async def debug_endpoint():
    """Debug endpoint to show environment."""
    logger.info("DEBUG: Debug endpoint accessed")
    
    return {
        "environment": "production" if os.getenv('VERCEL_ENV') else "development",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "full-version",
        "users_count": len(users_db),
        "templates_count": len(templates_db),
        "customers_count": len(customers_db),
        "senders_count": len(senders_db),
        "campaigns_count": len(campaigns_db),
        "files_count": len(files_db)
    }

# Test basic imports
@app.get("/test-imports")
async def test_imports():
    """Test if basic imports work."""
    logger.info("TEST-IMPORTS: Testing basic imports")
    
    results = {}
    
    # Test pydantic
    try:
        from pydantic import BaseModel
        results["pydantic"] = "✅ Working"
    except Exception as e:
        results["pydantic"] = f"❌ Failed: {e}"
    
    # Test pydantic-settings
    try:
        from pydantic_settings import BaseSettings
        results["pydantic-settings"] = "✅ Working"
    except Exception as e:
        results["pydantic-settings"] = f"❌ Failed: {e}"
    
    # Test motor (MongoDB)
    try:
        import motor
        results["motor"] = "✅ Working"
    except Exception as e:
        results["motor"] = f"❌ Failed: {e}"
    
    # Test PyJWT
    try:
        import jwt
        results["PyJWT"] = "✅ Working"
    except Exception as e:
        results["PyJWT"] = f"❌ Failed: {e}"
    
    return {
        "import_tests": results,
        "timestamp": datetime.utcnow().isoformat()
    }

# Export the app for Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 