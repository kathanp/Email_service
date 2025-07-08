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

# Simple in-memory storage - now user-specific
users_db = {}
user_templates_db = {}  # user_id -> templates
user_customers_db = {}  # user_id -> customers  
user_senders_db = {}    # user_id -> senders
user_campaigns_db = {}  # user_id -> campaigns
user_files_db = {}      # user_id -> files
user_subscriptions_db = {}  # user_id -> subscriptions
user_usage_db = {}      # user_id -> usage stats
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
        uid = payload.get("uid")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return email, uid
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

def get_user_data(user_id: str):
    """Get or create user-specific data structures."""
    if user_id not in user_templates_db:
        user_templates_db[user_id] = {}
    if user_id not in user_customers_db:
        user_customers_db[user_id] = {}
    if user_id not in user_senders_db:
        user_senders_db[user_id] = {}
    if user_id not in user_campaigns_db:
        user_campaigns_db[user_id] = {}
    if user_id not in user_files_db:
        user_files_db[user_id] = {}
    if user_id not in user_subscriptions_db:
        user_subscriptions_db[user_id] = {}
    if user_id not in user_usage_db:
        user_usage_db[user_id] = {
            "emails_sent_this_month": 0,
            "emails_sent_total": 0,
            "senders_used": 0,
            "templates_created": 0,
            "campaigns_created": 0
        }
    
    return {
        "templates": user_templates_db[user_id],
        "customers": user_customers_db[user_id],
        "senders": user_senders_db[user_id],
        "campaigns": user_campaigns_db[user_id],
        "files": user_files_db[user_id],
        "subscriptions": user_subscriptions_db[user_id],
        "usage": user_usage_db[user_id]
    }

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

@app.get("/api/auth/me")
async def get_current_user(request: Request):
    """Get current user information."""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header"
            )
        
        token = auth_header.split(" ")[1]
        
        # Decode the token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
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
        
        # Get user from database
        if email not in users_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = users_db[email]
        return {
            "uid": user.get("uid", user["id"]),
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user["full_name"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current user: {str(e)}"
        )

@app.get("/api/auth/session/{session_id}")
async def get_session(session_id: str):
    """Get session data."""
    try:
        logger.info(f"Getting session: {session_id}")
        logger.info(f"Available sessions: {list(sessions_db.keys())}")
        
        if session_id not in sessions_db:
            logger.error(f"Session {session_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        session = sessions_db[session_id]
        logger.info(f"Session found: {session}")
        
        user_email = session["user_email"]
        
        if user_email not in users_db:
            logger.error(f"User {user_email} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_email} not found"
            )
        
        user = users_db[user_email]
        logger.info(f"User found: {user}")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )

@app.get("/api/v1/google-auth/login-url")
async def get_google_login_url(request: Request):
    """Get Google OAuth login URL."""
    try:
        client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        
        # Use localhost for local development, production URL for production
        host = request.headers.get("host", "")
        if "localhost" in host or "127.0.0.1" in host:
            redirect_uri = "http://localhost:8000/api/v1/google-auth/callback"
        else:
            redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "https://www.mailsflow.net/auth/callback")
        
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth client ID not configured"
            )
        
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
async def google_auth_callback(code: str, request: Request):
    """Handle Google OAuth callback for production."""
    try:
        logger.info(f"Google OAuth callback received with code: {code}")
        
        # Mock implementation - in real app, exchange code for tokens
        # For now, we'll create a mock user based on the code
        # In production, you would exchange the code for user info from Google
        
        # Create a unique UID based on the code
        uid = f"google_{hash(code) % 100000}"
        user_email = f"google_user_{hash(code) % 10000}@example.com"
        
        logger.info(f"Created UID: {uid}, Email: {user_email}")
        
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
            logger.info(f"User stored in database: {users_db[user_email]}")
        
        # Create a session
        session_id = f"session_{hash(code) % 100000}"
        sessions_db[session_id] = {
            "user_email": user_email,
            "uid": uid,
            "access_token": access_token,
            "created_at": datetime.utcnow()
        }
        
        logger.info(f"Session created: {session_id}")
        logger.info(f"Available sessions: {list(sessions_db.keys())}")
        
        # Redirect to dashboard with session ID
        # Use localhost for local development, production URL for production
        host = request.headers.get("host", "")
        referer = request.headers.get("referer", "")
        
        if "localhost" in host or "127.0.0.1" in host:
            # Try to detect the frontend port from referer header
            if referer and "localhost:" in referer:
                # Extract port from referer (e.g., "http://localhost:3001/")
                port_match = referer.split("localhost:")[1].split("/")[0]
                frontend_port = port_match if port_match.isdigit() else "3001"
                dashboard_url = f"http://localhost:{frontend_port}/dashboard?session={session_id}"
            else:
                # Default to 3001 if we can't detect the port
                dashboard_url = f"http://localhost:3001/dashboard?session={session_id}"
        else:
            dashboard_url = f"https://www.mailsflow.net/dashboard?session={session_id}"
        
        logger.info(f"Redirecting to: {dashboard_url}")
        
        return RedirectResponse(url=dashboard_url)
        
    except Exception as e:
        logger.error(f"Google callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google callback failed: {str(e)}"
        )



# ===== STATS ENDPOINTS =====

@app.get("/api/stats/overview")
async def get_stats_overview(request: Request):
    """Get overview statistics for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        return {
            "total_campaigns": len(user_data["campaigns"]),
            "total_customers": len(user_data["customers"]),
            "total_templates": len(user_data["templates"]),
            "total_senders": len(user_data["senders"]),
            "total_files": len(user_data["files"]),
            "total_users": 1  # Current user only
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get stats overview error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats overview: {str(e)}"
        )

@app.get("/api/stats/campaigns")
async def get_campaign_stats(request: Request):
    """Get campaign statistics for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        campaigns = user_data["campaigns"]
        total_campaigns = len(campaigns)
        sent_campaigns = len([c for c in campaigns.values() if c.get("status") == "sent"])
        draft_campaigns = len([c for c in campaigns.values() if c.get("status") == "draft"])
        
        return {
            "total_campaigns": total_campaigns,
            "sent_campaigns": sent_campaigns,
            "draft_campaigns": draft_campaigns,
            "campaigns": list(campaigns.values())
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get campaign stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign stats: {str(e)}"
        )

# ===== TEMPLATES ENDPOINTS =====

@app.get("/api/templates")
async def get_templates(request: Request):
    """Get all templates for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        return {
            "templates": list(user_data["templates"].values()),
            "total": len(user_data["templates"])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get templates error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates: {str(e)}"
        )

@app.post("/api/templates")
async def create_template(request: Request):
    """Create a new template for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        body = await request.json()
        template_id = f"template_{len(user_data['templates']) + 1}_{uid}"
        
        template = {
            "id": template_id,
            "name": body.get("name", ""),
            "subject": body.get("subject", ""),
            "content": body.get("content", ""),
            "is_default": body.get("is_default", False),
            "created_at": datetime.utcnow().isoformat(),
            "user_id": uid
        }
        
        user_data["templates"][template_id] = template
        
        # Update usage stats
        user_data["usage"]["templates_created"] += 1
        
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create template error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )

@app.get("/api/templates/{template_id}")
async def get_template(template_id: str, request: Request):
    """Get a specific template for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if template_id not in user_data["templates"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        return user_data["templates"][template_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get template error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )

@app.put("/api/templates/{template_id}")
async def update_template(template_id: str, request: Request):
    """Update a template for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if template_id not in user_data["templates"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        body = await request.json()
        template = user_data["templates"][template_id]
        
        template.update({
            "name": body.get("name", template["name"]),
            "subject": body.get("subject", template["subject"]),
            "content": body.get("content", template["content"]),
            "updated_at": datetime.utcnow().isoformat()
        })
        
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update template error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}"
        )

@app.delete("/api/templates/{template_id}")
async def delete_template(template_id: str, request: Request):
    """Delete a template for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if template_id not in user_data["templates"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        deleted_template = user_data["templates"].pop(template_id)
        return {"message": "Template deleted successfully", "template": deleted_template}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete template error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete template: {str(e)}"
        )

@app.post("/api/templates/{template_id}/set-default")
async def set_default_template(template_id: str, request: Request):
    """Set a template as default for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if template_id not in user_data["templates"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Set all templates as non-default first
        for template in user_data["templates"].values():
            template["is_default"] = False
        
        # Set the specified template as default
        user_data["templates"][template_id]["is_default"] = True
        user_data["templates"][template_id]["updated_at"] = datetime.utcnow().isoformat()
        
        return {
            "message": "Default template updated successfully",
            "template_id": template_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set default template error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set default template: {str(e)}"
        )

# ===== CUSTOMERS ENDPOINTS =====

@app.get("/api/customers")
async def get_customers(request: Request):
    """Get all customers for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        return {
            "customers": list(user_data["customers"].values()),
            "total": len(user_data["customers"])
        }
    except HTTPException:
        raise
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
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        body = await request.json()
        
        customer_id = f"customer_{len(user_data['customers']) + 1}"
        
        customer = {
            "id": customer_id,
            "email": body.get("email", ""),
            "name": body.get("name", ""),
            "phone": body.get("phone", ""),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        user_data["customers"][customer_id] = customer
        
        return customer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create customer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create customer: {str(e)}"
        )

@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: str, request: Request):
    """Get a specific customer."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if customer_id not in user_data["customers"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return user_data["customers"][customer_id]
    except HTTPException:
        raise
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
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if customer_id not in user_data["customers"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        body = await request.json()
        user_data["customers"][customer_id].update({
            "email": body.get("email", user_data["customers"][customer_id]["email"]),
            "name": body.get("name", user_data["customers"][customer_id]["name"]),
            "phone": body.get("phone", user_data["customers"][customer_id]["phone"]),
            "updated_at": datetime.utcnow().isoformat()
        })
        
        return user_data["customers"][customer_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update customer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update customer: {str(e)}"
        )

@app.delete("/api/customers/{customer_id}")
async def delete_customer(customer_id: str, request: Request):
    """Delete a customer."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if customer_id not in user_data["customers"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        deleted_customer = user_data["customers"].pop(customer_id)
        return {"message": "Customer deleted successfully", "customer": deleted_customer}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete customer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete customer: {str(e)}"
        )

# ===== SENDERS ENDPOINTS =====

@app.get("/api/senders")
async def get_senders(request: Request):
    """Get all senders for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        return {
            "senders": list(user_data["senders"].values()),
            "total": len(user_data["senders"])
        }
    except HTTPException:
        raise
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
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        body = await request.json()
        
        sender_id = f"sender_{len(user_data['senders']) + 1}"
        
        sender = {
            "id": sender_id,
            "email": body.get("email", ""),
            "name": body.get("name", ""),
            "verified": body.get("verified", False),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        user_data["senders"][sender_id] = sender
        
        return sender
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create sender error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sender: {str(e)}"
        )

@app.get("/api/senders/{sender_id}")
async def get_sender(sender_id: str, request: Request):
    """Get a specific sender."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if sender_id not in user_data["senders"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )
        return user_data["senders"][sender_id]
    except HTTPException:
        raise
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
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if sender_id not in user_data["senders"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )
        
        body = await request.json()
        user_data["senders"][sender_id].update({
            "email": body.get("email", user_data["senders"][sender_id]["email"]),
            "name": body.get("name", user_data["senders"][sender_id]["name"]),
            "verified": body.get("verified", user_data["senders"][sender_id]["verified"]),
            "updated_at": datetime.utcnow().isoformat()
        })
        
        return user_data["senders"][sender_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update sender error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update sender: {str(e)}"
        )

@app.delete("/api/senders/{sender_id}")
async def delete_sender(sender_id: str, request: Request):
    """Delete a sender."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if sender_id not in user_data["senders"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )
        
        deleted_sender = user_data["senders"].pop(sender_id)
        return {"message": "Sender deleted successfully", "sender": deleted_sender}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete sender error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete sender: {str(e)}"
        )

@app.post("/api/senders/{sender_id}/set-default")
async def set_default_sender(sender_id: str, request: Request):
    """Set a sender as default."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if sender_id not in user_data["senders"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )
        
        # Set all senders as non-default first
        for sender in user_data["senders"].values():
            sender["is_default"] = False
        
        # Set the specified sender as default
        user_data["senders"][sender_id]["is_default"] = True
        user_data["senders"][sender_id]["updated_at"] = datetime.utcnow().isoformat()
        
        return {
            "message": "Default sender updated successfully",
            "sender_id": sender_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set default sender error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set default sender: {str(e)}"
        )

@app.post("/api/senders/{sender_id}/resend-verification")
async def resend_verification(sender_id: str, request: Request):
    """Resend verification email to sender."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if sender_id not in user_data["senders"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )
        
        # Mock verification email sent
        user_data["senders"][sender_id]["verification_sent_at"] = datetime.utcnow().isoformat()
        
        return {
            "message": "Verification email sent successfully",
            "sender_id": sender_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resend verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend verification: {str(e)}"
        )

# ===== CAMPAIGNS ENDPOINTS =====

@app.get("/api/campaigns")
async def get_campaigns(request: Request):
    """Get all campaigns for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        return {
            "campaigns": list(user_data["campaigns"].values()),
            "total": len(user_data["campaigns"])
        }
    except HTTPException:
        raise
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
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        body = await request.json()
        
        campaign_id = f"campaign_{len(user_data['campaigns']) + 1}"
        
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
        
        user_data["campaigns"][campaign_id] = campaign
        
        return campaign
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create campaign error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str, request: Request):
    """Get a specific campaign."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if campaign_id not in user_data["campaigns"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        return user_data["campaigns"][campaign_id]
    except HTTPException:
        raise
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
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if campaign_id not in user_data["campaigns"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        body = await request.json()
        user_data["campaigns"][campaign_id].update({
            "name": body.get("name", user_data["campaigns"][campaign_id]["name"]),
            "subject": body.get("subject", user_data["campaigns"][campaign_id]["subject"]),
            "content": body.get("content", user_data["campaigns"][campaign_id]["content"]),
            "status": body.get("status", user_data["campaigns"][campaign_id]["status"]),
            "sender_id": body.get("sender_id", user_data["campaigns"][campaign_id]["sender_id"]),
            "template_id": body.get("template_id", user_data["campaigns"][campaign_id]["template_id"]),
            "updated_at": datetime.utcnow().isoformat()
        })
        
        return user_data["campaigns"][campaign_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update campaign error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}"
        )

@app.delete("/api/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str, request: Request):
    """Delete a campaign."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if campaign_id not in user_data["campaigns"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        deleted_campaign = user_data["campaigns"].pop(campaign_id)
        return {"message": "Campaign deleted successfully", "campaign": deleted_campaign}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete campaign error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )

@app.post("/api/campaigns/{campaign_id}/send")
async def send_campaign(campaign_id: str, request: Request):
    """Send a campaign."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if campaign_id not in user_data["campaigns"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        user_data["campaigns"][campaign_id]["status"] = "sent"
        user_data["campaigns"][campaign_id]["sent_at"] = datetime.utcnow().isoformat()
        
        return {
            "message": "Campaign sent successfully",
            "campaign_id": campaign_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send campaign error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send campaign: {str(e)}"
        )

@app.post("/api/campaigns/validate-template")
async def validate_template(request: Request):
    """Validate a campaign template."""
    try:
        body = await request.json()
        template_content = body.get("template_content", "")
        
        # Mock validation
        is_valid = len(template_content) > 0
        
        return {
            "is_valid": is_valid,
            "message": "Template is valid" if is_valid else "Template is empty"
        }
    except Exception as e:
        logger.error(f"Validate template error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate template: {str(e)}"
        )

@app.post("/api/campaigns/preview")
async def preview_campaign(request: Request):
    """Preview a campaign."""
    try:
        body = await request.json()
        
        return {
            "preview": {
                "subject": body.get("subject", "Campaign Subject"),
                "content": body.get("content", "Campaign content preview..."),
                "recipient_count": body.get("recipient_count", 0)
            }
        }
    except Exception as e:
        logger.error(f"Preview campaign error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview campaign: {str(e)}"
        )

@app.get("/api/campaigns/{campaign_id}/status")
async def get_campaign_status(campaign_id: str, request: Request):
    """Get campaign status."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if campaign_id not in user_data["campaigns"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        campaign = user_data["campaigns"][campaign_id]
        
        return {
            "campaign_id": campaign_id,
            "status": campaign.get("status", "draft"),
            "progress": campaign.get("progress", 0),
            "sent_count": campaign.get("sent_count", 0),
            "total_count": campaign.get("total_count", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get campaign status error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign status: {str(e)}"
        )

# ===== FILES ENDPOINTS =====

@app.get("/api/files")
async def get_files(request: Request):
    """Get all files for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        return {
            "files": list(user_data["files"].values()),
            "total": len(user_data["files"])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get files error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get files: {str(e)}"
        )

@app.post("/api/files/upload")
async def upload_file(request: Request):
    """Upload a file for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        # For now, return a mock response since we don't have file storage set up
        file_id = f"file_{len(user_data['files']) + 1}_{uid}"
        
        file_record = {
            "id": file_id,
            "name": "uploaded_file.xlsx",
            "type": "excel",
            "size": 1024,
            "status": "uploaded",
            "created_at": datetime.utcnow().isoformat(),
            "user_id": uid
        }
        
        user_data["files"][file_id] = file_record
        
        return file_record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload file error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@app.post("/api/files/{file_id}/process")
async def process_file(file_id: str, request: Request):
    """Process a file for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if file_id not in user_data["files"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Update file status to processed
        user_data["files"][file_id]["status"] = "processed"
        user_data["files"][file_id]["processed_at"] = datetime.utcnow().isoformat()
        
        return {
            "message": "File processed successfully",
            "total_contacts": 150,
            "file_id": file_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process file error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )

@app.get("/api/files/{file_id}/preview")
async def preview_file(file_id: str, request: Request):
    """Preview a file for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        if file_id not in user_data["files"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Return mock preview data
        return {
            "file_id": file_id,
            "preview_data": [
                {"email": "john@example.com", "name": "John Doe"},
                {"email": "jane@example.com", "name": "Jane Smith"},
                {"email": "bob@example.com", "name": "Bob Johnson"}
            ],
            "total_rows": 3
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preview file error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview file: {str(e)}"
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

@app.get("/api/subscriptions/current")
async def get_current_subscription(request: Request):
    """Get current subscription for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        # Return user's subscription or create a default one
        if not user_data["subscriptions"]:
            # Create default subscription for new user
            user_data["subscriptions"]["current"] = {
                "id": f"sub_{uid}",
                "plan": "basic",
                "status": "active",
                "billing_cycle": "monthly",
                "current_period_start": datetime.utcnow().isoformat(),
                "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
        
        return user_data["subscriptions"]["current"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current subscription error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current subscription: {str(e)}"
        )

@app.get("/api/subscriptions/usage")
async def get_usage_stats(request: Request):
    """Get usage statistics for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        return user_data["usage"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get usage stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage stats: {str(e)}"
        )

@app.get("/api/subscriptions/plans")
async def get_subscription_plans():
    """Get available subscription plans."""
    try:
        return {
            "plans": [
                {
                    "id": "basic",
                    "name": "Basic",
                    "price_monthly": 9.99,
                    "price_yearly": 99.99,
                    "features": {
                        "email_limit": 1000,
                        "sender_limit": 5,
                        "template_limit": 10,
                        "api_access": False,
                        "priority_support": False,
                        "white_label": False,
                        "custom_integrations": False
                    }
                },
                {
                    "id": "pro",
                    "name": "Professional",
                    "price_monthly": 29.99,
                    "price_yearly": 299.99,
                    "features": {
                        "email_limit": 10000,
                        "sender_limit": 10,
                        "template_limit": 50,
                        "api_access": True,
                        "priority_support": False,
                        "white_label": False,
                        "custom_integrations": False
                    }
                },
                {
                    "id": "enterprise",
                    "name": "Enterprise",
                    "price_monthly": 99.99,
                    "price_yearly": 999.99,
                    "features": {
                        "email_limit": -1,  # Unlimited
                        "sender_limit": -1,  # Unlimited
                        "template_limit": -1,  # Unlimited
                        "api_access": True,
                        "priority_support": True,
                        "white_label": True,
                        "custom_integrations": True
                    }
                }
            ]
        }
    except Exception as e:
        logger.error(f"Get subscription plans error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription plans: {str(e)}"
        )

@app.post("/api/subscriptions/create")
async def create_subscription_endpoint(request: Request):
    """Create a new subscription for the current user."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        body = await request.json()
        plan_id = body.get("plan", "basic")
        billing_cycle = body.get("billing_cycle", "monthly")
        
        # Update user's subscription
        user_data["subscriptions"]["current"] = {
            "id": f"sub_{uid}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "plan": plan_id,
            "status": "active",
            "billing_cycle": billing_cycle,
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        return user_data["subscriptions"]["current"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create subscription error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )

@app.get("/api/subscriptions/stripe-key")
async def get_stripe_key():
    """Get Stripe publishable key."""
    try:
        # Mock Stripe key - in production this would be from environment variables
        return {
            "publishable_key": "pk_test_mock_stripe_key_for_demo"
        }
    except Exception as e:
        logger.error(f"Get Stripe key error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Stripe key: {str(e)}"
        )

@app.get("/api/v1/subscriptions/plans")
async def get_subscription_plans_v1():
    """Get available subscription plans (v1 endpoint)."""
    try:
        return [
            {
                "id": "basic",
                "name": "Basic",
                "price_monthly": 9.99,
                "price_yearly": 99.99,
                "features": {
                    "email_limit": 1000,
                    "sender_limit": 5,
                    "template_limit": 10,
                    "api_access": False,
                    "priority_support": False,
                    "white_label": False,
                    "custom_integrations": False
                }
            },
            {
                "id": "pro",
                "name": "Professional",
                "price_monthly": 29.99,
                "price_yearly": 299.99,
                "features": {
                    "email_limit": 10000,
                    "sender_limit": 10,
                    "template_limit": 50,
                    "api_access": True,
                    "priority_support": False,
                    "white_label": False,
                    "custom_integrations": False
                }
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price_monthly": 99.99,
                "price_yearly": 999.99,
                "features": {
                    "email_limit": -1,  # Unlimited
                    "sender_limit": -1,  # Unlimited
                    "template_limit": -1,  # Unlimited
                    "api_access": True,
                    "priority_support": True,
                    "white_label": True,
                    "custom_integrations": True
                }
            }
        ]
    except Exception as e:
        logger.error(f"Get subscription plans error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription plans: {str(e)}"
        )

@app.get("/api/v1/subscriptions/current")
async def get_current_subscription_v1(request: Request):
    """Get current subscription for the current user (v1 endpoint)."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        # Return user's subscription or create a default one
        if not user_data["subscriptions"]:
            # Create default subscription for new user
            user_data["subscriptions"]["current"] = {
                "id": f"sub_{uid}",
                "plan": "basic",
                "status": "active",
                "billing_cycle": "monthly",
                "current_period_start": datetime.utcnow().isoformat(),
                "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
        
        return user_data["subscriptions"]["current"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current subscription error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current subscription: {str(e)}"
        )

@app.post("/api/v1/subscriptions/create")
async def create_subscription_v1(request: Request):
    """Create a new subscription for the current user (v1 endpoint)."""
    try:
        email, uid = get_user_from_token(request)
        user_data = get_user_data(uid)
        
        body = await request.json()
        plan_id = body.get("plan", "basic")
        billing_cycle = body.get("billing_cycle", "monthly")
        
        # Update user's subscription
        user_data["subscriptions"]["current"] = {
            "id": f"sub_{uid}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "plan": plan_id,
            "status": "active",
            "billing_cycle": billing_cycle,
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        return user_data["subscriptions"]["current"]
    except HTTPException:
        raise
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
        "templates_count": len(user_templates_db),
        "customers_count": len(user_customers_db),
        "senders_count": len(user_senders_db),
        "campaigns_count": len(user_campaigns_db),
        "files_count": len(user_files_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 