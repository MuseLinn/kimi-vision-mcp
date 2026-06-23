"""Moonshot OpenAI-compatible vision provider."""

import base64
import mimetypes
from pathlib import Path

import httpx

from src.providers.base import VisionProvider


class MoonshotProvider(VisionProvider):
    """Vision provider backed by Moonshot AI API."""

    def __init__(self, api_key: str, base_url: str, model: str, timeout: int = 300):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def chat(self, messages: list[dict]) -> str:
        """Send a raw chat completion request."""
        return await self._chat(messages)

    async def _chat(self, messages: list[dict], json_mode: bool = False) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def analyze_image(
        self,
        image_b64: str,
        mime: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{image_b64}"},
                    },
                ],
            },
        ]
        return await self._chat(messages)

    async def analyze_video(
        self,
        video_path: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        path = Path(video_path)
        raw = path.read_bytes()
        video_b64 = base64.b64encode(raw).decode("utf-8")
        mime, _ = mimetypes.guess_type(str(path))
        mime = mime or "video/mp4"

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "video_url",
                        "video_url": {"url": f"data:{mime};base64,{video_b64}"},
                    },
                ],
            },
        ]
        return await self._chat(messages)
