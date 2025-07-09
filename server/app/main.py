from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, stats, files, templates, senders
from app.api.v1 import campaigns, google_auth, subscriptions
from app.core.config import settings
from app.db.mongodb import MongoDB
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Email Bot API",
    description="Email automation and customer management API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])
app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(senders.router, prefix="/api/senders", tags=["Senders"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(google_auth.router, prefix="/api/v1/google-auth", tags=["Google OAuth"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])

@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB on startup."""
    try:
        await MongoDB.connect_to_mongo()
        logger.info("Connected to MongoDB Atlas")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.warning("Running in development mode without database connection")
        logger.warning("Authentication and data persistence features will not work")
        # Don't raise the exception - allow the app to start without database

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown."""
    try:
        await MongoDB.close_mongo_connection()
        logger.info("Disconnected from MongoDB Atlas")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")

@app.get("/")
async def root():
    """Root endpoint."""
    try:
        # Test actual MongoDB connection by trying to access a collection
        collection = MongoDB.get_collection("users")
        db_status = "connected" if collection is not None else "disconnected (development mode)"
    except Exception as e:
        db_status = f"disconnected (error: {str(e)})"
    
    return {
        "message": "Email Bot API",
        "version": "1.0.0",
        "status": "running",
        "database": db_status
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test actual MongoDB connection by trying to access a collection
        collection = MongoDB.get_collection("users")
        db_status = "connected" if collection is not None else "disconnected"
        mode = "development" if collection is None else "production"
    except Exception as e:
        db_status = f"disconnected (error: {str(e)})"
        mode = "development"
    
    return {
        "status": "healthy", 
        "database": db_status,
        "mode": mode
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify server is working."""
    try:
        # Test actual MongoDB connection by trying to access a collection
        collection = MongoDB.get_collection("users")
        development_mode = collection is None
    except Exception as e:
        development_mode = True
    
    return {
        "message": "Server is working!",
        "timestamp": datetime.utcnow().isoformat(),
        "development_mode": development_mode
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
