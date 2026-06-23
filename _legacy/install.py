#!/usr/bin/env python3
"""
Video Analyzer MCP Server — 卸载脚本

用法:
    python install.py uninstall    # 卸载
"""

import sys
import shutil
from pathlib import Path

INSTALL_DIR = Path.home() / ".mcp" / "video-analyzer"


def cmd_uninstall():
    print("🗑️  Video Analyzer MCP Server — 卸载")
    print("=" * 50)
    
    if not INSTALL_DIR.exists():
        print("❌ 未找到安装目录，无需卸载")
        return
    
    confirm = input(f"\n确认删除 {INSTALL_DIR} 吗? [y/N]: ")
    if confirm.lower() != "y":
        print("已取消")
        return
    
    print(f"\n删除 {INSTALL_DIR}...")
    shutil.rmtree(INSTALL_DIR)
    print("✅ 已卸载")
    
    print("\n⚠️  请手动从 Agent 配置中删除 video-analyzer 相关配置")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        cmd_uninstall()
    else:
        print("Video Analyzer MCP Server — 卸载工具")
        print("")
        print("用法:")
        print("  python install.py uninstall")
        print("")
        print("或者使用一键卸载:")
        print("  curl -fsSL .../uninstall.sh | bash    # Linux/macOS")
        print("  irm .../uninstall.ps1 | iex            # Windows")


if __name__ == "__main__":
    main()
