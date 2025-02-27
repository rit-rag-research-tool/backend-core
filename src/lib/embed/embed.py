from abc import ABC, abstractmethod
from typing import Union
from PIL import Image
from typing import List



class EmbeddingClient(ABC):
    """Abstract Base Class for Embeding Clients."""

    @abstractmethod
    async def get_text_embedding(self, text: str) -> list[float]:
        """Get embedding for a text input."""
        pass

    @abstractmethod
    async def get_image_embedding(self, text: str, image: Union[bytes, Image.Image]) -> list[float]:
        """Get embedding for an image input."""
        pass
