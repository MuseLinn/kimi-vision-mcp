#!/usr/bin/env python3
"""Local installer / uninstaller for video-analyzer-mcp."""

import shutil
import sys
from pathlib import Path

PROJECT_DIR = Path.home() / "projects" / "video-analyzer-mcp"
MCP_DIR = Path.home() / ".mcp" / "video-analyzer"


def uninstall():
    print("🗑️  Uninstalling video-analyzer-mcp")
    for d in (PROJECT_DIR, MCP_DIR):
        if d.exists():
            shutil.rmtree(d)
            print(f"  Removed {d}")
    print("✅ Uninstalled. Remove the MCP config from your client manually.")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall()
    else:
        print("Usage: python install.py uninstall")


if __name__ == "__main__":
    main()
