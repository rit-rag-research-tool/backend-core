from lib import LLMClient
from PIL import Image
import io


def photo_to_text(photo: bytes, llm: LLMClient) -> str:
    prompt = """You are a professional photographer and you have taken this photo.
    Please write a description of the photo in a few sentences."""

    img = Image.open(photo)

    # Convert the PIL Image back to bytes using BytesIO
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=img.format or 'PNG')
    img_bytes.seek(0)

    llm_response = llm.summarize_file(prompt, img_bytes)
    return str(llm_response)