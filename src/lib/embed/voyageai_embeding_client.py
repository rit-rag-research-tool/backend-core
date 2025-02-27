import voyageai
from PIL import Image
from io import BytesIO
from typing import Union
from .embed import EmbeddingClient


class VoyageAIEmbeddingClient(EmbeddingClient):
    """Voyage AI multimodal embedding client."""

    def __init__(self, api_key: str, dim: int = 1024) -> None:
        self.client = voyageai.AsyncClient(api_key)  # type: ignore
        self.dim = dim

    async def get_text_embedding(self, text: str) -> list[float]:
        response = await self.client.multimodal_embed(
            inputs=[{"content": text}],
            model="voyage-multimodal-3"
        )
        return response.embeddings[0]


    async def get_image_embedding(self, text: str, image: Union[bytes, Image.Image]) -> list[float]:
        """
        Get embedding for an image input.
        """
        if isinstance(image, bytes):
            image = Image.open(BytesIO(image))

        response = await self.client.multimodal_embed(
            inputs=[{text: image}], 
            model="voyage-multimodal-3"
        )
        return response.embeddings[0]
