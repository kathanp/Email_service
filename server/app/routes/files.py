from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
from ..models.file import FileResponse
from ..services.file_service import FileService
from ..api.deps import get_current_user
from ..models.user import UserResponse

router = APIRouter()

@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload a file to the database."""
    file_service = FileService()
    return await file_service.upload_file(file, current_user.id, description)

@router.get("/", response_model=List[FileResponse])
async def get_user_files(current_user: UserResponse = Depends(get_current_user)):
    """Get all files uploaded by the current user."""
    file_service = FileService()
    return await file_service.get_user_files(current_user.id)

@router.get("/folder/{folder_id}", response_model=List[FileResponse])
async def get_files_by_folder(
    folder_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get files in a specific folder."""
    file_service = FileService()
    return await file_service.get_files_by_folder(current_user.id, folder_id)

@router.get("/uncategorized", response_model=List[FileResponse])
async def get_uncategorized_files(current_user: UserResponse = Depends(get_current_user)):
    """Get uncategorized files (not in any folder)."""
    file_service = FileService()
    return await file_service.get_files_by_folder(current_user.id, None)

@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific file by ID."""
    file_service = FileService()
    return await file_service.get_file_by_id(file_id, current_user.id)

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a file."""
    file_service = FileService()
    return await file_service.delete_file(file_id, current_user.id)

@router.post("/{file_id}/process")
async def process_file(
    file_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Process a file to extract contacts."""
    file_service = FileService()
    return await file_service.process_file(file_id, current_user.id)

@router.get("/{file_id}/preview")
async def preview_file(
    file_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Preview a file's data."""
    file_service = FileService()
    return await file_service.preview_file(file_id, current_user.id)

@router.put("/{file_id}/update")
async def update_file(
    file_id: str,
    update_data: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a file with new contact data."""
    file_service = FileService()
    return await file_service.update_file_data(file_id, current_user.id, update_data)

@router.put("/{file_id}/rename")
async def rename_file(
    file_id: str,
    rename_data: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Rename a file."""
    file_service = FileService()
    return await file_service.rename_file(file_id, current_user.id, rename_data.get("filename")) 