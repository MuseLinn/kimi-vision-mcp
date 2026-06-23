#!/usr/bin/env bash
set -euo pipefail

# Video Analyzer MCP Server — Bash 卸载脚本
# 用法: curl -fsSL https://raw.githubusercontent.com/MuseLinn/video-analyzer-mcp/master/uninstall.sh | bash

INSTALL_DIR="$HOME/.mcp/video-analyzer"

info() { echo -e "\033[36m[INFO]\033[0m $*"; }
ok()   { echo -e "\033[32m[OK]\033[0m   $*"; }
warn() { echo -e "\033[33m[WARN]\033[0m $*"; }
err()  { echo -e "\033[31m[ERR]\033[0m  $*"; }

if [ ! -d "$INSTALL_DIR" ]; then
    info "未找到安装目录 $INSTALL_DIR，无需卸载"
    exit 0
fi

info "正在卸载 Video Analyzer MCP Server..."
rm -rf "$INSTALL_DIR"
ok "已删除 $INSTALL_DIR"

echo ""
warn "请手动从 Agent 配置中删除 video-analyzer 相关配置："
echo "  - ~/.opencode/opencode.jsonc"
echo "  - ~/.hermes/config.yaml"
echo "  - Claude Desktop / Cursor 配置"
