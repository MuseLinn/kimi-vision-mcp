"""Abstract provider interface for vision-capable APIs."""

from abc import ABC, abstractmethod


class VisionProvider(ABC):
    """Base class for vision providers."""

    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        """Send a chat completion request and return the content string."""
        ...

    @abstractmethod
    async def analyze_image(
        self,
        image_b64: str,
        mime: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Analyze a base64-encoded image."""
        ...

    @abstractmethod
    async def analyze_video(
        self,
        video_path: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Analyze a local video file."""
        ...
