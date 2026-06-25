# kimi-vision-mcp

Vision-enabled MCP server backed by any OpenAI-compatible vision API. Brings image and video understanding to MCP clients that use text-only models (e.g., DeepSeek inside Claude Code / Claude Desktop).

## Features

- 🖼️ **Image understanding** — UI screenshots, diagrams, charts, error messages
- 🎬 **Video analysis** — structured summaries, key moments, scene-by-scene
- 🧩 **Scenario-specific tools** inspired by [Z.AI GLM Vision MCP Server](https://docs.z.ai/devpack/mcp/vision-mcp-server):
  - `vision_ui_to_artifact` — turn UI screenshots into code/specs/prompts
  - `vision_extract_text` — OCR for code, terminals, documents
  - `vision_diagnose_error` — analyze error screenshots and suggest fixes
  - `vision_understand_diagram` — interpret architecture/flow/UML/ER diagrams
  - `vision_analyze_data_viz` — extract insights from charts and dashboards
  - `vision_ui_diff_check` — compare before/after screenshots
  - `vision_analyze_image` — general-purpose image Q&A
  - `vision_analyze_video` — video summary and key moments
- 🔍 **`vision_list_models`** — list all available vision models
- ⚙️ **`vision_current_config`** — show active provider configuration
- 🔌 **Multiple transports**: stdio, SSE, Streamable HTTP

## Zero-Config Setup (kimi-code users)

If you have `~/.kimi-code/config.toml`, the MCP server **automatically discovers all vision-capable models** — no API keys or env vars needed for providers with direct keys.

```bash
# Just start the server — it reads your config.toml
python server.py
```

To set a default vision model, add to `~/.kimi-code/config.toml`:

```toml
[kimi-vision]
default_model = "opencode-go/mimo-v2.5"
timeout = 300
max_image_size_mb = 20
max_video_size_mb = 100
```

All fields are optional. Without `[kimi-vision]`, the first vision-capable model in your config is used.

## Configuration Priority

The server resolves the vision model in this order:

| Priority | Source | Example |
|----------|--------|---------|
| 1 | `VISION_API_KEY` + `VISION_BASE_URL` + `VISION_MODEL` env vars | Full manual control |
| 2 | `MOONSHOT_API_KEY` legacy env var | Moonshot API |
| 3 | `~/.kimi-code/config.toml` auto-discovery | Reads all `[providers.*]` and `[models.*]` sections |

Within config.toml, model selection follows:

| Priority | Source | Example |
|----------|--------|---------|
| 1 | `VISION_MODEL` env var | `opencode-go/mimo-v2.5` |
| 2 | `[kimi-vision] default_model` | `opencode-go/qwen3.5-plus` |
| 3 | First vision-capable model in config.toml | Auto |

## Environment Variables

All env vars are optional if `~/.kimi-code/config.toml` has a vision-capable model.

| Variable | Default | Description |
|----------|---------|-------------|
| `VISION_API_KEY` | — | API key (overrides provider in config.toml) |
| `VISION_BASE_URL` | — | OpenAI-compatible base URL |
| `VISION_MODEL` | — | Model ID (overrides `[kimi-vision] default_model`) |
| `MOONSHOT_API_KEY` | — | Legacy: Moonshot API key |
| `VISION_TIMEOUT` | `300` | API timeout in seconds |
| `VISION_MAX_IMAGE_SIZE_MB` | `20` | Max image file size |
| `VISION_MAX_VIDEO_SIZE_MB` | `100` | Max video file size |

## Requirements

- Python 3.10+
- Either:
  - `~/.kimi-code/config.toml` with a vision-capable provider, OR
  - A Moonshot API key (`MOONSHOT_API_KEY`), OR
  - Manual `VISION_API_KEY` + `VISION_BASE_URL` + `VISION_MODEL`

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
claude mcp add -s user kimi-vision \
  -- python /path/to/kimi-vision-mcp/server.py
```

No `--env` needed if `~/.kimi-code/config.toml` has vision models.

### Manual Configuration

```json
{
  "mcpServers": {
    "kimi-vision": {
      "type": "stdio",
      "command": "python",
      "args": ["/path/to/kimi-vision-mcp/server.py"],
      "env": {
        "VISION_MODEL": "opencode-go/mimo-v2.5"
      }
    }
  }
}
```

## MCP Tools

### Configuration

| Tool | Description |
|------|-------------|
| `vision_list_models` | List all vision-capable models discovered from config.toml |
| `vision_current_config` | Show current active provider and model |

### Vision Analysis

| Tool | Description |
|------|-------------|
| `vision_analyze_image` | General-purpose image understanding |
| `vision_ui_to_artifact` | Convert UI screenshot to code/spec/prompt |
| `vision_extract_text` | OCR for code, terminals, documents |
| `vision_diagnose_error` | Analyze error screenshots, suggest fixes |
| `vision_understand_diagram` | Interpret architecture/flow/UML/ER diagrams |
| `vision_analyze_data_viz` | Extract insights from charts/dashboards |
| `vision_ui_diff_check` | Compare two UI screenshots |
| `vision_analyze_video` | Video summary with key moments |

## Usage Example

In Claude Code or Claude Desktop:

```
Please use vision_analyze_image on /Users/me/screenshots/login.png and describe the layout.
```

```
Use vision_diagnose_error on /Users/me/screenshots/build_error.png to find why the build failed.
```

```
Use vision_list_models to see what vision models are available.
```

## Development

```bash
cd /path/to/kimi-vision-mcp
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-asyncio respx ruff
pytest
ruff check src tests server.py
```

## Running with SSE or Streamable HTTP

```bash
python server.py --transport sse --port 8000
python server.py --transport streamable-http --port 8000
```

## Uninstall

```bash
python install.py uninstall
```

## Documentation

- [Architecture](docs/architecture.md)
- [Tool Reference](docs/tools.md)
- [Development Guide](docs/development.md)

## License

MIT
