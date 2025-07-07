from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, stats, files, templates, senders, customers
from app.api.v1 import campaigns, google_auth, subscriptions
from app.core.config import settings
from app.db.mongodb import MongoDB
import logging
import os
import time
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info("=" * 50)
logger.info("EMAIL BOT API STARTING UP")
logger.info("=" * 50)
logger.info(f"Environment: {'production' if os.getenv('VERCEL_ENV') else 'development'}")
logger.info(f"Python version: {os.sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Files in current directory: {os.listdir('.')}")

app = FastAPI(
    title="Email Bot API",
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
    logger.info(f"Headers: {dict(request.headers)}")
    
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
logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with logging
logger.info("Including routers...")
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])
app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(senders.router, prefix="/api/senders", tags=["Senders"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(google_auth.router, prefix="/api/v1/google-auth", tags=["Google OAuth"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])
logger.info("All routers included successfully")

# Global variable to track database connection status
db_connected = False

@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB on startup."""
    global db_connected
    logger.info("=" * 30)
    logger.info("STARTUP: Connecting to MongoDB...")
    logger.info("=" * 30)
    
    try:
        logger.info(f"MongoDB URL: {settings.MONGODB_URL[:20]}...")  # Log first 20 chars for security
        logger.info(f"Database name: {settings.DATABASE_NAME}")
        
        await MongoDB.connect_to_mongo()
        logger.info("✅ SUCCESS: Connected to MongoDB Atlas")
        db_connected = True
    except Exception as e:
        logger.error(f"❌ FAILED: MongoDB connection error: {e}")
        logger.warning("⚠️  Running in development mode without database connection")
        logger.warning("⚠️  Authentication and data persistence features will not work")
        db_connected = False
        # Don't raise the exception - allow the app to start without database

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown."""
    logger.info("=" * 30)
    logger.info("SHUTDOWN: Closing MongoDB connection...")
    logger.info("=" * 30)
    try:
        await MongoDB.close_mongo_connection()
        logger.info("✅ SUCCESS: Disconnected from MongoDB Atlas")
    except Exception as e:
        logger.error(f"❌ ERROR: Closing MongoDB connection: {e}")

@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("ROOT: Root endpoint accessed")
    return {
        "message": "Email Bot API",
        "version": "1.0.0",
        "status": "running",
        "database": "connected" if db_connected else "disconnected (development mode)",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "production" if os.getenv('VERCEL_ENV') else "development"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("HEALTH: Health check endpoint accessed")
    
    # Check environment variables
    env_status = {
        "MONGODB_URL": "✅ Set" if settings.MONGODB_URL else "❌ Missing",
        "SECRET_KEY": "✅ Set" if settings.SECRET_KEY != "your-secret-key-change-this-in-production" else "❌ Default",
        "GOOGLE_CLIENT_ID": "✅ Set" if settings.GOOGLE_CLIENT_ID else "❌ Missing",
        "GOOGLE_CLIENT_SECRET": "✅ Set" if settings.GOOGLE_CLIENT_SECRET else "❌ Missing",
        "CORS_ORIGINS": "✅ Set" if settings.CORS_ORIGINS else "❌ Missing"
    }
    
    return {
        "status": "healthy", 
        "database": "connected" if db_connected else "disconnected",
        "mode": "development" if not db_connected else "production",
        "environment_variables": env_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint."""
    logger.info("TEST: Test endpoint accessed")
    return {
        "message": "Backend is working!",
        "timestamp": datetime.utcnow().isoformat(),
        "database_status": "connected" if db_connected else "disconnected"
    }

@app.get("/debug")
async def debug_endpoint():
    """Debug endpoint to show all configuration."""
    logger.info("DEBUG: Debug endpoint accessed")
    
    # Safe way to show config without exposing secrets
    safe_config = {
        "mongodb_url_length": len(settings.MONGODB_URL) if settings.MONGODB_URL else 0,
        "secret_key_length": len(settings.SECRET_KEY) if settings.SECRET_KEY else 0,
        "google_client_id_set": bool(settings.GOOGLE_CLIENT_ID),
        "google_client_secret_set": bool(settings.GOOGLE_CLIENT_SECRET),
        "cors_origins": settings.CORS_ORIGINS,
        "database_name": settings.DATABASE_NAME,
        "algorithm": settings.ALGORITHM,
        "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }
    
    return {
        "configuration": safe_config,
        "database_connected": db_connected,
        "environment": "production" if os.getenv('VERCEL_ENV') else "development",
        "timestamp": datetime.utcnow().isoformat()
    }

# Vercel handles the server, so we don't need uvicorn.run here
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
