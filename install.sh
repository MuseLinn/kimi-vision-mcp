#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$HOME/projects/video-analyzer-mcp"
MCP_DIR="$HOME/.mcp/video-analyzer"

echo "🚀 Installing video-analyzer-mcp to $PROJECT_DIR"

PYTHON=$(command -v python || command -v python3 || true)
if [ -z "$PYTHON" ]; then
    echo "❌ Python not found. Please install Python 3.10+."
    exit 1
fi

if [ -d "$PROJECT_DIR/.git" ]; then
    echo "Updating existing repository..."
    cd "$PROJECT_DIR"
    git pull
else
    echo "Cloning repository..."
    mkdir -p "$(dirname "$PROJECT_DIR")"
    git clone https://github.com/MuseLinn/video-analyzer-mcp.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

$PYTHON -m pip install -r requirements.txt

mkdir -p "$MCP_DIR"
ln -sf "$PROJECT_DIR/server.py" "$MCP_DIR/server.py"

echo "✅ Installed. Add this MCP server to your client:"
echo ""
echo "Claude Code / Desktop:"
echo "  claude mcp add -s user video-analyzer --env MOONSHOT_API_KEY=your_key -- python $PROJECT_DIR/server.py"
echo ""
echo "Or add manually to your MCP config:"
echo "  command: python"
echo "  args: [$PROJECT_DIR/server.py]"
echo "  env: { MOONSHOT_API_KEY: your_key }"
