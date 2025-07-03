from datetime import datetime
from typing import List, Optional
from bson import ObjectId
import io
import logging
from fastapi import HTTPException, status, UploadFile
from app.db.mongodb import MongoDB
from app.models.file import FileCreate, FileUpdate, FileInDB, FileResponse

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.files_collection = MongoDB.get_collection("files")
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {'.xlsx', '.xls', '.pdf'}

    async def upload_file(self, file: UploadFile, user_id: str, description: Optional[str] = None) -> FileResponse:
        """Upload and store a file in the database."""
        try:
            # Validate file extension first
            file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
            if f'.{file_extension}' not in self.allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type not allowed. Allowed types: {', '.join(self.allowed_extensions)}"
                )

            # Read file content
            file_content = await file.read()
            
            # Validate file size after reading
            if len(file_content) > self.max_file_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size exceeds maximum limit of {self.max_file_size // (1024*1024)}MB"
                )
            
            # Determine file type
            file_type = self._get_file_type(file.filename)

            # Create file document
            file_data = FileCreate(
                filename=file.filename,
                file_type=file_type,
                file_size=len(file_content),
                description=description,
                user_id=user_id,
                file_data=file_content
            )

            file_dict = file_data.dict()
            file_dict["upload_date"] = datetime.utcnow()
            file_dict["is_active"] = True
            file_dict["processed"] = False

            # Insert file into database
            result = await self.files_collection.insert_one(file_dict)
            
            # Get the created file
            created_file = await self.files_collection.find_one({"_id": result.inserted_id})
            
            return FileResponse(
                id=str(created_file["_id"]),
                filename=created_file["filename"],
                file_type=created_file["file_type"],
                file_size=created_file["file_size"],
                description=created_file.get("description"),
                user_id=created_file["user_id"],
                upload_date=created_file["upload_date"],
                is_active=created_file["is_active"],
                processed=created_file["processed"],
                contacts_count=created_file.get("contacts_count")
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File upload failed: {str(e)}"
            )

    async def get_user_files(self, user_id: str) -> List[FileResponse]:
        """Get all files uploaded by a user."""
        try:
            cursor = self.files_collection.find({"user_id": user_id, "is_active": True})
            files = await cursor.to_list(length=None)
            
            return [
                FileResponse(
                    id=str(file["_id"]),
                    filename=file["filename"],
                    file_type=file["file_type"],
                    file_size=file["file_size"],
                    description=file.get("description"),
                    user_id=file["user_id"],
                    upload_date=file["upload_date"],
                    is_active=file["is_active"],
                    processed=file["processed"],
                    contacts_count=file.get("contacts_count")
                )
                for file in files
            ]
        except Exception as e:
            logger.error(f"Error getting user files: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving files: {str(e)}"
            )

    async def get_file_by_id(self, file_id: str, user_id: str) -> FileResponse:
        """Get a specific file by ID (user can only access their own files)."""
        try:
            if not ObjectId.is_valid(file_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file ID"
                )

            file = await self.files_collection.find_one({
                "_id": ObjectId(file_id),
                "user_id": user_id,
                "is_active": True
            })

            if not file:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )

            return FileResponse(
                id=str(file["_id"]),
                filename=file["filename"],
                file_type=file["file_type"],
                file_size=file["file_size"],
                description=file.get("description"),
                user_id=file["user_id"],
                upload_date=file["upload_date"],
                is_active=file["is_active"],
                processed=file["processed"],
                contacts_count=file.get("contacts_count")
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting file by ID: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving file: {str(e)}"
            )

    async def delete_file(self, file_id: str, user_id: str) -> dict:
        """Delete a file (soft delete by setting is_active to False)."""
        try:
            if not ObjectId.is_valid(file_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file ID"
                )

            result = await self.files_collection.update_one(
                {
                    "_id": ObjectId(file_id),
                    "user_id": user_id,
                    "is_active": True
                },
                {"$set": {"is_active": False}}
            )

            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )

            return {"message": "File deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting file: {str(e)}"
            )

    async def process_file(self, file_id: str, user_id: str) -> dict:
        """Process a file to extract contacts."""
        try:
            file = await self.get_file_by_id(file_id, user_id)
            
            if file.processed:
                return {"message": "File already processed", "contacts_count": file.contacts_count}

            # Get file data from database
            file_doc = await self.files_collection.find_one({"_id": ObjectId(file_id)})
            file_data = file_doc["file_data"]

            # Process based on file type
            contacts_count = 0
            if file.file_type == "excel":
                contacts_count = await self._process_excel_file(file_data)
            elif file.file_type == "pdf":
                contacts_count = await self._process_pdf_file(file_data)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unsupported file type for processing"
                )

            # Update file as processed
            await self.files_collection.update_one(
                {"_id": ObjectId(file_id)},
                {
                    "$set": {
                        "processed": True,
                        "contacts_count": contacts_count,
                        "processed_at": datetime.utcnow()
                    }
                }
            )

            return {
                "message": "File processed successfully",
                "contacts_count": contacts_count
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing file: {str(e)}"
            )

    async def _process_excel_file(self, file_data: bytes) -> int:
        """Process Excel file and extract contacts."""
        try:
            # For now, return a placeholder count
            # In a real implementation, you would use pandas or openpyxl to read Excel files
            # and extract contact information
            logger.info("Excel file processing placeholder - returning estimated count")
            return 5  # Placeholder count
        except Exception as e:
            logger.error(f"Error processing Excel file: {str(e)}")
            return 0

    async def _process_pdf_file(self, file_data: bytes) -> int:
        """Process PDF file and extract contacts."""
        try:
            # For now, return a placeholder count
            # In a real implementation, you would use PyPDF2 or similar to extract text
            # and then use regex patterns to find email addresses
            return 0
        except Exception as e:
            logger.error(f"Error processing PDF file: {str(e)}")
            return 0

    def _get_file_type(self, filename: str) -> str:
        """Determine file type based on extension."""
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if extension in ['xlsx', 'xls']:
            return 'excel'
        elif extension == 'pdf':
            return 'pdf'
        else:
            return 'unknown' 