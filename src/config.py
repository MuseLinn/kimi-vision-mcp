"""Configuration management for video-analyzer-mcp."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Server settings loaded from environment variables."""

    api_key: str
    base_url: str
    model: str
    timeout: int
    max_image_size_mb: int
    max_video_size_mb: int


def _env_int(name: str, default: int, min_value: int, max_value: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got: {raw}") from exc
    if value < min_value or value > max_value:
        raise ValueError(f"{name} must be between {min_value} and {max_value}, got: {value}")
    return value


def load_settings(require_key: bool = True) -> Settings:
    """Load settings from environment variables.

    Args:
        require_key: If True, raise when MOONSHOT_API_KEY is missing.

    Raises:
        ValueError: When a required or malformed setting is encountered.
    """
    api_key = os.environ.get("MOONSHOT_API_KEY", "").strip()
    if require_key and not api_key:
        raise ValueError(
            "MOONSHOT_API_KEY is required. "
            "Set it as an environment variable or in the MCP server env config."
        )

    return Settings(
        api_key=api_key,
        base_url=os.environ.get("VISION_BASE_URL", "https://api.moonshot.ai/v1").rstrip("/"),
        model=os.environ.get("VISION_MODEL", "kimi-k2-6-code"),
        timeout=_env_int("VISION_TIMEOUT", 300, 10, 3600),
        max_image_size_mb=_env_int("VISION_MAX_IMAGE_SIZE_MB", 20, 1, 100),
        max_video_size_mb=_env_int("VISION_MAX_VIDEO_SIZE_MB", 100, 1, 500),
    )
