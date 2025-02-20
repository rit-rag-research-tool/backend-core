import os
import json
import time
import uuid
import asyncio
import uvicorn
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Header, Depends
from pydantic import BaseModel
from hashlib import sha256
from dotenv import load_dotenv

from typing import Any, Type, AsyncGenerator

from lib import User, MySQLClient, S3Pool, RedisClient, EmbeddingStatusResponse, RemoveKeyRequest

FILE_VERSION = "0.1.0"

# Load environment variables
load_dotenv()
def get_env(var: str, conv: Type[Any] = str) -> Any:
    value = os.getenv(var)
    if value is None:
        exit(f"ERROR: {var} is not set")
    return conv(value)

file_cache_client = RedisClient(
    host=get_env("FILE_CACHE_HOST"),
    port=int(get_env("FILE_CACHE_PORT")),
    db=0,
    decode_responses=True
)
general_cache_client = RedisClient(
    host=get_env("GENRAL_CACHE_HOST"),
    port=int(get_env("GENRAL_CACHE_PORT")),
    db=0,
    decode_responses=True
)


mysql_client = MySQLClient(
    host=get_env("MYSQL_HOST"),
    user=get_env("MYSQL_USER"),
    password=get_env("MYSQL_PASSWORD"),
    database=get_env("MYSQL_DATABASE"),
    port=int(get_env("MYSQL_PORT"))
)

s3_servers = get_env("S3_SERVERS").split(",")
s3_pool = S3Pool(
    s3_servers,
    get_env("S3_ACCESS_KEY"),
    get_env("S3_SECRET_KEY"),
    get_env("BUCKET_NAME"),
    general_cache_client.client  
)


# Dependency to get the authenticated user from the token header.
async def get_current_user(token: str = Header(...)) -> User:
    token = token.replace("Bearer ", "").strip() # Remove "Bearer" prefix, it will also check in the auth class so its not necessary to do so...
    user = User(token, dict(os.environ), general_cache_client.client)
    if not await user.verify_session():
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    await user.load_user_data()
    return user

# Simulated embedding process that writes to MySQL.
def process_embedding(file_hash: str, embedding_id: str, file: UploadFile = None) -> None:
    conn = mysql_client.connection
    file_cache_client.set_value(f"embedding_status:{embedding_id}", "Processing", expire_time=3600)
    time.sleep(5)
    file_cache_client.set_value(f"embedding_status:{embedding_id}", "Completed", expire_time=3600)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        if not general_cache_client.client.ping():
            raise ConnectionError("KeyDB is not reachable.")
        print("general_cache_client connection established.")
    except Exception as e:
        raise RuntimeError(f"Failed to connect to KeyDB: {str(e)}")
    
    try:
        if not file_cache_client.client.ping():
            raise ConnectionError("Redis is not reachable.")
        print("file_cache_client connection established.")
    except Exception as e:
        general_cache_client.close_connection()
        raise RuntimeError(f"Failed to connect to Redis: {str(e)}")
    
    if not mysql_client.is_connected():
        raise RuntimeError("MySQL is not reachable.")
    else:
        print("MySQL connection established.")
    
    try:
        results = await asyncio.gather(*(s3_pool.get_file_count(server) for server in s3_pool.s3_servers))
        print(results)
        if any(result == float('inf') for result in results):
            raise ConnectionError("Some or all S3 servers are not reachable.")
        print("S3 servers are reachable.")
    except Exception as e:
        general_cache_client.close_connection()
        file_cache_client.close_connection()
        mysql_client.close()
        raise RuntimeError(f"Failed to connect to S3 servers: {str(e)}")
    
    FILE_DRIFT = os.getenv("FILE_DRIFT")
    if not FILE_DRIFT.isdigit() or int(FILE_DRIFT) < 0:
        raise ValueError("FILE_DRIFT must be a positive integer")
    if FILE_DRIFT != "0":
        print("File drift monitoring is enabled.")
    else:
        print("FILE_DRIFT is set to 0. File drift monitoring is disabled.")
    
    print("-" * 20)
    print("Routes:")
    print("  /upload/")
    print("  /embedding-status/{embedding_id}")
    print("  /apikeys/new")
    print("  /apikeys")
    print("  /apikeys/remove")
    print("  /logout")
    print("-" * 20)
    
    yield
    general_cache_client.close_connection()
    file_cache_client.close_connection()
    mysql_client.close()
    print("Connections closed.")

app = FastAPI(lifespan=lifespan, title="RagStack", description=f"Backend Version: {FILE_VERSION}", version=FILE_VERSION, root_path="/src",) 

# File validation dependency.
async def file_validation(file: UploadFile = File(None)):
    if file is None or file.filename == "":
        raise HTTPException(status_code=400, detail="No file provided")
    return file

# --------------------------
# Routes
# --------------------------

@app.post("/upload/")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    
    # when a dupe file is uploaded, it sill generates a new embedding id, but the file is not reuploaded to s3, we could most likely cache the embbdings as well so we dont have to recompute them

    try:
        file = await file_validation(file)
        file_content = await file.read()
        file_hash = sha256(file_content).hexdigest()
        
        # Check for existing file metadata.
        existing_file_metadata = file_cache_client.get_value(file_hash)
        if existing_file_metadata:
            # If stored as a JSON string, convert to a dict.
            metadata = existing_file_metadata if isinstance(existing_file_metadata, dict) else json.loads(existing_file_metadata)
            if current_user.user_id not in metadata.get("users", []):
                metadata["users"].append(current_user.user_id)
            file_cache_client.set_value(file_hash, metadata)
        else:
            # Upload file using S3Pool.
            upload_success = await s3_pool.upload_file(os.getenv("BUCKET_NAME"), file_hash, file_content)
            print(f"File uploaded to S3: {upload_success}")
            if not upload_success:
                raise HTTPException(status_code=500, detail="Failed to upload file to S3")
            metadata = {
                "uploaded": datetime.utcnow().isoformat(),
                "server": upload_success,
                "users": [current_user.user_id]
            }
            file_cache_client.set_value(file_hash, metadata)
        
        # Create an embedding job.
        embedding_id = str(uuid.uuid4())
        general_cache_client.set_value(f"embedding_status:{embedding_id}", "Pending", expire_time=3600)
        background_tasks.add_task(process_embedding, file_hash, embedding_id, file)
        return {"message": "File uploaded successfully", "embedding_id": embedding_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.get("/embedding-status/{embedding_id}", response_model=EmbeddingStatusResponse)
async def get_embedding_status(embedding_id: str):
    try:
        status = general_cache_client.get_value(f"embedding_status:{embedding_id}")
        if not status:
            raise HTTPException(status_code=404, detail=f"Embedding job with ID '{embedding_id}' not found")
        return EmbeddingStatusResponse(embedding_id=embedding_id, status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/apikeys/new")
async def create_api_key(current_user: User = Depends(get_current_user)):
    new_key = await current_user.create_api_key()
    return {"message": "API key created", "api_key": new_key}

@app.get("/apikeys")
async def list_api_keys(current_user: User = Depends(get_current_user)):
    keys = await current_user.get_user_api_keys()
    return {"api_keys": keys}

@app.post("/apikeys/remove")
async def remove_api_key(request_data: RemoveKeyRequest, current_user: User = Depends(get_current_user)):
    if request_data.api_key not in current_user.api_keys:
        raise HTTPException(status_code=404, detail="API key not found")
    new_keys = [key for key in current_user.api_keys if key != request_data.api_key]
    await current_user.update_user_api_keys(new_keys)
    current_user.api_keys = new_keys
    return {"message": "API key removed", "api_keys": new_keys}

@app.post("/logout") #this is btroken rn so sad :(
async def logout(current_user: User = Depends(get_current_user)):
    print("Logging out user...")
    #await current_user.revoke_token()
    return {"message": "Token not revoked"}

# Uncomment for local development:
# if __name__ == "__main__":
#     uvicorn.run(app, host="localhost", port=8000)