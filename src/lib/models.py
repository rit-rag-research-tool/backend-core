from pydantic import BaseModel

# Data Models
class EmbeddingStatusResponse(BaseModel):
    embedding_id: str
    status: str  # Pending, Processing, Completed, Failed

class RemoveKeyRequest(BaseModel):
    api_key: str