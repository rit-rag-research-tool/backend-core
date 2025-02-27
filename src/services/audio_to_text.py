from lib import LLMClient
from PIL import Image
from io import BytesIO


def audio_to_text(audio: bytes, llm: LLMClient) -> str:
    prompt = """You are a professional transcriber, and you have been asked to transcribe this audio file.
    Please write the transcription in as much detail as possible."""


    audio_file = BytesIO(audio)
    llm_response = llm.summarize_file(prompt, audio_file)
    return str(llm_response)