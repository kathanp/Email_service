from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from ..models.folder import FolderCreate, FolderUpdate, FolderResponse
from ..services.folder_service import FolderService
from ..api.deps import get_current_user
from ..models.user import UserResponse

router = APIRouter()

@router.post("/", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder_data: FolderCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new folder."""
    folder_service = FolderService()
    return await folder_service.create_folder(folder_data, current_user.id)

@router.get("/", response_model=List[FolderResponse])
async def get_user_folders(current_user: UserResponse = Depends(get_current_user)):
    """Get all folders for the current user."""
    folder_service = FolderService()
    return await folder_service.get_user_folders(current_user.id)

@router.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific folder by ID."""
    folder_service = FolderService()
    return await folder_service.get_folder_by_id(folder_id, current_user.id)

@router.put("/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: str,
    folder_data: FolderUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a folder."""
    folder_service = FolderService()
    return await folder_service.update_folder(folder_id, current_user.id, folder_data)

@router.delete("/{folder_id}")
async def delete_folder(
    folder_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a folder and move its files to uncategorized."""
    folder_service = FolderService()
    return await folder_service.delete_folder(folder_id, current_user.id)

@router.put("/{folder_id}/files/{file_id}")
async def move_file_to_folder(
    folder_id: str,
    file_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Move a file to a folder."""
    folder_service = FolderService()
    return await folder_service.move_file_to_folder(file_id, folder_id, current_user.id)

@router.delete("/uncategorized/files/{file_id}")
async def move_file_to_uncategorized(
    file_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Move a file to uncategorized (remove from folder)."""
    folder_service = FolderService()
    return await folder_service.move_file_to_folder(file_id, None, current_user.id) 