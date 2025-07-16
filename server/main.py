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
import pandas as pd
import io
import csv

# Import routes
from app.routes import senders
from app.api.v1 import subscriptions, auth

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

# Include routes
app.include_router(senders.router, prefix="/api/senders", tags=["senders"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["subscriptions"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
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
        
        # Get only files belonging to this user, excluding file_data to prevent bytes serialization error
        files = list(db.files.find({"user_id": str(user["_id"]), "is_active": True}, {"file_data": 0}))
        
        # Convert ObjectId to string for JSON serialization
        for file in files:
            file["id"] = str(file["_id"])
            del file["_id"]
            # Ensure all dates are serializable
            if "upload_date" in file:
                file["upload_date"] = file["upload_date"].isoformat()
            if "processed_date" in file:
                file["processed_date"] = file["processed_date"].isoformat()
        
        return files
    except Exception as e:
        logger.error(f"Get files error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/files/upload")
async def upload_file(request: Request):
    """Upload a file."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Parse multipart form data
        form = await request.form()
        file = form.get("file")
        description = form.get("description", "Uploaded file")
        
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Get file info
        filename = file.filename
        file_content = await file.read()
        file_size = len(file_content)
        
        # Determine file type from extension
        if filename.lower().endswith(('.xlsx', '.xls')):
            file_type = "excel"
        elif filename.lower().endswith('.csv'):
            file_type = "csv"
        elif filename.lower().endswith('.pdf'):
            file_type = "pdf"
        else:
            # Try to detect based on content type or fallback to csv for text files
            if hasattr(file, 'content_type'):
                content_type = file.content_type.lower()
                if 'excel' in content_type or 'spreadsheet' in content_type:
                    file_type = "excel"
                elif 'csv' in content_type or 'text' in content_type:
                    file_type = "csv"
                else:
                    file_type = "csv"  # Default to CSV for unknown text files
            else:
                file_type = "csv"  # Default to CSV
        
        logger.info(f"File upload - filename: {filename}, detected type: {file_type}")
        
        # Create file document with actual filename and file data
        file_doc = {
            "user_id": str(user["_id"]),
            "filename": filename,
            "file_size": file_size,
            "upload_date": datetime.utcnow(),
            "processed": False,
            "contacts_count": 0,
            "file_type": file_type,
            "is_active": True,
            "description": description,
            "file_data": file_content  # Store the actual file content
        }
        
        result = db.files.insert_one(file_doc)
        
        # Return response without file_data to avoid serialization issues
        response_file = {
            "id": str(result.inserted_id),
            "user_id": str(user["_id"]),
            "filename": filename,
            "file_size": file_size,
            "upload_date": file_doc["upload_date"].isoformat(),
            "processed": False,
            "contacts_count": 0,
            "file_type": file_type,
            "is_active": True,
            "description": description
        }
        
        return {
            "message": "File uploaded successfully",
            "file": response_file,
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
            "user_id": str(user["_id"]),
            "is_active": True
        })
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Soft delete the file
        db.files.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"is_active": False}}
        )
        
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
        
        # Ensure the file belongs to the user and get file data
        file = db.files.find_one({
            "_id": ObjectId(file_id),
            "user_id": str(user["_id"]),
            "is_active": True
        })
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get file data
        file_data = file.get("file_data")
        if not file_data:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Parse file and count contacts
        contacts_count = 0
        file_type = file.get("file_type", "unknown")
        filename = file.get("filename", "")
        
        try:
            if file_type == "excel" or filename.lower().endswith(('.xlsx', '.xls')):
                # Parse Excel file with sheet validation
                try:
                    # Check number of sheets in Excel file
                    excel_file = pd.ExcelFile(io.BytesIO(file_data))
                    sheet_names = excel_file.sheet_names
                    
                    if len(sheet_names) == 0:
                        logger.error(f"No sheets found in Excel file {file_id}")
                        contacts_count = 0
                    elif len(sheet_names) > 1:
                        logger.error(f"Excel file {file_id} contains {len(sheet_names)} sheets. Only Excel files with exactly one sheet are supported.")
                        contacts_count = 0
                    else:
                        # Exactly one sheet found - process it
                        df = pd.read_excel(io.BytesIO(file_data))
                        # Clean the dataframe
                        df = df.dropna(how='all')  # Remove completely empty rows
                        contacts_count = len(df)
                        logger.info(f"Successfully processed Excel file with {contacts_count} contacts")
                        
                except Exception as excel_error:
                    logger.error(f"Error processing Excel file {file_id}: {str(excel_error)}")
                    contacts_count = 0
                
            elif file_type == "pdf" or filename.lower().endswith('.pdf'):
                # Parse PDF file with table detection
                try:
                    import tabula
                    
                    # Extract tables from PDF
                    tables = tabula.read_pdf(io.BytesIO(file_data), pages='all', multiple_tables=True)
                    
                    if len(tables) == 0:
                        logger.error(f"No tables found in PDF file {file_id}")
                        contacts_count = 0
                    elif len(tables) > 1:
                        logger.error(f"PDF file {file_id} contains {len(tables)} tables. Only PDFs with exactly one table are supported.")
                        contacts_count = 0
                    else:
                        # Exactly one table found - process it
                        df = tables[0]
                        # Clean the dataframe
                        df = df.dropna(how='all')  # Remove completely empty rows
                        contacts_count = len(df)
                        logger.info(f"Successfully processed PDF with {contacts_count} contacts")
                        
                except ImportError:
                    logger.error(f"PDF processing not available for file {file_id}")
                    contacts_count = 0
                except Exception as pdf_error:
                    logger.error(f"Error processing PDF {file_id}: {str(pdf_error)}")
                    contacts_count = 0
                
            elif file_type == "csv" or filename.lower().endswith('.csv'):
                # Parse CSV file with table validation
                try:
                    csv_content = file_data.decode('utf-8')
                except UnicodeDecodeError:
                    csv_content = file_data.decode('utf-8-sig')
                
                try:
                    # Check for multiple data sections in CSV
                    lines = csv_content.strip().split('\n')
                    if not lines:
                        logger.error(f"CSV file {file_id} is empty")
                        contacts_count = 0
                    else:
                        # Look for multiple header rows or data sections
                        header_rows = []
                        multiple_sections = False
                        
                        for i, line in enumerate(lines):
                            if line.strip() and not line.startswith('#'):  # Skip comments
                                # Check if this could be a header row (has common header patterns)
                                if any(keyword in line.lower() for keyword in ['name', 'email', 'contact', 'phone', 'address']):
                                    if i > 0 and header_rows:  # Found potential second header
                                        # Check if there's significant gap suggesting multiple tables
                                        if i - header_rows[-1] > 5:  # More than 5 rows gap
                                            multiple_sections = True
                                            break
                                    header_rows.append(i)
                        
                        if multiple_sections:
                            logger.error(f"CSV file {file_id} appears to contain multiple data sections. Only CSV files with one continuous data table are supported.")
                            contacts_count = 0
                        else:
                            # Process as single table
                            csv_reader = csv.DictReader(io.StringIO(csv_content))
                            contacts = list(csv_reader)
                            
                            # Validate that we have meaningful data
                            if not contacts:
                                logger.error(f"No data rows found in CSV file {file_id}")
                                contacts_count = 0
                            else:
                                # Check if all rows are empty
                                non_empty_rows = [row for row in contacts if any(str(value).strip() for value in row.values())]
                                if not non_empty_rows:
                                    logger.error(f"CSV file {file_id} contains only empty rows")
                                    contacts_count = 0
                                else:
                                    contacts_count = len(non_empty_rows)
                                    logger.info(f"Successfully processed CSV file with {contacts_count} contacts")
                        
                except Exception as csv_error:
                    logger.error(f"Error processing CSV file {file_id}: {str(csv_error)}")
                    contacts_count = 0
                
            else:
                # Fallback for unknown file types
                contacts_count = 0
                
        except Exception as parse_error:
            logger.error(f"Error processing file {file_id}: {str(parse_error)}")
            contacts_count = 0
        
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
        
        # Ensure the file belongs to the user and get file data
        file = db.files.find_one({
            "_id": ObjectId(file_id),
            "user_id": str(user["_id"]),
            "is_active": True
        })
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get file data
        file_data = file.get("file_data")
        if not file_data:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Parse file based on type
        contacts = []
        file_type = file.get("file_type", "unknown")
        filename = file.get("filename", "")
        
        logger.info(f"Preview file - filename: {filename}, file_type: {file_type}")
        
        try:
            if file_type == "excel" or filename.lower().endswith(('.xlsx', '.xls')):
                # Parse Excel file with sheet validation
                try:
                    # Check number of sheets in Excel file
                    excel_file = pd.ExcelFile(io.BytesIO(file_data))
                    sheet_names = excel_file.sheet_names
                    
                    if len(sheet_names) == 0:
                        contacts = [{"error": "No sheets found in Excel file"}]
                    elif len(sheet_names) > 1:
                        contacts = [{"error": f"Excel file contains {len(sheet_names)} sheets. Only Excel files with exactly one sheet are supported."}]
                    else:
                        # Exactly one sheet found - process it
                        df = pd.read_excel(io.BytesIO(file_data))
                        # Clean the dataframe
                        df = df.dropna(how='all')  # Remove completely empty rows
                        df = df.fillna('')  # Fill NaN values with empty strings
                        contacts = df.to_dict('records')
                        logger.info(f"Successfully extracted {len(contacts)} contacts from Excel sheet")
                        
                except Exception as excel_error:
                    logger.error(f"Error processing Excel file: {str(excel_error)}")
                    contacts = [{"error": f"Error processing Excel file: {str(excel_error)}"}]
                
            elif file_type == "pdf" or filename.lower().endswith('.pdf'):
                # Parse PDF file with table detection
                try:
                    import tabula
                    
                    # Extract tables from PDF
                    tables = tabula.read_pdf(io.BytesIO(file_data), pages='all', multiple_tables=True)
                    
                    if len(tables) == 0:
                        contacts = [{"error": "No tables found in PDF file"}]
                    elif len(tables) > 1:
                        contacts = [{"error": f"PDF contains {len(tables)} tables. Only PDFs with exactly one table are supported."}]
                    else:
                        # Exactly one table found - process it
                        df = tables[0]
                        # Clean the dataframe
                        df = df.dropna(how='all')  # Remove completely empty rows
                        df = df.fillna('')  # Fill NaN values with empty strings
                        contacts = df.to_dict('records')
                        logger.info(f"Successfully extracted {len(contacts)} contacts from PDF table")
                        
                except ImportError:
                    contacts = [{"error": "PDF processing not available. Please install tabula-py library."}]
                except Exception as pdf_error:
                    logger.error(f"Error processing PDF: {str(pdf_error)}")
                    contacts = [{"error": f"Error processing PDF: {str(pdf_error)}"}]
                
            elif file_type == "csv" or filename.lower().endswith('.csv') or file_type == "unknown":
                # Parse CSV file with table validation (also try for unknown types as they might be CSV)
                try:
                    csv_content = file_data.decode('utf-8')
                except UnicodeDecodeError:
                    # Try different encoding
                    csv_content = file_data.decode('utf-8-sig')
                
                try:
                    # Check for multiple data sections in CSV
                    lines = csv_content.strip().split('\n')
                    if not lines:
                        contacts = [{"error": "CSV file is empty"}]
                    else:
                        # Look for multiple header rows or data sections
                        header_rows = []
                        for i, line in enumerate(lines):
                            if line.strip() and not line.startswith('#'):  # Skip comments
                                # Check if this could be a header row (has common header patterns)
                                if any(keyword in line.lower() for keyword in ['name', 'email', 'contact', 'phone', 'address']):
                                    if i > 0 and header_rows:  # Found potential second header
                                        # Check if there's significant gap suggesting multiple tables
                                        if i - header_rows[-1] > 5:  # More than 5 rows gap
                                            contacts = [{"error": "CSV file appears to contain multiple data sections. Only CSV files with one continuous data table are supported."}]
                                            break
                                    header_rows.append(i)
                        
                        if 'error' not in str(contacts):
                            # Process as single table
                            csv_reader = csv.DictReader(io.StringIO(csv_content))
                            contacts = list(csv_reader)
                            
                            # Validate that we have meaningful data
                            if not contacts:
                                contacts = [{"error": "No data rows found in CSV file"}]
                            elif len(contacts) > 0:
                                # Check if all rows are empty
                                non_empty_rows = [row for row in contacts if any(str(value).strip() for value in row.values())]
                                if not non_empty_rows:
                                    contacts = [{"error": "CSV file contains only empty rows"}]
                                else:
                                    contacts = non_empty_rows
                                    logger.info(f"Successfully extracted {len(contacts)} contacts from CSV file")
                        
                except Exception as csv_error:
                    logger.error(f"Error processing CSV file: {str(csv_error)}")
                    contacts = [{"error": f"Error processing CSV file: {str(csv_error)}"}]
                    
            else:
                # Try to parse as CSV first before giving up
                try:
                    csv_content = file_data.decode('utf-8')
                    csv_reader = csv.DictReader(io.StringIO(csv_content))
                    contacts = list(csv_reader)
                    logger.info(f"Successfully parsed unknown file type as CSV")
                except Exception as csv_error:
                    logger.error(f"Failed to parse as CSV: {str(csv_error)}")
                    contacts = [{"error": f"Unsupported file type for preview. File type: {file_type}, Filename: {filename}"}]
                
        except Exception as parse_error:
            logger.error(f"Error parsing file {file_id}: {str(parse_error)}")
            contacts = [{"error": f"Error parsing file: {str(parse_error)}"}]
        
        return {
            "file_id": str(file["_id"]),
            "file_name": filename,
            "contacts": contacts,
            "total_contacts": len(contacts)
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
        
        # Get only templates belonging to this user (active only)
        templates = list(db.templates.find({"user_id": str(user["_id"]), "is_active": True}))
        
        # Convert ObjectId to string for JSON serialization
        for template in templates:
            template["id"] = str(template["_id"])
            del template["_id"]
            # Ensure all dates are serializable
            if "created_at" in template:
                template["created_at"] = template["created_at"].isoformat()
        
        return templates
    except Exception as e:
        logger.error(f"Get templates error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/templates")
async def create_template(request: Request):
    """Create a new template for the user."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get template data from request
        template_data = await request.json()
        
        # Create template document
        template_doc = {
            "user_id": str(user["_id"]),
            "name": template_data.get("name", "Untitled Template"),
            "subject": template_data.get("subject", ""),
            "content": template_data.get("content", ""),
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = db.templates.insert_one(template_doc)
        template_doc["id"] = str(result.inserted_id)
        del template_doc["_id"]
        template_doc["created_at"] = template_doc["created_at"].isoformat()
        
        return template_doc
    except Exception as e:
        logger.error(f"Create template error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/templates/{template_id}")
def delete_template(request: Request, template_id: str):
    """Delete a template."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Ensure the template belongs to the user
        template = db.templates.find_one({
            "_id": ObjectId(template_id),
            "user_id": str(user["_id"]),
            "is_active": True
        })
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Soft delete the template
        db.templates.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": {"is_active": False}}
        )
        
        return {"message": "Template deleted successfully"}
    except Exception as e:
        logger.error(f"Delete template error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/templates/{template_id}")
async def update_template(request: Request, template_id: str):
    """Update a template."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get template data from request
        template_data = await request.json()
        
        # Ensure the template belongs to the user
        template = db.templates.find_one({
            "_id": ObjectId(template_id),
            "user_id": str(user["_id"]),
            "is_active": True
        })
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Update template
        update_data = {
            "name": template_data.get("name", template["name"]),
            "subject": template_data.get("subject", template["subject"]),
            "content": template_data.get("content", template["content"]),
            "updated_at": datetime.utcnow()
        }
        
        db.templates.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": update_data}
        )
        
        # Return updated template
        updated_template = db.templates.find_one({"_id": ObjectId(template_id)})
        updated_template["id"] = str(updated_template["_id"])
        del updated_template["_id"]
        if "created_at" in updated_template:
            updated_template["created_at"] = updated_template["created_at"].isoformat()
        if "updated_at" in updated_template:
            updated_template["updated_at"] = updated_template["updated_at"].isoformat()
        
        return updated_template
    except Exception as e:
        logger.error(f"Update template error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/templates/{template_id}/set-default")
def set_default_template(request: Request, template_id: str):
    """Set a template as default."""
    try:
        db = get_database()
        email = get_user_from_token(request)
        user = db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Ensure the template belongs to the user
        template = db.templates.find_one({
            "_id": ObjectId(template_id),
            "user_id": str(user["_id"]),
            "is_active": True
        })
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Remove default flag from all user's templates
        db.templates.update_many(
            {"user_id": str(user["_id"])},
            {"$set": {"is_default": False}}
        )
        
        # Set this template as default
        db.templates.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": {"is_default": True}}
        )
        
        return {"message": "Template set as default successfully"}
    except Exception as e:
        logger.error(f"Set default template error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

# ===== SUBSCRIPTION ENDPOINTS =====
# Note: Subscription endpoints are now handled by the router in app/api/v1/subscriptions.py 