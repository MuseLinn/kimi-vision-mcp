# Architecture

## Overview

`video-analyzer-mcp` is a Python-based MCP (Model Context Protocol) server that exposes vision-capable tools to MCP clients such as Claude Code and Claude Desktop. It uses the Moonshot / Kimi OpenAI-compatible API as its vision backend, enabling text-only models (e.g., DeepSeek) to understand images and videos through tool calls.

## Why This Architecture?

The original implementation invoked the local `kimi` CLI via `subprocess`. This refactor replaces that with direct HTTP API calls because:

- The local CLI interface is unstable across major versions.
- Direct API calls are easier to test, deploy, and observe.
- API mode supports multiple providers and custom endpoints with minimal change.

## Layers

```
┌─────────────────────────────────────────┐
│  MCP Client (Claude Code / Desktop)     │
└──────────────┬──────────────────────────┘
               │ stdio / SSE / Streamable HTTP
               ▼
┌─────────────────────────────────────────┐
│  server.py  (FastMCP)                   │
│  • tool registration                    │
│  • transport handling                   │
│  • error formatting                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  src/vision/tools.py + src/video/       │
│  • input validation (Pydantic)          │
│  • prompt construction                  │
│  • orchestration                        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  src/providers/moonshot.py              │
│  • OpenAI-compatible chat completions   │
│  • image_url / video_url content blocks │
└──────────────┬──────────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────────┐
│  Moonshot API (kimi-k2.7-code, etc.)    │
└─────────────────────────────────────────┘
```

## Shared Utilities

- `src/config.py` — environment-based configuration, validates required settings.
- `src/media.py` — loads local files or downloads URLs, validates size and MIME type, base64 encodes images/videos.
- `src/prompts.py` — system prompts and user prompt templates for each tool.

## Provider Abstraction

`src/providers/base.py` defines `VisionProvider`. The current implementation is `MoonshotProvider`, but the interface allows future providers (Gemini, OpenAI, etc.) to be added without changing the tool layer.

## Error Handling

Each MCP tool wraps its implementation in a try/except and returns a JSON object with an `error` field on failure. This prevents a single failed tool call from crashing the server and gives the client actionable feedback.
