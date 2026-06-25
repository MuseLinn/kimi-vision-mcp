#!/usr/bin/env python3
"""Vision-enabled MCP server backed by Kimi Code CLI (ACP) or OpenAI-compatible API.

Provider priority:
  1. Explicit env vars (VISION_API_KEY + VISION_BASE_URL + VISION_MODEL)
  2. MOONSHOT_API_KEY legacy
  3. kimi-code config.toml auto-discovery (vision-capable models)
  4. KimiACP (local kimi binary)
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP

from src.config import load_settings, list_vision_models
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
    """Lazily initialise the vision provider with cascading fallback."""
    global _provider_instance
    async with _provider_lock:
        if _provider_instance is not None:
            return _provider_instance

        # Try settings cascade (env → moonshot → kimi-code config.toml)
        try:
            settings = load_settings()
            provider = MoonshotProvider(
                api_key=settings.api_key,
                base_url=settings.base_url,
                model=settings.model,
                timeout=settings.timeout,
            )
            _provider_instance = provider
            print(
                f"🟢 provider: Moonshot ({settings.model}) [source={settings.source}]",
                file=sys.stderr,
            )
            return _provider_instance
        except ValueError:
            pass

        # Final fallback: KimiACP (no API key needed, uses local kimi binary)
        try:
            provider = KimiACPProvider()
            await provider.start()
            _provider_instance = provider
            print("🟢 provider: KimiACP (via kimi acp)", file=sys.stderr)
            return _provider_instance
        except Exception as exc:
            print(
                f"⚠️  KimiACP failed: {exc}.  Set MOONSHOT_API_KEY or configure "
                "a vision model in ~/.kimi-code/config.toml.",
                file=sys.stderr,
            )
            raise


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

    # ── Configuration tools ──────────────────────────────────────────

    @mcp.tool(
        name="vision_list_models",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
    )
    async def vision_list_models() -> str:
        """List all vision-capable models discovered from kimi-code config.toml.

        Shows provider, model name, display name, and vision capabilities.
        Use this to understand which vision models are available before calling
        other vision tools. To switch models, set VISION_MODEL env var.
        """
        try:
            models = list_vision_models()
            result = {
                "available_models": [
                    {
                        "model_id": c.model_id,
                        "provider": c.provider,
                        "model": c.model,
                        "display_name": c.display_name,
                        "capabilities": []
                        + (["image_in"] if c.has_image else [])
                        + (["video_in"] if c.has_video else []),
                    }
                    for c in models.candidates
                ],
                "selected": (
                    {
                        "model_id": models.selected.model_id,
                        "display_name": models.selected.display_name,
                    }
                    if models.selected
                    else None
                ),
                "hint": "To switch, set env: VISION_MODEL=<model_id> or VISION_API_KEY + VISION_BASE_URL + VISION_MODEL",
            }
            return _format(result)
        except Exception as e:
            return _format({"error": str(e)})

    @mcp.tool(
        name="vision_current_config",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
    )
    async def vision_current_config() -> str:
        """Show the current vision provider configuration.

        Displays which provider is active, the model in use, and source
        (env / moonshot / kimi-code config.toml).
        """
        try:
            settings = load_settings(require_key=False)
            return _format(
                {
                    "source": settings.source,
                    "model": settings.model or "(not configured)",
                    "base_url": settings.base_url or "(not configured)",
                    "has_api_key": bool(settings.api_key),
                    "timeout": settings.timeout,
                    "max_image_size_mb": settings.max_image_size_mb,
                    "max_video_size_mb": settings.max_video_size_mb,
                }
            )
        except Exception as e:
            return _format({"error": str(e)})

    # ── Vision analysis tools ────────────────────────────────────────

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
