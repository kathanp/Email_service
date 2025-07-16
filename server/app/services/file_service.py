import os
import uuid
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
import io
import logging
from fastapi import HTTPException, status, UploadFile
from ..db.mongodb import MongoDB
from ..models.file import FileCreate, FileUpdate, FileInDB, FileResponse

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {'.xlsx', '.xls', '.csv', '.pdf'}

    def _get_files_collection(self):
        """Get files collection."""
        return MongoDB.get_collection("files")

    async def upload_file(self, file: UploadFile, user_id: str, description: Optional[str] = None) -> FileResponse:
        """Upload and store a file in the database."""
        try:
            logger.info(f"📁 File upload initiated for user {user_id}: {file.filename}")
            files_collection = self._get_files_collection()
            
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

            # Create file document with user isolation
            file_data = FileCreate(
                filename=file.filename,
                file_type=file_type,
                file_size=len(file_content),
                description=description,
                user_id=user_id,  # 🔒 CRITICAL: User isolation
                file_data=file_content
            )

            file_dict = file_data.dict()
            file_dict["upload_date"] = datetime.utcnow()
            file_dict["is_active"] = True
            file_dict["processed"] = False

            # Insert file into database
            result = await files_collection.insert_one(file_dict)
            
            # Get the created file
            created_file = await files_collection.find_one({"_id": result.inserted_id})
            
            logger.info(f"✅ File uploaded successfully for user {user_id}: {file.filename} (ID: {result.inserted_id})")
            
            return FileResponse(
                id=str(created_file["_id"]),
                filename=created_file["filename"],
                file_type=created_file["file_type"],
                file_size=created_file["file_size"],
                description=created_file.get("description"),
                user_id=created_file["user_id"],  # 🔒 User isolation maintained
                upload_date=created_file["upload_date"],
                is_active=created_file["is_active"],
                processed=created_file["processed"],
                contacts_count=created_file.get("contacts_count")
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error uploading file for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File upload failed: {str(e)}"
            )

    async def verify_file_ownership(self, file_id: str, user_id: str) -> bool:
        """Verify that a file belongs to the specified user."""
        try:
            files_collection = self._get_files_collection()
            
            if not ObjectId.is_valid(file_id):
                return False

            file = await files_collection.find_one({
                "_id": ObjectId(file_id),
                "user_id": user_id,
                "is_active": True
            })

            if file:
                logger.info(f"✅ File ownership verified: File {file_id} belongs to user {user_id}")
                return True
            else:
                logger.warning(f"⚠️ File ownership verification failed: File {file_id} does not belong to user {user_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Error verifying file ownership: {str(e)}")
            return False

    async def get_user_files(self, user_id: str) -> List[FileResponse]:
        """Get all files uploaded by a user with folder information."""
        try:
            files_collection = self._get_files_collection()
            
            # Create aggregation pipeline to include folder information
            pipeline = [
                {"$match": {"user_id": user_id, "is_active": True}},
                {
                    "$lookup": {
                        "from": "folders",
                        "let": {"folder_id": "$folder_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$_id", {"$toObjectId": "$$folder_id"}]},
                                            {"$eq": ["$user_id", user_id]}
                                        ]
                                    }
                                }
                            }
                        ],
                        "as": "folder_info"
                    }
                },
                {
                    "$addFields": {
                        "folder_name": {"$arrayElemAt": ["$folder_info.name", 0]},
                        "folder_color": {"$arrayElemAt": ["$folder_info.color", 0]}
                    }
                },
                {"$sort": {"upload_date": -1}}
            ]
            
            cursor = files_collection.aggregate(pipeline)
            files = await cursor.to_list(length=None)
            
            return [
                FileResponse(
                    id=str(file["_id"]),
                    filename=file["filename"],
                    file_type=file["file_type"],
                    file_size=file["file_size"],
                    description=file.get("description"),
                    folder_id=file.get("folder_id"),
                    user_id=file["user_id"],
                    upload_date=file["upload_date"],
                    is_active=file["is_active"],
                    processed=file["processed"],
                    contacts_count=file.get("contacts_count")
                ) for file in files
            ]
        except Exception as e:
            logger.error(f"Error getting user files: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get files: {str(e)}"
            )

    async def get_files_by_folder(self, user_id: str, folder_id: Optional[str] = None) -> List[FileResponse]:
        """Get files by folder (or uncategorized if folder_id is None)."""
        try:
            files_collection = self._get_files_collection()
            
            if folder_id:
                # Get files in specific folder
                query = {"user_id": user_id, "is_active": True, "folder_id": folder_id}
            else:
                # Get uncategorized files (no folder_id or folder_id is null)
                query = {
                    "user_id": user_id, 
                    "is_active": True,
                    "$or": [
                        {"folder_id": {"$exists": False}},
                        {"folder_id": None},
                        {"folder_id": ""}
                    ]
                }
            
            cursor = files_collection.find(query).sort("upload_date", -1)
            files = await cursor.to_list(length=None)
            
            return [
                FileResponse(
                    id=str(file["_id"]),
                    filename=file["filename"],
                    file_type=file["file_type"],
                    file_size=file["file_size"],
                    description=file.get("description"),
                    folder_id=file.get("folder_id"),
                    user_id=file["user_id"],
                    upload_date=file["upload_date"],
                    is_active=file["is_active"],
                    processed=file["processed"],
                    contacts_count=file.get("contacts_count")
                ) for file in files
            ]
        except Exception as e:
            logger.error(f"Error getting files by folder: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get files by folder: {str(e)}"
            )

    async def get_file_by_id(self, file_id: str, user_id: str) -> FileResponse:
        """Get a specific file by ID (user can only access their own files)."""
        try:
            files_collection = self._get_files_collection()
            
            if not ObjectId.is_valid(file_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file ID"
                )

            file = await files_collection.find_one({
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
            files_collection = self._get_files_collection()
            
            if not ObjectId.is_valid(file_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file ID"
                )

            result = await files_collection.update_one(
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
            files_collection = self._get_files_collection()
            file = await self.get_file_by_id(file_id, user_id)
            
            if file.processed:
                return {"message": "File already processed", "contacts_count": file.contacts_count}

            # Get file data from database
            file_doc = await files_collection.find_one({"_id": ObjectId(file_id)})
            file_data = file_doc["file_data"]

            # Process based on file type
            contacts_count = 0
            if file.file_type == "excel":
                contacts_count = await self._process_excel_file(file_data)
            elif file.file_type == "pdf":
                contacts_count = await self._process_pdf_file(file_data)
            elif file.file_type == "csv":
                contacts_count = await self._process_csv_file(file_data)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unsupported file type for processing"
                )

            # Update file as processed
            await files_collection.update_one(
                {"_id": ObjectId(file_id)},
                {"$set": {"processed": True, "contacts_count": contacts_count}}
            )

            return {"message": "File processed successfully", "contacts_count": contacts_count}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File processing failed: {str(e)}"
            )

    async def preview_file(self, file_id: str, user_id: str) -> dict:
        """Preview the data from a processed file."""
        try:
            files_collection = self._get_files_collection()
            file = await self.get_file_by_id(file_id, user_id)
            
            if not file.processed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File must be processed before previewing"
                )

            # Get file data from database
            file_doc = await files_collection.find_one({"_id": ObjectId(file_id)})
            file_data = file_doc["file_data"]

            # Extract preview data based on file type
            contacts = []
            if file.file_type == "excel":
                contacts = await self._preview_excel_file(file_data)
            elif file.file_type == "pdf":
                contacts = await self._preview_pdf_file(file_data)
            elif file.file_type == "csv":
                contacts = await self._preview_csv_file(file_data)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unsupported file type for preview"
                )

            return {"contacts": contacts, "file_id": file_id}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error previewing file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File preview failed: {str(e)}"
            )

    async def update_file_data(self, file_id: str, user_id: str, update_data: dict) -> dict:
        """Update file with new contact data."""
        try:
            files_collection = self._get_files_collection()
            
            # Verify file ownership
            file = await self.get_file_by_id(file_id, user_id)
            
            if not file.processed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File must be processed before updating"
                )
            
            # Validate update data
            if "contacts" not in update_data or not isinstance(update_data["contacts"], list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid update data. Expected 'contacts' array."
                )
            
            logger.info(f"📝 Updating file {file_id} for user {user_id} with {len(update_data['contacts'])} contacts")
            
            # Convert the new contact data to file format based on file type
            updated_file_data = None
            if file.file_type in ["excel", "csv"]:
                updated_file_data = await self._convert_contacts_to_file_data(
                    update_data["contacts"], 
                    file.file_type
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File type not supported for updates"
                )
            
            # Update the file document in database
            update_fields = {
                "file_data": updated_file_data,
                "contacts_count": len(update_data["contacts"]),
                "updated_at": datetime.utcnow(),
                "last_modified": datetime.utcnow()
            }
            
            result = await files_collection.update_one(
                {"_id": ObjectId(file_id)},
                {"$set": update_fields}
            )
            
            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            logger.info(f"✅ File {file_id} updated successfully")
            
            # Return the updated preview data
            return {
                "contacts": update_data["contacts"],
                "file_id": file_id,
                "message": "File updated successfully",
                "contacts_count": len(update_data["contacts"])
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File update failed: {str(e)}"
            )

    async def _convert_contacts_to_file_data(self, contacts: list, file_type: str) -> bytes:
        """Convert contact data back to file format."""
        try:
            import pandas as pd
            import io
            
            if not contacts:
                raise ValueError("No contacts provided")
            
            # Create DataFrame from contacts
            df = pd.DataFrame(contacts)
            
            # Convert to bytes based on file type
            buffer = io.BytesIO()
            
            if file_type == "excel":
                df.to_excel(buffer, index=False, engine='openpyxl')
            elif file_type == "csv":
                df.to_csv(buffer, index=False)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error converting contacts to file data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to convert contact data: {str(e)}"
            )

    async def rename_file(self, file_id: str, user_id: str, new_filename: str) -> dict:
        """Rename a file."""
        try:
            files_collection = self._get_files_collection()
            
            # Verify file ownership
            file = await self.get_file_by_id(file_id, user_id)
            
            if not new_filename or not new_filename.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Filename cannot be empty"
                )
            
            # Clean the filename
            clean_filename = new_filename.strip()
            
            logger.info(f"📝 Renaming file {file_id} from '{file.filename}' to '{clean_filename}' for user {user_id}")
            
            # Update the filename in database
            update_fields = {
                "filename": clean_filename,
                "updated_at": datetime.utcnow()
            }
            
            result = await files_collection.update_one(
                {"_id": ObjectId(file_id)},
                {"$set": update_fields}
            )
            
            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            logger.info(f"✅ File {file_id} renamed successfully to '{clean_filename}'")
            
            return {
                "message": "File renamed successfully",
                "filename": clean_filename,
                "file_id": file_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error renaming file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File rename failed: {str(e)}"
            )

    async def _preview_excel_file(self, file_data: bytes) -> list:
        """Preview Excel file data."""
        try:
            import pandas as pd
            df = pd.read_excel(io.BytesIO(file_data))
            # Convert DataFrame to list of dictionaries
            contacts = df.to_dict('records')
            return contacts
        except Exception as e:
            logger.error(f"Error previewing Excel file: {str(e)}")
            return []

    async def _preview_pdf_file(self, file_data: bytes) -> list:
        """Preview PDF file data."""
        try:
            # For PDF files, we'll return a placeholder since PDF parsing is complex
            # In a real implementation, you would extract text and parse it
            return [{"message": "PDF preview not implemented yet"}]
        except Exception as e:
            logger.error(f"Error previewing PDF file: {str(e)}")
            return []

    async def _preview_csv_file(self, file_data: bytes) -> list:
        """Preview CSV file data."""
        try:
            import pandas as pd
            df = pd.read_csv(io.BytesIO(file_data))
            # Convert DataFrame to list of dictionaries
            contacts = df.to_dict('records')
            return contacts
        except Exception as e:
            logger.error(f"Error previewing CSV file: {str(e)}")
            return []

    async def _process_excel_file(self, file_data: bytes) -> int:
        """Process Excel file to extract contacts."""
        # Placeholder implementation
        # In a real implementation, you would parse the Excel file
        # and extract contact information
        return 0

    async def _process_pdf_file(self, file_data: bytes) -> int:
        """Process PDF file to extract contacts."""
        # Placeholder implementation
        # In a real implementation, you would parse the PDF file
        # and extract contact information
        return 0

    async def _process_csv_file(self, file_data: bytes) -> int:
        """Process CSV file to extract contacts."""
        # Placeholder implementation
        # In a real implementation, you would parse the CSV file
        # and extract contact information
        return 0

    def _get_file_type(self, filename: str) -> str:
        """Determine file type based on extension."""
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        if extension in ['xlsx', 'xls']:
            return 'excel'
        elif extension == 'csv':
            return 'csv'
        elif extension == 'pdf':
            return 'pdf'
        else:
            return 'unknown' 