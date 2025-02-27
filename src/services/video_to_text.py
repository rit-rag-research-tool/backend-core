from lib import LLMClient
from PIL import Image
from io import BytesIO


def video_to_text(video: bytes, llm: LLMClient) -> str:
    prompt = """You are a professional transcriber, and you have been asked to transcribe this video file.
    Please write the transcription in as much detail as possible."""


    video_file = BytesIO(video)
    llm_response = llm.summarize_file(prompt, video_file)
    return str(llm_response)
