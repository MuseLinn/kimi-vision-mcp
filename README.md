# video-analyzer-mcp

Vision-enabled MCP server powered by [Moonshot / Kimi API](https://platform.moonshot.cn/). Brings image and video understanding to MCP clients that use text-only models (e.g., DeepSeek inside Claude Code / Claude Desktop).

> This project is a refactor of the original `video-analyzer-mcp`, replacing the local `kimi` CLI dependency with direct Moonshot OpenAI-compatible API calls.

## Features

- 🖼️ **Image understanding** via Kimi K2.6 / K2.7 Code vision models
- 🎬 **Video analysis** with structured summaries
- 🧩 **Scenario-specific tools** inspired by [Z.AI GLM Vision MCP Server](https://docs.z.ai/devpack/mcp/vision-mcp-server):
  - `vision_ui_to_artifact` — turn UI screenshots into code/specs/prompts
  - `vision_extract_text` — OCR for code, terminals, documents
  - `vision_diagnose_error` — analyze error screenshots and suggest fixes
  - `vision_understand_diagram` — interpret architecture/flow/UML/ER diagrams
  - `vision_analyze_data_viz` — extract insights from charts and dashboards
  - `vision_ui_diff_check` — compare before/after screenshots
  - `vision_analyze_image` — general-purpose image Q&A
  - `vision_analyze_video` — video summary and key moments
- 🔌 **Multiple transports**: stdio, SSE, Streamable HTTP
- ⚙️ **Simple config**: only needs `MOONSHOT_API_KEY`

## Requirements

- Python 3.10+
- A [Moonshot API key](https://platform.moonshot.cn/)

## Quick Install

### macOS / Linux

```bash
bash install.sh
```

### Windows

```powershell
.\install.ps1
```

### Claude Code / Desktop (one-liner)

```bash
claude mcp add -s user video-analyzer \
  --env MOONSHOT_API_KEY=your_api_key \
  -- python C:/Users/unive/projects/video-analyzer-mcp/server.py
```

Replace `C:/Users/unive` with your actual home directory path on macOS/Linux.

## Manual Configuration

Add to your Claude Desktop / Claude Code MCP config:

```json
{
  "mcpServers": {
    "video-analyzer": {
      "type": "stdio",
      "command": "python",
      "args": ["C:/Users/unive/projects/video-analyzer-mcp/server.py"],
      "env": {
        "MOONSHOT_API_KEY": "your_api_key",
        "VISION_MODEL": "kimi-k2-6-code"
      }
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MOONSHOT_API_KEY` | — | **Required.** Moonshot API key |
| `VISION_MODEL` | `kimi-k2-6-code` | Vision model to use |
| `VISION_BASE_URL` | `https://api.moonshot.ai/v1` | OpenAI-compatible base URL |
| `VISION_TIMEOUT` | `300` | API timeout in seconds |
| `VISION_MAX_IMAGE_SIZE_MB` | `20` | Max image file size |
| `VISION_MAX_VIDEO_SIZE_MB` | `100` | Max video file size |

## Usage Example

In Claude Code or Claude Desktop:

```
Please use vision_analyze_image on /Users/me/screenshots/login.png and describe the layout.
```

```
Use vision_diagnose_error on /Users/me/screenshots/build_error.png to find why the build failed.
```

## Development

```bash
cd C:/Users/unive/projects/video-analyzer-mcp
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-asyncio respx ruff
pytest
ruff check src tests server.py
```

## Running with SSE or Streamable HTTP

```bash
# SSE
python server.py --transport sse --port 8000

# Streamable HTTP
python server.py --transport streamable-http --port 8000
```

## Uninstall

```bash
python install.py uninstall
```

## License

MIT
