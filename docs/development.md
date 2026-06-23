# Development Guide

## Setup

```bash
cd C:/Users/unive/projects/video-analyzer-mcp
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-asyncio respx ruff
```

## Run Tests

```bash
pytest tests/ -v
```

## Lint and Format

```bash
ruff check src tests server.py
ruff format src tests server.py
```

## Project Structure

| Path | Responsibility |
|------|----------------|
| `server.py` | FastMCP server entrypoint and tool registration |
| `src/config.py` | Environment-based configuration |
| `src/media.py` | File/URL loading, validation, base64 encoding |
| `src/prompts.py` | System prompts and prompt builders |
| `src/providers/` | Vision provider abstraction and implementations |
| `src/vision/tools.py` | Image analysis tools |
| `src/video/analyzer.py` | Video analysis tool |
| `tests/` | Unit tests |
| `evals/` | MCP evaluation cases |

## Adding a New Vision Tool

1. Define a Pydantic input model in `src/vision/tools.py`.
2. Implement an async function that takes `(VisionProvider, InputModel)`.
3. Register the tool in `server.py` with `@mcp.tool(...)`.
4. Add a test in `tests/test_vision_tools.py`.
5. Update `docs/tools.md` and `README.md`.

## Adding a New Provider

1. Create a class inheriting from `src.providers.base.VisionProvider`.
2. Implement `chat`, `analyze_image`, and `analyze_video`.
3. Update `src/providers/__init__.py`.
4. Add tests in `tests/test_providers.py`.
