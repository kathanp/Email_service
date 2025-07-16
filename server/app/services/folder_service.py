import logging
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException, status
from ..db.mongodb import MongoDB
from ..models.folder import FolderCreate, FolderUpdate, FolderInDB, FolderResponse

logger = logging.getLogger(__name__)

class FolderService:
    def __init__(self):
        pass

    def _get_folders_collection(self):
        """Get folders collection."""
        return MongoDB.get_collection("folders")

    def _get_files_collection(self):
        """Get files collection."""
        return MongoDB.get_collection("files")

    async def create_folder(self, folder_data: FolderCreate, user_id: str) -> FolderResponse:
        """Create a new folder."""
        try:
            folders_collection = self._get_folders_collection()
            
            # Check if folder name already exists for this user
            existing_folder = await folders_collection.find_one({
                "user_id": user_id,
                "name": folder_data.name
            })
            
            if existing_folder:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Folder with this name already exists"
                )
            
            logger.info(f"📁 Creating folder '{folder_data.name}' for user {user_id}")
            
            # Create folder document
            folder_doc = {
                "name": folder_data.name,
                "description": folder_data.description,
                "color": folder_data.color or "#007bff",
                "user_id": user_id,
                "file_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await folders_collection.insert_one(folder_doc)
            folder_doc["_id"] = result.inserted_id
            
            logger.info(f"✅ Folder '{folder_data.name}' created successfully with ID {result.inserted_id}")
            
            return FolderResponse(
                id=str(result.inserted_id),
                name=folder_doc["name"],
                description=folder_doc["description"],
                color=folder_doc["color"],
                file_count=0,
                created_at=folder_doc["created_at"],
                updated_at=folder_doc["updated_at"]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Folder creation failed: {str(e)}"
            )

    async def get_user_folders(self, user_id: str) -> List[FolderResponse]:
        """Get all folders for a user."""
        try:
            folders_collection = self._get_folders_collection()
            files_collection = self._get_files_collection()
            
            # Get all folders for the user
            cursor = folders_collection.find({"user_id": user_id}).sort("created_at", 1)
            folders = await cursor.to_list(length=None)
            
            # Get file counts for each folder
            folder_responses = []
            for folder in folders:
                file_count = await files_collection.count_documents({
                    "user_id": user_id,
                    "folder_id": str(folder["_id"])
                })
                
                folder_responses.append(FolderResponse(
                    id=str(folder["_id"]),
                    name=folder["name"],
                    description=folder.get("description"),
                    color=folder.get("color", "#007bff"),
                    file_count=file_count,
                    created_at=folder["created_at"],
                    updated_at=folder["updated_at"]
                ))
            
            return folder_responses
            
        except Exception as e:
            logger.error(f"Error getting user folders: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get folders: {str(e)}"
            )

    async def get_folder_by_id(self, folder_id: str, user_id: str) -> FolderResponse:
        """Get a specific folder by ID."""
        try:
            folders_collection = self._get_folders_collection()
            files_collection = self._get_files_collection()
            
            folder = await folders_collection.find_one({
                "_id": ObjectId(folder_id),
                "user_id": user_id
            })
            
            if not folder:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Folder not found"
                )
            
            # Get file count
            file_count = await files_collection.count_documents({
                "user_id": user_id,
                "folder_id": folder_id
            })
            
            return FolderResponse(
                id=str(folder["_id"]),
                name=folder["name"],
                description=folder.get("description"),
                color=folder.get("color", "#007bff"),
                file_count=file_count,
                created_at=folder["created_at"],
                updated_at=folder["updated_at"]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting folder: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get folder: {str(e)}"
            )

    async def update_folder(self, folder_id: str, user_id: str, folder_data: FolderUpdate) -> FolderResponse:
        """Update a folder."""
        try:
            folders_collection = self._get_folders_collection()
            
            # Check if folder exists and belongs to user
            existing_folder = await folders_collection.find_one({
                "_id": ObjectId(folder_id),
                "user_id": user_id
            })
            
            if not existing_folder:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Folder not found"
                )
            
            # Check for name conflicts if name is being updated
            if folder_data.name:
                name_conflict = await folders_collection.find_one({
                    "user_id": user_id,
                    "name": folder_data.name,
                    "_id": {"$ne": ObjectId(folder_id)}
                })
                
                if name_conflict:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Folder with this name already exists"
                    )
            
            # Build update document
            update_doc = {"updated_at": datetime.utcnow()}
            if folder_data.name is not None:
                update_doc["name"] = folder_data.name
            if folder_data.description is not None:
                update_doc["description"] = folder_data.description
            if folder_data.color is not None:
                update_doc["color"] = folder_data.color
            
            # Update folder
            await folders_collection.update_one(
                {"_id": ObjectId(folder_id)},
                {"$set": update_doc}
            )
            
            logger.info(f"✅ Folder {folder_id} updated successfully")
            
            # Return updated folder
            return await self.get_folder_by_id(folder_id, user_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating folder: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Folder update failed: {str(e)}"
            )

    async def delete_folder(self, folder_id: str, user_id: str) -> dict:
        """Delete a folder and move its files to uncategorized."""
        try:
            folders_collection = self._get_folders_collection()
            files_collection = self._get_files_collection()
            
            # Check if folder exists
            folder = await folders_collection.find_one({
                "_id": ObjectId(folder_id),
                "user_id": user_id
            })
            
            if not folder:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Folder not found"
                )
            
            # Move all files in this folder to uncategorized (remove folder_id)
            await files_collection.update_many(
                {
                    "user_id": user_id,
                    "folder_id": folder_id
                },
                {"$unset": {"folder_id": ""}, "$set": {"updated_at": datetime.utcnow()}}
            )
            
            # Delete the folder
            await folders_collection.delete_one({"_id": ObjectId(folder_id)})
            
            logger.info(f"✅ Folder {folder_id} deleted successfully")
            
            return {"message": "Folder deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting folder: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Folder deletion failed: {str(e)}"
            )

    async def move_file_to_folder(self, file_id: str, folder_id: Optional[str], user_id: str) -> dict:
        """Move a file to a folder or to uncategorized."""
        try:
            files_collection = self._get_files_collection()
            folders_collection = self._get_folders_collection()
            
            # Check if file exists and belongs to user
            file_doc = await files_collection.find_one({
                "_id": ObjectId(file_id),
                "user_id": user_id
            })
            
            if not file_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # If moving to a folder, verify folder exists
            if folder_id:
                folder = await folders_collection.find_one({
                    "_id": ObjectId(folder_id),
                    "user_id": user_id
                })
                
                if not folder:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Folder not found"
                    )
                
                # Update file with folder_id
                await files_collection.update_one(
                    {"_id": ObjectId(file_id)},
                    {"$set": {"folder_id": folder_id, "updated_at": datetime.utcnow()}}
                )
            else:
                # Move to uncategorized (remove folder_id)
                await files_collection.update_one(
                    {"_id": ObjectId(file_id)},
                    {"$unset": {"folder_id": ""}, "$set": {"updated_at": datetime.utcnow()}}
                )
            
            logger.info(f"✅ File {file_id} moved to folder {folder_id or 'uncategorized'}")
            
            return {"message": "File moved successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error moving file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File move failed: {str(e)}"
            ) 