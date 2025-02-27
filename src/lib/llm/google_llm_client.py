from google import genai
from google.genai import types
from typing import Optional, Union, BinaryIO, Any
from .llm import LLMClient

class GoogleLLMClient(LLMClient):
    def __init__(self, api_key: str, model: str, grounding: bool = False):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.grounding = grounding

    async def generate_text(self, prompt: str, model: Optional[str] = None, max_output: Optional[int] = None) -> str:
        model = model or self.model

        response = await self.client.aio.models.generate_content(
            model=model, 
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_output if max_output else 500
            )
        )
        return str(response.text)

    async def summarize_file(self, prompt: str, file: Union[str, BinaryIO], model: Optional[str] = None) -> str:
        model = model or self.model
        uploaded_file = await self.client.aio.files.upload(file=file)

        response = await self.client.aio.models.generate_content(
            model=model, 
            contents=[prompt, uploaded_file]
        )
        return str(response.text)
