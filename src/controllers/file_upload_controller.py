from fastapi import HTTPException, BackgroundTasks, UploadFile, Request
from typing import Dict, Any
from hashlib import sha256
import json, os, uuid
from datetime import datetime

from lib import dependencies
from services import file_validation

# from services.embedding import process_embedding

async def upload_file_service(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile,
    current_user: Any
) -> Dict[str, Any]:
    
    # Get shared resources from app.state via dependency helper functions
    file_cache_client = dependencies.get_file_cache_client(request)
    general_cache_client = dependencies.get_general_cache_client(request)
    s3_pool = dependencies.get_s3_pool(request)

    try:
        # Validate and read the file; file_validation will raise if type unsupported
        file = file_validation(file)
        file_content = await file.read()
        file_hash = sha256(file_content).hexdigest()

        # Determine the file type from the attached attribute (set in file_validation)
        file_type = getattr(file, "file_type", "TXT")  # default to "TXT" if not set

        # Check for existing file metadata
        existing_file_metadata = file_cache_client.get_value(file_hash)
        if existing_file_metadata:
            # Convert to dict if stored as JSON
            metadata = (
                existing_file_metadata
                if isinstance(existing_file_metadata, dict)
                else json.loads(existing_file_metadata)
            )
            if current_user.user_id not in metadata.get("users", []):
                metadata["users"].append(current_user.user_id)
        else:
            # Upload file using S3Pool
            upload_success = await s3_pool.upload_file(
                str(os.getenv("BUCKET_NAME")), file_hash, file_content
            )
            print(f"File uploaded to S3: {upload_success}")
            if not upload_success:
                raise HTTPException(status_code=500, detail="Failed to upload file to S3")
            metadata = {
                "uploaded": datetime.utcnow().isoformat(),
                "server": upload_success,
                "users": [current_user.user_id],
                "file_type": file_type  # save the determined file type
            }
            file_cache_client.set_value(file_hash, metadata)

        # Create an embedding job.
        embedding_id = str(uuid.uuid4())
        general_cache_client.set_value(f"embedding_status:{embedding_id}", "Pending", expire_time=3600)
        background_tasks.add_task(process_embedding, file_hash, embedding_id, file)
        return {"message": "File uploaded successfully", "embedding_id": embedding_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
    
    finally:
        await file.close()

def process_embedding(file_hash: str, embedding_id: str, file: UploadFile) -> None:
    pass