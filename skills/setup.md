---
name: setup
description: Install or reinstall the kimi-vision MCP server — registers with Claude Code and configures the Moonshot API key
---

# kimi-vision-mcp: Setup

Registers the Kimi-powered vision MCP server with Claude Code.

## Prerequisites

- Python 3.10+
- A [Moonshot API key](https://platform.moonshot.cn/)
- The repo cloned locally (already done if installed via garage)

## Usage

```bash
claude mcp add -s user kimi-vision \
  --env MOONSHOT_API_KEY=your_key_here \
  --env VISION_MODEL=kimi-k2.7-code \
  -- python /path/to/kimi-vision-mcp/server.py
```

Replace `/path/to/kimi-vision-mcp/` with the actual path (e.g. `$HOME/projects/kimi-vision-mcp/` on macOS/Linux or `C:/Users/you/projects/kimi-vision-mcp/` on Windows).

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MOONSHOT_API_KEY` | — | **Required.** Moonshot API key |
| `VISION_MODEL` | `kimi-k2.7-code` | Vision model to use |
| `VISION_BASE_URL` | `https://api.moonshot.ai/v1` | OpenAI-compatible base URL |
| `VISION_TIMEOUT` | `300` | API timeout in seconds |

## Tools Provided

| Tool | Purpose |
|---|---|
| `vision_analyze_image` | General-purpose image Q&A |
| `vision_extract_text` | OCR for code, terminals, documents |
| `vision_diagnose_error` | Analyze error screenshots |
| `vision_understand_diagram` | Architecture/flow/UML/ER diagrams |
| `vision_analyze_data_viz` | Charts and dashboards insights |
| `vision_ui_to_artifact` | UI screenshots → code/specs |
| `vision_ui_diff_check` | Compare before/after screenshots |
| `vision_analyze_video` | Video summary and key moments |
