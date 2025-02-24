import os
from fastapi import UploadFile
from lib import FILE_TYPE_MAP

def file_validation(file: UploadFile) -> UploadFile:
    _, ext = os.path.splitext(str(file.filename))
    ext = ext.lower()

    if ext not in FILE_TYPE_MAP:
        raise ValueError(f"Unsupported file type: {ext}")

    setattr(file, 'file_type', FILE_TYPE_MAP[ext])
    return file
