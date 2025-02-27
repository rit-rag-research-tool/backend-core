from abc import ABC, abstractmethod
from typing import Optional, Union, BinaryIO


class LLMClient(ABC):
    """Abstract Base Class for LLM Clients."""

    @abstractmethod
    async def generate_text(self, prompt: str, model: Optional[str] = None, max_output: Optional[int] = None) -> str:
        """Generate text response from the model."""
        pass

    @abstractmethod
    async def summarize_file(self, prompt: str, file: Union[str, BinaryIO], model: Optional[str] = None) -> str:
        """Summarize the content of a file (text, PDF, etc.)."""
        pass
