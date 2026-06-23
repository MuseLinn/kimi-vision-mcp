"""
Core video analysis logic — calls kimi CLI via subprocess for reliable async execution.
Provides dynamic time estimation and graceful timeout handling.
"""

import subprocess
import json
import hashlib
from pathlib import Path


def _run_kimi(prompt: str, timeout: int = 300) -> str:
    """Run kimi CLI in quiet mode with the given prompt."""
    result = subprocess.run(
        ["kimi", "--quiet", "--prompt", prompt],
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result.stdout

DETAIL_PROMPTS = {
    "brief": (
        "分析这个视频。请只输出：\n"
        "1. 一句话概括（30字以内）\n"
        "2. 最多8个关键时间节点，每个用1个标签词\n"
        '输出纯 JSON：{"summary": "...", "key_moments": [{"time": "0:00", "label": "..."}]}'
    ),
    "smart": (
        "详细分析这个视频。请输出 JSON：\n"
        "1. summary: 一句话概括（50字内）\n"
        "2. key_moments: 10-20个关键节点，含 time/label/detail\n"
        "3. topics: 核心主题关键词列表\n"
        "4. visual_elements: 重要的视觉/动画元素描述\n"
        "不要输出 markdown 代码块，直接输出 JSON。"
    ),
    "detailed": (
        "对这个视频进行详细分析。输出 JSON：\n"
        "1. summary: 整体摘要（100字）\n"
        "2. key_moments: 按时间分段描述\n"
        "3. technical_content: 如有技术内容，提取核心概念和公式\n"
        "4. visual_style: 动画风格、配色、制作质量评价\n"
        "直接输出 JSON，不要 markdown。"
    ),
    "frames": (
        "对这个视频进行逐场景/逐帧级别的详细分析。"
        "描述每一段时间内的画面内容、文字、图表、动画细节。"
        "输出 JSON，包含 time 和 description 字段。"
    ),
}


def estimate_time(file_size_bytes: int, detail: str) -> str:
    """Estimate analysis time based on file size and detail level."""
    mb = file_size_bytes / (1024 * 1024)
    upload_time = max(5, mb * 5)
    multipliers = {"brief": 0.5, "smart": 1.0, "detailed": 1.5, "frames": 2.0}
    multiplier = multipliers.get(detail, 1.0)
    analysis_time = (30 + mb * 10) * multiplier
    total = upload_time + analysis_time
    
    if total < 60:
        return f"约 {int(total)} 秒"
    elif total < 120:
        return f"约 1-2 分钟"
    elif total < 300:
        return f"约 {int(total // 60)}-{int(total // 60) + 1} 分钟"
    else:
        return f"约 {int(total // 60)} 分钟"


def analyze_video(video_path: str, detail: str = "smart", prompt_override: str = "") -> dict:
    video_path = Path(video_path).resolve()
    if not video_path.exists():
        raise FileNotFoundError(f"视频不存在: {video_path}")

    file_size = video_path.stat().st_size
    time_estimate = estimate_time(file_size, detail)

    file_hash = hashlib.sha256(str(video_path).encode()).hexdigest()[:12]
    output_dir = Path.home() / ".video_analysis"
    output_dir.mkdir(exist_ok=True)
    full_output = output_dir / f"{file_hash}_{video_path.stem}.json"

    prompt = prompt_override or DETAIL_PROMPTS.get(detail, DETAIL_PROMPTS["smart"])
    prompt = f"【预计耗时】{time_estimate}\n\n{prompt}\n\n视频路径: {video_path}"

    raw = _run_kimi(prompt)

    result = {
        "video_path": str(video_path),
        "detail_level": detail,
        "file_size_mb": round(file_size / (1024 * 1024), 2),
        "estimated_time": time_estimate,
        "summary": raw[:300] if len(raw) > 300 else raw,
        "key_moments": [],
        "full_analysis_path": str(full_output),
    }

    try:
        cleaned = raw
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        parsed = json.loads(cleaned)
        for key in ["summary", "key_moments", "topics", "visual_elements", "technical_content", "visual_style"]:
            if key in parsed:
                result[key] = parsed[key]
    except Exception as e:
        result["_parse_error"] = True
        result["_raw_preview"] = raw[:500]
        result["_parse_error_detail"] = str(e)

    full_data = {**result, "_raw_output": raw}
    full_output.write_text(json.dumps(full_data, ensure_ascii=False, indent=2), encoding="utf-8")

    if detail == "brief":
        return {
            "summary": result.get("summary", ""),
            "key_moments": result.get("key_moments", [])[:8],
            "full_analysis_path": str(full_output),
            "hint": "需要更多细节？用 detail='smart' 重新分析",
        }
    elif detail == "smart":
        return {
            "summary": result.get("summary", ""),
            "key_moments": result.get("key_moments", [])[:20],
            "topics": result.get("topics", []),
            "visual_elements": result.get("visual_elements", []),
            "full_analysis_path": str(full_output),
            "token_estimate": f"~{len(json.dumps(result)) // 4} tokens",
        }
    else:
        return result
