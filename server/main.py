from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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
logger.info("EMAIL BOT API STARTING UP - SIMPLIFIED VERSION")
logger.info("=" * 50)
logger.info(f"Environment: {'production' if os.getenv('VERCEL_ENV') else 'development'}")
logger.info(f"Python version: {os.sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")

app = FastAPI(
    title="Email Bot API - Simplified",
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

@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("ROOT: Root endpoint accessed")
    return {
        "message": "Email Bot API - Simplified Version",
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
        "mode": "simplified",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Simplified version working!"
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint."""
    logger.info("TEST: Test endpoint accessed")
    return {
        "message": "Simplified backend is working!",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/debug")
async def debug_endpoint():
    """Debug endpoint to show environment."""
    logger.info("DEBUG: Debug endpoint accessed")
    
    return {
        "environment": "production" if os.getenv('VERCEL_ENV') else "development",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "simplified"
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