from fastapi import APIRouter, BackgroundTasks, File, UploadFile, Depends, Request
from typing import Dict, Any
from controllers import upload_file_service
from lib import get_current_user
from lib.user import User

router = APIRouter()

@router.post("/")
async def upload_file_endpoint(
    request: Request,  # Pass request object here
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    return await upload_file_service(request, background_tasks, file, current_user)
