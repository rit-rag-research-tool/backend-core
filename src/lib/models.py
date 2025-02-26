from pydantic import BaseModel


# Data Models
class EmbeddingStatusResponse(BaseModel):
    embedding_id: str
    status: str  # Pending, Processing, Completed, Failed

class RemoveKeyRequest(BaseModel):
    api_key: str


FILE_TYPE_MAP = {
    # High Priority: Documents & Programming Files (treated as text)
    ".doc": "TXT",
    ".docx": "TXT",
    ".rtf": "TXT",
    ".pdf": "TXT",    # we will most likely extract text from PDFs then embed them so we will need a new code for this but thats for later
    ".wpd": "TXT",
    ".txt": "TXT",
    ".md": "TXT",
    ".csv": "TXT",
    ".bat": "TXT",
    ".sh": "TXT",
    ".html": "TXT",
    ".css": "TXT",
    ".htm": "TXT",
    ".xhtml": "TXT",
    ".c": "TXT",
    ".h": "TXT",
    ".js": "TXT",
    ".py": "TXT",
    ".lua": "TXT",
    ".go": "TXT",

    # Medium Priority: Images & Audio
    ".jpeg": "PHO",
    ".jpg": "PHO",
    ".png": "PHO",
    ".gif": "PHO",
    ".heif": "PHO",
    ".bmp": "PHO",
    ".tif": "PHO",
    ".webp": "PHO",
    ".eps": "PHO",

    ".mp3": "AUD",
    ".wav": "AUD",
    ".wma": "AUD",
    ".aac": "AUD",

    # Low Priority: Video
    ".3gp": "VID",
    ".mp4": "VID",
    ".avi": "VID",
    ".mpg": "VID",
    ".mov": "VID",
    ".wmv": "VID",
}
    