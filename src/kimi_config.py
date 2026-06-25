"""Read kimi-code config.toml to auto-discover vision-capable models."""

import tomllib
from dataclasses import dataclass
from pathlib import Path


def _kimi_config_path() -> Path:
    return Path.home() / ".kimi-code" / "config.toml"


@dataclass(frozen=True)
class VisionCandidate:
    """A discovered vision-capable model with its provider details."""

    model_id: str  # e.g. "opencode-go/mimo-v2.5"
    provider: str  # e.g. "opencode-go"
    model: str  # model string for API, e.g. "mimo-v2.5"
    display_name: str
    api_key: str
    base_url: str
    has_image: bool
    has_video: bool


def discover_vision_models(config_path: Path | None = None) -> list[VisionCandidate]:
    """Parse kimi-code config.toml and return all vision-capable models.

    Filters for models whose capabilities include 'image_in' or 'video_in',
    then resolves each model's provider to get api_key and base_url.
    """
    path = config_path or _kimi_config_path()
    if not path.exists():
        return []

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return []

    providers: dict[str, dict] = data.get("providers", {})
    models: dict[str, dict] = data.get("models", {})

    candidates: list[VisionCandidate] = []

    for model_alias, model_cfg in models.items():
        caps = model_cfg.get("capabilities", [])
        has_image = "image_in" in caps
        has_video = "video_in" in caps
        if not has_image and not has_video:
            continue

        provider_id = model_cfg.get("provider", "")
        provider_cfg = providers.get(provider_id, {})
        if not provider_cfg:
            continue

        # Resolve api_key: fall back to oauth if direct key is empty
        api_key = provider_cfg.get("api_key", "")
        if not api_key and "oauth" in provider_cfg:
            api_key = ""  # oauth tokens are managed externally, pass empty

        base_url = provider_cfg.get("base_url", "")
        if not base_url:
            continue

        candidates.append(
            VisionCandidate(
                model_id=model_alias,
                provider=provider_id,
                model=model_cfg.get("model", ""),
                display_name=model_cfg.get("display_name", model_cfg.get("model", "")),
                api_key=api_key,
                base_url=base_url,
                has_image=has_image,
                has_video=has_video,
            )
        )

    return candidates


def select_best_vision_model(
    candidates: list[VisionCandidate],
    preferred: str = "",
) -> VisionCandidate | None:
    """Pick the best vision model.

    Priority:
    1. If `preferred` matches a model_id or model name, use that.
    2. Otherwise return the first candidate (order follows config.toml).
    """
    if not candidates:
        return None

    if preferred:
        for c in candidates:
            if preferred in (c.model_id, c.model, c.display_name):
                return c

    return candidates[0]
