from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging
import os
from datetime import datetime, timedelta
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Email Bot API")

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
templates_db = {}
customers_db = {}
senders_db = {}
campaigns_db = {}
files_db = {}
sessions_db = {}  # Add session storage

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
        
        # Create unique UID for the user
        uid = f"user_{len(users_db) + 1}_{hash(email) % 100000}"
        user_id = uid
        
        users_db[email] = {
            "uid": uid,
            "id": user_id,
            "email": email,
            "username": username,
            "full_name": full_name,
            "password": password,
            "created_at": datetime.utcnow()
        }
        
        # Create access token with UID for automatic login
        access_token = create_access_token(data={"sub": email, "uid": uid})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "uid": uid,
                "id": user_id,
                "email": email,
                "username": username,
                "full_name": full_name
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
        access_token = create_access_token(data={"sub": email, "uid": user.get("uid", user["id"])})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "uid": user.get("uid", user["id"]),
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

@app.get("/api/auth/session/{session_id}")
async def get_session(session_id: str):
    """Get session data."""
    try:
        if session_id not in sessions_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        session = sessions_db[session_id]
        user_email = session["user_email"]
        
        if user_email not in users_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = users_db[user_email]
        
        return {
            "access_token": session["access_token"],
            "token_type": "bearer",
            "user": {
                "uid": user["uid"],
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "full_name": user["full_name"]
            }
        }
        
    except Exception as e:
        logger.error(f"Get session error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )

@app.get("/api/v1/google-auth/login-url")
async def get_google_login_url():
    """Get Google OAuth login URL."""
    try:
        client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "https://www.mailsflow.net/auth/callback")
        
        if not client_id:
            return {
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=test&redirect_uri=https://www.mailsflow.net/auth/callback&response_type=code&scope=email profile",
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
        # For now, we'll create a mock user based on the code
        # In production, you would exchange the code for user info from Google
        
        # Create a unique UID based on the code
        uid = f"google_{hash(code) % 100000}"
        user_email = f"google_user_{hash(code) % 10000}@example.com"
        
        # Create user data with UID
        user_data = {
            "uid": uid,
            "id": uid,
            "email": user_email,
            "username": "Google User",
            "full_name": "Google User"
        }
        
        # Create proper JWT access token with UID
        access_token = create_access_token(data={"sub": user_email, "uid": uid})
        
        # Store user in database (if not already exists)
        if user_email not in users_db:
            users_db[user_email] = {
                "uid": uid,
                "id": uid,
                "email": user_data["email"],
                "username": user_data["username"],
                "full_name": user_data["full_name"],
                "created_at": datetime.utcnow()
            }
        
        # Create a session
        session_id = f"session_{hash(code) % 100000}"
        sessions_db[session_id] = {
            "user_email": user_email,
            "uid": uid,
            "access_token": access_token,
            "created_at": datetime.utcnow()
        }
        
        # Redirect to dashboard with session ID
        dashboard_url = f"https://www.mailsflow.net/dashboard?session={session_id}"
        return RedirectResponse(url=dashboard_url)
        
    except Exception as e:
        logger.error(f"Google callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google callback failed: {str(e)}"
        )

# ===== STATS ENDPOINTS =====

@app.get("/api/stats/overview")
async def get_stats_overview():
    """Get overview statistics."""
    try:
        return {
            "total_campaigns": len(campaigns_db),
            "total_customers": len(customers_db),
            "total_templates": len(templates_db),
            "total_senders": len(senders_db),
            "total_files": len(files_db),
            "total_users": len(users_db)
        }
    except Exception as e:
        logger.error(f"Stats overview error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )

@app.get("/api/stats/campaigns")
async def get_campaign_stats():
    """Get campaign statistics."""
    try:
        return {
            "total_campaigns": len(campaigns_db),
            "active_campaigns": len([c for c in campaigns_db.values() if c.get("status") == "active"]),
            "completed_campaigns": len([c for c in campaigns_db.values() if c.get("status") == "completed"]),
            "draft_campaigns": len([c for c in campaigns_db.values() if c.get("status") == "draft"])
        }
    except Exception as e:
        logger.error(f"Campaign stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign stats: {str(e)}"
        )

# ===== TEMPLATES ENDPOINTS =====

@app.get("/api/templates")
async def get_templates():
    """Get all email templates."""
    try:
        return {
            "templates": list(templates_db.values()),
            "total": len(templates_db)
        }
    except Exception as e:
        logger.error(f"Get templates error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates: {str(e)}"
        )

@app.post("/api/templates")
async def create_template(request: Request):
    """Create a new email template."""
    try:
        body = await request.json()
        template_id = f"template_{len(templates_db) + 1}"
        
        template = {
            "id": template_id,
            "name": body.get("name", ""),
            "subject": body.get("subject", ""),
            "content": body.get("content", ""),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        templates_db[template_id] = template
        
        return template
    except Exception as e:
        logger.error(f"Create template error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )

@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template."""
    try:
        if template_id not in templates_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        return templates_db[template_id]
    except Exception as e:
        logger.error(f"Get template error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )

@app.put("/api/templates/{template_id}")
async def update_template(template_id: str, request: Request):
    """Update a template."""
    try:
        if template_id not in templates_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        body = await request.json()
        templates_db[template_id].update({
            "name": body.get("name", templates_db[template_id]["name"]),
            "subject": body.get("subject", templates_db[template_id]["subject"]),
            "content": body.get("content", templates_db[template_id]["content"]),
            "updated_at": datetime.utcnow().isoformat()
        })
        
        return templates_db[template_id]
    except Exception as e:
        logger.error(f"Update template error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}"
        )

@app.delete("/api/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete a template."""
    try:
        if template_id not in templates_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        deleted_template = templates_db.pop(template_id)
        return {"message": "Template deleted successfully", "template": deleted_template}
    except Exception as e:
        logger.error(f"Delete template error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete template: {str(e)}"
        )

# ===== CUSTOMERS ENDPOINTS =====

@app.get("/api/customers")
async def get_customers():
    """Get all customers."""
    try:
        return {
            "customers": list(customers_db.values()),
            "total": len(customers_db)
        }
    except Exception as e:
        logger.error(f"Get customers error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get customers: {str(e)}"
        )

@app.post("/api/customers")
async def create_customer(request: Request):
    """Create a new customer."""
    try:
        body = await request.json()
        customer_id = f"customer_{len(customers_db) + 1}"
        
        customer = {
            "id": customer_id,
            "email": body.get("email", ""),
            "name": body.get("name", ""),
            "phone": body.get("phone", ""),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        customers_db[customer_id] = customer
        
        return customer
    except Exception as e:
        logger.error(f"Create customer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create customer: {str(e)}"
        )

@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get a specific customer."""
    try:
        if customer_id not in customers_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return customers_db[customer_id]
    except Exception as e:
        logger.error(f"Get customer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get customer: {str(e)}"
        )

@app.put("/api/customers/{customer_id}")
async def update_customer(customer_id: str, request: Request):
    """Update a customer."""
    try:
        if customer_id not in customers_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        body = await request.json()
        customers_db[customer_id].update({
            "email": body.get("email", customers_db[customer_id]["email"]),
            "name": body.get("name", customers_db[customer_id]["name"]),
            "phone": body.get("phone", customers_db[customer_id]["phone"]),
            "updated_at": datetime.utcnow().isoformat()
        })
        
        return customers_db[customer_id]
    except Exception as e:
        logger.error(f"Update customer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update customer: {str(e)}"
        )

@app.delete("/api/customers/{customer_id}")
async def delete_customer(customer_id: str):
    """Delete a customer."""
    try:
        if customer_id not in customers_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        deleted_customer = customers_db.pop(customer_id)
        return {"message": "Customer deleted successfully", "customer": deleted_customer}
    except Exception as e:
        logger.error(f"Delete customer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete customer: {str(e)}"
        )

# ===== SENDERS ENDPOINTS =====

@app.get("/api/senders")
async def get_senders():
    """Get all senders."""
    try:
        return {
            "senders": list(senders_db.values()),
            "total": len(senders_db)
        }
    except Exception as e:
        logger.error(f"Get senders error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get senders: {str(e)}"
        )

@app.post("/api/senders")
async def create_sender(request: Request):
    """Create a new sender."""
    try:
        body = await request.json()
        sender_id = f"sender_{len(senders_db) + 1}"
        
        sender = {
            "id": sender_id,
            "email": body.get("email", ""),
            "name": body.get("name", ""),
            "verified": body.get("verified", False),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        senders_db[sender_id] = sender
        
        return sender
    except Exception as e:
        logger.error(f"Create sender error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sender: {str(e)}"
        )

@app.get("/api/senders/{sender_id}")
async def get_sender(sender_id: str):
    """Get a specific sender."""
    try:
        if sender_id not in senders_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )
        return senders_db[sender_id]
    except Exception as e:
        logger.error(f"Get sender error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sender: {str(e)}"
        )

@app.put("/api/senders/{sender_id}")
async def update_sender(sender_id: str, request: Request):
    """Update a sender."""
    try:
        if sender_id not in senders_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )
        
        body = await request.json()
        senders_db[sender_id].update({
            "email": body.get("email", senders_db[sender_id]["email"]),
            "name": body.get("name", senders_db[sender_id]["name"]),
            "verified": body.get("verified", senders_db[sender_id]["verified"]),
            "updated_at": datetime.utcnow().isoformat()
        })
        
        return senders_db[sender_id]
    except Exception as e:
        logger.error(f"Update sender error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update sender: {str(e)}"
        )

@app.delete("/api/senders/{sender_id}")
async def delete_sender(sender_id: str):
    """Delete a sender."""
    try:
        if sender_id not in senders_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )
        
        deleted_sender = senders_db.pop(sender_id)
        return {"message": "Sender deleted successfully", "sender": deleted_sender}
    except Exception as e:
        logger.error(f"Delete sender error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete sender: {str(e)}"
        )

# ===== CAMPAIGNS ENDPOINTS =====

@app.get("/api/campaigns")
async def get_campaigns():
    """Get all campaigns."""
    try:
        return {
            "campaigns": list(campaigns_db.values()),
            "total": len(campaigns_db)
        }
    except Exception as e:
        logger.error(f"Get campaigns error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaigns: {str(e)}"
        )

@app.post("/api/campaigns")
async def create_campaign(request: Request):
    """Create a new campaign."""
    try:
        body = await request.json()
        campaign_id = f"campaign_{len(campaigns_db) + 1}"
        
        campaign = {
            "id": campaign_id,
            "name": body.get("name", ""),
            "subject": body.get("subject", ""),
            "content": body.get("content", ""),
            "status": body.get("status", "draft"),
            "sender_id": body.get("sender_id", ""),
            "template_id": body.get("template_id", ""),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        campaigns_db[campaign_id] = campaign
        
        return campaign
    except Exception as e:
        logger.error(f"Create campaign error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get a specific campaign."""
    try:
        if campaign_id not in campaigns_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        return campaigns_db[campaign_id]
    except Exception as e:
        logger.error(f"Get campaign error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign: {str(e)}"
        )

@app.put("/api/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, request: Request):
    """Update a campaign."""
    try:
        if campaign_id not in campaigns_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        body = await request.json()
        campaigns_db[campaign_id].update({
            "name": body.get("name", campaigns_db[campaign_id]["name"]),
            "subject": body.get("subject", campaigns_db[campaign_id]["subject"]),
            "content": body.get("content", campaigns_db[campaign_id]["content"]),
            "status": body.get("status", campaigns_db[campaign_id]["status"]),
            "sender_id": body.get("sender_id", campaigns_db[campaign_id]["sender_id"]),
            "template_id": body.get("template_id", campaigns_db[campaign_id]["template_id"]),
            "updated_at": datetime.utcnow().isoformat()
        })
        
        return campaigns_db[campaign_id]
    except Exception as e:
        logger.error(f"Update campaign error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}"
        )

@app.delete("/api/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Delete a campaign."""
    try:
        if campaign_id not in campaigns_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        deleted_campaign = campaigns_db.pop(campaign_id)
        return {"message": "Campaign deleted successfully", "campaign": deleted_campaign}
    except Exception as e:
        logger.error(f"Delete campaign error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )

@app.post("/api/campaigns/{campaign_id}/send")
async def send_campaign(campaign_id: str):
    """Send a campaign."""
    try:
        if campaign_id not in campaigns_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        campaigns_db[campaign_id]["status"] = "sent"
        campaigns_db[campaign_id]["sent_at"] = datetime.utcnow().isoformat()
        
        return {
            "message": "Campaign sent successfully",
            "campaign_id": campaign_id
        }
    except Exception as e:
        logger.error(f"Send campaign error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send campaign: {str(e)}"
        )

# ===== FILES ENDPOINTS =====

@app.get("/api/files")
async def get_files():
    """Get all files."""
    try:
        return {
            "files": list(files_db.values()),
            "total": len(files_db)
        }
    except Exception as e:
        logger.error(f"Get files error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get files: {str(e)}"
        )

@app.post("/api/files")
async def create_file(request: Request):
    """Create a new file record."""
    try:
        body = await request.json()
        file_id = f"file_{len(files_db) + 1}"
        
        file_record = {
            "id": file_id,
            "name": body.get("name", ""),
            "type": body.get("type", ""),
            "size": body.get("size", 0),
            "url": body.get("url", ""),
            "created_at": datetime.utcnow().isoformat()
        }
        
        files_db[file_id] = file_record
        
        return file_record
    except Exception as e:
        logger.error(f"Create file error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create file: {str(e)}"
        )

@app.get("/api/files/{file_id}")
async def get_file(file_id: str):
    """Get a specific file."""
    try:
        if file_id not in files_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        return files_db[file_id]
    except Exception as e:
        logger.error(f"Get file error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file: {str(e)}"
        )

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file."""
    try:
        if file_id not in files_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        deleted_file = files_db.pop(file_id)
        return {"message": "File deleted successfully", "file": deleted_file}
    except Exception as e:
        logger.error(f"Delete file error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )

# ===== SUBSCRIPTIONS ENDPOINTS =====

@app.get("/api/subscriptions")
async def get_subscriptions():
    """Get all subscriptions."""
    try:
        return {
            "subscriptions": [],
            "total": 0,
            "message": "No subscriptions found"
        }
    except Exception as e:
        logger.error(f"Get subscriptions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscriptions: {str(e)}"
        )

@app.post("/api/subscriptions")
async def create_subscription(request: Request):
    """Create a new subscription."""
    try:
        body = await request.json()
        return {
            "id": "sub_1",
            "plan": body.get("plan", "basic"),
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Create subscription error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )

# ===== BASIC ENDPOINTS =====

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Email Bot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": "/api/auth/*",
            "stats": "/api/stats/*",
            "templates": "/api/templates/*",
            "customers": "/api/customers/*",
            "senders": "/api/senders/*",
            "campaigns": "/api/campaigns/*",
            "files": "/api/files/*",
            "subscriptions": "/api/subscriptions/*"
        }
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
        "message": "Email Bot API is working!",
        "users_count": len(users_db),
        "templates_count": len(templates_db),
        "customers_count": len(customers_db),
        "senders_count": len(senders_db),
        "campaigns_count": len(campaigns_db),
        "files_count": len(files_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 