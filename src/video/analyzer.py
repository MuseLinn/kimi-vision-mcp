"""Video analysis using vision provider."""

import json

from pydantic import BaseModel, Field

from src.media import load_media
from src.providers.base import VisionProvider
from src.prompts import SYSTEM_PROMPTS, build_user_prompt, DetailLevel


class AnalyzeVideoInput(BaseModel):
    path: str = Field(..., description="Local video path or http(s) URL")
    detail: str = Field(default="smart", description="brief | smart | detailed | frames")
    focus: str = Field(default="", description="Focus instruction, e.g. 'analyze 0:15-0:25'")
    prompt_override: str = Field(default="", description="Override default prompt entirely")


def _estimate_time(size_bytes: int, detail: str) -> str:
    mb = size_bytes / (1024 * 1024)
    multipliers = {"brief": 0.5, "smart": 1.0, "detailed": 1.5, "frames": 2.0}
    multiplier = multipliers.get(detail, 1.0)
    seconds = (30 + mb * 10) * multiplier + max(5, mb * 5)
    if seconds < 60:
        return f"约 {int(seconds)} 秒"
    return f"约 {int(seconds // 60)}-{int(seconds // 60) + 1} 分钟"


def _extract_json(text: str) -> dict:
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"summary": text[:300], "key_moments": []}


async def analyze_video_file(provider: VisionProvider, params: AnalyzeVideoInput) -> dict:
    media = load_media(params.path, max_size_mb=100)
    estimate = _estimate_time(media.size_bytes, params.detail)

    if params.prompt_override:
        system = "You are a video analysis assistant."
        user = params.prompt_override
    else:
        system = SYSTEM_PROMPTS["analyze_video_file"]
        user = build_user_prompt("analyze video", DetailLevel(params.detail), params.focus)
        user = f"【预计耗时】{estimate}\n\n{user}\n\nVideo path: {media.path}"

    raw = await provider.analyze_video(str(media.path), system, user)
    parsed = _extract_json(raw)

    return {
        "summary": parsed.get("summary", raw[:300]),
        "key_moments": parsed.get("key_moments", []),
        "topics": parsed.get("topics", []),
        "visual_elements": parsed.get("visual_elements", []),
        "file_size_mb": round(media.size_bytes / (1024 * 1024), 2),
        "estimated_time": estimate,
        "detail_level": params.detail,
    }
