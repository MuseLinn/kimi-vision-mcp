#!/usr/bin/env python3
"""
Video Analyzer MCP Server
让支持 MCP 的 Agent 通过 kimi CLI 进行原生视频多模态分析。

Transport: stdio (默认) / sse / streamable-http
Usage:    python server.py [--transport stdio|sse|streamable-http] [--port PORT]
"""

import sys
import argparse
import json
import tempfile
import urllib.request
import re
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP
from analyzer import analyze_video, estimate_time, DETAIL_PROMPTS


def _download_if_url(source: str) -> str:
    """If source is a URL, download to a temp file and return the local path."""
    if source.startswith(("http://", "https://")):
        suffix = Path(source.split("?")[0]).suffix or ".mp4"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            urllib.request.urlretrieve(source, f.name)
            return f.name
    return source


def _build_focus_prompt(base_prompt: str, focus: str) -> str:
    """Inject time-range / focus instructions into the prompt."""
    if not focus:
        return base_prompt

    time_pattern = r"(\d+:\d+(?::\d+)?(?:\s*-\s*\d+:\d+(?::\d+)?)?|\d+s?\s*-\s*\d+s?)"
    time_match = re.search(time_pattern, focus)

    focus_instruction = f"\n\n【用户特别关注】{focus}\n"
    if time_match:
        focus_instruction += (
            f"请重点分析视频中 {time_match.group(0)} 这一时间段的内容，"
            f"同时结合前后上下文进行评价。"
        )
    else:
        focus_instruction += "请特别关注上述内容，并在分析中重点回应。"

    return base_prompt + focus_instruction


def main():
    parser = argparse.ArgumentParser(description="Video Analyzer MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP/SSE transport (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for HTTP/SSE transport (default: 127.0.0.1)"
    )
    args = parser.parse_args()

    mcp = FastMCP(
        "video-analyzer",
        host=args.host,
        port=args.port,
    )

    @mcp.tool()
    def analyze_video_file(
        path: str,
        detail: str = "smart",
        focus: str = "",
        prompt_override: str = ""
    ) -> str:
        """
        分析视频内容。支持本地路径或 http(s) URL，支持时间聚焦。

        预计耗时：
        - < 1MB 视频 + brief: 约 30-60 秒
        - 1-10MB 视频 + smart: 约 1-3 分钟
        - 10-50MB 视频 + smart: 约 2-5 分钟
        - > 50MB 视频 + detailed/frames: 可能 5 分钟以上

        如果 Agent 配置的超时较短，建议先用 detail='brief' 快速预览。

        Args:
            path: 本地视频路径或 URL
            detail: 详细程度 — brief(最快) | smart(推荐) | detailed | frames(最慢)
            focus: 聚焦指令，如 "分析 0:15-0:25 的过渡动画"
            prompt_override: 完全自定义分析指令（可选，覆盖所有默认 prompt）

        Returns:
            JSON 字符串，包含 summary / key_moments / full_analysis_path 等
        """
        try:
            local_path = _download_if_url(path)

            if prompt_override:
                final_prompt = _build_focus_prompt(prompt_override, focus)
            else:
                base = DETAIL_PROMPTS.get(detail, DETAIL_PROMPTS["smart"])
                final_prompt = _build_focus_prompt(base, focus)

            result = analyze_video(
                local_path,
                detail=detail,
                prompt_override=final_prompt
            )
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                error_msg += (
                    "\n\n提示：视频分析耗时取决于文件大小和 detail 级别。"
                    "建议：1) 在 MCP 配置中增加 timeout（如 300 秒）；"
                    "2) 先用 detail='brief' 快速预览；"
                    "3) 缩短视频时长或压缩后再分析。"
                )
            return json.dumps({"error": error_msg, "path": path}, ensure_ascii=False, indent=2)

    if args.transport == "stdio":
        mcp.run()
    elif args.transport == "sse":
        print(f"Video Analyzer MCP Server starting on SSE mode at http://{args.host}:{args.port}/sse", file=sys.stderr)
        mcp.run(transport="sse")
    elif args.transport == "streamable-http":
        print(f"Video Analyzer MCP Server starting on Streamable HTTP mode at http://{args.host}:{args.port}/mcp", file=sys.stderr)
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
