import os
import json
from lib import CromaDBClient, get_env, get_croma_client, FILE_TYPE_MAP, get_s3_pool, get_llm_client, get_embedding_client
from lib.models import EmbeddingStatusResponse
from typing import Dict, Any
from fastapi import Request, UploadFile, Header
from .process_pdf import process_pdf
from .photo_to_text import photo_to_text
from .audio_to_text import audio_to_text
from .video_to_text import video_to_text

async def process_embedding(hash: str, embedding_id: str, file: UploadFile, request: Request, server: str,  collection: str = Header(..., alias="collection")) -> None:

    env = get_env(request)
    croma_client = get_croma_client(request)
    s3_pool = get_s3_pool(request)
    llm_client = get_llm_client(request)
    embedding_client = get_embedding_client(request)
    
    original_name = getattr(file, "file_name", "unknown")
    original_extension = getattr(file, "file_extension", "unknown")
    
    file_type = getattr(file, "file_type", None)
    if file_type is None:
        raise ValueError("File type not set")
    
    if file_type not in FILE_TYPE_MAP:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    file_content = file.file.read()

    extracted_text: str = ""
    photos: list[bytes] = []

    if file_type == "PDF":
        extracted_text, photos = process_pdf(file_content)
    elif file_type == "TXT":
        extracted_text = file_content.decode("utf-8")
    elif file_type == "PHO":
        extracted_text = photo_to_text(file_content, llm_client)
        photos = [file_content]
    elif file_type == "AUD":
        extracted_text = audio_to_text(file_content)
    elif file_type == "VID":
        extracted_text = video_to_text(file_content)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    if extracted_text:
        if "/d/=/-t/" in extracted_text:
            extracted_text_by_page = extracted_text.split("/d/=/-t/")
            text_chunks = chunk_text_by_page(extracted_text_by_page)
        else:   
            text_chunks = chunk_text(extracted_text)
        chunck_id = 0
        embeding_data = {"verison": "0.1.0" ,"text_chunks": len(text_chunks), "photos": len(photos), "embedding_id": embedding_id, "hash": hash, "related_data": [], "orignal_name": original_name, "orignal_type": original_extension}
        for chunk in text_chunks:
            chunck_id += 1
            embedding = await embedding_client.get_text_embedding(chunk)
            croma_client.add_document(collection_name=collection, uri=server, embeddings=embedding, hash=hash)
            await s3_pool.upload_file(str(env["BUCKET_NAME"]), f"{hash}/embedings/{chunck_id}.TXT", chunk.encode("utf-8"))
            await s3_pool.upload_file(str(env["BUCKET_NAME"]), f"{hash}/embedings/{chunck_id}.TXT.ENB", json.dumps(embedding).encode("utf-8"))
    if photos:
        formatted_photo_data = [format_photo_data(photo) for photo in photos]
        chunck_id = 0
        for photo_data in formatted_photo_data:
            chunck_id += 1
            if text_chunks[chunck_id-1] == None:
                photo_discription = photo_to_text(photo_data, llm_client)
                photo_discription = chunk_text(extracted_text)
                embedding = await embedding_client.get_image_embedding(photo_discription[0], photo_data)
            else:
                embedding = await embedding_client.get_image_embedding(text_chunks[chunck_id-1], photo_data)
                
            croma_client.add_document(collection_name=collection, uri=server, embeddings=embedding, hash=hash)
            await s3_pool.upload_file(str(env["BUCKET_NAME"]), f"{hash}/embedings/{chunck_id}.PHO", json.dumps(photo_data).encode("utf-8"))
            await s3_pool.upload_file(str(env["BUCKET_NAME"]), f"{hash}/embedings/{chunck_id}.PHO.ENB", json.dumps(embedding).encode("utf-8"))

    
    await s3_pool.upload_file(str(env["BUCKET_NAME"]), f"{hash}/embedings/data.json", json.dumps(embeding_data).encode("utf-8"))
    
