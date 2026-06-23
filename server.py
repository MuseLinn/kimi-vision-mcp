#!/usr/bin/env python3
"""Vision-enabled MCP server backed by Kimi Code CLI (ACP) or Moonshot API."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP

from src.config import load_settings
from src.providers.kimi_acp import KimiACPProvider
from src.providers.moonshot import MoonshotProvider
from src.video.analyzer import AnalyzeVideoInput, analyze_video_file
from src.vision.tools import (
    AnalyzeDataVizInput,
    AnalyzeImageInput,
    DiagnoseErrorInput,
    ExtractTextInput,
    UIToArtifactInput,
    UIDiffInput,
    UnderstandDiagramInput,
    analyze_data_visualization,
    analyze_image,
    diagnose_error_screenshot,
    extract_text_from_screenshot,
    ui_diff_check,
    ui_to_artifact,
    understand_technical_diagram,
)

_provider_instance = None
_provider_lock = asyncio.Lock()


async def _get_provider():
    """Lazily initialise the vision provider.

    Priority:
    1. ``KimiACPProvider`` – if ``kimi`` binary is available (no API key needed)
    2. ``MoonshotProvider`` – if ``MOONSHOT_API_KEY`` is set
    """
    global _provider_instance
    async with _provider_lock:
        if _provider_instance is not None:
            return _provider_instance

        api_key = os.environ.get("MOONSHOT_API_KEY", "").strip()

        if not api_key:
            # Try ACP (Kimi Code CLI) — no API key required
            try:
                provider = KimiACPProvider()
                await provider.start()
                _provider_instance = provider
                print("🟢 provider: KimiACP (via kimi acp)", file=sys.stderr)
                return _provider_instance
            except Exception as exc:
                print(
                    f"⚠️  KimiACP failed: {exc}.  Set MOONSHOT_API_KEY for "
                    "Moonshot API fallback.",
                    file=sys.stderr,
                )
                raise

        # Fallback: Moonshot OpenAI-compatible API
        settings = load_settings()
        provider = MoonshotProvider(
            api_key=settings.api_key,
            base_url=settings.base_url,
            model=settings.model,
            timeout=settings.timeout,
        )
        _provider_instance = provider
        print(f"🟢 provider: Moonshot ({settings.model})", file=sys.stderr)
        return _provider_instance


def _format(result) -> str:
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False, indent=2)
    return str(result)


def main():
    parser = argparse.ArgumentParser(description="Vision-enabled MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
    )
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    mcp = FastMCP("kimi-vision", host=args.host, port=args.port)

    @mcp.tool(
        name="vision_ui_to_artifact",
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    async def vision_ui_to_artifact(params: UIToArtifactInput) -> str:
        """Convert a UI screenshot into code, prompt, spec, or description."""
        try:
            p = await _get_provider()
            return _format(await ui_to_artifact(p, params))
        except Exception as e:
            return _format({"error": str(e)})

    @mcp.tool(
        name="vision_extract_text",
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    async def vision_extract_text(params: ExtractTextInput) -> str:
        """Extract text from a screenshot (code, terminal, document, or general)."""
        try:
            p = await _get_provider()
            return _format(await extract_text_from_screenshot(p, params))
        except Exception as e:
            return _format({"error": str(e)})

    @mcp.tool(
        name="vision_diagnose_error",
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    async def vision_diagnose_error(params: DiagnoseErrorInput) -> str:
        """Analyze an error screenshot and propose actionable fixes."""
        try:
            p = await _get_provider()
            return _format(await diagnose_error_screenshot(p, params))
        except Exception as e:
            return _format({"error": str(e)})

    @mcp.tool(
        name="vision_understand_diagram",
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    async def vision_understand_diagram(params: UnderstandDiagramInput) -> str:
        """Interpret architecture, flow, UML, ER, or system diagrams."""
        try:
            p = await _get_provider()
            return _format(await understand_technical_diagram(p, params))
        except Exception as e:
            return _format({"error": str(e)})

    @mcp.tool(
        name="vision_analyze_data_viz",
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    async def vision_analyze_data_viz(params: AnalyzeDataVizInput) -> str:
        """Read charts/dashboards and surface insights."""
        try:
            p = await _get_provider()
            return _format(await analyze_data_visualization(p, params))
        except Exception as e:
            return _format({"error": str(e)})

    @mcp.tool(
        name="vision_ui_diff_check",
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    async def vision_ui_diff_check(params: UIDiffInput) -> str:
        """Compare two UI screenshots and flag visual or implementation drift."""
        try:
            p = await _get_provider()
            return _format(await ui_diff_check(p, params))
        except Exception as e:
            return _format({"error": str(e)})

    @mcp.tool(
        name="vision_analyze_image",
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    async def vision_analyze_image(params: AnalyzeImageInput) -> str:
        """General-purpose image understanding."""
        try:
            p = await _get_provider()
            return _format(await analyze_image(p, params))
        except Exception as e:
            return _format({"error": str(e)})

    @mcp.tool(
        name="vision_analyze_video",
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    async def vision_analyze_video(params: AnalyzeVideoInput) -> str:
        """Analyze a local or remote video."""
        try:
            p = await _get_provider()
            return _format(await analyze_video_file(p, params))
        except Exception as e:
            return _format({"error": str(e)})

    if args.transport == "stdio":
        mcp.run()
    elif args.transport == "sse":
        print(
            f"Server starting on SSE at http://{args.host}:{args.port}/sse",
            file=sys.stderr,
        )
        mcp.run(transport="sse")
    elif args.transport == "streamable-http":
        print(
            f"Server starting on Streamable HTTP at http://{args.host}:{args.port}/mcp",
            file=sys.stderr,
        )
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
