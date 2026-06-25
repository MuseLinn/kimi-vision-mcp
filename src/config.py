"""Configuration management for kimi-vision-mcp.

Priority order for resolving vision model:
  1. Explicit env vars: VISION_API_KEY + VISION_BASE_URL + VISION_MODEL
  2. Legacy env var: MOONSHOT_API_KEY (Moonshot API fallback)
  3. kimi-code config.toml auto-discovery (read-only, filters vision-capable models)

MCP-specific defaults (default_model, timeout, etc.) live in ~/.kimi-vision/config.toml
— this is a SEPARATE file, never touches ~/.kimi-code/config.toml.
"""

import os
from dataclasses import dataclass, field

from src.kimi_config import (
    VisionCandidate,
    discover_vision_models,
    load_mcp_config,
    select_best_vision_model,
)


@dataclass(frozen=True)
class Settings:
    """Server settings loaded from environment variables or kimi-code config."""

    api_key: str
    base_url: str
    model: str
    timeout: int
    max_image_size_mb: int
    max_video_size_mb: int
    source: str = "env"  # "env", "moonshot", "kimi-code"


@dataclass
class VisionModelList:
    """Summary of available vision models discovered from kimi-code config."""

    candidates: list[VisionCandidate] = field(default_factory=list)
    selected: VisionCandidate | None = None


def _env_int(name: str, default: int, min_value: int, max_value: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got: {raw}") from exc
    if value < min_value or value > max_value:
        raise ValueError(f"{name} must be between {min_value} and {max_value}, got: {value}")
    return value


def _try_kimi_code_config() -> tuple[str, str, str, str] | None:
    """Try to read kimi-code config.toml and return (api_key, base_url, model, display_name)."""
    candidates = discover_vision_models()
    if not candidates:
        return None

    # Get MCP config default_model if no env override
    mcp_cfg = load_mcp_config()
    preferred = mcp_cfg.default_model if mcp_cfg else ""

    selected = select_best_vision_model(candidates, preferred)
    if selected is None:
        return None

    return selected.api_key, selected.base_url, selected.model, selected.display_name


def load_settings(require_key: bool = True) -> Settings:
    """Load settings with cascading fallback:

    1. Explicit VISION_API_KEY / VISION_BASE_URL / VISION_MODEL env vars
    2. MOONSHOT_API_KEY legacy env var
    3. kimi-code config.toml auto-discovery (read-only, with MCP config defaults)
    """
    # Read MCP config (~/.kimi-vision/config.toml) for defaults
    mcp_cfg = load_mcp_config()
    kv_timeout = mcp_cfg.timeout if mcp_cfg else 300
    kv_max_image = mcp_cfg.max_image_size_mb if mcp_cfg else 20
    kv_max_video = mcp_cfg.max_video_size_mb if mcp_cfg else 100

    # Env vars override MCP config defaults; validated via _env_int
    timeout = _env_int("VISION_TIMEOUT", kv_timeout, 10, 3600)
    max_image = _env_int("VISION_MAX_IMAGE_SIZE_MB", kv_max_image, 1, 100)
    max_video = _env_int("VISION_MAX_VIDEO_SIZE_MB", kv_max_video, 1, 500)

    # Priority 1: explicit env vars
    api_key = os.environ.get("VISION_API_KEY", "").strip()
    base_url = os.environ.get("VISION_BASE_URL", "").strip()
    model = os.environ.get("VISION_MODEL", "").strip()

    if api_key and base_url and model:
        return Settings(
            api_key=api_key,
            base_url=base_url.rstrip("/"),
            model=model,
            timeout=timeout,
            max_image_size_mb=max_image,
            max_video_size_mb=max_video,
            source="env",
        )

    # Priority 2: MOONSHOT_API_KEY legacy
    moonshot_key = os.environ.get("MOONSHOT_API_KEY", "").strip()
    if moonshot_key:
        return Settings(
            api_key=moonshot_key,
            base_url=(base_url or "https://api.moonshot.ai/v1").rstrip("/"),
            model=model or "kimi-k2.7-code",
            timeout=timeout,
            max_image_size_mb=max_image,
            max_video_size_mb=max_video,
            source="moonshot",
        )

    # Priority 3: kimi-code config.toml auto-discovery
    kimi = _try_kimi_code_config()
    if kimi:
        k_api, k_url, k_model, k_name = kimi
        if k_api:  # has API key (non-oauth provider)
            return Settings(
                api_key=k_api,
                base_url=k_url.rstrip("/"),
                model=k_model,
                timeout=timeout,
                max_image_size_mb=max_image,
                max_video_size_mb=max_video,
                source="kimi-code",
            )

    if require_key:
        raise ValueError(
            "No vision model configured. Set one of:\n"
            "  1. VISION_API_KEY + VISION_BASE_URL + VISION_MODEL\n"
            "  2. MOONSHOT_API_KEY\n"
            "  3. A vision-capable model in ~/.kimi-code/config.toml\n"
            "\n"
            "To set MCP defaults, create ~/.kimi-vision/config.toml:\n"
            '  default_model = "opencode-go/mimo-v2.5"'
        )

    return Settings(
        api_key="",
        base_url="",
        model="",
        timeout=timeout,
        max_image_size_mb=max_image,
        max_video_size_mb=max_video,
        source="none",
    )


def list_vision_models() -> VisionModelList:
    """Discover all vision-capable models from kimi-code config.toml.

    Selection priority:
      1. VISION_MODEL env var
      2. default_model in ~/.kimi-vision/config.toml
      3. First candidate
    """
    candidates = discover_vision_models()
    mcp_cfg = load_mcp_config()
    preferred = mcp_cfg.default_model if mcp_cfg else ""
    selected = select_best_vision_model(candidates, preferred)
    return VisionModelList(candidates=candidates, selected=selected)
