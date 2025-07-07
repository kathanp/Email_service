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
    """Preview the data from a processed file."""
    file_service = FileService()
    return await file_service.preview_file(file_id, current_user.id) 